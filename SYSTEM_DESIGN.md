# System Design - GPT Share Manager vNext

## 1. 전체 구조

```text
Browser
  ↓
Flask App
  ↓
SQLite ./instance/app.db
  ↓
Gemini API
```

배포 구조:

```text
OCI Ubuntu
  ├─ Docker Compose
  │   └─ Flask + Gunicorn Container
  ├─ ./instance/app.db
  └─ optional reverse proxy later
```

MVP에서는 단일 Flask 컨테이너와 SQLite 파일을 사용한다. Caddy/Nginx/HTTPS는 제출 전 시간이 허용될 때 추가한다. Google OAuth 운영 테스트에는 HTTPS가 필요할 수 있으므로, 운영 도메인 설정은 별도 배포 문서에서 관리한다.

## 2. 기술 스택

```text
Python 3.12 이상 권장
Flask
SQLAlchemy
Flask-Login
Authlib
cryptography
google-generativeai 또는 google-genai 계열 SDK 중 Codex가 확인 가능한 안정 패키지
Jinja2
Vanilla JS
Tailwind CDN
pytest
Docker Compose
SQLite
uv
```

주의:

```text
Gemini SDK 패키지명과 모델명은 실제 연수/개발 환경에서 확인한 뒤 .env로 지정한다.
모델명은 코드에 하드코딩하지 않는다.
```

## 3. 권장 저장소 구조

```text
gpt-share-manager-vnext/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extensions.py
│  ├─ models.py
│  ├─ auth/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ main/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ reservations/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ ai/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ admin/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ services/
│  │  ├─ crypto_service.py
│  │  ├─ gemini_service.py
│  │  ├─ prompt_review_service.py
│  │  └─ report_service.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ index.html
│  │  ├─ auth/
│  │  ├─ reservations/
│  │  ├─ ai/
│  │  └─ admin/
│  └─ static/
├─ tests/
├─ data/
│  └─ .gitkeep
├─ docs/
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
├─ uv.lock
├─ .env.example
├─ .gitignore
├─ README.md
├─ PROJECT_INSTRUCTIONS.md
├─ PRD.md
├─ SYSTEM_DESIGN.md
├─ DEVELOPMENT_PLAN.md
├─ TASK.md
└─ PROJECT_STATUS.md
```

MVP에서는 `models.py` 단일 파일로 시작한다. 모델이 커지면 테스트 후 `app/models/`로 분리한다.

## 4. 설정값

`.env.example` 예시:

```env
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///instance/app.db
APP_ENCRYPTION_KEY=generate-fernet-key
SESSION_COOKIE_SECURE=false

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
ALLOWED_GOOGLE_DOMAIN=

GEMINI_MODEL=gemini-3.1-light
GEMINI_MAX_INPUT_CHARS=3000
GEMINI_MAX_OUTPUT_TOKENS=1200
MAX_DAILY_AI_CALLS_PER_USER=50
```

운영에서는 다음 값을 반드시 변경한다.

```text
SECRET_KEY
APP_ENCRYPTION_KEY
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
SESSION_COOKIE_SECURE=true
```

## 5. 데이터 모델

### User

```text
id: int PK
email: string unique nullable false
name: string
password_hash: string nullable
role: string default 'user'  # admin/user
google_sub: string nullable unique
is_active: bool default true
created_at: datetime
updated_at: datetime
```

원칙:

```text
password_hash는 로컬 로그인 사용자만 사용한다.
google_sub는 Google OAuth 사용자 식별값이다.
최소 1명의 admin을 유지한다.
```

### UserApiKey

```text
id: int PK
user_id: FK User.id unique
encrypted_api_key: text nullable false
api_key_last4: string nullable
provider: string default 'gemini'
created_at: datetime
updated_at: datetime
```

원칙:

```text
평문 API Key 저장 금지
화면에는 last4만 표시
삭제 가능
```

### AiResource

```text
id: int PK
name: string
provider: string  # GPT, Gemini, Claude, etc.
description: text nullable
is_active: bool default true
created_at: datetime
updated_at: datetime
```

예시:

```text
GPT Pro 공용 계정 A
GPT Pro 공용 계정 B
Gemini 교육용 계정
```

주의:

```text
이 모델은 리소스 이름만 저장한다.
실제 계정 ID/PW는 저장하지 않는다.
```

### Reservation

```text
id: int PK
user_id: FK User.id
resource_id: FK AiResource.id
start_at: datetime
end_at: datetime
purpose: string
status: string  # reserved, cancelled, completed
created_at: datetime
updated_at: datetime
```

예약 충돌 기준:

```text
같은 resource_id에서 cancelled가 아닌 예약끼리 시간이 겹치면 생성 불가
조건: new_start < existing_end AND new_end > existing_start
```

### UsageLog

```text
id: int PK
user_id: FK User.id
reservation_id: FK Reservation.id nullable
resource_id: FK AiResource.id nullable
work_type: string
summary: text
prompt_text: text nullable
result_note: text nullable
created_at: datetime
updated_at: datetime
```

### PromptReview

```text
id: int PK
user_id: FK User.id
original_prompt: text
work_type: string
options_json: text
review_score: int nullable
review_result_json: text
improved_prompt: text
model_name: string
created_at: datetime
```

### AiCallLog

```text
id: int PK
user_id: FK User.id
feature: string  # prompt_review, ops_report
model_name: string
input_chars: int
output_chars: int nullable
status: string  # success, error
error_message: text nullable
created_at: datetime
```

실제 토큰 수가 SDK에서 제공되지 않으면 문자열 길이 기준으로 저장한다.

## 6. 권한 정책

```text
비로그인 사용자:
- index/login/register만 접근 가능

user:
- 본인 예약 생성/조회/취소
- 본인 사용 로그 작성/조회
- 본인 Gemini API Key 설정
- 본인 프롬프트 점검 기록 조회

admin:
- 전체 예약 조회
- 전체 사용 로그 조회
- AI 리소스 관리
- 사용자 목록 조회
- 운영 보고서 생성
```

MVP에서는 `admin`과 `user` 2단계만 구현한다.

## 7. 주요 Route 설계

### Auth

```text
GET  /auth/login
POST /auth/login
GET  /auth/register
POST /auth/register
GET  /auth/logout
GET  /auth/google/login
GET  /auth/google/callback
```

### Main

```text
GET /              # landing 또는 dashboard redirect
GET /dashboard
GET /healthz
```

### Settings

```text
GET  /settings/api-key
POST /settings/api-key
POST /settings/api-key/delete
POST /settings/api-key/test
```

### Reservations

```text
GET  /reservations
GET  /reservations/new
POST /reservations
POST /reservations/<id>/cancel
POST /reservations/<id>/complete
```

### Usage Logs

```text
GET  /logs
GET  /logs/new
POST /logs
GET  /logs/<id>
```

### Prompt Review

```text
GET  /ai/prompt-review
POST /ai/prompt-review
GET  /ai/prompt-reviews
GET  /ai/prompt-reviews/<id>
```

### Admin

```text
GET  /admin
GET  /admin/users
GET  /admin/reservations
GET  /admin/logs
GET  /admin/resources
POST /admin/resources
POST /admin/resources/<id>/toggle
GET  /admin/reports
POST /admin/reports/generate
```

Admin report는 시간이 부족하면 후순위로 둔다.

## 8. Gemini 호출 구조

앱의 다른 부분은 Gemini SDK를 직접 호출하지 않는다.

```text
route
  ↓
prompt_review_service
  ↓
gemini_service
  ↓
Gemini API
```

### gemini_service 책임

```text
사용자 API Key 복호화
모델명 로드
입력 길이 제한
API 호출
에러 처리
AiCallLog 저장
```

### prompt_review_service 책임

```text
사용자 입력 검증
점검용 시스템 프롬프트 조립
정해진 출력 형식 요청
Gemini 응답 파싱/정리
PromptReview 저장
```

## 9. 프롬프트 점검용 출력 형식

Gemini에는 가능하면 JSON 형식을 요청한다. 단, JSON 파싱 실패 시 Markdown 원문도 저장한다.

요청 출력 구조:

```json
{
  "score": 82,
  "strengths": ["목적이 명확함"],
  "missing_elements": ["출력 형식", "평가 기준"],
  "improved_prompt": "...",
  "rationale": ["출력 형식을 추가해 재사용성을 높임"],
  "safety_notes": ["학생 개인정보 입력 금지"]
}
```

## 10. 보안 설계

### API Key 암호화

```text
cryptography.Fernet 사용
APP_ENCRYPTION_KEY 환경변수에서 암호화 키 로드
DB에는 encrypted_api_key만 저장
api_key_last4는 표시용으로만 저장
```

### 비밀번호

```text
werkzeug.security.generate_password_hash
werkzeug.security.check_password_hash
```

### XSS 방지

```text
Jinja autoescape 사용
사용자 입력을 safe 처리하지 않음
Markdown 렌더링은 MVP에서 생략하거나 plain text로 표시
```

### CSRF

MVP에서는 Flask-WTF 도입 여부를 Codex가 판단해 제안한다. 시간이 부족하면 최소한 상태 변경 요청은 POST로 제한하고, 이후 개선 과제로 CSRF 보호를 문서화한다.

## 11. 테스트 설계

필수 테스트:

```text
/healthz 응답 테스트
User password hash 테스트
API Key 암호화/복호화 테스트
API Key가 평문으로 저장되지 않는지 테스트
예약 충돌 테스트
본인 데이터 접근 제한 테스트
Prompt review 프롬프트 조립 테스트
Gemini API 호출 mock 테스트
```

테스트 실행:

```bash
uv run pytest
```

## 12. Docker 설계

### docker-compose.yml

```text
services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./instance:/app/instance
```

MVP에서는 DB 컨테이너를 추가하지 않는다.

### Dockerfile 원칙

```text
python slim 이미지 사용
uv 설치
uv sync --locked 또는 동등한 재현 설치
gunicorn으로 실행
/app/instance 디렉터리 생성
```

## 13. 배포 설계

로컬:

```bash
docker compose up --build
```

OCI:

```bash
git pull
docker compose up -d --build
```

운영 주의:

```text
OCI 보안 규칙에서 80/443 또는 테스트 포트 개방
OAuth Redirect URI 운영 URL 등록
.env 운영값 분리
./instance/app.db 백업
```

## 14. 향후 확장

```text
SQLite → Docker PostgreSQL
admin/subadmin/user 권한 세분화
프롬프트 템플릿 저장소
공용 AI 계정별 정책 안내
사용 통계 차트
월간 보고서 PDF/Markdown 다운로드
Caddy HTTPS 자동화
```
