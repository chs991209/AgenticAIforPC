import json


def format_team_prompt(intent: str, keywords: list[str]) -> str:
    """
    Build the kickoff prompt that the orchestrator sees in a team.

    The keywords are JSON-encoded so that elements containing spaces
    (e.g. "아이브 뮤직 비디오", "Bruno Mars MV") survive intact through
    the LLM round-trip — agents must treat each array element as one
    atomic query.
    """
    if not keywords:
        return ""
    return f"intent: {intent}\nkeywords: {json.dumps(keywords, ensure_ascii=False)}"
