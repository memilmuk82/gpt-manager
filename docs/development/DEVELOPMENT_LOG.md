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

