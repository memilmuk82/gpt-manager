# Repository Structure

## 관련 문서

[README](../../README.md) · [교육과정](../EDUCATION.md) · [시스템 설계](../../SYSTEM_DESIGN.md)


## 현재 구조

```text
gpt-manager/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ defaults.py
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
│  │  ├─ legal_markdown_service.py
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
│  │  ├─ legal/
│  │  │  └─ document.html
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
│  ├─ conftest.py
│  ├─ test_admin.py
│  ├─ test_api_keys.py
│  ├─ test_app.py
│  ├─ test_auth.py
│  ├─ test_config.py
│  ├─ test_google_oauth.py
│  ├─ test_health.py
│  ├─ test_legal_pages.py
│  ├─ test_prompt_reviews.py
│  ├─ test_reservations.py
│  ├─ test_usage_logs.py
│  ├─ test_user_model.py
│  └─ e2e/
├─ docs/
│  ├─ development/
│  │  └─ 2026-07-03_ADMIN_RESERVATION_UI_UPDATE.md
│  └─ legal/
│     ├─ TERMS.md
│     └─ PRIVACY_POLICY.md
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
예약 충돌, OAuth, 암호화, 프롬프트 정리 조립은 services에 둔다.
DB 모델은 app/models/__init__.py에 모아 둔다. 현재 User, Reservation, AppSetting, GuideItem 등 운영 모델을 포함한다.
Jinja 템플릿은 기능별 하위 디렉터리로 분리한다.
공통 안내 UI는 templates/partials에 둔다.
관리자 설정/안내문구 기본값은 app/defaults.py에 둔다.
이용약관/개인정보처리방침 원문은 docs/legal Markdown 파일로 관리한다.
법적 Markdown 렌더링은 services/legal_markdown_service.py에서 제한 문법과 escape 처리로 수행한다. Docker 이미지는 docs 전체를 제외하되 TERMS.md와 PRIVACY_POLICY.md만 포함해야 /terms, /privacy가 동작한다. 단, 약관과 개인정보처리방침의 내용 타당성은 테스트 코드가 아니라 수동 검토와 기관 검토로 확인한다.
SQLite DB는 ./instance/app.db에 저장하고 Docker Compose에서 ./instance를 /app/instance로 마운트한다.
```

## 과도한 구조화 금지

```text
Repository 패턴 선행 도입 금지
Service 계층 과잉 분리 금지
DTO/Form/Schema 계층 선행 도입 금지
테스트 없는 파일 이동 금지
```
