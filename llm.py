"""llm.py - the ONE place where our code talks to an AI model.

FDE habit #1: put every call to an outside service behind a single function.
That is exactly why adding a second provider (OpenAI) only touched this file:
the six patterns never know or care which AI is answering.

Providers:  "anthropic" (Claude)  and  "openai".
  * The visitor can pick one, or we guess from the key: keys starting "sk-ant-" are
    Claude keys; other "sk-" keys are OpenAI keys.
  * Models are set by environment variables (no code edits):
        CLAUDE_MODEL  (default claude-sonnet-4-5)
        OPENAI_MODEL  (default gpt-4o-mini  -> change it to the model your key can use)

DEMO MODE: no key -> fake answers, free, so the wiring can be tested.

BRING-YOUR-OWN-KEY: each web visitor's key lives in a "context variable", a sticky note
that belongs to ONE visitor's run only. We never write keys to disk or logs.
"""
import contextvars
import json
import os
import time
import urllib.error
import urllib.request

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-5")           # Claude model
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")           # OpenAI model
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

_api_key: contextvars.ContextVar = contextvars.ContextVar("api_key", default=None)
_provider: contextvars.ContextVar = contextvars.ContextVar("provider", default=None)
_force_demo: contextvars.ContextVar = contextvars.ContextVar("force_demo", default=False)


class LLMError(Exception):
    """An error from the AI service. `status` is the HTTP code (401 = bad key, 429 = limit...)."""

    def __init__(self, status: int, detail: str = ""):
        super().__init__(f"AI service returned HTTP {status}")
        self.status = status
        self.detail = detail  # kept for debugging, never shown to users (may echo part of a key)


def set_api_key(key: str | None):
    """Remember this visitor's key for the current run only."""
    return _api_key.set((key or "").strip() or None)


def set_provider(provider: str | None) -> None:
    """'anthropic', 'openai', or anything else = guess from the key."""
    _provider.set(provider if provider in ("anthropic", "openai") else None)


def force_demo() -> None:
    """Web app: if a visitor gave no key, stay in demo mode. Never fall back to the HOST's
    own key, or the seller would silently pay for visitors' usage."""
    _force_demo.set(True)


def current_key() -> str | None:
    typed = _api_key.get()
    if typed or _force_demo.get():
        return typed
    wanted = _provider.get()
    if wanted == "openai":
        return os.environ.get("OPENAI_API_KEY")
    if wanted == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY")
    return os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")


def current_provider() -> str | None:
    key = current_key()
    if key is None:
        return None
    if _provider.get():
        return _provider.get()
    if _api_key.get():  # a key the visitor typed: guess from its look
        return "openai" if key.startswith("sk-") and not key.startswith("sk-ant-") else "anthropic"
    return "anthropic" if key == os.environ.get("ANTHROPIC_API_KEY") else "openai"


def active_model() -> str:
    return OPENAI_MODEL if current_provider() == "openai" else MODEL


def is_mock() -> bool:
    return current_key() is None


def _call_openai(key: str, system: str, user: str, max_tokens: int) -> str:
    """Call OpenAI's chat endpoint with plain HTTPS (no extra package to install)."""
    body = json.dumps({
        "model": OPENAI_MODEL,
        "max_completion_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(
        OPENAI_BASE_URL.rstrip("/") + "/chat/completions", data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as err:
        raise LLMError(err.code, err.read().decode(errors="replace")[:300]) from None
    except urllib.error.URLError as err:
        raise LLMError(0, str(err.reason)) from None
    return data["choices"][0]["message"]["content"] or ""


def _call_anthropic(key: str, system: str, user: str, max_tokens: int) -> str:
    import anthropic  # imported here so demo mode works without the package

    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                  messages=[{"role": "user", "content": user}])
    return resp.content[0].text


def call_llm(system: str, user: str, max_tokens: int = 1500, retries: int = 3) -> str:
    """Send one request to the chosen AI and return the text answer."""
    key = current_key()
    if key is None:
        # Fake answer that echoes the role, so you can see data flowing through.
        return f"[MOCK ANSWER]\nRole: {system[:70]}...\nInput seen: {user[:90]}..."

    send = _call_openai if current_provider() == "openai" else _call_anthropic
    for attempt in range(1, retries + 1):
        try:
            return send(key, system, user, max_tokens)
        except Exception as err:  # network blip, rate limit, bad key...
            status = getattr(err, "status", None) or getattr(err, "status_code", None)
            print(f"  ! call failed (attempt {attempt}/{retries}): {type(err).__name__} {status or ''}")
            no_credit = status == 429 and "insufficient_quota" in str(getattr(err, "detail", ""))
            if attempt == retries or status in (400, 401, 403, 404) or no_credit:  # retrying will not help
                raise
            time.sleep(2 * attempt)  # wait a little longer each time
