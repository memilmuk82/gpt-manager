# Repository Structure

## 현재 구조

```text
gpt-manager/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extensions.py
│  ├─ models/
│  │  └─ __init__.py
│  ├─ auth/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ reservations/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ logs/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ prompts/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ settings/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ admin/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ services/
│  │  ├─ access_policy.py
│  │  ├─ encryption_service.py
│  │  ├─ oauth_service.py
│  │  ├─ prompt_review_service.py
│  │  └─ reservation_service.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ index.html
│  │  ├─ dashboard.html
│  │  ├─ guide.html
│  │  ├─ partials/
│  │  │  └─ _auth_info.html
│  │  ├─ auth/
│  │  ├─ reservations/
│  │  │  ├─ index.html
│  │  │  ├─ new.html
│  │  │  └─ today.html
│  │  ├─ logs/
│  │  ├─ prompts/
│  │  ├─ settings/
│  │  └─ admin/
│  └─ static/
├─ tests/
├─ docs/
├─ instance/
├─ Dockerfile
├─ compose.yaml
├─ pyproject.toml
├─ uv.lock
├─ .env.example
├─ README.md
├─ PROJECT_STATUS.md
├─ SYSTEM_DESIGN.md
├─ TASK.md
└─ PROJECT_INSTRUCTIONS.md
```

## 구조 원칙

```text
route는 요청/응답과 인증 흐름을 담당한다.
예약 충돌, OAuth, 암호화, 프롬프트 점검 조립은 services에 둔다.
DB 모델은 app/models/__init__.py에 모아 둔다.
Jinja 템플릿은 기능별 하위 디렉터리로 분리한다.
공통 안내 UI는 templates/partials에 둔다.
SQLite DB는 ./instance/app.db에 저장하고 Docker Compose에서 ./instance를 /app/instance로 마운트한다.
```

## 과도한 구조화 금지

```text
Repository 패턴 선행 도입 금지
Service 계층 과잉 분리 금지
DTO/Form/Schema 계층 선행 도입 금지
테스트 없는 파일 이동 금지
```
