"""Thin OpenAI-compatible client for the shared Dojo LLM gateway.

The workshop routes every model call through ONE gateway (a LiteLLM proxy) so
attendees never handle real provider keys, and you can cap spend and rate-limit.
The gateway speaks the OpenAI API, so this same client reaches Claude Opus 5,
GPT-6, Gemini 3.x, etc. via the model aliases configured on the gateway.

Environment (set as Codespaces secrets, not committed):
  DOJO_API_BASE_URL   e.g. https://your-gateway.example/v1
  DOJO_API_KEY        session-scoped key issued by the facilitator

If neither is set, gateway_configured() returns False and the belts fall back to
their offline / mock paths, so everything still runs with no keys.
"""
from __future__ import annotations

import os

# Auto-load a .env in the repo root if present, so attendees can set the gateway
# keys with a single pasted line (DOJO_API_BASE_URL / DOJO_API_KEY) and nothing else.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

MODEL_ALIASES = {"opus": "claude-opus-5", "gpt": "gpt-6", "gemini": "gemini-3"}


def gateway_configured() -> bool:
    return bool(os.getenv("DOJO_API_BASE_URL") and os.getenv("DOJO_API_KEY"))


def complete(prompt: str, model: str = "opus", system: str | None = None,
             temperature: float = 0.2, max_tokens: int = 1500) -> str:
    """Send one chat completion through the gateway and return the text."""
    if not gateway_configured():
        raise RuntimeError(
            "LLM gateway not configured: set DOJO_API_BASE_URL and DOJO_API_KEY "
            "(see facilitator/api_gateway.md), or use the offline/mock path."
        )
    from openai import OpenAI  # LiteLLM gateway is OpenAI-compatible

    client = OpenAI(base_url=os.environ["DOJO_API_BASE_URL"],
                    api_key=os.environ["DOJO_API_KEY"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    # DOJO_MODEL lets you force a real model name (e.g. when pointing straight at
    # OpenAI/Anthropic for a local test) without editing the aliases above.
    model_name = os.getenv("DOJO_MODEL") or MODEL_ALIASES.get(model, model)
    params = {"model": model_name, "messages": messages,
              "temperature": temperature, "max_tokens": max_tokens}

    # Some newer models reject certain params over the OpenAI-compatible API
    # (e.g. 'temperature is deprecated', or they want 'max_completion_tokens').
    # Strip/rename the offending param and retry, so any model just works.
    for _ in range(4):
        try:
            resp = client.chat.completions.create(**params)
            return resp.choices[0].message.content or ""
        except Exception as e:  # openai.BadRequestError and friends
            msg = str(e).lower()
            if "temperature" in msg and "temperature" in params:
                params.pop("temperature"); continue
            if "max_tokens" in msg and "max_tokens" in params:
                params["max_completion_tokens"] = params.pop("max_tokens"); continue
            raise
    # last attempt (let any error surface)
    resp = client.chat.completions.create(**params)
    return resp.choices[0].message.content or ""
