import re
import json


def _msg_text(msg) -> str:
    content = getattr(msg, "content", None)
    if callable(content):
        content = content()
    if content is None:
        return ""
    return content if isinstance(content, str) else str(content)


def extract_final_answer(task_result) -> dict | None:
    """
    Extract the JSON action object from the most recent message that contains
    the 'CONTENTGENERATIONDONE' termination token. Returns None if not found
    or not valid JSON.
    """
    messages = getattr(task_result, "messages", [])
    for msg in reversed(messages):
        content = _msg_text(msg)
        if "CONTENTGENERATIONDONE" not in content:
            continue
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        return obj if isinstance(obj, dict) else None
    return None
