from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

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

gemini_client00 = OpenAIChatCompletionClient(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL,
    model_info=_GEMINI_INFO,
    temperature=0.0,
)
gemini_client01 = OpenAIChatCompletionClient(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL,
    model_info=_GEMINI_INFO,
    temperature=0.1,
)
gemini_client02 = OpenAIChatCompletionClient(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL,
    model_info=_GEMINI_INFO,
    temperature=0.2,
)
gemini_client03 = OpenAIChatCompletionClient(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL,
    model_info=_GEMINI_INFO,
    temperature=0.3,
)
gemini_client04 = OpenAIChatCompletionClient(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_BASE_URL,
    model_info=_GEMINI_INFO,
    temperature=0.4,
)
