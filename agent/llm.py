"""Single provider-agnostic LLM call. Provider and model come from .env."""

from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _client():
    provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
    api_key = os.environ.get("API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("API_KEY is missing from .env")
    if provider != "openai":
        raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}. Add a branch in agent/llm.py.")
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def complete(messages: list[dict], temperature: float = 0.0, model: str | None = None) -> dict:
    """Return {text, tokens_in, tokens_out, latency_ms, model, provider}."""
    provider = os.environ.get("LLM_PROVIDER", "").strip()
    model = model or os.environ.get("LLM_MODEL", "").strip()
    if not model:
        raise RuntimeError("LLM_MODEL is missing from .env")
    client = _client()
    started = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    latency_ms = (time.perf_counter() - started) * 1000
    usage = resp.usage
    return {
        "text": (resp.choices[0].message.content or "").strip(),
        "tokens_in": int(getattr(usage, "prompt_tokens", 0) or 0),
        "tokens_out": int(getattr(usage, "completion_tokens", 0) or 0),
        "latency_ms": latency_ms,
        "model": model,
        "provider": provider,
    }
