import functools
import os
from typing import Any

from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-2.5-flash"

_GEMINI_INFO = ModelInfo(
    vision=True,
    function_calling=True,
    json_output=True,
    family=ModelFamily.UNKNOWN,
    structured_output=True,
    multiple_system_messages=True,
)


@functools.cache
def _client(temperature: float) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL,
        model_info=_GEMINI_INFO,
        temperature=temperature,
    )


_VALID_NAMES = {f"gemini_client0{i}": i / 10 for i in range(5)}


def __getattr__(name: str) -> Any:
    if name in _VALID_NAMES:
        return _client(_VALID_NAMES[name])
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted({*globals(), *_VALID_NAMES})
