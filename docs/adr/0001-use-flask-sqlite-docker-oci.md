# ADR 0001 - Flask + SQLite + Docker Compose + OCI 사용

## 결정

이번 제출용 MVP는 Flask + SQLite + Docker Compose + OCI 단일 인스턴스로 구현한다.

## 이유

```text
3일 안에 완성 가능하다.
사용자가 익숙한 기술 흐름이다.
로컬과 서버 환경을 Docker Compose로 맞출 수 있다.
SQLite로 DB 운영 부담을 줄일 수 있다.
```

## 제외

```text
Vercel/Firebase
OCI Managed Database
PostgreSQL 선행 도입
Kubernetes
```

## 결과

빠른 제출과 안정적인 시연을 우선한다. 추후 필요하면 Docker Compose PostgreSQL로 확장한다.
