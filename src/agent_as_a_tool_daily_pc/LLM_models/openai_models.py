from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import _model_info as _ai_info
from dotenv import load_dotenv
import os

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

model_client00 = OpenAIChatCompletionClient(
    model="gpt-5.4-nano", api_key=API_KEY, temperature=0.0
)
model_client01 = OpenAIChatCompletionClient(
    model="gpt-5.4-nano", api_key=API_KEY, temperature=0.1
)
model_client02 = OpenAIChatCompletionClient(
    model="gpt-5.4-nano", api_key=API_KEY, temperature=0.2
)
model_client03 = OpenAIChatCompletionClient(
    model="gpt-5.4-nano", api_key=API_KEY, temperature=0.3
)
model_client04 = OpenAIChatCompletionClient(
    model="gpt-5.4-nano", api_key=API_KEY, temperature=0.4
)
