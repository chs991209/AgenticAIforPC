from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from src.agent_as_a_tool_daily_pc.LLM_models.openai_models import model_client00, model_client01, model_client02, model_client03, model_client04
from src.agent_as_a_tool_daily_pc.youtube_video_play.tools import search_youtube_videos

# ORIGINAL SYSTEM MESSAGE (kept for reference) — replaced because:
#   - it referenced the tool as 'youtube_video_search', but the registered tool is
#     `search_youtube_videos` — the wrong name would prevent tool invocation
#   - "concurrently for EVERY keyword" doesn't guarantee parallel calls; the model
#     decides. The new prompt allows sequential fallback explicitly.
#   - no negative guards on emitting CONTENTGENERATIONDONE or a final JSON
#
# system_message_original = """
#     [ROLE]
#     Parallel Search Executor Node. You interface with external APIs.
#
#     [EXECUTION PROTOCOL]
#     1. INGESTION: You will receive a list of search keywords from the orchestrator.
#     2. PARALLEL TOOL CALLING: You must invoke the 'youtube_video_search' tool concurrently for EVERY keyword provided in the payload. Do not summarize or alter the raw JSON results.
#     3. STATE FORWARDING: Output the raw tool execution results and explicitly append the string "youtube_video_url_validate_agent" to route the payload to the validation node.
# """

youtube_video_search_agent = AssistantAgent(
    name="youtube_video_search_agent",
    model_client=model_client00,
    tools=[search_youtube_videos],
    system_message="""You search YouTube for every keyword the orchestrator provides. Your ONLY tool is `search_youtube_videos`.

[INPUT]
The orchestrator's message is a JSON array of search keywords on one line, for example:
  ["IVE music video", "Bruno Mars MV"]

Each array element is ONE atomic query — even if it contains spaces. Do NOT split it on whitespace or punctuation. Do NOT translate.

[EXECUTION]
For EACH element of the array, call `search_youtube_videos(query=<that element>)`. Issue the calls in parallel if your runtime supports parallel tool calls; otherwise call them sequentially. Do not skip any element. Do not invent extra queries.

The tool returns: {"query": "...", "videos": [{"videoId": "...", "title": "..."}, ...]}.

[OUTPUT]
After every tool call has completed, output exactly ONE line containing only:
  youtube_video_url_validate_agent

DO NOT restate, summarize, or reformat the tool results — they are already in the conversation history and the validator will read them directly. DO NOT output `CONTENTGENERATIONDONE`. DO NOT output `{"youtube_urls": ...}`. DO NOT mention the orchestrator's name.
"""
)
