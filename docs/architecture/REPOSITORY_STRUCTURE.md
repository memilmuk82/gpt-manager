# Repository Structure

## 권장 구조

```text
gpt-share-manager-vnext/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extensions.py
│  ├─ models.py
│  ├─ auth/
│  ├─ main/
│  ├─ reservations/
│  ├─ ai/
│  ├─ admin/
│  ├─ services/
│  ├─ templates/
│  └─ static/
├─ tests/
├─ data/
├─ docs/
├─ Dockerfile
├─ docker-compose.yml
├─ pyproject.toml
├─ uv.lock
├─ .env.example
├─ README.md
├─ PROJECT_INSTRUCTIONS.md
├─ PRD.md
├─ SYSTEM_DESIGN.md
├─ DEVELOPMENT_PLAN.md
├─ TASK.md
└─ PROJECT_STATUS.md
```

## 구조 원칙

```text
route는 요청/응답만 담당한다.
비즈니스 로직은 services에 둔다.
DB 모델은 MVP에서 models.py 하나로 시작한다.
모델 파일이 커지면 테스트 후 app/models/로 분리한다.
Gemini 호출은 services/gemini_service.py에만 둔다.
API Key 암호화는 services/crypto_service.py에 둔다.
```

## 과도한 구조화 금지

```text
Repository 패턴 선행 도입 금지
Service 계층 과잉 분리 금지
DTO/Form/Schema 계층 선행 도입 금지
테스트 없는 파일 이동 금지
```
