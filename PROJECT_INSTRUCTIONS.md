# 생성형 AI 계정 공동 사용 지원 시스템 - Project Instructions

## 관련 문서

[README](README.md) · [현재 상태](PROJECT_STATUS.md) · [개발 로그](docs/development/DEVELOPMENT_LOG.md)


## 1. 문서 목적

이 문서는 `gpt-share-manager-vnext` 프로젝트의 개발 원칙을 정의한다.

이번 프로젝트는 2026-07-03 제출을 목표로 하는 연수 결과물이다. 따라서 장기 학습용 완성형 프로젝트가 아니라, 3일 안에 작동·시연·설명 가능한 MVP를 완성하는 것이 우선이다. 2026-07-02 현재 RC 운영 검증은 완료되었으며, 이후 변경은 최종 문서·시연 정리 중심으로 제한한다.

적용 대상:

```text
사용자
ChatGPT
Codex
추후 새 대화창
추후 유지보수자
```

## 2. 최우선 목표

```text
2026-07-02까지 OCI에서 작동하는 RC1 완성
2026-07-03에는 코드 수정 없이 최종 테스트와 제출만 수행
```

성공 기준:

```text
로컬 Docker Compose 실행 성공
OCI Docker Compose 실행 성공
로컬 로그인 성공
Google OAuth 로그인 또는 운영 Redirect URI 설정 확인
예약 생성/조회/취소 가능
오늘 예약 조회 가능
사용 로그 작성 가능
Gemini API Key 등록/삭제 가능
프롬프트 점검기 실행 가능
생성/점검 결과 저장 가능
README로 시연 흐름 설명 가능
이용약관/개인정보처리방침/정보관리책임자 안내 가능
pytest 기본 테스트 통과
```

## 3. 최우선 철학

```text
AI가 개발자를 대체하지 않는다.
AI는 개발자의 이해와 판단을 보조한다.
모든 개발 프로세스의 최종 통제권은 사용자에게 있다.
```

이번 프로젝트는 공부용 상세 구현보다 제출용 완성을 우선한다. 다만 다음 원칙은 유지한다.

```text
기능 단위로 작게 구현한다.
기능마다 테스트한다.
테스트 후 소규모 리팩토링한다.
리팩토링 후 다시 테스트한다.
문서를 갱신한 뒤 다음 기능으로 넘어간다.
```

## 4. Feature Complete Cycle

모든 기능은 아래 흐름을 따른다.

```text
1. 기능 목표 확인
2. 변경 계획 제시
3. 사용자 승인
4. 구현
5. TDD/pytest 실행
6. 소규모 리팩토링 검토
7. 리팩토링 필요 시 수행
8. 다시 TDD/pytest 실행
9. PROJECT_STATUS.md 갱신
10. DEVELOPMENT_LOG.md 갱신
11. 다음 기능 진행
```

중요:

```text
테스트 실패 상태로 다음 기능 진행 금지
리팩토링과 신규 기능 추가를 한 번에 수행 금지
기능 완료 후 문서 갱신 없이 다음 Phase 진행 금지
```

## 5. 최우선 금지 사항

```text
승인 없는 기능 삭제 금지
승인 없는 정책 변경 금지
승인 없는 DB 구조 변경 금지
승인 없는 권한 정책 변경 금지
승인 없는 보안 완화 금지
승인 없는 대규모 리팩토링 금지
승인 없는 필요성 불명확한 선행 구조화 금지
테스트 없는 파일 이동/함수 이동 금지
테스트 없이 다음 Phase 진행 금지
Codex 자동 commit 금지
Codex 자동 push 금지
Codex에게 전체 프로젝트를 한 번에 자동 생성시키는 방식 금지
```

보안 관련 금지:

```text
GPT 계정 ID 저장 금지
GPT 계정 비밀번호 저장 금지
공용 GPT 계정 접속 정보를 DB/Settings/Guide에 저장 금지
Gemini API Key 프론트엔드 노출 금지
Gemini API Key 평문 저장 금지
사용자 비밀번호 평문 저장 금지
학생 개인정보 입력 기능 구현 금지
학교 내부 민감자료 업로드 기능 구현 금지
법적 문서 Markdown raw HTML 실행 금지
```

기술 범위 관련 금지:

```text
React/Vue/Svelte 임의 도입 금지
PDF/HWP/HWPX 파싱 기능 구현 금지
자유 채팅형 챗봇 구현 금지
PostgreSQL 선행 도입 금지
OCI Managed Database 사용 금지
복잡한 결제/과금 관리 구현 금지
```

## 6. 작업 전 필수 보고

Codex는 파일 수정 전 아래 항목을 먼저 보고한다.

```text
이번 단계 목표
변경/생성 대상 파일
각 파일 역할
변경 이유
영향 범위
예상 부작용
검증 방법
다음 단계로 넘어가는 기준
```

사용자가 Phase 단위 진행을 승인하면 해당 Phase 내부에서는 필요한 파일을 수정할 수 있다. 단, Phase 범위를 벗어난 기능 추가는 다시 승인받는다.

## 7. ChatGPT / Codex / 사용자 역할 분리

```text
ChatGPT:
- 기획
- 설계
- 정책 판단
- 보안 검토
- Codex 결과 리뷰
- 제출용 설명 문서 정리

Codex:
- 파일 생성
- Flask 코드 구현
- 테스트 코드 작성
- Docker Compose 작성
- pytest 실행
- 소규모 리팩토링
- 문서 갱신 초안 작성

사용자:
- 최종 결정
- 승인
- 테스트 결과 확인
- Git commit/push 여부 결정
- OCI 배포 최종 확인
```

## 8. 모델/추론 수준 사용 원칙

```text
즉시:
- 단순 문구
- README 일부 수정
- Tailwind 조정
- 커밋 메시지 초안

중간:
- 일반 CRUD
- Jinja 화면
- 단순 테스트
- 문서 초안

높음:
- Flask 구조 검토
- 테스트 설계
- 오류 분석
- 서버/클라이언트 연동

Pro:
- PRD
- SYSTEM_DESIGN
- DB 설계
- 인증/OAuth
- API Key 보안
- Docker/OCI 배포 구조
- 배포 전 최종 점검
```

이번 프로젝트에서는 페이퍼워크 이후 구현 대화는 Codex 중심으로 진행한다. 막히는 설계·보안 판단만 ChatGPT로 가져온다.

## 9. 기술 스택 원칙

```text
Backend: Flask
DB: SQLite MVP
ORM: SQLAlchemy
Auth: Flask-Login + Google OAuth(Authlib 권장)
Password: Werkzeug password hash 또는 동등한 안전한 해시
API Key Encryption: cryptography.Fernet
Frontend: Jinja2 SSR + Vanilla JS + Tailwind CDN
Package: uv + pyproject.toml + uv.lock
Test: pytest
Deploy: Docker Compose + OCI 단일 인스턴스
```

MVP에서는 다음을 사용하지 않는다.

```text
Alembic
PostgreSQL
OCI Managed DB
Kubernetes
Celery
Redis
React/Vue/Svelte
Tailwind 빌드 파이프라인
```

단, SQLAlchemy ORM과 `DATABASE_URL` 환경변수 구조를 사용하여 추후 Docker PostgreSQL 전환 가능성은 열어둔다.

## 10. DB 원칙

```text
MVP DB: SQLite
DB 파일: ./instance/app.db
Docker Compose에서 ./instance 볼륨 마운트
PostgreSQL 전환 가능하도록 DATABASE_URL 사용
SQLite 전용 raw SQL에 의존하지 않음
```

확장 전략:

```text
MVP: SQLite
운영 확대: Docker Compose PostgreSQL 컨테이너
대규모 운영: 필요해진 뒤 외부 DB 검토
```

OCI Managed Database는 이번 프로젝트와 일반적인 교내 운영 규모에서는 제외한다.

## 11. AI/Gemini 사용 원칙

Gemini API는 다음 용도로만 사용한다.

```text
1. 프롬프트 점검
2. 프롬프트 개선
3. 개선 이유 설명
4. 선택 기능: 사용 로그 기반 운영 보고서 생성
```

금지:

```text
자유 채팅 UI
무제한 대화
학생정보 기반 생성
교육과정 PDF/HWP/HWPX 전체 분석
GPT 계정 사용량 자동 조회
```

비용 통제:

```text
입력 글자 수 제한
출력 토큰 제한
정해진 기능 버튼에서만 API 호출
결과 저장 후 재조회 시 API 재호출 금지
Gemini 기본 모델은 gemini-3.1-flash-lite이며 모델명은 환경변수로 관리
```

## 12. 보안 원칙

### 로컬 계정

```text
비밀번호 평문 저장 금지
안전한 password hash 사용
로그인 실패 메시지는 과도한 정보 제공 금지
```

### Google OAuth

```text
Google OAuth 로그인 지원
로컬/운영 Redirect URI 분리
운영에서는 HTTPS 전제
허용 도메인 제한은 선택 기능으로 두되, MVP에서는 설정 가능하게 설계
```

### API Key

```text
Gemini API Key는 사용자별 설정에 저장
DB에는 암호화된 ciphertext만 저장
암호화 키는 APP_ENCRYPTION_KEY 환경변수에 저장
화면에는 전체 키를 다시 보여주지 않음
마스킹 표시만 허용
삭제 기능 제공
프론트엔드로 API Key 전달 금지
로그에 API Key 출력 금지
```

### 세션/쿠키

```text
SESSION_COOKIE_HTTPONLY=True
운영 HTTPS에서는 SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Lax 이상
SECRET_KEY 환경변수 사용
```

## 13. Frontend 원칙

```text
Jinja2 SSR + Vanilla JS + Tailwind CDN 사용
HTML 문자열 실행 금지
사용자 입력 출력 시 escape 처리
innerHTML에 신뢰할 수 없는 값 직접 삽입 금지
서버 검증을 프론트 검증으로 대체 금지
```

## 14. 문서 갱신 원칙

기능 하나가 끝날 때마다 다음 문서를 갱신한다.

```text
PROJECT_STATUS.md
DEVELOPMENT_LOG.md
docs/development/TEST_REPORT.md
```

문서에는 다음을 남긴다.

```text
무엇을 구현했는가
왜 그렇게 구현했는가
테스트 결과
남은 작업
리팩토링 여부
다음 Phase 기준
```

## 15. Release Freeze 원칙

```text
2026-07-02: RC1 생성, OCI 배포, 핵심 테스트 완료
2026-07-03: 기능 추가 금지, 리팩토링 금지, 코드 구조 변경 금지
```

2026-07-03에는 다음만 허용한다.

```text
실행 확인
로그인 확인
Gemini API 확인
예약/로그/프롬프트 점검 시연
README 오타 수정
제출 자료 정리
```
