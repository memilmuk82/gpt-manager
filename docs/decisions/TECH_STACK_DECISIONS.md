# Tech Stack Decisions

## 관련 문서

[README](../../README.md) · [교육과정](../EDUCATION.md) · [ADR 0001](../adr/0001-use-flask-sqlite-docker-oci.md)


## 1. Flask 채택

채택 이유:

```text
사용자가 익숙하다.
수업 자료와 연결된다.
Codex가 안정적으로 구현하기 쉽다.
Docker Compose + OCI 배포가 단순하다.
```

채택하지 않은 것:

```text
FastAPI: API 서버에는 좋지만 이번 MVP는 Jinja SSR 웹앱이므로 Flask가 더 단순하다.
Django: 기능은 강하지만 3일 MVP에는 무겁다.
Next.js/Vercel: 연수 예시와 맞지만 사용자의 장기 운영 환경과 맞지 않는다.
```

## 2. SQLite 채택

채택 이유:

```text
3일 MVP에 적합하다.
Docker 없이도 실행 가능하다.
OCI 단일 인스턴스에서 관리가 쉽다.
사용자 수와 동시 쓰기가 많지 않다.
```

확장 전략:

```text
MVP: SQLite
확장: Docker Compose PostgreSQL 컨테이너
제외: OCI Managed Database
```

## 3. Jinja2 + Vanilla JS + Tailwind CDN 채택

채택 이유:

```text
빠르게 구현 가능하다.
빌드 파이프라인이 필요 없다.
백엔드 중심 앱에 적합하다.
React/Vue보다 제출용 MVP에 안정적이다.
```

## 4. uv 채택

채택 이유:

```text
pyproject.toml 기반 관리
lock file 재현성
Docker/OCI 환경 통일
명령 흐름 단순
```

## 5. Docker Compose + OCI 채택

채택 이유:

```text
로컬과 서버 실행 환경을 맞출 수 있다.
사용자가 OCI를 선호하고 통제 가능하다.
Vercel/Firebase보다 Flask 구조와 맞다.
OCI 단일 인스턴스에서 충분하다.
```

## 6. Gemini 경량 모델 채택

채택 이유:

```text
연수 요구사항과 맞다.
프롬프트 정리은 고급 추론보다 패턴 기반 개선에 가깝다.
비용을 줄일 수 있다.
자유 채팅이 아니라 정형 기능 호출이라 안정적이다.
```

주의:

```text
기본 모델은 gemini-3.1-flash-lite이며 모델명은 .env의 GEMINI_MODEL로 관리한다.
코드에 모델명을 하드코딩하지 않는다.
```
