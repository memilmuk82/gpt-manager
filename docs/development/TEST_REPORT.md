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

Docker Compose 리빌드:
명령: docker compose up -d --build
결과: PASS
컨테이너: gpt-manager-web-1 Up
healthz: 200 {"status":"ok"}
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

## Release Candidate OCI 운영 배포 검증

```text
날짜: 2026-07-01
단계: OCI 운영 배포 및 운영 환경 검증

GitHub:
master pushed: PASS
latest commit deployed: 926e3f1 fix: migrate legacy sqlite user columns

OCI 배포:
git pull: PASS, Already up to date
docker compose build: PASS
docker compose up -d: PASS
container status: PASS, gpt-manager-web-1 Up

Health Check:
GET /healthz: PASS, 200 {"status":"ok"}

운영 DB 보정:
user.auth_provider: PASS
user.approval_status: PASS

운영 로컬 검증:
메인 페이지 접속: PASS
회원가입 및 세션 생성: PASS
로컬 로그인: PASS
세션 유지: PASS
예약 목록 조회: PASS
예약 추가: PASS
예약 완료 상태 변경: PASS
Gemini API Key 등록/교체: PASS
Gemini API Key 삭제: PASS
CRUD 후 세션 유지: PASS

운영 OAuth 검증:
결과: BLOCKED
원인: GOOGLE_CLIENT_ID와 GOOGLE_CLIENT_SECRET이 운영 .env에 설정되어 있지 않음
현재 동작: GET /auth/google/login -> 302 /auth/login
필요 조치: Google Cloud Console OAuth Client 생성 후 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI 설정 및 컨테이너 재기동
```

Release Freeze 판정:

```text
보류
사유: Google OAuth 운영 검증 미완료
```

## SQLite instance 영속성 검증

```text
날짜: 2026-07-01
목표: SQLite DB가 컨테이너 내부 전용 저장소가 아니라 host bind mount의 ./instance/app.db에 유지되는지 확인

구성 확인:
SQLite DB 컨테이너: 없음
Docker Compose bind mount: ./instance:/app/instance
DATABASE_URL: sqlite:///instance/app.db
SQLite 파일: /app/instance/app.db
Host 파일: ./instance/app.db

재기동 검증:
docker compose down: PASS
docker compose up -d: PASS
/healthz: PASS, {"status":"ok"}

down 전 데이터:
users=3
reservations=2

down/up 후 데이터:
users=3
reservations=2

pytest:
uv run pytest: 47 passed
```



## 2026-07-02 UI/예약/권한 및 운영 도메인 검증

```text
날짜: 2026-07-02
범위: Apps Script 기준 UI 문구 정리, 홈/사용 안내, 오늘 예약, 보조관리자, 운영 도메인 확인

pytest:
명령: uv run pytest
결과: PASS
PASS: 50
FAIL: 0

추가 문법 검사:
python3 -m py_compile app/config.py app/models/__init__.py app/services/access_policy.py app/admin/routes.py app/reservations/routes.py app/routes/main.py
결과: PASS

Docker 재빌드:
docker compose down: PASS
docker compose up -d --build: PASS
container status: gpt-manager-web-1 Up

로컬 HTTP:
GET http://127.0.0.1:5000/: 200 OK
GET http://127.0.0.1:5000/healthz: 200 OK

운영 도메인:
DNS dev-gpt.memilmuk82.com: 129.154.221.2
GET https://dev-gpt.memilmuk82.com/: 200 OK
GET http://dev-gpt.memilmuk82.com/: 301 -> https://dev-gpt.memilmuk82.com/
GET https://dev-gpt.memilmuk82.com/healthz: 200 {"status":"ok"}
GET https://dev-gpt.memilmuk82.com/reservations/today: 302 /auth/login?next=%2Freservations%2Ftoday

추가 테스트 파일:
tests/test_reservations.py - 오늘 예약 날짜 필터 및 취소 예약 제외
tests/test_admin.py - assistant_admin 관리자 화면 접근
tests/test_auth.py - ASSISTANT_ADMIN_EMAILS 자동 role 부여
```

## 2026-07-02 법적 고지 페이지 검증

```text
날짜: 2026-07-02
범위: 이용약관, 개인정보처리방침, 정보관리책임자, Copyright Footer, Markdown 렌더링

문법 검사:
python3 -m py_compile app/routes/main.py app/services/legal_markdown_service.py app/__init__.py
결과: PASS

부분 pytest:
uv run pytest tests/test_legal_pages.py tests/test_app.py tests/test_auth.py
결과: PASS
PASS: 17
FAIL: 0

전체 pytest:
uv run pytest
결과: PASS
PASS: 55
FAIL: 0

Playwright E2E:
npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0
```

검증 범위:

```text
Footer Copyright 출력
Footer 이용약관 링크 /terms 이동
Footer 개인정보처리방침 링크 /privacy 이동
/terms 정상 출력
/privacy 정상 출력
Markdown 파일 변경 시 페이지 반영
raw HTML/script 이스케이프 처리
승인 대기 사용자 /terms, /privacy 접근 가능
기존 회원가입/로그인/예약/API Key E2E 흐름 유지
```

## 2026-07-02 문서 최신화 검증

```text
날짜: 2026-07-02
범위: README, 상태 문서, 설계 문서, 릴리스 체크리스트, 구조 문서, 보안 결정 문서 최신화

Markdown 코드펜스 검사:
전체 *.md 코드펜스 균형 확인
결과: PASS

pytest:
uv run pytest
결과: PASS, 55 passed

오래된 상태 문구 검색:
README/TASK/PROJECT_STATUS/SYSTEM_DESIGN/DEVELOPMENT_PLAN/docs 주요 문서에서 50 passed 및 95f51ca 기준 현재 상태 문구 검색
결과: 현재 상태 문서에서는 제거 완료
참고: 과거 개발 로그의 당시 검증 기록은 보존
```


## 2026-07-03 관리자/예약/안내 UI 확장 검증

```text
날짜: 2026-07-03
범위: 관리자 설정/안내문구/사용자/등록요청/통계/테스트 실행, 사용 신청 시간 계산/충돌 확인, 사용 안내 데이터화, 문서 최신화
```

문법 검사:

```text
명령: python3 -m py_compile app/models/__init__.py app/__init__.py app/admin/routes.py app/reservations/routes.py app/routes/main.py app/auth/routes.py app/config.py app/defaults.py
결과: PASS
```

전체 pytest:

```text
명령: uv run pytest
결과: PASS
PASS: 55
FAIL: 0
```

Playwright E2E:

```text
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0
```

로컬 화면 검증:

```text
서버: http://127.0.0.1:5001
로그인: review.admin@senedu.kr / ReviewAdmin!2026
/dashboard: 200
/reservations/new: 200
/reservations/today: 200
/reservations: 200
/guide: 200
/admin: 200
/admin?section=settings: 200
/admin?section=guides: 200
/admin?section=users: 200
/admin?section=requests: 200
/admin?section=stats: 200
/admin?section=tests: 200
```

예약 충돌 API:

```text
GET /reservations/conflicts?resource_id=<id>&start_at=2026-07-03T17:45&end_at=2026-07-03T18:45
결과: 200
응답: {"ok": true, "has_conflict": false, "message": "동시간대 예약이 없습니다."}
```

검증 범위:

```text
기존 인증/관리자/예약/로그/API Key/프롬프트 점검 테스트 유지
새 예약 필수 입력값 work_type, safety_confirmed 반영
E2E 등록 요청/로그인/사용 신청/예약 완료/API Key 흐름 유지
관리자 주요 섹션 렌더링 확인
```

## 2026-07-03 senedu.kr 도메인 제한 해제 검증

```text
범위: Google OAuth hd 힌트 제거, 신규 로컬/Google 계정 자동 승인, 기존 관리자 권한 정책 유지
python3 -m py_compile app/services/access_policy.py app/services/oauth_service.py app/config.py app/auth/routes.py: PASS
uv run pytest: PASS, 55 passed
npm run test:e2e: PASS, 1 passed
```


## 2026-07-03 신청 항목 관리 및 검증 보강 결과

```text
범위: AI 리소스/작업유형 관리자 관리, 안내 문구 Settings 연동, 인증번호 담당자 2명 제한, Google OAuth 관리자 승인 정책, 관리자 pytest fallback, Docker dev dependency 설치

전체 pytest:
명령: uv run pytest
결과: PASS
PASS: 61
FAIL: 0

Playwright E2E:
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0

Docker Compose 리빌드:
명령: docker compose up -d --build
결과: PASS
컨테이너: gpt-manager-web-1 Up
healthz: 200 {"status":"ok"}
```

추가 테스트 범위:

```text
관리자 AI 리소스/작업유형 저장 후 사용 신청 폼 반영
안내 문구 관리에서 GPT 접속/인증번호 안내 Settings 저장 후 홈 화면 반영
인증번호 담당자 최대 2명 제한
관리자 테스트 실행 명령: python -m pytest 및 uv run --frozen pytest fallback
Google OAuth 신규/기존 사용자 승인 및 관리자 권한 부여
```


## 2026-07-03 주요 화면 문구 Settings 연동 검증

```text
범위: GPT 접속 안내 제목, 사용 신청 안내 문구, 사용 신청 보조 문구, 사용 안내 소개 문구의 Settings 기반 렌더링

전체 pytest:
명령: uv run pytest
결과: PASS
PASS: 65
FAIL: 0

Playwright E2E:
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0
```

Docker Compose 리빌드:
명령: docker compose up -d --build
결과: PASS
컨테이너: gpt-manager-web-1 Up
healthz: 200 {"status":"ok"}


추가 테스트 범위:

```text
관리자 설정값 auth_info_title이 홈 화면 GPT 접속 안내 제목으로 표시됨
reservation_intro_text와 reservation_helper_text가 사용 신청 화면에 표시됨
guide_intro_text가 사용 안내 화면에 표시됨
```


## 2026-07-03 프롬프트 점검 UI 최신화 검증

```text
범위: 상단 프롬프트 점검 메뉴, 홈 빠른 이동, 프롬프트 점검 목록/생성/상세 화면 최신 UI, 구버전 PROMPT REVIEWS 표기 제거

전체 pytest:
명령: uv run pytest
결과: PASS
PASS: 65
FAIL: 0

Playwright E2E:
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0

Docker Compose 리빌드:
명령: docker compose up -d --build
결과: PASS
컨테이너: gpt-manager-web-1 Up
healthz: 200 {"status":"ok"}
```

추가 테스트 범위:

```text
홈 화면에 프롬프트 점검 빠른 이동 카드 표시
프롬프트 점검 목록과 새 점검 화면 렌더링
구버전 PROMPT REVIEWS 텍스트 미노출
```


## 2026-07-03 개인 설정 및 API Key 화면 최신화 검증

```text
범위: 승인 사용자 badge의 /settings/api-key 링크, Gemini API Key 설정 화면 최신 UI, 구버전 SETTINGS 표기 제거

전체 pytest:
명령: uv run pytest
결과: PASS
PASS: 65
FAIL: 0

Playwright E2E:
명령: npm run test:e2e
결과: PASS
PASS: 1
FAIL: 0

Docker Compose 리빌드:
명령: docker compose up -d --build
결과: PASS
컨테이너: gpt-manager-web-1 Up
healthz: 200 {"status":"ok"}
```

추가 테스트 범위:

```text
승인 사용자 badge가 /settings/api-key 링크로 렌더링됨
Gemini API Key 설정 화면에 개인 설정 문구와 최신 제목 표시
구버전 SETTINGS 텍스트 미노출
```
