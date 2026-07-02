# 생성형 AI 계정 공동 사용 지원 시스템

Flask 기반의 공용 생성형 AI 계정 예약·사용 기록 관리 웹앱입니다. Gemini API는 자유 채팅이 아니라 사용자가 작성한 프롬프트를 점검하고 개선하는 정형 기능에만 사용합니다.

## 1. 현재 상태

```text
상태: Release Candidate 운영 검증 완료
최근 검증일: 2026-07-02
테스트: uv run pytest, 50 passed
운영 도메인: https://dev-gpt.memilmuk82.com
배포: OCI Ubuntu + Docker Compose + Gunicorn + Nginx + HTTPS
현재 커밋: 95f51ca ui: add today reservations and assistant admin
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
senedu.kr 계정 자동 승인
외부 로컬/Google 계정 관리자 승인 대기
관리자 및 보조관리자 사용자 승인/정지 관리
공용 생성형 AI 계정 예약 생성/조회/취소/완료
오늘 예약 전체 현황 조회
예약 충돌 검증
사용 로그 작성/조회
사용자별 Gemini API Key 암호화 저장/삭제/확인
Gemini 기반 프롬프트 점검 결과 저장/조회
관리자 대시보드 요약
사용 안내 화면
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
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
ADMIN_EMAILS
ASSISTANT_ADMIN_EMAILS
SESSION_COOKIE_SECURE
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

Google Cloud Console의 Authorized redirect URI와 `.env`의 `GOOGLE_REDIRECT_URI`는 반드시 같은 값이어야 합니다.

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

현재 `compose.yaml`은 호스트 `127.0.0.1:5000`에 바인딩합니다. 운영 공개 접속은 Nginx가 `https://dev-gpt.memilmuk82.com`에서 이 컨테이너로 프록시합니다.

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
2. senedu.kr 계정이면 자동 승인, 외부 계정이면 승인 대기
3. /dashboard 에서 현재 사용중, 다음 예약, 오늘 예약 요약 확인
4. /reservations/new 에서 예약 생성
5. /reservations/today 에서 날짜별 전체 예약 확인
6. /logs 에서 사용 로그 작성
7. /settings/api-key 에서 Gemini API Key 등록
8. /prompts 에서 프롬프트 점검 실행
9. /guide 에서 사용 안내 확인
```

### 관리자/보조관리자 흐름

```text
1. ADMIN_EMAILS 또는 ASSISTANT_ADMIN_EMAILS에 포함된 이메일로 회원가입 또는 Google 로그인
2. /admin 에서 전체 요약 확인
3. /admin/users 에서 pending 사용자 승인
4. 필요 시 사용자 정지
```

## 9. 제출 시연 흐름

```text
1. 앱 목적 설명: 공용 생성형 AI 계정 직접 제어가 아닌 예약·기록·프롬프트 개선 도구
2. 로컬 로그인 또는 Google OAuth 로그인
3. senedu.kr 자동 승인/외부 계정 승인 대기 정책 설명
4. 홈 화면에서 현재 사용중/다음 예약/오늘 예약 요약 확인
5. 사용 신청으로 예약 생성 및 충돌 검증 설명
6. 오늘 예약 화면에서 전체 예약 현황 확인
7. 사용 로그 작성
8. Gemini API Key 등록 화면에서 암호화 저장 원칙 설명
9. 프롬프트 점검 실행 및 결과 저장 확인
10. 관리자/보조관리자 대시보드와 사용자 승인 화면 확인
11. Docker Compose/OCI/Nginx 배포 구조 설명
12. 보안 제외 범위 설명: 계정 ID/PW 저장 안 함, 학생 개인정보 입력 안 함
```

## 10. 테스트

```bash
uv run pytest
```

현재 테스트 결과:

```text
50 passed
```

현재 테스트 범위:

```text
app factory와 /healthz
Config와 SQLite 경로 정규화
User 모델 비밀번호 해시
로컬 회원가입/로그인/로그아웃
승인 대기/정지 계정 접근 제어
Google OAuth 기본 흐름과 userinfo mock
관리자 및 보조관리자 권한
예약 생성/취소/완료 및 충돌 검증
오늘 예약 날짜별 조회 및 취소 예약 제외
사용 로그 생성/조회 접근 제한
Gemini API Key 암호화 저장/교체/삭제/복호화 확인
프롬프트 점검 Gemini 호출 mock 및 저장/조회
관리자 대시보드와 사용자 승인/정지
```

## 11. 보안 원칙

```text
생성형 AI 계정 ID/PW 저장 금지
실제 사용량 자동 조회 금지
Gemini API Key 평문 저장 금지
Gemini API Key 프론트엔드 노출 금지
사용자 비밀번호 평문 저장 금지
학생 개인정보 입력 금지
자유 채팅형 챗봇 미제공
.env Git 커밋 금지
운영 SECRET_KEY와 APP_ENCRYPTION_KEY 고정 설정
HTML 문자열 safe 렌더링 금지
```

## 12. 주요 문서

```text
PROJECT_STATUS.md: 현재 상태와 완료 항목
docs/development/DEVELOPMENT_LOG.md: 단계별 개발 로그
docs/development/TEST_REPORT.md: 테스트 결과 기록
docs/deployment/OCI_DEV_SERVER_SETUP.md: OCI 서버 준비와 Docker Compose/Nginx 실행
docs/deployment/GOOGLE_OAUTH_REDIRECT_URI.md: Google OAuth Redirect URI 설정 절차
SYSTEM_DESIGN.md: 현재 시스템 구조와 데이터/라우트 설계
```
