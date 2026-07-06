from autogen_agentchat.agents import AssistantAgent, UserProxyAgent

from src.agent_as_a_tool_daily_pc.LLM_models.openai_models import (
    model_client00 as openai_model_client00,
    model_client01 as openai_model_client01,
    model_client02 as openai_model_client02,
    model_client03 as openai_model_client03,
    model_client04 as openai_model_client04,
)
from src.agent_as_a_tool_daily_pc.LLM_models.gemini_models import (
    gemini_client00 as gemini_model_client00,
    gemini_client01 as gemini_model_client01,
    gemini_client02 as gemini_model_client02,
    gemini_client03 as gemini_model_client03,
    gemini_client04 as gemini_model_client04,
)
from src.agent_as_a_tool_daily_pc.LLM_models.claude_models import (
    claude_client00 as claude_model_client00,
    claude_client01 as claude_model_client01,
    claude_client02 as claude_model_client02,
    claude_client03 as claude_model_client03,
    claude_client04 as claude_model_client04,
)


# ORIGINAL SYSTEM MESSAGE (kept for reference) — replaced because:
#   - the two-stage protocol was described as parallel obligations, not as a state machine,
#     so the model would compress fan-out and termination into a single first-turn reply
#   - the "Once you receive the validated URLs" qualifier was soft; the "You MUST append
#     ... at the very end of your message" sentence read as universal and dominated
#   - there was no explicit way to disambiguate turn-1 vs turn-N (no source-based switch)
#
# system_message_original = """
#     [ROLE]
#     Orchestrator Node. You manage parallel execution state and final payload delivery for the downstream ActionGeneratorAgent. You do not execute tools.
#
#     [ROUTING PROTOCOL]
#     1. FAN-OUT DELEGATION: Extract all search keywords from the user prompt. Pass the entire list of keywords in a single message and explicitly output the string "youtube_video_search_agent" to trigger parallel tool execution.
#     2. FAN-IN AGGREGATION: Await the validated URL array from the validator node.
#
#     [TERMINATION CONTRACT]
#     Once you receive the validated URLs, output them as a strict JSON object: {"open_webbrowser": ["url1", "url2"]}.
#     You MUST append the exact string "CONTENTGENERATIONDONE" at the very end of your message to cleanly terminate the session state.
# """

youtube_video_play_planning_agent = AssistantAgent(
    name="youtube_video_play_planning_agent",
    # Planner must hold a strict STATE A / STATE B machine. Claude is too
    # conversational for this role — it asks clarifying questions instead of
    # silently re-emitting JSON. Keep on OpenAI for deterministic routing.
    model_client=openai_model_client00,
    # model_client=claude_model_client00,
    system_message="""You are the orchestrator for the YouTube playback team. You do NOT call tools. You route work between sub-agents and emit the final payload.

Your behavior depends ENTIRELY on the SOURCE of the most recent message in the conversation. There are exactly two states. Never combine them.

============================================================
STATE A — most recent message source is `user`
============================================================
This is the FAN-OUT phase.

The user message has this shape (two lines):
  intent: <one word>
  keywords: ["keyword 1", "keyword 2", ...]

The `keywords` value is a JSON array. Each element is ONE atomic search query, even if it contains spaces.

DO, in this exact order:
  1. Output the keywords JSON array on a single line, EXACTLY as you received it — same elements, same order, same quoting, no edits.
  2. On a new line, output exactly: youtube_video_search_agent

DO NOT, under any circumstances on this turn:
  - DO NOT split, merge, translate, paraphrase, or reorder any element of the array.
  - DO NOT output the string `CONTENTGENERATIONDONE`.
  - DO NOT output any object like `{"open_webbrowser": ...}`.
  - DO NOT mention `youtube_video_url_validate_agent`.

============================================================
STATE B — most recent message source is `youtube_video_url_validate_agent`
============================================================
This is the FAN-IN / TERMINATION phase.

The validator's message contains a JSON array of YouTube watch URLs (possibly empty).

DO, in this exact order:
  1. Output exactly one JSON object on its own line:
     {"open_webbrowser": ["url1", "url2", ...]}
     If the validator returned an empty array, output: {"open_webbrowser": []}
  2. On the next line, output exactly: CONTENTGENERATIONDONE

DO NOT, under any circumstances on this turn:
  - DO NOT call any agent by name.
  - DO NOT add any text after `CONTENTGENERATIONDONE`.
  - DO NOT wrap the JSON in markdown code fences.

============================================================
If neither state applies, output nothing.
"""
)

