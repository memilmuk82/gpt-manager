# BYOK AI 사용 안내

## 목적

BYOK(Bring Your Own Key)는 학교 또는 관리자가 공용 LLM API Key를 제공하지 않고, 사용자가 본인 명의의 API Key로 AI Provider를 호출하는 운영 방식이다. 이 프로젝트의 AI 기능은 자유 채팅이 아니라 사용자가 작성한 거친 요청을 구조화된 프롬프트로 정리하는 제한된 업무 기능으로만 제공한다.

## 지원 Provider

현재 지원 Provider는 다음 3개다.

| Provider | 설정 화면 표시 | 비고 |
| --- | --- | --- |
| OpenAI | OpenAI | 사용자 본인 OpenAI API Key 필요 |
| Google Gemini | Google Gemini | 사용자 본인 Google AI Studio 또는 관련 API Key 필요 |
| Anthropic Claude | Anthropic Claude | 사용자 본인 Anthropic API Key 필요 |

OpenRouter는 현재 지원하지 않는다. 관리자는 공용 API Key를 발급하거나 배포하지 않는다.

## 사용자 흐름

1. 사용자는 각 Provider 서비스에서 본인 계정으로 API Key를 발급한다.
2. `/settings/api-key` 화면에서 Provider를 선택하면 모델 목록이 페이지 전체 새로고침 없이 해당 Provider 기준으로 자동 갱신된다.
3. 사용자는 모델을 선택하고 API Key를 서버에 암호화 저장하거나, 저장하지 않고 프롬프트 정리 실행 시 일회성으로 입력한다.
4. 연결 테스트 또는 모델 목록 새로고침을 실행하면 선택한 Provider API를 실제로 호출할 수 있다. 자동 갱신에 실패하면 모델 영역의 상태 메시지를 확인하고 수동 새로고침으로 다시 시도할 수 있다.
5. 프롬프트 정리 기능을 실행하면 사용자가 입력한 요청과 정리 목표가 선택한 Provider API로 전송될 수 있다.

## 저장 방식

| 방식 | 설명 | 적합한 상황 |
| --- | --- | --- |
| 일회성 입력 | API Key를 서버 DB에 저장하지 않고 실행 화면에서 한 번만 사용한다. | 공용 PC, 공동 계정 환경, 키 저장을 원하지 않는 사용자 |
| 서버 암호화 저장 | 사용자가 저장을 선택한 경우 `LLM_KEY_ENCRYPTION_SECRET` 기반 암호문과 마지막 4자리만 DB에 저장한다. | 개인 장비에서 같은 Provider를 반복 사용할 때 |
| 브라우저 저장 | 현재 브라우저의 localStorage에 저장한다. 서버 저장은 아니지만 같은 브라우저 사용자가 접근할 수 있다. | 개인 장비에서만 제한적으로 사용 |

API Key 원문은 화면에 다시 표시하지 않는다. 관리자와 다른 사용자는 원문을 조회할 수 없다.

## 비용과 사용량 책임

API Key 발급, 결제 수단 등록, Provider별 사용량 한도, 과금 정책 확인은 사용자 본인의 책임이다. 연결 테스트, 모델 목록 새로고침, 프롬프트 정리 실행도 Provider 정책에 따라 비용이 발생하거나 사용량이 차감될 수 있다.

운영자는 앱 차원의 일일, 월간, 짧은 시간 내 연속 요청 제한을 둘 수 있지만, 이것이 Provider 과금 한도나 결제 차단을 대신하지는 않는다.

## 외부 전송과 입력 금지 항목

프롬프트 정리 실행 시 다음 정보가 선택한 Provider API 처리 목적으로 외부 서비스에 전송될 수 있다.

- 사용자가 입력한 원문 요청
- 정리 목표와 선택한 템플릿 정보
- 앱이 조립한 시스템/사용자 프롬프트

다음 항목은 입력하지 않는다.

- 학생 이름, 학번, 연락처 등 개인정보
- 성적, 생활기록부, 상담 내용 등 민감하거나 보호가 필요한 자료
- 평가 문항 원본, 정답, 채점 기준 등 비공개 평가 자료
- 학교 내부 계정, 비밀번호, 인증번호, API Key, 업무상 비밀 자료

## 운영 점검 기준

- `.env`에 `LLM_KEY_ENCRYPTION_SECRET`을 설정하고 DB에 저장하지 않는다.
- Docker logs, 오류 메시지, CSV export에 API Key 원문이 포함되지 않게 유지한다.
- Provider 추가, OpenRouter 지원, 자유 채팅 UI 추가는 별도 ADR 또는 보안 결정 문서로 승인한 뒤 진행한다.
- 약관과 개인정보처리방침에는 외부 Provider 전송 가능성과 사용자 책임을 계속 명시한다.

## 관련 문서

- [ADR 0004 - 사용자별 BYOK LLM Provider 설정](../adr/0004-byok-llm-provider-settings.md)
- [Security Decisions](../decisions/SECURITY_DECISIONS.md)
- [개인정보처리방침](../legal/PRIVACY_POLICY.md)
- [이용약관](../legal/TERMS.md)
