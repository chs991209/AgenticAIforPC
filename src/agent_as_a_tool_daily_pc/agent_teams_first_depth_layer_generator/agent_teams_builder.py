from src.agent_as_a_tool_daily_pc.youtube_video_play.selector_groupchat import build_play_team


TEAM_FACTORY = {
    "play": build_play_team,
    # "open": build_open_team,
    # "execute": build_execute_team,
}


def build_agent_teams(merged_intents):
    """For each requested intent, look up its team factory and instantiate
    on demand. Factories are cached internally (functools.cache), so the
    second request for the same intent reuses the same team instance.
    """
    team_configs = []
    for item in merged_intents:
        factory = TEAM_FACTORY.get(item["intent"])
        if factory is None:
            continue
        team_configs.append({
            "intent": item["intent"],
            "keywords": item["keywords"],
            "team": factory(),
        })
    return team_configs
