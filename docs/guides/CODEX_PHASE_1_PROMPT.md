# Codex Prompt - Phase 1

아래 지시문을 Codex에 붙여넣는다.

---

너는 `gpt-share-manager-vnext` 프로젝트의 보조 개발자다.

먼저 다음 문서를 읽어라.

```text
CODEX_START_HERE.md
PROJECT_INSTRUCTIONS.md
PRD.md
SYSTEM_DESIGN.md
DEVELOPMENT_PLAN.md
TASK.md
PROJECT_STATUS.md
```

현재 작업은 다음이다.

```text
Phase 1: Flask + SQLite + Docker Compose 기본 골격 생성
```

중요 원칙:

```text
파일 수정 전 변경 계획을 먼저 보고한다.
사용자가 Phase 1 진행을 승인하면 파일을 생성한다.
Phase 1 범위를 벗어난 로그인, 예약, Gemini 기능은 구현하지 않는다.
테스트 없이 다음 Phase로 넘어가지 않는다.
```

먼저 아래를 보고하고 멈춰라.

```text
1. 이해한 프로젝트 목표
2. Phase 1 생성 파일 목록
3. 각 파일 역할
4. 사용할 패키지
5. 실행 명령어
6. 테스트 명령어
7. 예상 위험 요소
8. 완료 기준
```

사용자가 승인하면 Phase 1을 구현한다.

Phase 1 구현 범위:

```text
uv 프로젝트 초기화
Flask app factory
config.py
extensions.py
/healthz
index page
base template
Tailwind CDN
Dockerfile
docker-compose.yml
.env.example
pytest 기본 테스트
README 실행 방법 보완
PROJECT_STATUS.md 갱신
DEVELOPMENT_LOG.md 갱신
TEST_REPORT.md 갱신
```

완료 후 보고:

```text
1. 생성/수정 파일
2. 핵심 구현 내용
3. 테스트 결과
4. Docker 실행 결과
5. 남은 위험 요소
6. 다음 Phase 제안
```
