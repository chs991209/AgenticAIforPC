import functools
import os
from typing import Any

from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import _model_info as _ai_info
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

_GPT_54_NANO_DATED = "gpt-5.4-nano-2026-03-17"
_ai_info._MODEL_POINTERS.setdefault("gpt-5.4-nano", _GPT_54_NANO_DATED)
_ai_info._MODEL_INFO.setdefault(_GPT_54_NANO_DATED, ModelInfo(
    vision=True,
    function_calling=True,
    json_output=True,
    family=ModelFamily.GPT_5,
    structured_output=True,
    multiple_system_messages=True,
))
_ai_info._MODEL_TOKEN_LIMITS.setdefault(_GPT_54_NANO_DATED, 400_000)


@functools.cache
def _client(temperature: float) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model="gpt-5.4-nano", api_key=API_KEY, temperature=temperature
    )


# Lazy attribute access: `from openai_models import model_client03` returns a
# client built on first reference and cached thereafter. Clients no agent
# imports are never instantiated.
_VALID_NAMES = {f"model_client0{i}": i / 10 for i in range(5)}


def __getattr__(name: str) -> Any:
    if name in _VALID_NAMES:
        return _client(_VALID_NAMES[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted({*globals(), *_VALID_NAMES})
