# 생성형 AI 계정 공동 사용 지원 시스템

## 리뷰용 테스트 계정

리뷰용 관리자 계정은 기본으로 자동 생성되지 않습니다. 제출 시연이나 외부 리뷰에 임시 관리자 계정이 필요할 때만 `.env`에 아래 값을 명시합니다.

```text
ENABLE_REVIEW_ADMIN=true
REVIEW_ADMIN_EMAIL=review.admin@senedu.kr
REVIEW_ADMIN_PASSWORD=<강한 임시 비밀번호>
```

이 계정은 Google OAuth 계정이 아닙니다. 로그인 화면의 Google 로그인 버튼이 아니라 이메일과 비밀번호 입력 폼에 위 이메일과 임시 비밀번호를 직접 입력해야 로그인됩니다. 운영 전에는 `ENABLE_REVIEW_ADMIN=false`로 두거나 관리자 화면에서 해당 계정을 비활성화하세요.

## 개발 배경과 기술 선택 이유

이 프로젝트는 종로산업정보학교 AI컴퓨터과의 1년 학과 커리큘럼을 반영해, 학생들이 2학기 개인 프로젝트에서 유사한 구조의 서비스를 만들 수 있도록 Flask - SQLite - OCI 흐름을 우선해 설계했습니다. 현재 학생들은 3월부터 Python, Flask, SQLite를 학습했고, 현재 단계에서는 Flask와 SQLite로 CRUD 웹사이트를 직접 만들고 있습니다. 기본 개발 환경은 WSL2 Ubuntu입니다.

2학기에는 SQLAlchemy를 이용해 백엔드 데이터 모델을 다루고, 칸반보드로 개인 프로젝트 일정과 기능 구현 과정을 관리할 예정입니다. 프론트엔드는 생성형 AI의 도움을 받아 화면을 빠르게 개선하되, 백엔드 기본 뼈대와 핵심 CRUD 흐름은 학생들이 직접 만들도록 수업을 구성합니다. 이후 가능하면 OCI에 개인 인스턴스를 구축해 배포하고, 어려운 경우 학교 서버에 올려 시연회를 진행할 예정입니다.

따라서 이 앱은 복잡한 클라우드 관리형 DB나 과도한 프레임워크보다, 학생들이 수업에서 배운 Flask, SQLite, WSL2 Ubuntu 기반 개발 흐름에서 출발해 SQLAlchemy와 서버 배포까지 자연스럽게 확장할 수 있는 구조를 선택했습니다.

Flask 기반의 공용 생성형 AI 계정 예약·사용 기록 관리 웹앱입니다. Gemini API는 자유 채팅이 아니라 사용자가 작성한 프롬프트를 점검하고 개선하는 정형 기능에만 사용합니다.

## 1. 현재 상태

```text
상태: 운영 보안/예약-로그 연동 보완 및 문서화 완료
최근 검증일: 2026-07-03
테스트: uv run pytest, 71 passed
E2E: npm run test:e2e, 1 passed
운영 도메인: https://dev-gpt.memilmuk82.com
배포: OCI Ubuntu + Docker Compose + Gunicorn + Nginx + HTTPS
최근 기능 브랜치: codex/admin-reservation-ui-docs
```

## 2. 프로젝트 성격

이 앱은 생성형 AI 계정 로그인을 직접 통제하거나 실제 ChatGPT 사용량을 자동 조회하지 않습니다. 공용 계정 ID/PW도 저장하지 않습니다.

대신 다음을 관리합니다.

```text
누가
언제
어떤 생성형 AI 계정을
어떤 목적으로 예약했고
어떤 프롬프트와 결과를 사용했는가
```

## 3. 주요 기능

```text
로컬 회원가입/로그인/로그아웃
Google OAuth 로그인
Google OAuth 실제 이메일 도메인 제한 검증
관리자/보조관리자는 ADMIN_EMAILS, ASSISTANT_ADMIN_EMAILS 기준으로만 부여
도메인 제한 없는 계정 자동 승인
로컬 신규 계정 자동 승인
CSRF 토큰 기반 POST 요청 보호
관리자 및 보조관리자 사용자 승인/정지/수정/CSV 일괄 등록 관리
인증번호 담당자는 최대 2명까지 지정됩니다.
공용 생성형 AI 계정 예약 생성/조회/취소/완료
오늘 예약 전체 현황 조회
예약 충돌 검증 및 충돌 확인 버튼
완료 예약의 사용 로그 작성 유도 및 예약 자동 선택
사용 로그 작성/조회
사용자별 Gemini API Key 암호화 저장/삭제/확인
상단 사용자 badge에서 개인 Gemini API Key 설정으로 이동할 수 있습니다.
Gemini 기반 프롬프트 점검 결과 저장/조회
사용자별 일일 Gemini 프롬프트 점검 호출 제한
프롬프트 점검 화면은 상단 메뉴와 홈 빠른 이동에서 접근할 수 있습니다.
관리자 설정 관리, 안내문구 관리, AI 리소스/작업유형 관리, 사용자 통계, 전체 테스트 실행
관리자가 수정할 수 있는 사용 안내 화면
GPT 접속 안내 제목, 사용 신청 안내 문구, 사용 안내 소개 문구를 Settings로 관리
공통 Footer Copyright/정보관리책임자 표시
/terms 이용약관 페이지
/privacy 개인정보처리방침 페이지
Markdown 기반 법적 문서 관리
Docker Compose 배포
```

## 4. 환경변수 준비

```bash
cp .env.example .env
```

운영 또는 제출 시연 환경에서는 최소한 아래 값을 변경합니다.

```text
SECRET_KEY
APP_ENCRYPTION_KEY
ENABLE_REVIEW_ADMIN
REVIEW_ADMIN_EMAIL
REVIEW_ADMIN_PASSWORD
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
ADMIN_EMAILS
ASSISTANT_ADMIN_EMAILS
SESSION_COOKIE_SECURE
WTF_CSRF_ENABLED
MAX_DAILY_AI_CALLS_PER_USER
```

`APP_ENCRYPTION_KEY`는 Fernet 키 형식이어야 합니다.

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

로컬 개발 기본 Redirect URI:

```text
http://localhost:5000/auth/google/callback
```

현재 운영 Redirect URI:

```text
https://dev-gpt.memilmuk82.com/auth/google/callback
```

Google Cloud Console의 Authorized redirect URI와 `.env`의 `GOOGLE_REDIRECT_URI`는 반드시 같은 값이어야 합니다. `ALLOWED_GOOGLE_DOMAIN`을 설정하면 OAuth 요청의 `hd` 힌트뿐 아니라 콜백에서 반환된 실제 이메일 도메인도 같은 값인지 검증합니다.

## 5. 로컬 실행

```bash
uv sync
uv run flask --app run run --debug
```

확인:

```bash
curl http://localhost:5000/healthz
```

예상 응답:

```json
{"status":"ok"}
```

브라우저 접속:

```text
http://localhost:5000
```

## 6. Docker Compose 실행

```bash
docker compose up -d --build
```

확인:

```bash
curl http://127.0.0.1:5000/healthz
```

중지:

```bash
docker compose down
```

현재 `compose.yaml`은 호스트 `127.0.0.1:5000`에 바인딩합니다. 운영 공개 접속은 Nginx가 `https://dev-gpt.memilmuk82.com`에서 이 컨테이너로 프록시합니다. Docker 이미지는 관리자 전체 테스트 실행을 위해 dev dependency group도 설치합니다.

SQLite 운영 DB 백업:

```bash
bash scripts/backup_sqlite.sh instance/app.db backups
```

SQLite 운영 DB 복원 전에는 컨테이너를 중지한 뒤 실행합니다. 기존 DB는 `.before-restore-YYYYmmdd-HHMMSS` 파일로 한 번 더 보관됩니다.

```bash
docker compose down
bash scripts/restore_sqlite.sh backups/app-YYYYmmdd-HHMMSS.db instance/app.db
docker compose up -d --build
```

## 7. 시연 데이터 준비

fresh DB에서는 예약에 사용할 생성형 AI 계정 리소스가 자동 생성되지 않습니다. 예약 시연 전에 최소 1개의 리소스를 준비합니다.

로컬 실행 환경:

```bash
uv run python -c "from app import create_app; from app.extensions import db; from app.models import AiResource; app=create_app(); ctx=app.app_context(); ctx.push(); AiResource.query.filter_by(name='학교 공용 생성형 AI 계정 A').first() or db.session.add(AiResource(name='학교 공용 생성형 AI 계정 A', provider='OpenAI', description='Shared AI resource')); db.session.commit(); ctx.pop()"
```

Docker Compose 실행 환경:

```bash
docker compose exec web python -c "from app import create_app; from app.extensions import db; from app.models import AiResource; app=create_app(); ctx=app.app_context(); ctx.push(); AiResource.query.filter_by(name='학교 공용 생성형 AI 계정 A').first() or db.session.add(AiResource(name='학교 공용 생성형 AI 계정 A', provider='OpenAI', description='Shared AI resource')); db.session.commit(); ctx.pop()"
```

생성 후 `/reservations/new`에서 리소스가 보이면 예약 생성 시연을 진행할 수 있습니다.

## 8. 기본 사용 흐름

### 사용자 흐름

```text
1. /auth/register 에서 회원가입 또는 /auth/login 에서 로그인
2. 이메일 도메인과 관계없이 신규 계정은 자동 승인
3. /dashboard 에서 현재 사용중, 다음 예약, 오늘 예약 요약 확인
4. /reservations/new 에서 예약 생성
5. /reservations/today 에서 날짜별 전체 예약 확인
6. 예약 완료 후 /logs/new?reservation_id=... 또는 /logs 에서 사용 로그 작성
7. /settings/api-key 에서 Gemini API Key 등록
8. /prompts 에서 프롬프트 점검 실행
9. /guide 에서 사용 안내 확인
10. Footer에서 이용약관과 개인정보처리방침 확인
```

### 관리자/보조관리자 흐름

```text
1. Google 로그인 계정은 즉시 승인되지만 관리자 권한은 ADMIN_EMAILS 또는 ASSISTANT_ADMIN_EMAILS 설정에 따라 부여
2. 로컬 계정도 ADMIN_EMAILS 또는 ASSISTANT_ADMIN_EMAILS 설정에 따라 관리자 또는 보조관리자 권한 부여
3. /admin 에서 전체 요약 확인
4. /admin 에서 설정 관리, 안내문구 관리, AI 리소스/작업유형 관리, 사용자 관리, 등록 요청 관리, 통계 조회 실행
5. /admin/users 에서 사용자 수정, 활성/비활성, 권한, 인증번호 담당자 여부 관리
6. 필요 시 CSV 일괄 등록 또는 전체 테스트 실행
```

## 9. 제출 시연 흐름

```text
1. 앱 목적 설명: 공용 생성형 AI 계정 직접 제어가 아닌 예약·기록·프롬프트 개선 도구
2. 로컬 로그인 또는 Google OAuth 로그인
3. 도메인 제한 해제 및 신규 계정 자동 승인 정책 설명
4. 홈 화면에서 현재 사용중/다음 예약/오늘 예약 요약 확인
5. 사용 신청으로 예약 생성 및 충돌 검증 설명
6. 오늘 예약 화면에서 전체 예약 현황 확인
7. 사용 로그 작성
8. Gemini API Key 등록 화면에서 암호화 저장 원칙 설명
9. 프롬프트 점검 실행 및 결과 저장 확인
10. Footer에서 /terms, /privacy 법적 고지 페이지 확인
11. 관리자/보조관리자 대시보드와 사용자 승인 화면 확인
12. Docker Compose/OCI/Nginx 배포 구조 설명
13. 보안 제외 범위 설명: 계정 ID/PW 저장 안 함, 학생 개인정보 입력 안 함
```

## 10. 테스트

```bash
uv run pytest
```

현재 테스트 결과:

```text
71 passed
```

현재 테스트 범위:

```text
app factory와 /healthz
Config와 SQLite 경로 정규화
User 모델 비밀번호 해시
로컬 회원가입/로그인/로그아웃
승인 대기/정지 계정 접근 제어
Google OAuth 기본 흐름, userinfo mock, 도메인 제한 및 권한 승격 방지
CSRF 토큰 검증
관리자 및 보조관리자 권한
예약 생성/취소/완료 및 충돌 검증
오늘 예약 날짜별 조회 및 취소 예약 제외
사용 로그 생성/조회 접근 제한
Gemini API Key 암호화 저장/교체/삭제/복호화 확인
프롬프트 점검 Gemini 호출 mock, 일일 호출 제한 및 저장/조회
관리자 대시보드, AI 리소스/작업유형 관리, 사용자 승인/정지
Footer 법적 고지 링크
/terms, /privacy Markdown 렌더링
Markdown raw HTML/script 이스케이프
Playwright 핵심 사용자 흐름
```

## 11. 보안 원칙

```text
생성형 AI 계정 ID/PW 저장 금지
실제 사용량 자동 조회 금지
Gemini API Key 평문 저장 금지
Gemini API Key 프론트엔드 노출 금지
사용자 비밀번호 평문 저장 금지
사용자 비밀번호는 현재 Werkzeug 기본 `scrypt:32768:8:1` salted one-way hash로 저장되며 복호화 대상이 아님
학생 개인정보 입력 금지
자유 채팅형 챗봇 미제공
.env Git 커밋 금지
운영 SECRET_KEY와 APP_ENCRYPTION_KEY 고정 설정
법적 문서 Markdown raw HTML escape 처리
임의 HTML 문자열 safe 렌더링 금지
```

## 12. 주요 문서

```text
PROJECT_STATUS.md: 현재 상태와 완료 항목
docs/development/DEVELOPMENT_LOG.md: 단계별 개발 로그
docs/development/TEST_REPORT.md: 테스트 결과 기록
docs/deployment/OCI_DEV_SERVER_SETUP.md: OCI 서버 준비와 Docker Compose/Nginx 실행
docs/deployment/GOOGLE_OAUTH_REDIRECT_URI.md: Google OAuth Redirect URI 설정 절차
docs/legal/TERMS.md: 이용약관 원문
docs/legal/PRIVACY_POLICY.md: 개인정보처리방침 원문
SYSTEM_DESIGN.md: 현재 시스템 구조와 데이터/라우트 설계
```
