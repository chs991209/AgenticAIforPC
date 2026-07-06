import json
import asyncio
from typing import Dict, List, Any
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from src.agent_as_a_tool_daily_pc.query_decomposition.agent import intent_classifier
from src.agent_as_a_tool_daily_pc.agent_teams_first_depth_layer_generator import TEAM_FACTORY
# Explicitly define the NLP domain boundary
INTENT_LABELS = {"play", "open", "execute"}
team_factory = TEAM_FACTORY

async def classify_and_merge_intents(prompt: str) -> List[Dict[str, Any]]:
    # team_factory: Dict[str, Any]
    """
    단일 패스로 의도 분류 및 키워드 병합을 수행하는 통합 함수.
    INTENT_LABELS(도메인 검증)와 team_factory(실행 검증)를 모두 통과한 결과만 반환합니다.
    """
    cancellation_token = CancellationToken()
    try:
        # 1. LLM 호출
        response = await asyncio.wait_for(
            intent_classifier.on_messages(
                messages=[TextMessage(content=prompt, source="user")],
                cancellation_token=cancellation_token,
            ),
            timeout=20.0,
        )

        # 2. 응답 텍스트 추출
        reply = ""
        if hasattr(response, "chat_message") and hasattr(response.chat_message, "content"):
            reply = response.chat_message.content.strip()
        elif hasattr(response, "content"):
            reply = response.content.strip()

        # Markdown 코드 블록 제거
        if reply.startswith("```"):
            lines = reply.split("\n")
            if len(lines) >= 3:
                reply = "\n".join(lines[1:-1]).strip()
            else:
                reply = reply.replace("```json", "").replace("```", "").strip()

        # 3. JSON 파싱
        parsed = json.loads(reply)
        parsed_dict = {}

        # 4. 방어적 포맷팅 및 INTENT_LABELS(1차) 검증
        if isinstance(parsed, list):
            for obj in parsed:
                intent = obj.get("intent")
                keywords = obj.get("keywords", [])
                # 1차 검증: 허용된 라벨인지 확인
                if intent in INTENT_LABELS:
                    parsed_dict.setdefault(intent, []).extend(
                        keywords if isinstance(keywords, list) else [keywords] if keywords else []
                    )
        elif isinstance(parsed, dict):
            for intent, keywords in parsed.items():
                # 1차 검증: 허용된 라벨인지 확인
                if intent in INTENT_LABELS:
                    parsed_dict[intent] = keywords

        # 5. team_factory(2차) 검증 및 중복 키워드 병합
        result = []
        for intent, keywords in parsed_dict.items():
            # 2차 검증: 실제 실행 가능한 팀이 세팅되어 있는지 확인
            if intent not in team_factory:
                continue

            if not isinstance(keywords, list):
                keywords = [keywords] if keywords else []

            # 중복 키워드 제거 (순서 유지)
            seen = set()
            unique_keywords = []
            for kw in keywords:
                kw_str = str(kw).strip()
                if kw_str and kw_str not in seen:
                    seen.add(kw_str)
                    unique_keywords.append(kw_str)

            if unique_keywords:
                result.append({"intent": intent, "keywords": unique_keywords})

        return result

    except asyncio.TimeoutError:
        print("[classify_and_merge_intents] Intent classification timed out.")
        return []
    except json.JSONDecodeError as err:
        print(f"[classify_and_merge_intents] JSON Parse Error: {err}\nRaw reply: {reply}")
        return []
    except Exception as e:
        print(f"[classify_and_merge_intents] Unexpected Error: {e}")
        return []