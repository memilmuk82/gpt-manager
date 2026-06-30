# TASK - Current Codex Work

## 현재 작업

```text
Phase 1: 프로젝트 기본 골격 생성
```

## 작업 전 지시

Codex는 먼저 아래 내용을 보고하고 멈춘다.

```text
1. 프로젝트 목표 이해 요약
2. 생성할 파일/폴더 목록
3. Phase 1에서 구현할 범위
4. 사용 패키지 목록
5. 실행 명령어
6. 테스트 방법
7. 위험 요소
```

사용자가 `Phase 1 진행`이라고 승인하면 파일을 생성한다.

## Phase 1 목표

```text
Flask + SQLite + Docker Compose 기반 최소 실행 앱을 만든다.
```

## Phase 1 구현 범위

```text
1. uv 프로젝트 초기화
2. Flask app factory 작성
3. config.py 작성
4. extensions.py 작성
5. SQLAlchemy 초기화
6. /healthz route 작성
7. base.html과 index.html 작성
8. Tailwind CDN 적용
9. Dockerfile 작성
10. docker-compose.yml 작성
11. .env.example 작성
12. pytest 기본 테스트 작성
13. README 초안 작성
```

## Phase 1 제외 범위

```text
로그인 구현
Google OAuth 구현
예약 CRUD
Gemini API 호출
API Key 암호화
관리자 화면
```

## Phase 1 완료 조건

```text
uv run pytest 통과
docker compose up --build 실행 성공
브라우저에서 /healthz 확인 가능
브라우저에서 / 확인 가능
PROJECT_STATUS.md 갱신
DEVELOPMENT_LOG.md 갱신
docs/development/TEST_REPORT.md 갱신
```

## Phase 1 테스트 기준

필수 테스트:

```text
tests/test_health.py
- GET /healthz returns 200
- response JSON contains status ok

tests/test_app.py
- app factory creates Flask app
- index page returns 200
```

명령:

```bash
uv run pytest
```

Docker 확인:

```bash
docker compose up --build
curl http://localhost:5000/healthz
```

## Phase 1 문서 갱신

Phase 1 완료 후 다음 문서를 갱신한다.

```text
PROJECT_STATUS.md
DEVELOPMENT_LOG.md
docs/development/TEST_REPORT.md
```

## 다음 Phase 예고

```text
Phase 2: 인증
- User 모델
- 로컬 로그인
- 비밀번호 hash
- Google OAuth 기본 구조
- admin seed
```
