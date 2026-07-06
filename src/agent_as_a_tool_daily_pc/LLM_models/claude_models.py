import functools
import os
from typing import Any

from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Default to Haiku 4.5 — cheapest tier, matches the router/extractor workload
# (temp=0, strict output formats). Swap to "claude-sonnet-4-6" or
# "claude-opus-4-7" if a specific agent needs stronger reasoning.
# CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
# CLAUDE_MODEL = "claude-opus-4-8"

# Claude 4.5/4.6/4.7 are newer than autogen-ext 0.7.5's built-in registry, so
# capability info is passed explicitly on every client (same pattern as Gemini).
_CLAUDE_INFO = ModelInfo(
    vision=True,
    function_calling=True,
    json_output=True,
    family=ModelFamily.UNKNOWN,
    structured_output=True,
    multiple_system_messages=False,  # Anthropic models take a single system prompt
)


# Claude 4.5+ models (sonnet-4-6, opus-4-7, opus-4-8) deprecated the
# `temperature` sampling parameter — sending it returns a 400. Older models
# (e.g. claude-haiku-3-* and earlier) still accept it. Names listed here are
# omitted from the request payload.
_MODELS_WITHOUT_TEMPERATURE: frozenset[str] = frozenset({
    "claude-sonnet-4-6",
    "claude-opus-4-7",
    "claude-opus-4-8",
})


def _accepts_temperature(model: str) -> bool:
    return model not in _MODELS_WITHOUT_TEMPERATURE


@functools.cache
def _build_client(temperature: float | None) -> AnthropicChatCompletionClient:
    kwargs: dict[str, Any] = {
        "model": CLAUDE_MODEL,
        "api_key": ANTHROPIC_API_KEY,
        "model_info": _CLAUDE_INFO,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    return AnthropicChatCompletionClient(**kwargs)


def _client(temperature: float) -> AnthropicChatCompletionClient:
    """Return a cached Claude client. For models that no longer accept
    `temperature`, the parameter is dropped and every `claude_client0X`
    name resolves to the same cached instance.
    """
    effective = temperature if _accepts_temperature(CLAUDE_MODEL) else None
    return _build_client(effective)


# Explicit temperature mapping — edit a value to retune a specific client without
# touching the agents that depend on it. Lazy: only the clients you import are built.
_VALID_NAMES: dict[str, float] = {
    "claude_client00": 0.0,
    "claude_client01": 0.1,
    "claude_client02": 0.2,
    "claude_client03": 0.3,
    "claude_client04": 0.4,
}


def __getattr__(name: str) -> Any:
    if name in _VALID_NAMES:
        return _client(_VALID_NAMES[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted({*globals(), *_VALID_NAMES})
