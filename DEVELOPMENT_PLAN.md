# Development Plan - 생성형 AI 계정 공동 사용 지원 시스템

## 관련 문서

[README](README.md) · [현재 상태](PROJECT_STATUS.md) · [개발 로그](docs/development/DEVELOPMENT_LOG.md)


## 문서 성격

이 문서는 초기 개발 일정과 Phase 계획을 보존하는 기록 문서입니다. 현재 완료 상태와 운영 검증 결과는 [PROJECT_STATUS.md](PROJECT_STATUS.md), 상세 변경 이력은 [docs/development/DEVELOPMENT_LOG.md](docs/development/DEVELOPMENT_LOG.md)를 기준으로 확인합니다.

## 1. 마감 기준

```text
현재 기준: 2026-06-30 오전, 한국시간
제출 목표: 2026-07-03 오후
RC1 목표: 2026-07-02
```

## 2. 전체 전략

```text
새로운 교육 생성기 개발 금지
기존 GPT 공유앱의 운영 문제를 Flask 앱으로 재설계
BYOK LLM API는 사용자 요청을 구조화된 프롬프트로 정리/개선하는 데만 사용
3일 안에 완성 가능한 기능만 구현
```

## 3. 일정

### 2026-06-30

목표: 프로젝트 골격과 인증/DB 기반 구축

```text
문서 패킷 완성
OCI 개발 서버 준비
저장소 생성
uv 프로젝트 초기화
Flask app factory
SQLite 연결
Docker Compose
기본 템플릿
로컬 로그인
Google OAuth 기본 구조
pytest 기본 테스트
```

완료 기준:

```text
로컬 또는 OCI에서 docker compose up 성공
/healthz 통과
로컬 로그인 가능
pytest 통과
PROJECT_STATUS.md 갱신
```

### 2026-07-01

목표: 핵심 업무 기능 구현

```text
AI 리소스 기본 데이터
예약 CRUD
예약 충돌 검증
사용 로그 CRUD
AI Provider/API Key 설정
API Key 암호화 저장
프롬프트 정리기 구현
LLM adapter mock 테스트
```

완료 기준:

```text
예약 생성/취소 가능
사용 로그 작성 가능
프롬프트 정리 실행 가능
API Key 평문 저장 안 됨
pytest 통과
```

### 2026-07-02

목표: RC1 완성 및 OCI 배포

```text
관리자 대시보드
Google OAuth 로그인
senedu.kr 자동 승인 + 외부 계정 관리자 승인제
가능하면 운영 보고서 생성
UI 정리
README 작성
시연 흐름 작성
OCI 배포
OAuth redirect 확인
senedu.kr 자동 승인 및 외부 계정 승인제 확인
최종 통합 테스트
```

완료 기준:

```text
OCI URL에서 앱 접근 가능
핵심 시나리오 시연 가능
README만 보고 실행 가능
RC1 태그 또는 commit 준비
```

### 2026-07-03

목표: 기능 동결 후 제출

```text
기능 추가 금지
리팩토링 금지
코드 구조 변경 금지
최종 실행 테스트
제출 자료 정리
```

허용 작업:

```text
README 오타 수정
시연 문구 정리
.env.example 보완
스크린샷 추가
```

## 4. Phase 구성

### Phase 0. 문서/프로젝트 준비

```text
문서 읽기
구현 계획 보고
사용자 승인
```

### Phase 1. 기본 골격

```text
uv 프로젝트 초기화
Flask app factory
config/extensions
/healthz
base template
Dockerfile/docker-compose
pytest 기본 테스트
```

### Phase 2. 인증

```text
User 모델
로컬 회원가입/로그인/로그아웃
비밀번호 hash
Google OAuth 구조
admin seed
권한 decorator
```

### Phase 3. 예약/로그

```text
AiResource 모델
Reservation 모델
UsageLog 모델
예약 CRUD
충돌 검증
사용 로그 CRUD
```

### Phase 4. API Key 설정

```text
UserApiKey 모델
Fernet 암호화
등록/삭제/마스킹/테스트
암호화 테스트
```

### Phase 5. 프롬프트 정리기

```text
PromptReview 모델
프롬프트 정리 입력 폼
정리 프롬프트 조립
LLM adapter 호출
결과 저장
복사/조회
mock 테스트
```

### Phase 6. 관리자/보고서

```text
관리자 대시보드
전체 예약/로그/프롬프트 정리 결과 확인
AI 리소스 관리
Google OAuth 로그인 및 senedu.kr 자동 승인/외부 계정 승인제
가능하면 운영 보고서 생성
```

### Phase 7. 배포/제출

```text
README
.env.example
OCI 배포
최종 테스트
제출용 설명 정리
```

## 5. 우선순위

### 반드시 완료

```text
Flask 실행
Docker Compose
SQLite
로컬 로그인
Google OAuth 구조
예약 CRUD
사용 로그
AI Provider/API Key 설정
프롬프트 정리기
기본 테스트
README
```

### 추가로 완료된 확장 기능

```text
운영 보고서 생성
프롬프트 결과 Markdown 다운로드
관리자 리소스/작업유형 관리 UI
사용 통계 요약
관리자 테스트 실행과 테스트 파일별 설명 표시
BYOK Provider 확장과 Anthropic 기본 추천 모델 정리
```

### 하지 않는다

```text
파일 업로드
교육자료 생성기
채팅 UI
PostgreSQL
복잡한 권한
네이버웍스 연동
실사용량 자동 조회
```

## 6. 작업 단위 완료 조건

각 Phase 완료 조건:

```text
기능 구현 완료
pytest 통과
수동 시연 가능
리팩토링 필요 여부 검토
필요 시 소규모 리팩토링 완료
재테스트 통과
PROJECT_STATUS.md 갱신
DEVELOPMENT_LOG.md 갱신
TEST_REPORT.md 갱신
```

## 7. 위험 관리

### Google OAuth가 지연될 경우

```text
로컬 로그인 완성
Google OAuth route와 설정 구조 완성
README에 Redirect URI 설정 방법 문서화
```

### Gemini SDK/모델명 이슈가 생길 경우

```text
Provider별 추천 모델과 사용자 선택 모델로 분리
Provider별 호출부를 app/services/llm adapter에 격리
테스트는 mock으로 통과
실제 호출은 설정 확인 후 진행
```

### OCI 배포가 지연될 경우

```text
로컬 Docker Compose 실행을 제출 기준으로 확보
OCI 배포 절차를 README에 문서화
가능하면 7월 2일 오전 이전에 배포 시도
```

### UI가 부족할 경우

```text
Tailwind CDN으로 최소 화면만 구성
기능 동작을 우선
예쁜 UI보다 시연 가능성 우선
```


## 8. 현재 완료 상태

```text
작성 시점: 2026-07-04
상태: 운영 편의 기능 보완, UI 개선, 문서 포털 정리, 테스트 설명 화면 반영 완료
운영 도메인: https://dev-gpt.memilmuk82.com
pytest: 88 passed
Playwright E2E: 1 passed
Docker Compose + Gunicorn + Nginx + HTTPS 운영 확인
오늘 예약 화면, 월간 예약 캘린더, 미작성 로그 알림 구현 완료
BYOK OpenAI/Gemini/Anthropic Provider 설정과 프롬프트 정리 구현 완료
관리자 테스트 실행 결과의 파일별 검증 설명 표시 완료
보조관리자 권한, 월간 운영 보고서, 감사 로그, DB 백업/CSV 내보내기 구현 완료
/terms, /privacy Markdown 법적 고지 페이지 구현 완료
```

이 문서는 초기 개발 계획을 보존한다. 실제 현재 상태는 `PROJECT_STATUS.md`와 `TASK.md`를 기준으로 확인한다.
