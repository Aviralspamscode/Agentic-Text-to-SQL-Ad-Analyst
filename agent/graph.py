"""LangGraph text-to-SQL agent."""

from __future__ import annotations

import json
import re
import time
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agent.llm import complete
from agent.prompts import (
    ANSWER_CALIBRATED,
    ANSWER_SYSTEM,
    GENERATE_CALIBRATED,
    GENERATE_SYSTEM,
    PLAN_SYSTEM,
    REPAIR_SYSTEM,
)
from agent.tools import execute_sql, retrieve_fewshot, retrieve_schema, validate_sql
from eval.compare import SQL_STATUS, normalize_status


class AgentState(TypedDict, total=False):
    question: str
    config: str
    model: str
    retrieved_schema: str
    plan: str
    sql: str
    validation_error: str
    result_df: Any
    attempts: int
    answer: str
    chart_spec: dict
    tokens_in: int
    tokens_out: int
    latency_ms: float
    node_logs: list
    refused: bool
    status: str
    assumption: str


def _add_usage(state: AgentState, node: str, payload: dict) -> None:
    state["tokens_in"] = int(state.get("tokens_in") or 0) + payload.get("tokens_in", 0)
    state["tokens_out"] = int(state.get("tokens_out") or 0) + payload.get("tokens_out", 0)
    logs = list(state.get("node_logs") or [])
    logs.append(
        {
            "node": node,
            "tokens_in": payload.get("tokens_in", 0),
            "tokens_out": payload.get("tokens_out", 0),
            "latency_ms": payload.get("latency_ms", 0),
        }
    )
    state["node_logs"] = logs


def retrieve_node(state: AgentState) -> AgentState:
    t0 = time.perf_counter()
    cfg = state.get("config") or "B"
    schema = retrieve_schema(state["question"], config=cfg)
    if cfg in {"C", "D", "E", "F"}:
        schema = schema + "\n\n" + retrieve_fewshot(state["question"])
    state["retrieved_schema"] = schema
    state["attempts"] = 0
    state["tokens_in"] = state.get("tokens_in") or 0
    state["tokens_out"] = state.get("tokens_out") or 0
    state["node_logs"] = list(state.get("node_logs") or [])
    state["node_logs"].append(
        {"node": "retrieve_schema", "tokens_in": 0, "tokens_out": 0, "latency_ms": (time.perf_counter() - t0) * 1000}
    )
    return state


def _model(state: AgentState) -> str | None:
    return state.get("model") or None


def _gen_system(state: AgentState) -> str:
    return GENERATE_CALIBRATED if (state.get("config") or "") in {"D", "E", "F"} else GENERATE_SYSTEM


def _answer_system(state: AgentState) -> str:
    return ANSWER_CALIBRATED if (state.get("config") or "") in {"D", "E", "F"} else ANSWER_SYSTEM


_DESTRUCTIVE = re.compile(
    r"\b(insert|update|delete|drop|truncate|alter|create|reload|erase|wipe)\b",
    re.IGNORECASE,
)


def plan_node(state: AgentState) -> AgentState:
    if _DESTRUCTIVE.search(state.get("question") or ""):
        state["plan"] = "REFUSE"
        state["node_logs"] = list(state.get("node_logs") or [])
        state["node_logs"].append({"node": "plan", "tokens_in": 0, "tokens_out": 0, "latency_ms": 0})
        return state
    out = complete(
        [
            {"role": "system", "content": PLAN_SYSTEM},
            {
                "role": "user",
                "content": f"Schema:\n{state['retrieved_schema']}\n\nQuestion:\n{state['question']}",
            },
        ],
        temperature=0.0,
        model=_model(state),
    )
    _add_usage(state, "plan", out)
    state["plan"] = out["text"]
    return state


def generate_node(state: AgentState) -> AgentState:
    if (state.get("config") or "") in {"D", "E", "F"} and _DESTRUCTIVE.search(state.get("question") or ""):
        state["sql"] = "REFUSE"
        return state
    plan = state.get("plan") or ""
    user = f"Schema:\n{state['retrieved_schema']}\n\nQuestion:\n{state['question']}"
    if plan:
        user += f"\n\nPlan:\n{plan}"
    out = complete(
        [
            {"role": "system", "content": _gen_system(state)},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        model=_model(state),
    )
    _add_usage(state, "generate_sql", out)
    state["sql"] = out["text"]
    return state


def validate_node(state: AgentState) -> AgentState:
    clean, err = validate_sql(state.get("sql") or "")
    if err:
        state["validation_error"] = err
        state["sql"] = state.get("sql") or ""
        return state
    state["sql"] = clean or ""
    state["validation_error"] = ""
    if clean and clean.upper() in SQL_STATUS:
        state["refused"] = True
        state["status"] = SQL_STATUS[clean.upper()]
    return state


def execute_node(state: AgentState) -> AgentState:
    if state.get("refused") or (state.get("sql") or "").upper() in SQL_STATUS:
        state["result_df"] = None
        return state
    try:
        state["result_df"] = execute_sql(state["sql"])
        state["validation_error"] = ""
    except Exception as exc:  # noqa: BLE001
        state["validation_error"] = f"execution error: {exc}"
        state["result_df"] = None
    return state


def repair_node(state: AgentState) -> AgentState:
    state["attempts"] = int(state.get("attempts") or 0) + 1
    out = complete(
        [
            {"role": "system", "content": REPAIR_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Schema:\n{state['retrieved_schema']}\n\nQuestion:\n{state['question']}\n\n"
                    f"SQL:\n{state.get('sql')}\n\nError:\n{state.get('validation_error')}"
                ),
            },
        ],
        temperature=0.0,
        model=_model(state),
    )
    _add_usage(state, "repair", out)
    state["sql"] = out["text"]
    return state


def answer_node(state: AgentState) -> AgentState:
    token = (state.get("sql") or "").strip().upper()
    if state.get("refused") or token in SQL_STATUS:
        preview = f"No query was run. Token={token or state.get('status')}."
    elif state.get("result_df") is None:
        preview = f"No result. Last error: {state.get('validation_error')}"
    else:
        df = state["result_df"].copy()
        from agent.tools import LABEL_COLUMNS

        for col in df.columns:
            if col.lower() in LABEL_COLUMNS:
                df[col] = df[col].map(lambda v: f"label:{v}" if v is not None else v)
        preview = df.head(20).to_csv(index=False)
    out = complete(
        [
            {"role": "system", "content": _answer_system(state)},
            {
                "role": "user",
                "content": f"Question: {state['question']}\n\nResult table:\n{preview}",
            },
        ],
        temperature=0.0,
        model=_model(state),
    )
    _add_usage(state, "answer", out)
    text = out["text"]
    chart = {"chart": "table", "x": None, "y": None}
    assumption = ""
    parsed_status = None
    if "{" in text:
        try:
            blob = text[text.index("{") : text.rindex("}") + 1]
            meta = json.loads(blob)
            chart = {
                "chart": meta.get("chart", "table"),
                "x": meta.get("x"),
                "y": meta.get("y"),
            }
            assumption = str(meta.get("assumption") or "")
            parsed_status = normalize_status(meta.get("status"))
            text = text[: text.index("{")].strip()
        except (ValueError, json.JSONDecodeError):
            pass
    if token in SQL_STATUS:
        status = SQL_STATUS[token]
    elif parsed_status:
        status = parsed_status
    elif state.get("result_df") is not None:
        status = "ANSWERED"
    else:
        status = "NOT_IN_DATA"
    state["answer"] = text
    state["chart_spec"] = chart
    state["status"] = status
    state["assumption"] = assumption
    return state


def _after_validate(state: AgentState) -> str:
    if state.get("validation_error"):
        return "repair" if int(state.get("attempts") or 0) < 2 else "answer"
    return "execute"


def _after_execute(state: AgentState) -> str:
    if state.get("validation_error"):
        return "repair" if int(state.get("attempts") or 0) < 2 else "answer"
    return "answer"


def _after_repair(state: AgentState) -> str:
    return "validate"


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("retrieve_schema", retrieve_node)
    g.add_node("generate_sql", generate_node)
    g.add_node("validate", validate_node)
    g.add_node("execute", execute_node)
    g.add_node("repair", repair_node)
    g.add_node("answer", answer_node)
    g.add_node("plan", plan_node)
    g.add_edge(START, "retrieve_schema")
    g.add_conditional_edges(
        "retrieve_schema",
        lambda s: "plan" if (s.get("config") or "") in {"E", "F"} else "generate_sql",
    )
    g.add_edge("plan", "generate_sql")
    g.add_edge("generate_sql", "validate")
    g.add_conditional_edges("validate", _after_validate)
    g.add_conditional_edges("execute", _after_execute)
    g.add_conditional_edges("repair", _after_repair)
    g.add_edge("answer", END)
    return g.compile()


_APP = None


def run_question(question: str, config: str = "B", model: str | None = None) -> AgentState:
    global _APP
    t0 = time.perf_counter()
    if _APP is None:
        _APP = build_graph()
    state: AgentState = {"question": question, "config": config}
    if model:
        state["model"] = model
    result = _APP.invoke(state)
    result["latency_ms"] = (time.perf_counter() - t0) * 1000
    return result
