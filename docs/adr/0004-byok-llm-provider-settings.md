# ADR 0004 - 사용자별 BYOK LLM Provider 설정

## 상태

Accepted

## 결정

AI 기능은 관리자 공용 API Key가 아니라 사용자별 BYOK 방식으로 동작한다. 지원 Provider는 OpenAI, Google Gemini, Anthropic Claude 3개로 제한하며 OpenRouter는 현재 지원하지 않는다.

API Key는 기본적으로 서버 DB에 저장하지 않는다. 사용자가 서버 저장을 선택한 경우에만 `LLM_KEY_ENCRYPTION_SECRET` 기반 암호화 값, 마지막 4자리, Provider, 선택 모델, 활성 상태, 등록일, 최근 사용일을 저장한다.

## 이유

사용자 본인 키와 결제 책임을 분리하고, 일반 웹 관리자와 다른 사용자가 API Key 원문에 접근하지 못하게 하기 위해서다. 프롬프트 정리 기능은 자유 채팅이 아니라 거친 요청을 실행 가능한 구조화 프롬프트로 재작성하는 제한된 업무 기능으로 유지한다.

## 결과

- Provider별 adapter 구조를 사용한다.
- Provider 변경 시 설정 화면의 모델 select는 페이지 전체 새로고침 없이 자동 부분 갱신한다. 모델 목록 새로고침 실패 시 Provider별 추천 모델 목록으로 fallback하며, 수동 새로고침 버튼은 재시도 경로로 유지한다. Anthropic Claude 기본 추천 목록은 `claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-opus-4-8`이며, API 조회 결과에 `claude-opus-4-7` 등 다른 모델이 포함되면 그대로 선택 가능하게 표시한다.
- 연결 테스트와 정리 실행은 비용이 발생할 수 있음을 UI에 안내한다.
- 일일, 월간, 짧은 시간 내 연속 요청 제한을 적용한다.
- 관리자 화면에는 등록 여부와 마지막 4자리 등 메타데이터만 표시한다.
