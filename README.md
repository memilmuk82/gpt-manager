# GPT Share Manager vNext

공용 AI 계정 예약·사용 기록 관리와 Gemini 기반 프롬프트 점검을 지원하는 Flask 웹앱입니다.

## 1. 현재 상태

```text
현재 Phase: Phase 2 완료
구현 범위: Flask 기본 골격, SQLite 설정, 로컬 회원가입/로그인/로그아웃, 보호된 대시보드, pytest
제외 범위: Google OAuth, 예약 CRUD, Gemini API 호출, API Key 암호화
```

## 2. 핵심 기능 목표

```text
로컬 로그인
Google OAuth 로그인
공용 AI 리소스 예약
사용 로그 작성
Gemini API Key 사용자별 설정
프롬프트 점검/개선
관리자 대시보드
Docker Compose 실행
```

## 3. 프로젝트 성격

이 앱은 GPT 계정 로그인을 통제하거나 실제 ChatGPT 사용량을 자동 조회하지 않습니다.

대신 다음을 관리합니다.

```text
누가
언제
어떤 AI 리소스를
어떤 목적으로 예약했고
어떤 프롬프트와 결과를 사용했는가
```

Gemini API는 사용자가 작성한 프롬프트를 점검하고 개선하는 데 사용합니다.

## 4. 실행 방법

### 환경변수 준비

```bash
cp .env.example .env
```

운영 환경에서는 `.env`의 `SECRET_KEY`, `APP_ENCRYPTION_KEY`, OAuth 값을 반드시 변경합니다.

### 로컬 실행

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

### Docker 실행

```bash
docker compose up --build
```

확인:

```bash
curl http://localhost:5000/healthz
```

5000 포트가 이미 사용 중이면 기존 Flask 프로세스를 종료하거나 임시 검증용으로 다른 호스트 포트를 사용합니다.

## 5. 로컬 인증 확인

브라우저에서 다음 흐름을 확인합니다.

```text
/auth/register 에서 회원가입
/dashboard 자동 이동
Logout 클릭
/auth/login 에서 로그인
/dashboard 접근 확인
```

비밀번호는 DB에 평문으로 저장하지 않고 Werkzeug password hash로 저장합니다.

## 6. 테스트

```bash
uv run pytest
```

현재 Phase 2 테스트:

```text
tests/test_app.py
- app factory creates Flask app
- index page returns 200

tests/test_health.py
- /healthz returns 200
- response JSON contains status ok

tests/test_auth.py
- register creates user
- duplicate email is rejected
- login success allows dashboard
- login failure uses generic message
- dashboard requires login
- logout blocks dashboard

tests/test_user_model.py
- password hash roundtrip
- plaintext password is not stored

tests/test_config.py
- relative SQLite path is rooted at ./data
- in-memory SQLite URL is preserved
```

## 7. 제출 시연 흐름

```text
1. 로그인
2. AI 리소스 예약
3. 사용 로그 작성
4. Gemini API Key 등록
5. 프롬프트 점검 실행
6. 개선된 프롬프트 확인
7. 관리자 대시보드 확인
```

## 8. 보안 원칙

```text
GPT 계정 ID/PW 저장 금지
Gemini API Key 평문 저장 금지
비밀번호 평문 저장 금지
학생 개인정보 입력 금지
자유 채팅형 챗봇 미제공
```
