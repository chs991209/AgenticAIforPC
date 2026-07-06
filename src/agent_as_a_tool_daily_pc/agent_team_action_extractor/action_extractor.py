import re
import json


_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")
_TERMINATION_TOKEN = "CONTENTGENERATIONDONE"


def message_text(msg) -> str:
    """Best-effort text extraction from any autogen message type.

    Works for TextMessage (str content), tool messages whose `content`
    is callable, and structured payloads (falls back to str()).
    """
    content = getattr(msg, "content", None)
    if callable(content):
        content = content()
    if content is None:
        return ""
    return content if isinstance(content, str) else str(content)


def extract_final_answer(task_result) -> dict | None:
    """Extract the JSON action object from the most recent message that
    contains the termination token. Returns None if no such message exists
    or the embedded JSON is invalid.
    """
    messages = getattr(task_result, "messages", [])
    for msg in reversed(messages):
        content = message_text(msg)
        if _TERMINATION_TOKEN not in content:
            continue
        match = _JSON_BLOCK_RE.search(content)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        return obj if isinstance(obj, dict) else None
    return None
