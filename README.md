# AgenticAIForPC — Agent 서버 가이드

자연어 명령(예: `"아이브 뮤직비디오 재생해 줘"`)을 받아 여러 LLM 에이전트가 협업해 실행 가능한 액션(YouTube URL 등)을 만들어 주는 FastAPI 서버.

의도(intent) 체계는 **`play`(미디어 재생) · `open`(웹사이트 열기) · `execute`(로컬 앱 실행)** 세 가지로 정의되어 있습니다.

## 1. 빠른 시작

```bash
git clone <저장소> && cd AgenticAIForPC
python3.12 -m venv agenticai-daily-microsoft
source agenticai-daily-microsoft/bin/activate   # Windows: ...\Scripts\activate
pip install -r requirements.txt
```

`.env` (프로젝트 루트, 커밋 금지):
```env
OPENAI_API_KEY=sk-...          # 필수
YOUTUBE_API_KEY=AIza...        # 필수
GEMINI_API_KEY=AIza...         # 선택
ANTHROPIC_API_KEY=sk-ant-...   # 선택 (Claude 사용 시)
```

실행 & 테스트 (프로젝트 루트에서):
```bash
uvicorn src.agent_as_a_tool_daily_pc.call_agents_as_tools:app --reload

curl -X POST http://127.0.0.1:8000/generate_actions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "아이브 뮤직비디오 재생해 줘"}'
# → {"actions_list": [{"open_webbrowser": ["https://www.youtube.com/watch?v=..."]}]}
```

## 2. 동작 원리

```
프롬프트 → intent_classifier → intent_router → build_agent_teams
        → team.run_stream: planner → search → validator → planner
                                     (YouTube API)  ("CONTENTGENERATIONDONE"로 종료)
        → extract_final_answer → {"open_webbrowser": [...]}
```

`play` 팀은 3개 에이전트로 구성되며 모두 temperature 0.0:

| 에이전트 | 역할 |
|---|---|
| `youtube_video_play_planning_agent` | 오케스트레이터 (라우팅 + 최종 페이로드) |
| `youtube_video_search_agent` | `search_youtube_videos` 도구 호출 |
| `youtube_video_url_validate_agent` | 검색 결과 → URL 리스트 |

라우팅은 LLM이 아니라 `cover_candidate_func`의 **메시지 소스 기반 상태 머신**이 결정 → 예측 가능.

## 3. 디렉토리 구조

```
src/agent_as_a_tool_daily_pc/
├── call_agents_as_tools.py            # FastAPI 진입점 (POST /generate_actions)
├── LLM_models/                        # openai / gemini / claude 클라이언트 (lazy, temp 0.0~0.4)
├── query_decomposition/agent.py       # intent_classifier
├── graph_based_intent_route/          # 의도 분류 + 키워드 병합
├── agent_teams_first_depth_layer_generator/  # intent → team 매핑
├── agent_teams_prompt_recombinator/   # 팀별 입력 프롬프트 포매터
├── agent_team_action_extractor/       # 최종 JSON 추출
└── youtube_video_play/
    ├── planning/  search/  url_validate/     # 에이전트 3종
    ├── tools/youtube_video_search.py         # YouTube Data API 도구
    └── selector_groupchat/team.py            # SelectorGroupChat + candidate_func
```

## 4. 모델(provider) 전환

에이전트 파일의 `model_client=` 한 줄만 바꾸면 됨. 세 provider 모두 `xxx_client00..04`(temp 0.0~0.4)를 lazy 제공.

```python
model_client=openai_model_client00   # 기본
model_client=gemini_model_client00   # Gemini 2.5 Flash
model_client=claude_model_client00   # Claude
```

- **라우팅/추출/도구 호출** 노드는 `gpt-5.4-nano`(OpenAI) 권장 — 엄격한 출력 형식 준수가 가장 안정적.
- Claude Sonnet 4.6+ / Opus 4.7+ 는 `temperature` 미지원 → `claude_models.py`가 자동으로 파라미터를 생략함. 이 모델들은 지시를 재협상하려는 경향이 있어 상태 머신 노드에는 부적합.
- Claude가 유리한 경우: 사용자 대상 문장 생성, 복잡한 분해, 긴 컨텍스트 요약.

## 5. 의도(intent) 팀 구성

의도는 `intent_classifier` system message와 `intent_router.py`의 `INTENT_LABELS`에 등록되며, 각 의도는 전용 팀에 매핑됩니다.

1. 팀(planner/executor + `SelectorGroupChat`)을 구성.
2. `agent_teams_builder.py`의 `TEAM_FACTORY`에 `"intent": 팀` 매핑.
3. 팀 플래너가 `CONTENTGENERATIONDONE` 종료 토큰 + 최종 JSON 형식을 지키면 `extract_final_answer`가 그대로 동작.

## 6. 자주 마주치는 문제

| 증상 | 해결 |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | 프로젝트 루트에서 실행 |
| `ModuleNotFoundError: No module named 'anthropic'` | `pip install anthropic` (Claude 사용 시) |
| `temperature is deprecated for this model` | Claude 4.5+ 사용 — `claude_models.py`가 자동 생략하므로 최신 코드로 갱신 |
| 응답이 `{"open_webbrowser":[]}` | 검색 결과가 영상이 아님 (채널/플레이리스트) — 키워드를 구체화 |
| `Team 'play' did not complete properly` | 플래너가 종료 토큰 미출력 — 플래너를 OpenAI로 두면 안정적 |

## 7. 개발 팁

- **모델 선택 기준**: 라우터/추출/도구 호출 → temp 0.0 (`client00`); 분류 → 0.0~0.3; 요약/재작성 → 0.3~0.6; 창작 → 0.6+.
- **시스템 메시지 원칙**: 한 에이전트당 한 책임 / 다상태는 메시지 소스 기반 STATE A·B로 분기 / 금지사항(`DO NOT`)을 명시.
- 팀·클라이언트는 첫 호출 시 1회 생성 후 재사용 (lazy). 첫 요청만 약간 느림.

## 8. 라이선스
배포 전 시크릿 키와 모델 비용 확인.
