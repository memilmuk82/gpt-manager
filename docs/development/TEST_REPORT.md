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

tests/test_reservations.py
- reservation create/cancel flow
- reservation ownership filtering
- overlap conflict rejection
- back-to-back and different resource allowance
- cancelled reservation does not block new reservation
- inactive resource rejected
- end time must be after start

tests/test_usage_logs.py
- usage log can be created from reservation
- usage log can be created with resource only
- owned reservation is required
- user cannot view another user's usage log

tests/test_api_keys.py
- settings page requires login
- API Key encryption roundtrip
- plaintext API Key is not stored
- masked key display uses last4 only
- API Key can be replaced and deleted
- saved API Key decrypt check redirects successfully

tests/test_prompt_reviews.py
- prompt review requires login
- saved API Key is required
- mocked Gemini result is saved
- too-long prompt is rejected
- user cannot view another user's prompt review
- prompt builder includes required sections
```

## Phase 3 테스트 결과

```text
날짜: 2026-07-01
Phase: Phase 3
명령: uv run pytest
결과: PASS
PASS: 25
FAIL: 0
수정 내용: AiResource/Reservation/UsageLog 모델, 예약 CRUD, 예약 충돌 검증, 사용 로그 CRUD 추가
재테스트 결과: 25 passed
```

## Phase 4 테스트 결과

```text
날짜: 2026-07-01
Phase: Phase 4
명령: uv run pytest
결과: PASS
PASS: 30
FAIL: 0
수정 내용: UserApiKey 모델, Fernet 암호화 저장, API Key 마스킹/삭제/복호화 확인 추가
재테스트 결과: 30 passed
```

## Phase 5 테스트 결과

```text
날짜: 2026-07-01
Phase: Phase 5
추론 수준: 높음
명령: uv run pytest
결과: PASS
PASS: 36
FAIL: 0
수정 내용: PromptReview 모델, 프롬프트 점검 화면, Gemini 호출 service, mock 테스트 추가
재테스트 결과: 36 passed
```


## Phase 6 테스트 결과

```text
날짜: 2026-07-01
Phase: Phase 6
추론 수준: 높음
명령: uv run pytest
결과: PASS
PASS: 46
FAIL: 0
수정 내용: 관리자 대시보드, 사용자 승인/정지 관리, senedu.kr 자동 승인, 외부 계정 승인 대기, Google OAuth 기본 흐름 추가
재테스트 결과: 46 passed
```

## Phase 6 테스트 파일

```text
tests/test_admin.py
- non-admin cannot access admin dashboard
- admin can view and approve pending user
- admin cannot suspend self

tests/test_google_oauth.py
- Google login redirects to Google with hd=senedu.kr
- senedu.kr Google account is auto-approved
- external Google account remains pending
- unverified Google email is rejected

tests/test_auth.py additions
- external local registration waits for admin approval
- admin email registration gets admin role
- suspended user cannot login
```

## 실행 명령

```bash
uv run pytest
```

## Phase 7 테스트 결과

```text
날짜: 2026-07-01
Phase: Phase 7
추론 수준: 높음
명령: uv run pytest
결과: PASS
PASS: 46
FAIL: 0
수정 내용: README 최신화, .env.example 보강, Google OAuth Redirect URI 문서 추가, OCI 배포 문서 보완
재테스트 결과: 46 passed
```

Docker Compose 확인:

```text
명령: docker compose build
결과: PASS, image gpt-manager-web built

명령: docker compose up -d
결과: PASS, gpt-manager-web-1 started

명령: curl http://localhost:5000/healthz
결과: PASS, {"status":"ok"}

명령: docker compose down
결과: PASS, 검증용 컨테이너와 네트워크 정리 완료
```

남은 외부 검증:

```text
OCI 실제 서버 배포
Google Cloud Console 운영 Redirect URI 등록
OCI URL 기준 Google OAuth 수동 로그인 확인
```

## Release Candidate 검증 결과

```text
날짜: 2026-07-01
단계: Release Candidate 검증
추론 수준: 높음

1단계 pytest:
명령: uv run pytest
결과: PASS
PASS: 47
FAIL: 0

2단계 Playwright E2E:
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0
검증 범위: 메인 페이지 접속, 회원가입/로그인, 예약 목록 조회, 예약 추가, 예약 상태 변경, API Key 등록/교체/삭제, 새로고침 후 데이터 유지

환경 준비:
명령: npm install
결과: PASS
명령: npx playwright install chromium
결과: PASS
명령: sudo npx playwright install-deps chromium
결과: PASS
```

주의:

```text
Playwright E2E는 /tmp/gpt-manager-e2e.db를 사용한다.
앱 기능 코드는 변경하지 않았고, 테스트 인프라만 추가했다.
```

## Release Candidate 운영 버그 수정 검증

```text
날짜: 2026-07-01
문제: 운영 SQLite DB의 user 테이블에 Phase 6 컬럼(auth_provider, approval_status)이 없어 /auth/register 500 발생
원인: db.create_all()은 기존 테이블에 신규 컬럼을 추가하지 않음
수정: SQLite 기존 user 테이블에 누락된 auth_provider, approval_status 컬럼을 앱 시작 시 보수적으로 추가
영향 범위: SQLite 기존 DB 스키마 호환성, 앱 기능 코드 동작 변경 없음

재검증:
uv run pytest: 47 passed
npm run test:e2e: 1 passed
```
