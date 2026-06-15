from src.agent_as_a_tool_daily_pc.youtube_video_play.selector_groupchat import play_team


TEAM_FACTORY = {
    "play": play_team,
    # "open": open_team,
    # "execute": execute_team,
}


def build_agent_teams(merged_intents):
    team_configs = []
    for item in merged_intents:
        team = TEAM_FACTORY.get(item["intent"])
        if team is None:
            continue
        team_configs.append({
            "intent": item["intent"],
            "keywords": item["keywords"],
            "team": team,
        })
    return team_configs
