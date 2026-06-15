from typing import List, Sequence

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat

from src.agent_as_a_tool_daily_pc.LLM_models.openai_models import model_client03

from src.agent_as_a_tool_daily_pc.youtube_video_play.planning import youtube_video_play_planning_agent
from src.agent_as_a_tool_daily_pc.youtube_video_play.youtube_video_search import youtube_video_search_agent
from src.agent_as_a_tool_daily_pc.youtube_video_play.youtube_video_url_validate import youtube_video_url_validate_agent

user_proxy_agent = UserProxyAgent(name="user_proxy_agent")

def cover_candidate_func(planning_agent: AssistantAgent, sub_agents: List[AssistantAgent]):
    """Build a deterministic source-keyed router for the YouTube playback team.

    State machine:
        user                              -> planner
        planner (fan-out)                 -> whichever sub-agent it named
        search agent (any message type)   -> validator
        validator                         -> planner (fan-in / terminate)
        anything else                     -> planner (safe fallback)
    """
    planner_name = planning_agent.name
    sub_agents_by_name = {agent.name: agent for agent in sub_agents}
    sub_agents_names_list = [agent.name for agent in sub_agents]
    search_name = "youtube_video_search_agent"
    validator_name = "youtube_video_url_validate_agent"

    def candidate_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> List[str]:
        last = messages[-1]
        source = last.source

        if source == "user":
            return [planner_name]

        if source == planner_name:
            text = last.to_text()
            named = [name for name in sub_agents_names_list if name in text]
            if named:
                return named
            return [planner_name]

        if source == search_name:
            if validator_name in sub_agents_by_name:
                return [validator_name]
            return [planner_name]

        if source == validator_name:
            return [planner_name]

        return [planner_name]

    return candidate_func

text_mention_termination = TextMentionTermination("CONTENTGENERATIONDONE")

max_messages_termination = MaxMessageTermination(max_messages=100)

_termination_condition = text_mention_termination | max_messages_termination

selector_prompt = """Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent.
"""

team = SelectorGroupChat(
    participants=[user_proxy_agent, youtube_video_play_planning_agent, youtube_video_search_agent, youtube_video_url_validate_agent],
    model_client=model_client03,
    termination_condition=_termination_condition,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=False,  # Allow an agent to speak multiple turns in a row.
    candidate_func=cover_candidate_func(youtube_video_play_planning_agent, [youtube_video_search_agent, youtube_video_url_validate_agent])
)




