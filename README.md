# GPT Share Manager vNext

공용 AI 계정 예약·사용 기록 관리와 Gemini 기반 프롬프트 점검을 지원하는 Flask 웹앱입니다.

## 1. 현재 상태

```text
현재 Phase: Phase 7 진행 중
구현 범위: 로컬 로그인, Google OAuth 기본 흐름, 계정 승인제, 예약/사용 로그, Gemini API Key 암호화 저장, 프롬프트 점검기, 관리자 대시보드, Docker Compose
제출 준비: README, .env.example, OAuth Redirect URI 안내, OCI 배포 절차, 최종 테스트 정리
```

## 2. 프로젝트 성격

이 앱은 GPT 계정 로그인을 통제하거나 실제 ChatGPT 사용량을 자동 조회하지 않습니다. GPT 계정 ID/PW도 저장하지 않습니다.

대신 다음을 관리합니다.

```text
누가
언제
어떤 AI 리소스를
어떤 목적으로 예약했고
어떤 프롬프트와 결과를 사용했는가
```

Gemini API는 자유 채팅이 아니라 사용자가 작성한 프롬프트를 점검하고 개선하는 정형 도구에만 사용합니다.

## 3. 주요 기능

```text
로컬 회원가입/로그인/로그아웃
Google OAuth 로그인 기본 흐름
senedu.kr 계정 자동 승인
외부 로컬/Google 계정 관리자 승인 대기
관리자 사용자 승인/정지 관리
공용 AI 리소스 예약 생성/조회/취소/완료
예약 충돌 검증
사용 로그 작성/조회
사용자별 Gemini API Key 암호화 저장/삭제/확인
Gemini 기반 프롬프트 점검 결과 저장/조회
관리자 대시보드 요약
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
SESSION_COOKIE_SECURE
```

`APP_ENCRYPTION_KEY`는 Fernet 키 형식이어야 합니다.

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

로컬 개발 기본 Redirect URI는 다음과 같습니다.

```text
http://localhost:5000/auth/google/callback
```

OCI/운영 환경에서는 실제 접속 주소에 맞춰 Google Cloud Console의 승인된 리디렉션 URI와 `.env`의 `GOOGLE_REDIRECT_URI`를 같은 값으로 설정합니다. 자세한 절차는 `docs/deployment/GOOGLE_OAUTH_REDIRECT_URI.md`를 참고합니다.

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
docker compose up --build
```

백그라운드 실행:

```bash
docker compose up -d --build
```

확인:

```bash
curl http://localhost:5000/healthz
```

중지:

```bash
docker compose down
```

5000 포트가 이미 사용 중이면 기존 Flask/Gunicorn 프로세스를 종료하거나 `compose.yaml`의 호스트 포트를 임시로 변경해 검증합니다.

## 7. 시연 데이터 준비

fresh DB에서는 예약에 사용할 AI 리소스가 자동 생성되지 않습니다. 예약 시연 전에 최소 1개의 리소스를 준비합니다.

로컬 실행 환경:

```bash
uv run python -c "from app import create_app; from app.extensions import db; from app.models import AiResource; app=create_app(); ctx=app.app_context(); ctx.push(); AiResource.query.filter_by(name='GPT Pro 공용 계정 A').first() or db.session.add(AiResource(name='GPT Pro 공용 계정 A', provider='OpenAI', description='Shared AI resource')); db.session.commit(); ctx.pop()"
```

Docker Compose 실행 환경:

```bash
docker compose exec web python -c "from app import create_app; from app.extensions import db; from app.models import AiResource; app=create_app(); ctx=app.app_context(); ctx.push(); AiResource.query.filter_by(name='GPT Pro 공용 계정 A').first() or db.session.add(AiResource(name='GPT Pro 공용 계정 A', provider='OpenAI', description='Shared AI resource')); db.session.commit(); ctx.pop()"
```

생성 후 `/reservations/new`에서 `GPT Pro 공용 계정 A`가 보이면 예약 생성 시연을 진행할 수 있습니다.

## 8. 기본 사용 흐름

### 사용자 흐름

```text
1. /auth/register 에서 회원가입
2. senedu.kr 계정이면 자동 승인, 외부 계정이면 승인 대기
3. /reservations 에서 AI 리소스 예약 생성
4. /logs 에서 사용 로그 작성
5. /settings/api-key 에서 Gemini API Key 등록
6. /prompts 에서 프롬프트 점검 실행
7. 저장된 점검 결과 확인
```

### 관리자 흐름

```text
1. ADMIN_EMAILS에 포함된 이메일로 회원가입 또는 Google 로그인
2. /admin 에서 전체 요약 확인
3. /admin/users 에서 pending 사용자 승인
4. 필요 시 사용자 정지
```

## 9. 제출 시연 흐름

```text
1. 앱 목적 설명: 공용 AI 계정 직접 제어가 아닌 예약·기록·프롬프트 개선 도구
2. 로컬 로그인 또는 Google OAuth 로그인
3. senedu.kr 자동 승인/외부 계정 승인 대기 정책 설명
4. AI 리소스 예약 생성 및 충돌 검증 설명
5. 사용 로그 작성
6. Gemini API Key 등록 화면에서 암호화 저장 원칙 설명
7. 프롬프트 점검 실행 및 결과 저장 확인
8. 관리자 대시보드와 사용자 승인 화면 확인
9. Docker Compose/OCI 단일 인스턴스 배포 구조 설명
10. 보안 제외 범위 설명: GPT 계정 ID/PW 저장 안 함, 학생 개인정보 입력 안 함
```

## 10. 테스트

```bash
uv run pytest
```

현재 테스트 범위:

```text
app factory와 /healthz
Config와 SQLite 경로 정규화
User 모델 비밀번호 해시
로컬 회원가입/로그인/로그아웃
승인 대기/정지 계정 접근 제어
Google OAuth 기본 흐름과 userinfo mock
예약 생성/취소/완료 및 충돌 검증
사용 로그 생성/조회 접근 제한
Gemini API Key 암호화 저장/교체/삭제/복호화 확인
프롬프트 점검 Gemini 호출 mock 및 저장/조회
관리자 대시보드와 사용자 승인/정지
```

## 11. 보안 원칙

```text
GPT 계정 ID/PW 저장 금지
GPT 실제 사용량 자동 조회 금지
Gemini API Key 평문 저장 금지
Gemini API Key 프론트엔드 노출 금지
사용자 비밀번호 평문 저장 금지
학생 개인정보 입력 금지
자유 채팅형 챗봇 미제공
.env Git 커밋 금지
운영 SECRET_KEY와 APP_ENCRYPTION_KEY 고정 설정
```

## 12. 문서

```text
PROJECT_STATUS.md: 현재 phase와 완료 항목
docs/development/DEVELOPMENT_LOG.md: phase별 개발 로그
docs/development/TEST_REPORT.md: 테스트 결과 기록
docs/deployment/OCI_DEV_SERVER_SETUP.md: OCI 서버 준비와 Docker Compose 실행
docs/deployment/GOOGLE_OAUTH_REDIRECT_URI.md: Google OAuth Redirect URI 설정 절차
```
