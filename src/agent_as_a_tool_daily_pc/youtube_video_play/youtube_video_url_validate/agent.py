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
#   - "if videoId is non-unique-id_string" is grammatically and semantically unclear
#   - no concrete definition of a valid videoId (length, charset)
#   - no negative guards against emitting CONTENTGENERATIONDONE or final JSON
#
# system_message_original = """
#     [ROLE]
#     Payload Validator and Transformer Node.
#
#     [TRANSFORMATION PROTOCOL]
#     1. PARSING: Analyze the batched search results provided by the search node.
#     2. EXTRACTION: For each keyword's result, extract ONLY the first 'videoId'.
#     3. MAPPING: Transform each 'videoId' into the strict format: "https://www.youtube.com/watch?v=<videoId>". Silently drop any failed searches(and if videoId is non-unique-id_string) or empty results.
#     4. STATE RETURN: Output the final list of validated URLs and explicitly append the string "youtube_video_play_planning_agent" to return control to the orchestrator.
# """

youtube_video_url_validate_agent = AssistantAgent(
    name="youtube_video_url_validate_agent",
    # model_client=openai_model_client00,
    model_client=claude_model_client00,
    system_message="""You collect YouTube watch URLs from the search tool's results.

[INPUT]
The conversation history contains one or more `search_youtube_videos` tool results produced by `youtube_video_search_agent`. Each tool result has the shape:
  {"query": "<original keyword>", "videos": [{"videoId": "<11-char id>", "title": "<title>"}, ...]}

The tool has ALREADY filtered out channels and playlists. Every videoId is guaranteed to be an 11-character string from [A-Za-z0-9_-].

[TRANSFORMATION]
Process the tool results IN THE ORDER they appear in the conversation. For each tool result:
  1. Look at `videos[0]` (the first video for that query).
  2. If `videos` is missing or empty, SKIP this query (do not emit a URL for it).
  3. Otherwise, build the URL: https://www.youtube.com/watch?v=<videos[0].videoId>

NEVER invent or guess a videoId. NEVER pull a videoId from a different query's results.

[OUTPUT]
Output exactly two parts, in order:
  1. ONE JSON array on a single line, containing all the URLs you built, in the same order the queries were processed:
     ["https://www.youtube.com/watch?v=...", "https://www.youtube.com/watch?v=..."]
     If no valid URLs exist, output: []
  2. On a NEW line, the literal string: youtube_video_play_planning_agent

DO NOT output `CONTENTGENERATIONDONE`. DO NOT output `{"open_webbrowser": ...}` — that belongs to the orchestrator. DO NOT add commentary or markdown code fences.
"""
)


