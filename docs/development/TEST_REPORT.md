# Test Report

## 테스트 원칙

```text
기능 구현 후 pytest 실행
리팩토링 후 pytest 재실행
테스트 실패 상태로 다음 Phase 진행 금지
```

## Phase 1 테스트 결과

```text
날짜: 2026-06-30
Phase: Phase 1
명령: uv run pytest
결과: PASS
PASS: 4
FAIL: 0
수정 내용: Flask app factory, /healthz, /, 기본 템플릿, Docker/uv 설정 추가
재테스트 결과: 4 passed
```

## Phase 2 테스트 결과

```text
날짜: 2026-06-30
Phase: Phase 2
명령: uv run pytest
결과: PASS
PASS: 14
FAIL: 0
수정 내용: User 모델, 로컬 회원가입/로그인/로그아웃, /dashboard 보호, 인증 테스트 추가
리팩토링: SQLite 상대 경로를 ./data 기준 절대 경로로 정규화
재테스트 결과: 14 passed
```

Docker 확인:

```text
명령: docker compose up --build -d
결과: 이미지 빌드 성공, 컨테이너 시작은 호스트 5000 포트 점유로 실패
원인: 127.0.0.1:5000을 별도 flask 프로세스가 사용 중
대체 검증: docker run -p 5001:5000 gpt-manager-web:latest
/healthz: HTTP 200, {"status":"ok"}
/: HTTP 200
/dashboard: HTTP 302, /auth/login?next=%2Fdashboard
정리: 임시 컨테이너 삭제 완료
```

## Phase 2 테스트 파일

```text
tests/test_app.py
- app factory creates app
- index page returns 200

tests/test_health.py
- /healthz returns 200
- response contains status ok

tests/test_auth.py
- register creates user and redirects to dashboard
- duplicate email is rejected
- login success allows dashboard access
- login failure uses generic message
- dashboard requires login
- logout blocks dashboard access

tests/test_user_model.py
- password hash roundtrip
- plaintext password is not stored

tests/test_config.py
- relative SQLite DATABASE_URL is rooted at ./data
- in-memory SQLite DATABASE_URL is unchanged
```

## Phase 3 예정 테스트

```text
reservation conflict detection
cancelled reservation does not conflict
user can see own reservations
usage log can be created by authenticated user
```

## Phase 4 예정 테스트

```text
API Key encryption roundtrip
plaintext API Key is not stored
masked key display uses last4 only
```

## Phase 5 예정 테스트

```text
prompt review prompt builder includes selected options
Gemini call is mocked in tests
PromptReview is saved for current user
```

## 실행 명령

```bash
uv run pytest
```
