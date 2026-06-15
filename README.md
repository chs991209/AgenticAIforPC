# AgenticAIForPC — Agent 서버 실행 가이드

자연어 명령(예: `"아이브 뮤직비디오 재생해 줘"`)을 받아 **여러 LLM 에이전트가 협업**해서 실행 가능한 액션(예: YouTube URL 목록)을 만들어 주는 FastAPI 서버입니다.

---

## 1. 빠른 시작 (3분)

### 1.1. 사전 준비물
- Python **3.12** (다른 버전은 권장하지 않음)
- OpenAI API 키 (`gpt-5.4-nano` 사용 가능 계정)
- YouTube Data API v3 키 (Google Cloud Console에서 발급)
- (선택) Gemini API 키 — OpenAI 대신 사용하고 싶을 때

### 1.2. 설치
```bash
git clone <이 저장소>
cd AgenticAIForPC

# 가상환경 생성 (Python 3.12)
python3.12 -m venv agenticai-daily-microsoft
source agenticai-daily-microsoft/bin/activate    # macOS / Linux
# Windows: agenticai-daily-microsoft\Scripts\activate

pip install -r requirements.txt
```

### 1.3. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 만들고 다음을 추가하세요.

```env
# 필수
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=AIza...

# 선택 — Gemini로 전환하고 싶다면
GEMINI_API_KEY=AIza...
```

> `.env`는 절대 커밋하지 마세요. `.gitignore`에 이미 포함되어 있는지 확인하세요.

### 1.4. 서버 실행
프로젝트 루트(`AgenticAIForPC/`)에서:

```bash
uvicorn src.agent_as_a_tool_daily_pc.call_agents_as_tools:app --reload
```

기본 주소: `http://127.0.0.1:8000`

### 1.5. 동작 테스트
다른 터미널에서:

```bash
curl -X POST http://127.0.0.1:8000/generate_actions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "아이브 뮤직비디오 재생해 줘"}'
```

응답 예시:
```json
{
  "actions_list": [
    {"youtube_urls": ["https://www.youtube.com/watch?v=6ZUIwj3FgUY"]}
  ]
}
```

---

## 2. 동작 원리 (한눈에 보기)

```
유저 프롬프트
   ↓
[1] intent_classifier        → {"play": ["아이브 뮤직비디오"]}
   ↓
[2] intent_router (병합/검증) → [{"intent": "play", "keywords": [...]}]
   ↓
[3] build_agent_teams        → intent별 SelectorGroupChat 인스턴스
   ↓
[4] team.run_stream(task)    ─┬─ planner ─→ search_agent ─→ validator ─→ planner
                              │             (YouTube API)
                              └─ "CONTENTGENERATIONDONE" 토큰으로 종료
   ↓
[5] extract_final_answer     → {"youtube_urls": [...]}
   ↓
JSON 응답
```

`play` 의도의 경우 다음 3개 에이전트가 협업합니다:

| 에이전트 | 역할 | temperature |
|---|---|---|
| `youtube_video_play_planning_agent` | 오케스트레이터 (라우팅 + 최종 페이로드) | 0.0 |
| `youtube_video_search_agent` | `search_youtube_videos` 도구 호출 | 0.0 |
| `youtube_video_url_validate_agent` | 검색 결과 → 깨끗한 URL 리스트 | 0.0 |

라우팅은 LLM에 맡기지 않고 `cover_candidate_func`가 **메시지 소스 기반 상태 머신**으로 결정합니다 — 즉, 예측 가능한 흐름을 보장합니다.

---

## 3. 디렉토리 구조

```
src/agent_as_a_tool_daily_pc/
├── call_agents_as_tools.py            # FastAPI 진입점 (POST /generate_actions)
├── LLM_models/
│   ├── openai_models.py               # model_client00..04 (gpt-5.4-nano, 기본)
│   └── gemini_models.py               # gemini_client00..04 (선택)
├── query_decomposition/
│   └── agent.py                       # intent_classifier
├── graph_based_intent_route/
│   └── intent_router.py               # 의도 분류 + 키워드 병합
├── agent_teams_first_depth_layer_generator/
│   └── agent_teams_builder.py         # intent → team 매핑
├── agent_teams_prompt_recombinator/
│   └── team_prompt_recombinator.py    # 팀별 입력 프롬프트 포매터
├── agent_team_action_extractor/
│   └── action_extractor.py            # 최종 JSON 추출
└── youtube_video_play/
    ├── planning/agent.py              # 플래닝 에이전트
    ├── youtube_video_search/agent.py  # 검색 에이전트
    ├── youtube_video_url_validate/agent.py  # 검증 에이전트
    ├── tools/youtube_video_search.py  # YouTube Data API 호출 도구
    └── selector_groupchat/team.py     # SelectorGroupChat + candidate_func
```

---

## 4. OpenAI ↔ Gemini 전환

현재 모든 에이전트는 `openai_models.py`의 `model_client00..04`를 import합니다 (`gpt-5.4-nano`, 0.0~0.4 temperature).

Gemini로 한 에이전트만 바꾸려면 해당 파일의 import를 교체하세요:

```python
# 변경 전
from src.agent_as_a_tool_daily_pc.LLM_models.openai_models import model_client00

# 변경 후
from src.agent_as_a_tool_daily_pc.LLM_models.gemini_models import gemini_client00 as model_client00
```

`gemini_models.py`는 Google의 OpenAI 호환 엔드포인트를 사용하므로 코드의 다른 부분은 손댈 필요가 없습니다.

> 주의: 플래너/검색/검증 에이전트처럼 **엄격한 출력 형식**이 필요한 노드는 `gpt-5.4-nano`(OpenAI)가 더 안정적입니다. Gemini-flash로 바꾸면 가끔 JSON 경계를 흩트리는 경우가 있습니다.

---

## 5. 새 의도(intent) 추가하는 법

예) `open` (웹사이트 열기) 의도를 추가하려면:

1. `intent_classifier`의 system message에 이미 `open`은 정의되어 있습니다 (확장 시 추가 작성).
2. `INTENT_LABELS`(`graph_based_intent_route/intent_router.py`)에 `"open"` 포함 확인.
3. **새 팀을 만든다**: `src/agent_as_a_tool_daily_pc/site_open_browser/` 아래에 planner/executor 에이전트와 `SelectorGroupChat` 인스턴스를 만듭니다.
4. `agent_teams_builder.py`의 `TEAM_FACTORY`에 등록:
   ```python
   TEAM_FACTORY = {
       "play": play_team,
       "open": open_team,    # ← 추가
   }
   ```
5. 새 팀의 플래너에도 동일한 종료 토큰(`CONTENTGENERATIONDONE`)과 최종 페이로드 형식을 따르게 하면 `extract_final_answer`가 그대로 동작합니다.

---

## 6. 자주 마주치는 문제

| 증상 | 원인 | 해결 |
|---|---|---|
| `ModuleNotFoundError: No module named 'src'` | uvicorn을 잘못된 디렉토리에서 실행 | 프로젝트 루트(`AgenticAIForPC/`)에서 실행하세요. |
| `KeyError: 'gpt-5.4-nano-2026-03-17'` | autogen이 모델 정보를 모름 | `openai_models.py`의 monkey-patch가 먼저 import되었는지 확인하세요. 정상 흐름에서는 자동으로 처리됩니다. |
| 응답이 `{"youtube_urls":[]}` | 검색어가 너무 모호해서 채널/플레이리스트만 반환됨 | 검색 도구가 채널을 필터링하므로 정상입니다. 키워드를 더 구체적으로 입력하세요. |
| `Team 'play' did not complete properly` | 플래너가 `CONTENTGENERATIONDONE`을 안 보냄 | 플래너의 시스템 메시지가 STATE A/B 구조를 유지하는지 확인하세요. 모델을 OpenAI로 교체하면 안정성이 올라갑니다. |
| 응답에 한국어가 깨져 보임 | 콘솔 인코딩 문제 | 클라이언트(curl 등)에 영향, 서버 처리에는 무관. `--data-binary @file.json` 사용 권장. |

---

## 7. 개발 팁

- **로그를 더 자세히 보고 싶으면**: `call_agents_as_tools.py`의 `Console(team.run_stream(...))`을 유지하세요. 각 에이전트의 turn이 콘솔에 출력됩니다.
- **새 에이전트를 만들 때 temperature 기준**:
  - 라우터 / 추출기 / 도구 호출자 → `0.0` (`model_client00`)
  - 분류기 → `0.0~0.3` (`model_client01`, `model_client02`)
  - 요약/재작성 → `0.3~0.6` (`model_client03`)
  - 창작 → `0.6+` (`model_client04`)
- **에이전트 시스템 메시지 작성 원칙**:
  - 한 에이전트당 한 가지 책임만
  - 상태가 여러 개면 **메시지 소스 기반의 STATE A / STATE B 구조**로 명시 분기
  - 금지 사항(`DO NOT ...`)을 명시적으로 적기 — 약한 모델일수록 효과 큼

---

## 8. 라이선스 / 기여
사내/연구용 prototype. 외부 배포 전에는 시크릿 키 사용량과 모델 비용을 반드시 확인하세요.
