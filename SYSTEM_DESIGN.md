# System Design - 생성형 AI 계정 공동 사용 지원 시스템

## 1. 전체 구조

```text
Browser
  ↓ HTTPS
Nginx reverse proxy
  ↓ localhost:5000
Docker Compose web service
  ↓
Flask + Gunicorn
  ↓
SQLite ./instance/app.db
  ↓
Gemini API, Google OAuth
```

운영 배포:

```text
OCI Ubuntu
  ├─ Nginx HTTPS reverse proxy
  ├─ Docker Compose
  │   └─ Flask + Gunicorn container
  ├─ ./instance/app.db
  └─ .env 운영 설정
```

현재 운영 도메인:

```text
https://dev-gpt.memilmuk82.com
```

## 2. 기술 스택

```text
Python 3.12
Flask
SQLAlchemy
Flask-Login
Requests 기반 Google OAuth userinfo/token 호출
cryptography.Fernet
Jinja2
Tailwind CDN
pytest
Docker Compose
SQLite
uv
Gunicorn
Nginx
OCI Ubuntu
```

## 3. 설정값

주요 환경변수:

```env
APP_TITLE=ChatGPT Pro 5X 공동 사용 지원 시스템
ORGANIZATION_NAME=종로산업정보학교
SECRET_KEY=<strong-random-secret>
DATABASE_URL=sqlite:///instance/app.db
APP_ENCRYPTION_KEY=<fernet-key>
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://dev-gpt.memilmuk82.com/auth/google/callback
ALLOWED_GOOGLE_DOMAIN=senedu.kr
ADMIN_EMAILS=<comma-separated-admin-emails>
ASSISTANT_ADMIN_EMAILS=<comma-separated-assistant-admin-emails>
REVIEW_ADMIN_EMAIL=review.admin@senedu.kr
REVIEW_ADMIN_PASSWORD=<review-admin-password>
GEMINI_MODEL=gemini-3.5-flash
GEMINI_MAX_INPUT_CHARS=3000
GEMINI_MAX_OUTPUT_TOKENS=1200
MAX_DAILY_AI_CALLS_PER_USER=50
```

## 4. 데이터 모델

### User

```text
id: int PK
email: string unique nullable false
name: string
department: string
extension: string
password_hash: string nullable
role: string default 'user'  # user/admin/assistant_admin
google_sub: string nullable unique
auth_provider: string default 'local'
approval_status: string default 'approved'  # pending/approved/suspended
is_active: bool default true
is_auth_manager: bool default false
sort_order: int default 100
created_at: datetime
updated_at: datetime
```

권한 helper:

```text
is_approved
is_admin
is_assistant_admin
can_access_admin
```

### AiResource

```text
id: int PK
name: string
provider: string
description: text nullable
is_active: bool default true
is_auth_manager: bool default false
sort_order: int default 100
created_at: datetime
updated_at: datetime
```

주의:

```text
리소스 이름만 저장한다.
실제 공용 계정 ID/PW는 저장하지 않는다.
```

### Reservation

```text
id: int PK
user_id: FK User.id
resource_id: FK AiResource.id
start_at: datetime
end_at: datetime
work_type: string
purpose: string
description: text
safety_confirmed: bool
status: string  # reserved, cancelled, completed
created_at: datetime
updated_at: datetime
```

예약 충돌 기준:

```text
같은 resource_id에서 cancelled가 아닌 예약끼리 시간이 겹치면 생성 불가
조건: new_start < existing_end AND new_end > existing_start
```


### AppSetting

```text
key: string PK
value: text
label: string
help_text: string
sort_order: int
updated_at: datetime
```

용도:

```text
앱 제목, 학교/부서명, 인증 안내, 업무게시판 안내, 로그아웃 안내, AI 활용 권장 순서, 기본 사용 시간, 장시간 사용 기준을 관리자 화면에서 수정한다.
템플릿에서는 context_processor의 setting_value(key, default)로 조회한다.
```

### GuideItem

```text
id: int PK
code: string unique
category: string
title: string
body: text
sort_order: int
is_active: bool
created_at: datetime
updated_at: datetime
```

용도:

```text
사용 안내 화면에 표시되는 적합 업무, 부적합 업무, 개인정보/민감정보, 평가 보안, 학생부 안내 문구를 관리자가 수정한다.
HTML 문자열은 실행하지 않고 텍스트로 표시한다.
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

### UserApiKey

```text
id: int PK
user_id: FK User.id
provider: string default 'gemini'
encrypted_api_key: text
key_last4: string
created_at: datetime
updated_at: datetime
```

### PromptReview

```text
id: int PK
user_id: FK User.id
source_prompt: text
review_goal: string
assembled_prompt: text
review_result: text
model_name: string
created_at: datetime
updated_at: datetime
```

## 5. 권한 정책

```text
비로그인 사용자:
- index/login/register/google login/callback, /guide, /terms, /privacy 접근 가능

pending 사용자:
- /auth/pending, logout, /guide, /terms, /privacy 접근 가능

user:
- 홈/사용 안내 접근
- 본인 예약 생성/조회/취소/완료
- 오늘 예약 전체 현황 조회
- 본인 사용 로그 작성/조회
- 본인 Gemini API Key 설정
- 본인 프롬프트 점검 기록 조회

assistant_admin:
- user 권한
- /admin 접근
- /admin에서 설정 관리, 안내문구 관리, 사용자 관리, 등록 요청 관리, 통계 조회, 전체 테스트 실행
- /admin/users에서 사용자 승인/정지/수정

admin:
- assistant_admin과 동일한 운영 관리 접근
```

보조관리자는 `User.role == "assistant_admin"`으로 구분한다. 관리자는 `admin`, 보조관리자는 `assistant_admin`, 일반 사용자는 `user` role을 사용한다.

## 6. 주요 Route

### Main

```text
GET /              # 비로그인 시작 화면
GET /dashboard     # 승인 사용자 홈
GET /guide         # 사용 안내
GET /terms         # 이용약관
GET /privacy       # 개인정보처리방침
GET /healthz
```

### Auth

```text
GET  /auth/login
POST /auth/login
GET  /auth/register
POST /auth/register
GET  /auth/google/login
GET  /auth/google/callback
GET  /auth/pending
POST /auth/logout
```

### Reservations

```text
GET  /reservations              # 내 예약
GET  /reservations/today        # 날짜별 전체 예약 현황
GET  /reservations/new          # 사용 신청
GET  /reservations/conflicts    # 동시간대 예약 충돌 확인 JSON API
POST /reservations
POST /reservations/<id>/cancel
POST /reservations/<id>/complete
```


### Admin

```text
GET  /admin                         # 관리자 허브 및 섹션 화면
GET  /admin/users                   # 사용자 관리 섹션 호환 URL
POST /admin/settings                # AppSetting 저장
POST /admin/guides                  # GuideItem 저장
POST /admin/users                   # 사용자 추가
POST /admin/users/bulk              # CSV 사용자 일괄 등록
POST /admin/users/<id>/update       # 사용자 정보 수정
POST /admin/users/<id>/approve      # 등록 요청 승인
POST /admin/users/<id>/suspend      # 사용자 비활성/등록 요청 반려
POST /admin/users/<id>/activate     # 사용자 활성화
POST /admin/tests/run               # pytest 전체 테스트 실행
```

### Logs

```text
GET  /logs
GET  /logs/new
POST /logs
GET  /logs/<id>
```

### Prompt Reviews

```text
GET  /prompts
GET  /prompts/new
POST /prompts
GET  /prompts/<id>
```

### Settings

```text
GET  /settings/api-key
POST /settings/api-key
POST /settings/api-key/test
POST /settings/api-key/delete
```

### Admin

```text
GET  /admin
GET  /admin/users
POST /admin/users/<id>/approve
POST /admin/users/<id>/suspend
```

## 7. UI 구조

```text
base.html: 공통 헤더/네비게이션/flash 메시지/Footer 법적 고지
index.html: 비로그인 시작 화면
dashboard.html: 현재 사용중, 다음 예약, 인증번호 안내, 빠른 메뉴, 오늘 예약 요약
guide.html: 사용 안내
partials/_auth_info.html: 생성형 AI 계정 접속 및 인증번호 안내
legal/document.html: Markdown 기반 이용약관/개인정보처리방침 출력
reservations/today.html: 날짜별 전체 예약 현황
```

네비게이션:

```text
홈
사용 신청
오늘 예약
내 예약
사용 기록
프롬프트 점검
사용 안내
설정
관리자(admin/assistant_admin만)
```

## 8. Gemini 호출 구조

```text
prompts route
  ↓
prompt_review_service
  ↓
Gemini REST API
```

원칙:

```text
Gemini API Key는 사용자별 암호화 저장값을 복호화해 사용한다.
모델명은 GEMINI_MODEL 환경변수로 관리한다.
입력 길이와 출력 토큰 상한을 환경변수로 제한한다.
테스트에서는 Gemini 호출을 mock 처리한다.
```

## 9. 보안 설계

```text
Jinja autoescape 사용
사용자 입력 safe 처리 금지
Gemini API Key 평문 저장 금지
비밀번호 평문 저장 금지
SECRET_KEY와 APP_ENCRYPTION_KEY는 환경변수 사용
SESSION_COOKIE_HTTPONLY=True
운영 HTTPS에서는 SESSION_COOKIE_SECURE=true 권장
상태 변경 요청은 POST로 제한
공용 생성형 AI 계정 ID/PW 저장 금지
학생 개인정보 입력 금지
법적 문서 Markdown raw HTML/script escape 처리
/terms, /privacy는 URL 공유 가능하되 인증 정보와 무관한 공개 문서만 제공
```

CSRF 보호는 제출 이후 보완 과제로 남아 있다.

## 10. 테스트

```text
uv run pytest: 55 passed
npm run test:e2e: 1 passed
```

주요 테스트 범위:

```text
인증/승인/정지 흐름
Google OAuth mock
관리자/보조관리자 접근
예약 충돌/취소/완료
오늘 예약 날짜 필터
사용 로그 소유권
API Key 암호화
프롬프트 점검 mock
법적 고지 Footer와 /terms, /privacy
Markdown raw HTML/script 이스케이프
healthz/config/model
```

## 11. Docker/배포

현재 `compose.yaml`:

```yaml
services:
  web:
    build: .
    ports:
      - "127.0.0.1:5000:5000"
    env_file:
      - .env
    volumes:
      - ./instance:/app/instance
```

운영 재배포:

```bash
git pull
docker compose down
docker compose up -d --build
curl http://127.0.0.1:5000/healthz
curl https://dev-gpt.memilmuk82.com/healthz
curl https://dev-gpt.memilmuk82.com/terms
curl https://dev-gpt.memilmuk82.com/privacy
```

## 12. 향후 확장

```text
CSRF 보호 도입
관리자 리소스 관리 UI
사용 통계 차트
월간 보고서 생성
SQLite 백업 자동화
Docker PostgreSQL 전환
권한 세분화
```


## 9. SQLite 호환 보정 및 기본 데이터

```text
기존 SQLite DB에 신규 컬럼이 없으면 앱 시작 시 ALTER TABLE로 누락 컬럼을 추가한다.
TESTING 설정에서는 자동 시드를 건너뛰어 테스트 격리를 유지한다.
운영/개발 DB에는 기본 AppSetting, GuideItem, GPT Pro 리소스, 리뷰용 관리자 계정을 자동 생성한다.
```

기본 데이터 출처:

```text
app/defaults.py
```
