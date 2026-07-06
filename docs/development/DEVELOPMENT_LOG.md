# Development Log

## 관련 문서

[README](../../README.md) · [현재 상태](../../PROJECT_STATUS.md) · [테스트 리포트](TEST_REPORT.md)


## 2026-06-30 - Phase 0

### 결정

```text
새 교육자료 생성 앱은 만들지 않음
기존 GPT 공유앱을 Flask 기반으로 재설계
BYOK LLM API는 프롬프트 정리/개선에 사용
SQLite + Docker Compose + OCI 단일 인스턴스 사용
2026-07-02 RC1, 2026-07-03 기능 동결 원칙 채택
```

### 이유

```text
수업안/평가계획 생성기는 NotebookLM/ChatGPT로 대체 가능성이 높음
사용자가 실제로 계속 쓸 가능성이 낮음
기존 GPT 공유앱은 운영 시스템으로 앱의 존재 이유가 명확함
프롬프트 정리기는 BYOK LLM API 활용 조건을 자연스럽게 충족함
```

### 다음 작업

```text
Codex에 문서 패킷 전달
Phase 1 기본 골격 생성
pytest와 Docker Compose 확인
```

## 2026-06-30 - Phase 1

### 구현

```text
Flask app factory 작성
환경변수 기반 Config 작성
SQLAlchemy extension 초기화
/ 및 /healthz route 작성
Jinja base/index template 작성
Tailwind CDN 적용
uv pyproject.toml 및 uv.lock 생성
Dockerfile 및 compose.yaml 작성
pytest 기본 테스트 작성
```

### 제외

```text
로그인 구현 제외
Google OAuth 구현 제외
예약 CRUD 제외
BYOK LLM API 호출 제외
API Key 암호화 제외
관리자 화면 제외
```

### 검증

```text
uv run pytest: 4 passed
docker compose up --build -d: success
curl /healthz: 200 {"status":"ok"}
curl /: 200
```

### 다음 작업

```text
Phase 2 인증 구현 계획 보고
User 모델, 로컬 로그인, Google OAuth 구조, admin seed 검토
```

## 2026-06-30 - Phase 2

### 구현

```text
Flask-Login 의존성 추가
LoginManager 초기화
User 모델 추가
Werkzeug password hash/check 적용
로컬 회원가입 구현
로컬 로그인 구현
POST 로그아웃 구현
/dashboard 로그인 보호 구현
인증 및 대시보드 Jinja 템플릿 작성
인메모리 SQLite 테스트 fixture 작성
인증/비밀번호/설정 테스트 작성
```

### 제외

```text
Google OAuth 구현 제외
BYOK LLM API 구현 제외
예약 CRUD 제외
사용 로그 구현 제외
API Key 암호화 구현 제외
관리자 기능 구현 제외
```

### 리팩토링 검토

```text
상대 SQLite DATABASE_URL이 Flask instance 경로로 해석될 수 있어 ./data 기준 절대 경로 정규화 추가
비밀번호 처리는 User 모델 메서드로 캡슐화
로그인 실패 메시지는 이메일 존재 여부를 드러내지 않는 단일 문구로 유지
CSRF는 Phase 2 범위에서 도입하지 않고 후속 보완 사항으로 기록
```

### 검증

```text
uv run pytest: 14 passed
리팩토링 후 uv run pytest: 14 passed
docker compose up --build -d: image build success, host 5000 port already in use
docker run -p 5001:5000 gpt-manager-web:latest: success
/healthz on 5001: 200 {"status":"ok"}
/ on 5001: 200
/dashboard on 5001: 302 to /auth/login?next=%2Fdashboard
```

### 다음 작업

```text
Phase 3 예약/로그 구현 계획 보고
AiResource, Reservation, UsageLog 모델과 예약 충돌 테스트 설계
```



## 2026-07-01 - Phase 3

### 구현

```text
AiResource 모델 추가
Reservation 모델 및 상태값 추가
UsageLog 모델 추가
예약 목록/생성/취소/완료 구현
예약 시간 파싱 및 충돌 검증 service 추가
사용 로그 목록/생성/상세 조회 구현
예약/로그 템플릿 작성
예약/로그 접근을 현재 사용자로 제한
```

### 검증

```text
uv run pytest: 25 passed
```

### 다음 작업

```text
Phase 4 AI Provider/API Key 암호화 설정 구현
UserApiKey 모델, Fernet 암호화, 등록/삭제/마스킹 테스트 추가
```

## 2026-07-01 - Phase 4

### 구현

```text
cryptography 의존성 사용
UserApiKey 모델 추가
Fernet 기반 암호화/복호화 service 추가
/settings/api-key 화면 추가
AI Provider/API Key 등록/교체/삭제 구현
저장 상태 마지막 4자리 마스킹 표시
저장된 키 복호화 확인 기능 추가
내비게이션과 대시보드 문구 갱신
```

### 보안 메모

```text
API Key 원문은 DB에 저장하지 않음
화면에는 마지막 4자리만 표시
운영 환경에서는 APP_ENCRYPTION_KEY를 Fernet 키로 고정 설정 필요
```

### 검증

```text
uv run pytest: 30 passed
```

### 다음 작업

```text
Phase 5 프롬프트 정리기 구현
PromptReview 모델, LLM adapter 호출 service, mock 테스트 작성
```


## 2026-07-01 - Phase 5

### 추론 수준

```text
높음
```

### 구현

```text
PromptReview 모델 추가
프롬프트 정리 목록/입력/상세 화면 추가
정리 프롬프트 조립 service 추가
Gemini REST 호출 service 추가
저장된 AI Provider/API Key 복호화 후 호출에 사용
LLM adapter 호출부 mock 테스트 추가
입력 길이 제한 및 사용자별 접근 제한 구현
Gemini Provider 기본 모델을 gemini-3.1-flash-lite로 갱신
```

### 예정 보강

```text
Phase 6에서 Google OAuth 로그인 구현
ALLOWED_GOOGLE_DOMAIN=senedu.kr 기준으로 Google 로그인 계정 제한
필요 시 로컬 회원가입도 senedu.kr 도메인으로 제한
```

### 검증

```text
uv run pytest: 36 passed
```

### 다음 작업

```text
Phase 6 관리자 대시보드 및 Google OAuth senedu.kr 제한 구현
```


## 2026-07-01 - Phase 6

### 추론 수준

```text
높음
```

### 정책 결정

```text
senedu.kr 계정은 자동 승인
그 외 Google 계정과 로컬 이메일 계정은 pending 상태로 등록
관리자가 승인하면 사용 가능
정지된 계정은 로그인/기능 접근 차단
```

### 구현

```text
User approval_status/auth_provider 필드 추가
ApprovalStatus 값 추가
전역 승인 상태 접근 제어 before_request 추가
관리자 대시보드 추가
사용자 승인/정지 관리 화면 추가
Google OAuth login/callback 기본 라우트 추가
Google userinfo fetch service 추가
Google callback에서 email_verified/sub/email 검증
ADMIN_EMAILS 설정 추가
ALLOWED_GOOGLE_DOMAIN 기본값을 senedu.kr로 설정
로그인/회원가입 화면에 승인제 안내 추가
```

### 검증

```text
uv run pytest: 46 passed
```

### 다음 작업

```text
Phase 7 README/.env.example/배포 문서 정리
OCI 배포 및 실제 Google OAuth Redirect URI 확인
최종 제출 테스트
```


## 2026-07-01 - Phase 7

### 추론 수준

```text
높음
```

### 진행

```text
README를 Phase 7 기준으로 최신화
.env.example에 운영/OAuth 설정 주석 보강
Google OAuth Redirect URI 설정 문서 추가
OCI Dev Server 문서의 compose/env 예시를 현재 앱 설정과 일치하도록 보완
```

### 검증

```text
uv run pytest: 46 passed
docker compose build: success
docker compose up -d: success
curl http://localhost:5000/healthz: {"status":"ok"}
docker compose down: success
```

### 남은 작업

```text
OCI 실제 서버에서 .env 운영값 설정
Google Cloud Console Redirect URI 등록
OCI URL에서 OAuth 로그인 수동 확인
제출 전 최종 시연 리허설
```

## 2026-07-01 - Release Candidate 검증

### 추론 수준

```text
높음
```

### 검증

```text
uv run pytest: 47 passed
Playwright E2E 테스트 인프라 추가
npm run test:e2e: 1 passed
```

### Playwright 검증 범위

```text
메인 페이지 접속
회원가입 및 로컬 로그인
예약 목록 조회
예약 추가
예약 완료 상태 변경
AI Provider/API Key 등록/교체/삭제
새로고침 후 예약/API Key 상태 유지 확인
```

### 변경 범위

```text
앱 기능 코드 변경 없음
Playwright 테스트 설정과 E2E 테스트 추가
Release Candidate 검증 결과 문서화
```

### 다음 작업

```text
검증 커밋 후 master push
OCI 운영 서버 git pull/build/up
운영 /healthz, OAuth, 로컬 로그인, CRUD, 세션 유지 검증
모든 운영 검증 PASS 시 Release Freeze 전환
```

### 운영 버그 수정

```text
운영 DB가 Phase 6 이전 user 스키마라 auth_provider/approval_status 컬럼이 누락됨
/auth/register에서 no such column: user.auth_provider 발생
SQLite 앱 시작 시 누락 컬럼을 추가하는 호환성 migration 추가
기존 사용자 approval_status 기본값은 approved로 유지
```

### 재검증

```text
uv run pytest: 47 passed
npm run test:e2e: 1 passed
```

## 2026-07-01 - OCI 운영 배포 검증

### 배포

```text
git pull: Already up to date
docker compose build: success
docker compose up -d: success
```

### 운영 버그

```text
1. 기존 SQLite user 테이블에 auth_provider/approval_status 누락
   - 앱 시작 시 SQLite 호환성 migration 추가
   - pytest 47 passed
   - Playwright E2E 1 passed

2. 운영 .env 승인 정책 누락
   - ALLOWED_GOOGLE_DOMAIN=senedu.kr 설정
   - ADMIN_EMAILS=admin@senedu.kr 설정

3. 운영 APP_ENCRYPTION_KEY가 Fernet 형식이 아님
   - 유효한 Fernet 키로 교체
```

### 운영 검증 결과

```text
/healthz: PASS
로컬 로그인: PASS
예약 CRUD 성격 검증: PASS
API Key 등록/교체/삭제: PASS
세션 유지: PASS
Google OAuth: 2026-07-01 당시 미설정. 2026-07-02에 운영 Redirect URI와 도메인 응답 확인 완료
```

### Release Freeze 판정

```text
2026-07-01 당시 보류
2026-07-02 도메인/OAuth Redirect URI 확인 후 RC 운영 검증 완료 상태로 갱신
```

## 2026-07-01 - SQLite instance 저장 구조 확인

### 확인

```text
SQLite DB 컨테이너 없음
기존 구성은 ./data:/app/data bind mount 사용
요구 기준에 맞춰 ./instance:/app/instance bind mount로 전환
운영 DATABASE_URL=sqlite:///instance/app.db 확인
기존 data/app.db와 동일 크기의 instance/app.db 존재 확인
```

### 변경

```text
기본 DB 경로를 instance/app.db로 변경
Dockerfile 생성 디렉터리를 /app/instance로 변경
compose.yaml bind mount를 ./instance:/app/instance로 변경
.env.example과 배포/설계 문서를 instance 기준으로 갱신
```



## 2026-07-02 - UI/예약/보조관리자/도메인 검증

### 구현

```text
공통 헤더를 생성형 AI 계정 공동 사용 지원 시스템 기준으로 정리
비로그인 시작 화면 문구 일반화
승인 사용자 홈 화면에 현재 사용중/다음 예약/접속 안내/빠른 메뉴/오늘 예약 요약 추가
사용 안내 화면 /guide 추가
오늘 예약 화면 /reservations/today 추가
보조관리자 role assistant_admin 추가
ASSISTANT_ADMIN_EMAILS 환경변수 추가
관리자 탭과 /admin 접근을 admin 또는 assistant_admin에게 허용
사용자 관리 화면에서 assistant_admin을 보조관리자로 표시
```

### 검증

```text
uv run pytest: 50 passed
python3 -m py_compile: PASS
docker compose down: PASS
docker compose up -d --build: PASS
http://127.0.0.1:5000/: 200 OK
https://dev-gpt.memilmuk82.com/: 200 OK
https://dev-gpt.memilmuk82.com/healthz: 200 {"status":"ok"}
/reservations/today 비로그인 접근: 302 /auth/login?next=...
```

### 배포

```text
git push origin master: PASS
최신 커밋: 95f51ca ui: add today reservations and assistant admin
Docker 이미지 재빌드 완료
Nginx HTTPS 도메인 응답 확인 완료
Google OAuth Redirect URI: https://dev-gpt.memilmuk82.com/auth/google/callback
```

## 2026-07-02 - 법적 고지 페이지 추가

### 구현

```text
docs/legal/TERMS.md Markdown 이용약관 작성
docs/legal/PRIVACY_POLICY.md Markdown 개인정보처리방침 작성
/terms 라우트 추가
/privacy 라우트 추가
공통 Footer에 Copyright, 기관명, 대표번호, 이용약관, 개인정보처리방침 표시
법적 문서를 HTML 템플릿에 직접 작성하지 않고 Markdown 파일에서 렌더링하도록 구성
승인 대기 사용자도 /terms, /privacy 접근 가능하도록 허용 endpoint 추가
```

### Markdown 렌더링 및 보안

```text
app/services/legal_markdown_service.py 추가
제한된 Markdown 문법만 HTML로 변환
본문 텍스트와 raw HTML은 html.escape로 이스케이프
템플릿에서는 렌더링된 allowlist HTML만 safe 처리
프론트에 API Key 또는 비밀값 노출 없음
개인정보/학생 민감정보/평가 문항 원본을 입력하지 말라는 정책 문구를 문서에 명시
```

### 검증

```text
python3 -m py_compile app/routes/main.py app/services/legal_markdown_service.py app/__init__.py: PASS
uv run pytest tests/test_legal_pages.py tests/test_app.py tests/test_auth.py: 17 passed
uv run pytest: 55 passed
npm run test:e2e: 1 passed
```

### 추가 검토 필요

```text
법률 문구는 프로젝트 운영 목적에 맞춰 작성했으나 최종 고지는 개인정보보호법/교육기관 내부 정책 기준의 법률 검토 필요
개인정보 보유 기간, 파기 절차, 제3자 제공/국외 이전 해당 여부는 실제 운영 정책 확정 후 문서 보완 필요
```

## 2026-07-02 - README 및 문서 최신화

### 범위

```text
README.md 최신 상태 반영
PROJECT_STATUS.md와 TASK.md 최신 커밋/검증 상태 반영
SYSTEM_DESIGN.md에 /terms, /privacy, Footer, Markdown 렌더링 보안 반영
RELEASE_CHECKLIST.md에 법적 페이지와 E2E 확인 항목 추가
REPOSITORY_STRUCTURE.md에 legal service/template/docs/test 파일 반영
SECURITY_DECISIONS.md에 Markdown 법적 문서 렌더링 제한 결정 추가
MANIFEST.md에 docs/legal 문서 추가
```

### 검증

```text
전체 Markdown 코드펜스 균형 검사: PASS
uv run pytest: 55 passed
오래된 README/TASK/상태 문서의 50 passed 및 95f51ca 기준 문구 제거 확인
문서만 변경되어 앱 컨테이너 재빌드 필요성은 낮음
```


## 2026-07-03 - 관리자/예약/안내 UI 확장 및 수업 맥락 문서화

### 배경

```text
종로산업정보학교 AI컴퓨터과 1년 교육과정 반영
1학기 Python, Flask, SQLite, CRUD 학습 흐름과 연결
2학기 SQLAlchemy, 칸반보드 기반 개인 프로젝트, 생성형 AI 프론트엔드 보조, 학생 주도 백엔드 구현 흐름 반영
OCI 개인 인스턴스 또는 학교 서버 배포 시연 흐름 고려
```

### 구현

```text
README 상단 리뷰용 관리자 계정 안내 추가
README에 Flask - SQLite - OCI 선택 이유와 수업 맥락 추가
app/defaults.py 추가: 작업 유형, 기본 설정, 기본 안내문구 중앙화
User 모델 확장: department, extension, is_auth_manager, sort_order
Reservation 모델 확장: work_type, description, safety_confirmed
AppSetting, GuideItem 모델 추가
SQLite 기존 DB 호환 컬럼 보정 추가
기본 설정/안내문구/리소스/리뷰용 관리자 계정 자동 시드 추가
관리자 설정 관리, 안내문구 관리, 사용자 관리, CSV 일괄 등록, 등록 요청 관리, 통계 조회, 전체 테스트 실행 구현
사용 신청 작업 유형 드롭다운, 사용 시간 자동 계산, 사용 전 확인, 충돌 확인 API 구현
홈/오늘 예약/내 예약/사용 안내/미등록 사용자/등록 요청/관리자 화면 디자인 정리
사용 안내 화면을 GuideItem 기반으로 전환
```

### 문서

```text
docs/development/2026-07-03_ADMIN_RESERVATION_UI_UPDATE.md 추가
PROJECT_STATUS.md 최신 상태 반영
TASK.md 최신 작업 상태 반영
SYSTEM_DESIGN.md 새 모델/라우트/SQLite 보정/기본 데이터 구조 반영
REPOSITORY_STRUCTURE.md app/defaults.py와 변경 기록 문서 반영
MANIFEST.md 변경 기록 문서 추가
TEST_REPORT.md 검증 결과 추가
```

### 검증

```text
python3 -m py_compile app/models/__init__.py app/__init__.py app/admin/routes.py app/reservations/routes.py app/routes/main.py app/auth/routes.py app/config.py app/defaults.py: PASS
uv run pytest: PASS, 55 passed
npm run test:e2e: PASS, 1 passed
로컬 Flask 서버 http://127.0.0.1:5001 주요 화면 200 확인
/reservations/conflicts JSON API 확인: ok=true, has_conflict=false
```

## 2026-07-03 - senedu.kr 도메인 제한 해제

### 변경

```text
ALLOWED_GOOGLE_DOMAIN 기본값을 빈 값으로 변경
Google OAuth authorization URL에서 기본 hd=senedu.kr 힌트 제거
신규 로컬/Google 계정 initial_approval_status를 도메인과 관계없이 approved로 변경
관리자/보조관리자 role 지정은 ADMIN_EMAILS, ASSISTANT_ADMIN_EMAILS 기준 유지
```

### 검증

```text
python3 -m py_compile app/services/access_policy.py app/services/oauth_service.py app/config.py app/auth/routes.py: PASS
uv run pytest: PASS, 55 passed
npm run test:e2e: PASS, 1 passed
```


## 2026-07-03 - 신청 항목 관리 및 검증 보강

### 변경

```text
WorkType 모델 추가 및 DEFAULT_WORK_TYPES 시드 처리
관리자 신청 항목 관리 섹션 추가: AI 리소스와 작업유형 생성/수정/활성화 관리
사용 신청 화면 작업유형을 DB active WorkType 기준으로 표시하고 비어 있으면 기본값 fallback
안내 문구 관리에서 GPT 접속/인증번호 안내 Settings도 함께 수정 가능하도록 확장
인증번호 담당자 최대 2명 제한을 사용자 추가/수정/CSV 일괄 등록에 적용
Google OAuth 로그인 사용자는 승인 상태와 관리자 권한으로 등록 또는 승격
관리자 전체 테스트 실행이 pytest 모듈 미탑재 환경에서 uv run --frozen pytest로 fallback
Dockerfile에서 관리자 테스트 실행 지원을 위해 dev dependency group 설치
README, PROJECT_STATUS, RELEASE_CHECKLIST, TEST_REPORT, 변경 기록 문서 최신화
```

### 검증

```text
uv run pytest: PASS, 61 passed
npm run test:e2e: PASS, 1 passed
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: 200 {"status":"ok"}
```


## 2026-07-03 - 주요 화면 문구 Settings 연동

### 변경

```text
auth_info_title 기본 설정 추가
reservation_intro_text, reservation_helper_text 기본 설정 추가
guide_intro_text 기본 설정 추가
관리자 안내 문구 관리 화면에서 GPT 접속 안내 제목, 사용 신청 안내 문구, 사용 안내 소개 문구까지 수정 가능하도록 확장
홈/사용 안내의 GPT 접속 안내 제목을 Settings 기반으로 렌더링
사용 신청 화면 상단 안내 문구를 Settings 기반으로 렌더링
사용 안내 화면 소개 문구를 Settings 기반으로 렌더링
설정 관리 화면에서 긴 안내 문구 필드는 textarea로 표시
관리자 문구 설정 렌더링 테스트 추가
```

### 검증

```text
uv run pytest: PASS, 65 passed
npm run test:e2e: PASS, 1 passed
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: 200 {"status":"ok"}
```


## 2026-07-03 - 프롬프트 정리 UI 최신화

### 변경

```text
상단 네비게이션에 프롬프트 정리 메뉴 추가
홈 빠른 이동에 프롬프트 정리 카드 추가
프롬프트 정리 목록 화면에서 구버전 PROMPT REVIEWS 표기를 제거하고 최신 카드/테이블 톤으로 정리
새 프롬프트 정리 화면 입력 폼과 민감정보 경고 UI 정리
정리 결과 상세 화면을 원본 요청과 AI 정리 결과 2열 카드로 정리
프롬프트 정리 메뉴/화면 문구 렌더링 테스트 추가
```

### 검증

```text
uv run pytest: PASS, 65 passed
npm run test:e2e: PASS, 1 passed
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: 200 {"status":"ok"}
```


## 2026-07-03 - 개인 설정 및 API Key 화면 최신화

### 변경

```text
상단 승인 사용자 badge를 개인 AI Provider/API Key 설정 링크로 전환
미승인 사용자는 기존 badge 표시 유지
AI Provider/API Key 설정 화면을 최신 카드형 UI로 정리
저장 상태, 보안 안내, 새 API Key 저장 폼을 분리
프롬프트 정리 화면으로 이동하는 버튼과 홈으로 이동하는 버튼 추가
API Key 설정 화면에서 구버전 SETTINGS 표기 제거
사용자 badge 링크와 API Key 설정 화면 렌더링 테스트 추가
```

### 검증

```text
uv run pytest: PASS, 65 passed
npm run test:e2e: PASS, 1 passed
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: 200 {"status":"ok"}
```

## 🧹 2026-07-04 - 문서 구조 정리 및 최신화

### 배경

README가 프로젝트 포털, 교육과정, 기술 선택, 현재 상태, 주요 문서 목록을 모두 길게 반복하면서 `PROJECT_STATUS.md`, `docs/EDUCATION.md`, `docs/decisions/TECH_STACK_DECISIONS.md`와 역할이 일부 겹쳤다. 또한 `TASK.md`, `SYSTEM_DESIGN.md`, `docs/development/RELEASE_CHECKLIST.md`에는 이전 테스트 수치와 RC 기준 문구가 남아 있었다.

### 변경

```text
README에 주요 섹션 이모지 적용
README 기술 선택 상세 표를 요약 표로 축약하고 상세 문서 링크 유지
README 하단 중복 문서 목록을 문서 관리 원칙으로 축약
PROJECT_STATUS를 현재 상태 중심으로 재구성
TASK를 현재 문서 정리 완료 상태와 다음 운영 TODO 중심으로 최신화
CODEX_START_HERE를 현재 유지보수/문서 검증 흐름에 맞게 수정
RELEASE_CHECKLIST를 2026-07-04 기준 테스트 수치와 운영 전 확인 항목으로 갱신
MANIFEST에 누락된 교육/배포/법적/개발 기록 문서 반영
SYSTEM_DESIGN의 CSRF 보호 상태와 테스트 수치 최신화
DEVELOPMENT_PLAN의 현재 완료 상태 최신화
```

### 검증

```text
Markdown 코드블록 검증: PASS, 오류 0
Markdown 로컬 링크 검증: PASS, 오류 0
오래된 현재 상태 문구 검색: 현재 문서에서는 제거 완료
과거 테스트 수치: DEVELOPMENT_LOG와 날짜별 TEST_REPORT 기록에는 이력 보존
```

## 🧪 2026-07-04 - RC 운영 CRUD 검증 더미데이터 추가

### 배경

리뷰와 시연 과정에서 빈 화면이 아니라 실제 운영되는 서비스처럼 각 메뉴를 확인할 수 있도록 `RC 운영 CRUD 검증 1782896313` 태그의 더미데이터를 추가했다.

### 변경

```text
scripts/seed_demo_data.py 추가
시연용 사용자 6명 생성
AI 리소스 4개와 작업유형 4개 생성
오늘/과거/미래/취소/완료 예약 12건 생성
사용 로그 4건과 프롬프트 정리 기록 4건 생성
AI Provider/API Key 더미 암호화 저장 3건 생성
관리자 감사 로그 4건 생성
운영 공지 배너 활성화
README에 더미 계정과 seed 실행 방법 문서화
프롬프트 정리 실제 라우트 /prompt-reviews 문서 보정
```

### 검증

```text
python3 -m py_compile scripts/seed_demo_data.py: PASS
uv run python scripts/seed_demo_data.py --date 2026-07-04: PASS
반복 실행 후 중복 증가 없음
주요 메뉴 smoke test: /dashboard, /reservations, /reservations/today, /reservations/calendar, /logs, /prompt-reviews, /settings/api-key, /admin, /admin/users 모두 200
```


## 2026-07-04 - BYOK LLM Provider 기반 프롬프트 정리 확장

```text
사용자별 OpenAI, Google Gemini, Anthropic Claude Provider 설정 추가
API Key 기본 비저장, 선택 시 LLM_KEY_ENCRYPTION_SECRET 기반 암호화 저장 구현
Provider별 모델 선택, 모델 목록 새로고침 fallback, 연결 테스트 구현
OpenRouter는 구현 범위에서 제외
프롬프트 정리 흐름을 구조화된 프롬프트 정리 기능으로 확장
일일/월간/5초 연속 요청 제한 적용
관리자 화면에 API Key 원문 없는 등록 상태 메타데이터만 표시
README, SYSTEM_DESIGN, PRD, PROJECT_STATUS, PROJECT_INSTRUCTIONS, 보안/법적 문서 반영
```

## 2026-07-04 - BYOK 문서 정합성 및 중복 정리

```text
프로젝트 전체 Markdown 문서의 Gemini 단일 Provider/프롬프트 점검 표현을 BYOK 프롬프트 정리 기준으로 정리
README의 BYOK 보안 상세 중복 설명을 SECURITY_DECISIONS와 ADR 0004 참조 구조로 축소
ADR 0002를 superseded 문서로 정리하고 ADR 0004를 현재 기준으로 명확화
법적 문서의 외부 Provider 전송 설명을 OpenAI, Google Gemini, Anthropic Claude 기준으로 정리
```

## 2026-07-04 - 테스트 메뉴 설명 강화 및 BYOK 지시문 최신화

### 변경 배경

관리자 전체 테스트 실행 화면이 pytest 원문 결과는 보여주지만, 각 테스트 파일이 어떤 기능을 검증하는지 이해하기 어려웠다. 또한 Anthropic Claude 기본 추천 모델 목록과 프로젝트 지시문에 현재 구현 상태 기준의 작업 원칙을 명확히 반영할 필요가 있었다.

### 변경 내용

- 관리자 테스트 실행 결과에 테스트 파일별 검증 대상, 주요 검증 내용, PASS/FAIL/SKIP/NOT RUN 상태 표시 추가
- pytest 원문 로그와 기존 결과/요약 UI 유지
- Anthropic Claude 기본 추천 모델에서 claude-opus-4-7 제거, claude-opus-4-8 반영
- 모델 목록 새로고침 시 Provider API 조회 결과는 그대로 표시하는 기존 동작 유지
- PROJECT_INSTRUCTIONS.md에 이미 구현된 기능은 패스하고 미구현/부분 구현/버그만 처리하는 원칙 추가
- README, PROJECT_STATUS, SYSTEM_DESIGN, RELEASE_CHECKLIST, ADR 0004의 테스트 수치와 설명 최신화

### 삭제/정리

- 오래된 테스트 수치 문구를 현재 88 passed 기준으로 교체
- 중복 구현이나 불필요한 코드 파일 삭제는 수행하지 않음. 삭제 가능한 독립 중복 파일은 확인되지 않았고, 기존 문서는 역할이 달라 보존함

### 검증

```text
uv run python -m py_compile app/services/llm/registry.py: PASS
uv run pytest tests/test_api_keys.py tests/test_prompt_reviews.py: PASS, 20 passed
uv run pytest: PASS, 88 passed
관리자 /admin/tests/run 렌더링 확인: PASS
Anthropic API 새로고침 결과에 claude-opus-4-7 포함 시 그대로 반환 확인: PASS
```


## 2026-07-05 - Footer 개인정보 노출 최소화

```text
공통 Footer에서 정보관리책임자 이름과 개인 업무메일 mailto 링크 제거
Footer 표시 항목을 기관명, 대표번호, 이용약관, 개인정보처리방침 링크로 정리
이용약관과 개인정보처리방침 원문은 기존 내용 유지
README, PRD, PROJECT_STATUS, PROJECT_INSTRUCTIONS, 개발 로그, 테스트 리포트의 Footer 설명 최신화
```

### 검증

```text
uv run pytest tests/test_legal_pages.py: PASS, 5 passed
```


## 2026-07-05 - UX/운영 마감 보완 및 문서 재정렬

### 변경 배경

```text
프로젝트가 과제 제출과 시연 단계에 가까워져 대형 기능 추가보다 사용 흐름 마찰 제거와 문서 구조 정합성이 중요해졌다.
관리자 기본 비밀번호와 관리자 테스트 실행 기능은 과제 사이트 의도에 따라 유지했다.
```

### 변경 내용

```text
예약 생성 화면에서 입력 변경 시 충돌 여부 자동 확인
충돌 확인 중 또는 충돌 발생 시 예약 등록 버튼 비활성화
max_duration_minutes 설정을 예약 화면 직접 입력 제한과 안내 문구에 반영
모바일 내비게이션을 홈, 사용 신청, 오늘 예약, 더보기 구조로 정리
관리자 CSV 내보내기에 기간, 사용자, AI 리소스, 작업 유형, 상태, 검색어 필터 추가
SQLite 백업 생성 시 최근 20개만 보관하고 오래된 app-*.db 정리
백업 목록에 생성 시각 표시
README, PROJECT_STATUS, SYSTEM_DESIGN, RELEASE_CHECKLIST, TEST_REPORT, TASK, MANIFEST 최신화
상세 변경 기록을 docs/development/2026-07-05_UX_OPERATIONAL_FINISHING.md로 분리
```

### 검증

```text
python3 -m py_compile app/admin/routes.py app/reservations/routes.py: PASS
uv run pytest tests/test_reservations.py tests/test_admin.py: PASS, 30 passed
uv run pytest: PASS, 91 passed
npm run test:e2e: PASS, 1 passed
git diff --check: PASS
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: PASS, {"status":"ok"}
```


## 2026-07-05 - UI 디자인 시스템 실제 적용 및 문서 정합성 갱신

### 변경 배경

```text
docs/ui의 UI Guide, Design System, Design Decisions가 실제 코드 적용 단계로 넘어갔다.
교사용 학교 업무 플랫폼에 맞는 light operational SaaS UI를 실제 템플릿과 CSS에 반영하고, 문서가 구현 이전 표현을 계속 담지 않도록 정리했다.
```

### 변경 내용

```text
app/static/styles.css 디자인 토큰, radius, button, badge, table, alert, log panel 규칙 정리
base.html header/nav/footer/flash/main spacing 정리, role=alert와 CSRF submit hook 유지
Landing/Auth/Dashboard/Reservations/Logs/Prompts/Admin Test Result 화면 UI 정리
Prompt Result의 비교 구현 오해 가능 표현을 단일 Provider 검토 메모로 조정
form label visible text, table overflow, 긴 한국어 줄바꿈, focus-visible 점검
docs/ui 3개 문서와 개발/검증 문서에 실제 구현 결과 반영
상세 변경 기록을 docs/development/2026-07-05_UI_DESIGN_SYSTEM_IMPLEMENTATION.md로 분리
```

### 검증

```text
git diff --check: PASS
uv run pytest: PASS, 91 passed
npm run test:e2e: PASS, 1 passed
Playwright desktop/mobile overflow check: PASS
```

## 2026-07-05 - 프로필 화면, 관리자 테스트 실패 힌트, E2E 범위 확장

### 변경 배경

```text
추가 작업 후보 중 사이트 성격을 바꾸지 않는 항목만 적용했다.
개인 계정 요약과 관리자 테스트 실패 분석 보조는 현재 단일 Provider 학교 업무 플랫폼 흐름 안에서 제공 가능하다.
```

### 변경 내용

```text
/profile 읽기 전용 개인 프로필 화면 추가
헤더 사용자 badge를 개인 프로필 링크로 변경하고 기존 AI Provider 설정 URL은 CTA로 유지
관리자 테스트 결과에 실패 원인 요약과 해결 힌트 카드 추가
테스트 파일별 표에 실패 요약/해결 힌트 컬럼 추가
Playwright E2E에 Profile, Guide, Settings, Prompt 입력, Reservations, mobile Dashboard, Admin Users/Test/API Key overflow 검증 추가
multi-provider 비교, streaming, 자유형 챗봇 등 사이트 성격을 바꾸는 기능은 제외 유지
```

### 검증

```text
python3 -m py_compile app/admin/routes.py app/routes/main.py: PASS
uv run pytest: PASS, 95 passed
npm run test:e2e: PASS, 2 passed
```

## 2026-07-05 - 예약 직접 입력 최대 시간 8시간 반영

### 변경 내용

```text
max_duration_minutes 기본값을 180분에서 480분으로 변경
운영 DB에 기존 기본값 180이 남아 있으면 앱 초기화 시 480으로 보정
예약 화면 직접 입력 max와 안내 문구가 기본 480분으로 표시되도록 테스트 추가
```

### 검증

```text
python3 -m py_compile app/__init__.py app/defaults.py app/reservations/routes.py: PASS
uv run pytest tests/test_config.py tests/test_reservations.py: PASS, 17 passed
uv run pytest: PASS, 97 passed
npm run test:e2e: PASS, 2 passed
```

## 2026-07-06 - 법적 문서 단위 테스트 제거 및 문서 정합성 정리

### 변경 내용

```text
tests/test_legal_pages.py 삭제
약관과 개인정보처리방침 내용 검증은 테스트 코드가 아니라 수동 검토와 기관 검토 대상으로 정리
관리자 테스트 카탈로그에서 삭제된 테스트 파일 항목 제거
저장소 구조 문서의 tests 목록을 실제 파일 구조에 맞게 갱신
현재 상태 문서의 pytest 기준을 92 passed로 갱신
```

### 검증

```text
uv run pytest: PASS, 92 passed
npm run test:e2e: PASS, 2 passed
```

## 2026-07-06 - 법적 문서 렌더링 테스트 복원

### 변경 내용

```text
tests/test_legal_pages.py를 현재 코드 기준으로 복원
테스트 범위는 Footer 링크, 공개 접근, Markdown 렌더링, raw HTML escape 확인으로 한정
약관과 개인정보처리방침의 법적 내용 타당성은 자동 테스트가 아니라 수동 검토와 기관 검토 대상으로 유지
관리자 테스트 카탈로그와 저장소 구조 문서에 복원된 테스트 파일 반영
현재 상태 문서의 pytest 기준을 97 passed로 갱신
```

### 검증

```text
uv run pytest tests/test_legal_pages.py: PASS, 5 passed
uv run pytest: PASS, 97 passed
```

## 2026-07-06 - Docker 법적 문서 포함 기준 문서화

### 변경 내용

```text
Docker 빌드에서 docs 전체는 제외하되 /terms와 /privacy 런타임에 필요한 TERMS.md, PRIVACY_POLICY.md만 포함하도록 문서화
README, PROJECT_STATUS, REPOSITORY_STRUCTURE, .dockerignore 주석에 법적 Markdown 런타임 의존성 반영
Docker 재빌드 후 /healthz, /terms, /privacy 응답 확인 기준 추가
```

### 검증

```text
Docker Compose rebuild: PASS, gpt-manager-web-1 Up
curl http://127.0.0.1:5000/healthz: PASS, {"status":"ok"}
curl http://127.0.0.1:5000/terms: PASS, 200
curl http://127.0.0.1:5000/privacy: PASS, 200
```
