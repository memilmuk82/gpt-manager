# ADR 0002 - 초기 단일 Provider 프롬프트 정리 결정

## 상태

Superseded by [ADR 0004](0004-byok-llm-provider-settings.md).

## 기존 결정

초기 구현에서는 BYOK LLM API를 자유 챗봇이 아니라 프롬프트 정리/개선 기능에 제한해 사용했다. 당시 구현 범위는 Google Gemini 단일 Provider였다.

## 현재 기준

현재 AI 기능은 사용자별 BYOK 방식으로 OpenAI, Google Gemini, Anthropic Claude 3개 Provider를 지원한다. 관리자는 공용 API Key를 제공하지 않고, OpenRouter는 현재 지원하지 않는다. API Key 저장과 관리자 표시 정책은 ADR 0004를 기준으로 한다.
