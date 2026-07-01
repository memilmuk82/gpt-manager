# Development Log

## 2026-06-30 - Phase 0

### 결정

```text
새 교육자료 생성 앱은 만들지 않음
기존 GPT 공유앱을 Flask 기반으로 재설계
Gemini API는 프롬프트 점검/개선에 사용
SQLite + Docker Compose + OCI 단일 인스턴스 사용
2026-07-02 RC1, 2026-07-03 기능 동결 원칙 채택
```

### 이유

```text
수업안/평가계획 생성기는 NotebookLM/ChatGPT로 대체 가능성이 높음
사용자가 실제로 계속 쓸 가능성이 낮음
기존 GPT 공유앱은 운영 시스템으로 앱의 존재 이유가 명확함
프롬프트 점검기는 Gemini API 활용 조건을 자연스럽게 충족함
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
Gemini API 호출 제외
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
Gemini API 구현 제외
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
Phase 4 Gemini API Key 암호화 설정 구현
UserApiKey 모델, Fernet 암호화, 등록/삭제/마스킹 테스트 추가
```

## 2026-07-01 - Phase 4

### 구현

```text
cryptography 의존성 사용
UserApiKey 모델 추가
Fernet 기반 암호화/복호화 service 추가
/settings/api-key 화면 추가
Gemini API Key 등록/교체/삭제 구현
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
Phase 5 프롬프트 점검기 구현
PromptReview 모델, Gemini 호출 service, mock 테스트 작성
```


## 2026-07-01 - Phase 5

### 추론 수준

```text
높음
```

### 구현

```text
PromptReview 모델 추가
프롬프트 점검 목록/입력/상세 화면 추가
점검 프롬프트 조립 service 추가
Gemini REST 호출 service 추가
저장된 Gemini API Key 복호화 후 호출에 사용
Gemini 호출부 mock 테스트 추가
입력 길이 제한 및 사용자별 접근 제한 구현
GEMINI_MODEL 기본값을 gemini-3.5-flash로 갱신
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
