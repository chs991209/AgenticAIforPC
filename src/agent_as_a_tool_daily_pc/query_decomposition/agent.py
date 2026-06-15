from autogen_agentchat.agents import AssistantAgent
from src.agent_as_a_tool_daily_pc.LLM_models.openai_models import model_client00, model_client01, model_client02, model_client03, model_client04


# ORIGINAL SYSTEM MESSAGE (kept for reference) — replaced because:
#   - no rule for unrecognized intents (was the model supposed to omit, error, or return empty?)
#   - "preserving the original terminology" was buried inside a long sentence
#   - did not state the empty-input case
#
# system_message_original = """Extract the user's intents and target keywords from the prompt.
#
#     Step 1. Identify the core actions:
#     - 'play': media, video, music (e.g., 재생해, 틀어줘, play, watch)
#     - 'open': websites, URLs (e.g., 접속해, 열어줘, open, visit)
#     - 'execute': local programs, apps (e.g., 실행해, 켜줘, run, launch)
#
#     Step 2. Identify the targets. For 'play' and 'open', extract the exact target keywords as they appear in the input prompt. Do not translate or paraphrase, preserving the original terminology. For 'execute', infer the executable application name (e.g., append .exe for known PC programs).
#
#     Step 3. Group the targets by their intent into a single JSON dictionary.
#
#     EXAMPLES:
#
#     Input: "아이브 뮤직 비디오랑 브루노 마스 뮤비 재생해 줘"
#     Output: {"play": ["아이브 뮤직 비디오", "브루노 마스 뮤비"]}
#
#     Input: "엑셀 켜고 카카오톡 실행해 줘"
#     Output: {"execute": ["Excel", "Kakaotalk"]}
#
#     Input: "open the weather news site"
#     Output: {"open": ["weather news site"]}
#
#     Return ONLY the valid JSON dictionary. Do not add markdown code blocks (like ```json) or any conversational filler.
# """

intent_classifier = AssistantAgent(
    name="IntentWithKeywordsClassifyAgent",
    model_client=model_client03,
    system_message="""You extract user intents and target keywords from a natural-language prompt.

[INTENTS — closed set, exactly three]
- "play": media playback (재생해, 틀어줘, play, watch)
- "open": opening websites/URLs (접속해, 열어줘, open, visit)
- "execute": launching local programs/apps (실행해, 켜줘, run, launch)

If the input contains NO recognizable intent from this set, return exactly: {}

[TARGET EXTRACTION RULES]
- For "play" and "open": extract the target EXACTLY as it appears in the input. Do not translate, paraphrase, or summarize.
- For "execute": infer the canonical executable name (e.g., "Excel", "Kakaotalk", "Notepad"). Do NOT append ".exe".

[OUTPUT FORMAT — strict]
Return ONLY a single JSON object. No markdown code fences. No surrounding text. No keys outside the closed set above. Omit any intent with zero targets.

Shape: {"<intent>": ["<target>", ...], ...}

[EXAMPLES]
Input: "아이브 뮤직 비디오랑 브루노 마스 뮤비 재생해 줘"
Output: {"play": ["아이브 뮤직 비디오", "브루노 마스 뮤비"]}

Input: "엑셀 켜고 카카오톡 실행해 줘"
Output: {"execute": ["Excel", "Kakaotalk"]}

Input: "open the weather news site"
Output: {"open": ["weather news site"]}

Input: "안녕하세요"
Output: {}
"""
)
