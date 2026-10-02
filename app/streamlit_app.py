"""Read-only text-to-SQL analyst. Default graph = config D."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.graph import run_question
from eval.run_eval import inr_cost, load_pricing

st.set_page_config(page_title="Ad analyst (read-only)", layout="wide")

prices = load_pricing()

st.sidebar.title("Session")
st.sidebar.caption("Read-only DuckDB. Config D (calibrated prompts + few-shot).")
st.sidebar.divider()
if "last_latency" not in st.session_state:
    st.session_state.last_latency = None
    st.session_state.last_cost = None
    st.session_state.history = []

lat = st.session_state.last_latency
cost = st.session_state.last_cost
st.sidebar.metric("Last latency", f"{lat:.0f} ms" if lat is not None else "—")
st.sidebar.metric("Last cost", f"₹{cost:.4f}" if cost is not None else "—")
st.sidebar.caption(
    "₹ uses official gpt-4o-mini prices in `eval/pricing.yaml` "
    f"({prices.get('USD_PER_1M_INPUT_TOKENS')}/{prices.get('USD_PER_1M_OUTPUT_TOKENS')} "
    f"USD per 1M, USDINR {prices.get('USD_TO_INR')})."
)

st.title("Criteo warehouse analyst")
st.warning(
    "This agent can only run a single SELECT. It will refuse INSERT/UPDATE/DELETE/DROP "
    "and anything that is not in the warehouse."
)

q = st.chat_input("Ask a question about the warehouse")
if q:
    with st.spinner("Running config D…"):
        state = run_question(q, config="D")
    cost_inr = inr_cost(int(state.get("tokens_in") or 0), int(state.get("tokens_out") or 0), prices)
    st.session_state.last_latency = state.get("latency_ms")
    st.session_state.last_cost = cost_inr
    st.session_state.history.append({"q": q, "state": state, "cost": cost_inr})

for turn in st.session_state.history:
    state = turn["state"]
    with st.chat_message("user"):
        st.write(turn["q"])
    with st.chat_message("assistant"):
        status = state.get("status") or "—"
        assumption = state.get("assumption") or ""
        st.markdown(f"**Status:** `{status}`")
        if assumption:
            st.markdown(f"**Assumption:** {assumption}")
        elif status == "ANSWERED":
            st.caption("Assumption: (none recorded)")
        st.write(state.get("answer") or "")
        with st.expander("SQL"):
            st.code(state.get("sql") or "", language="sql")
        df = state.get("result_df")
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.dataframe(df, use_container_width=True)
            spec = state.get("chart_spec") or {}
            kind = spec.get("chart") or "table"
            x, y = spec.get("x"), spec.get("y")
            if kind == "bar" and x in df.columns and y in df.columns:
                st.plotly_chart(px.bar(df, x=x, y=y), use_container_width=True)
            elif kind == "line" and x in df.columns and y in df.columns:
                st.plotly_chart(px.line(df, x=x, y=y), use_container_width=True)
        st.caption(
            f"{state.get('latency_ms', 0):.0f} ms · "
            f"₹{(turn['cost'] if turn['cost'] is not None else 0):.4f} · "
            f"{state.get('tokens_in', 0)} / {state.get('tokens_out', 0)} tokens"
        )
