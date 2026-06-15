from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from autogen_agentchat.ui import Console
# from agents.intent import classify_intents_with_keywords
# from agents.groupchat import build_agent_teams
# from agent_utils.groupchat.groupchat_manager import (
#     extract_final_answer,
#     format_team_prompt,
# )
from src.agent_as_a_tool_daily_pc.graph_based_intent_route.intent_router import classify_and_merge_intents
from src.agent_as_a_tool_daily_pc.agent_teams_prompt_recombinator import format_team_prompt
from src.agent_as_a_tool_daily_pc.agent_teams_first_depth_layer_generator import build_agent_teams
from src.agent_as_a_tool_daily_pc.agent_team_action_extractor import extract_final_answer, message_text
import httpx
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to actual frontend domain(s) if in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_actions")
async def generate_actions_in_agent_teams(request: Request):
    """
    User Prompt
    : Execute daily jobs in an Agentic AI app.
    Agent Team Request
    : Generate actions for those tasks and send it to the User Client(PC).
    :param request:
    :return:
    """

    body = await request.json()
    prompt = body.get("prompt").strip()
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "User prompt is required."})
    print(f'User Prompt: {prompt}')

    decomposed_prompt = await classify_and_merge_intents(prompt)
    for intent_index, item in enumerate(decomposed_prompt, start=1):
        intent = item["intent"]
        keywords = item["keywords"]
        print(f'Intent: {intent}, {intent_index}', end=" ")
        print('Keywords:', end=" ")
        for keyword in keywords:
            print(f'{keyword},', end=" ")
        print()

    if len(decomposed_prompt):
        team_configs = build_agent_teams(decomposed_prompt)
        actions_list = []
        for config in team_configs:
            intent = config["intent"]
            keywords = config["keywords"]

            t0 = time.perf_counter()
            team = config["team"]
            t1 = time.perf_counter()
            await team.reset()
            t2 = time.perf_counter()

            prompt = format_team_prompt(intent, keywords)

            try:
                actions = await Console(team.run_stream(task=prompt))
                t3 = time.perf_counter()

                messages = getattr(actions, "messages", [])
                has_actions_done = any(
                    "CONTENTGENERATIONDONE" in message_text(msg)
                    for msg in messages
                )
                if not has_actions_done:
                    print("----ACTIONERROR:INCOMPLETEACTIONGENERATIONERROR-----------------")
                    print(f"Team '{intent}' did not complete properly - no CONTENTGENERATIONDONE found")
                    return Exception(f"Team '{intent}' did not complete properly - no CONTENTGENERATIONDONE found")
                action = extract_final_answer(actions)
                t4 = time.perf_counter()

                print(
                    f"[timing] team-fetch={t1 - t0:.4f}s  "
                    f"reset={t2 - t1:.4f}s  "
                    f"run_stream={t3 - t2:.4f}s  "
                    f"extract={t4 - t3:.4f}s  "
                    f"total={t4 - t0:.4f}s"
                )

                if action is None:
                    print("----ACTIONERROR:NOFOUNDACTIONERROR-----------------")
                    print(f"Team '{intent}' did not generate action properly - no action found")
                    return Exception(f"Team '{intent}' did not generate action properly - no action found")
                actions_list.append(action)


            except Exception as e:
                print("---------Error-------------------")
                print(f"Team '{intent}' had encountered an error: {e}")

        return JSONResponse(content={"actions_list": actions_list}, status_code=200)
    return JSONResponse(content={"error": "Intent not recognized"}, status_code=400)