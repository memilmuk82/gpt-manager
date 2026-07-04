# ✅ Project Status - 생성형 AI 계정 공동 사용 지원 시스템

## 🔗 관련 문서

[README](README.md) · [교육과정](docs/EDUCATION.md) · [시스템 설계](SYSTEM_DESIGN.md) · [개발 로그](docs/development/DEVELOPMENT_LOG.md) · [테스트 리포트](docs/development/TEST_REPORT.md)

## 🧭 1. 프로젝트 개요

```text
프로젝트명: gpt-share-manager-vnext
표시명: ChatGPT Pro 5X 공동 사용 지원 시스템
목적: 공용 생성형 AI 계정 예약·사용 기록 관리 + BYOK 기반 AI 프롬프트 정리
지원 Provider: OpenAI, Google Gemini, Anthropic Claude
OpenRouter: 현재 미지원
운영 도메인: https://dev-gpt.memilmuk82.com
현재 브랜치: master
```

이 문서는 현재 구현 상태와 검증 결과를 요약합니다. 설치, 실행, 시연 흐름은 [README.md](README.md)를 기준으로 확인합니다.

## ✅ 2. 현재 상태

```text
상태: BYOK AI Provider 기반 프롬프트 정리 확장 완료
최근 검증일: 2026-07-04
pytest: PASS, 88 passed
Playwright E2E: PASS, 1 passed
Docker Compose rebuild: PASS, gpt-manager-web-1 Up, /healthz 200
운영 Health Check: PASS, /healthz 200 {"status":"ok"}
HTTPS 도메인: PASS, dev-gpt.memilmuk82.com 200 OK
HTTP -> HTTPS: PASS, 301 redirect
```

최근 반영된 핵심 작업:

```text
리뷰용 테스트 계정 README 상단 배치
Codex/ChatGPT 개발 보조 활용 사실 문서화
README 개발 배경과 기술 선택 이유 중복 정리
운영 편의 기능 및 관리자 기능 문서화
Apple HIG + Material 3 Expressive 방향의 UI 시스템 개선 기록 반영
RC 운영 CRUD 검증 1782896313 시연 더미데이터 seed 스크립트 추가 및 DB 주입 완료
```

## 🧱 3. 확정된 방향

```text
Flask + SQLite + Docker Compose + OCI 단일 인스턴스
Gunicorn 컨테이너 + Nginx HTTPS reverse proxy
AI API는 사용자별 BYOK 방식으로 프롬프트 정리/개선에만 제한적으로 사용
자유 채팅형 챗봇은 만들지 않음
생성형 AI 계정 실제 사용량 자동 조회는 하지 않음
공용 계정 ID/PW 저장하지 않음
```

## 🧩 4. 확정 기술 스택

```text
Backend: Flask
DB: SQLite ./instance/app.db
ORM: SQLAlchemy
Auth: Flask-Login + Google OAuth
API Key Encryption: cryptography.Fernet
Frontend: Jinja2 + Tailwind CDN + Vanilla JavaScript
Package: uv
Test: pytest + Playwright
Deploy: Docker Compose + Gunicorn + Nginx + OCI Ubuntu
```

상세한 기술 선택 이유는 [docs/EDUCATION.md](docs/EDUCATION.md)와 [docs/decisions/TECH_STACK_DECISIONS.md](docs/decisions/TECH_STACK_DECISIONS.md)를 기준으로 확인합니다.

## ⚙️ 5. 현재 구현 기능

```text
비로그인 시작 화면
로컬 로그인/회원가입/로그아웃
Google OAuth 로그인
승인 대기/정지 계정 접근 제어
사용 신청/내 예약/오늘 예약/월간 예약 캘린더
예약 충돌 확인 API와 사용 규칙 동의 버전 기록
사용 로그 작성/조회/검색/필터
완료 예약 미작성 로그 알림과 자동 선택
홈 KPI 카드와 운영 공지 배너
사용자별 AI Provider/API Key 설정, 암호화 저장/삭제/연결 테스트/모델 새로고침
BYOK 프롬프트 정리, 템플릿, 저장/조회, 검색, Markdown 다운로드
관리자/보조관리자 대시보드
사용자 승인/정지/수정/CSV 일괄 등록
인증번호 담당자 최대 2명 제한
관리자 설정, 안내문구, 주요 화면 문구, AI 리소스/작업유형 관리
월간 운영 보고서, 감사 로그, DB 백업, CSV 내보내기, 전체 테스트 실행
/terms, /privacy 법적 고지 페이지와 공통 Footer 링크
```

## 🛡️ 6. 권한 정책

```text
비로그인: 시작 화면, 로그인, 회원가입, Google OAuth 시작, /terms, /privacy 가능
승인 대기 사용자: pending 화면으로 제한
일반 사용자: 본인 예약/로그/API Key/프롬프트 정리, 오늘 예약 전체 현황 조회
보조관리자 assistant_admin: 일반 사용자 기능 + /admin 및 /admin/users 접근
관리자 admin: 보조관리자와 동일한 운영 관리 접근
정지 사용자: 로그인/기능 접근 차단
```

보조관리자 자동 지정:

```text
ASSISTANT_ADMIN_EMAILS=<comma-separated-emails>
```

## 🧪 7. 운영 검증 결과

```text
DNS: dev-gpt.memilmuk82.com -> 129.154.221.2
HTTPS: 200 OK
HTTP: 301 -> HTTPS
/healthz: 200 {"status":"ok"}
/reservations/today: 비로그인 302 /auth/login?next=...
/terms: 200 OK
/privacy: 200 OK
Docker container: gpt-manager-web-1 Up
Port binding: 127.0.0.1:5000 -> container 5000
```

## 🧾 8. 테스트 결과

```text
uv run pytest: PASS, 88 passed
npm run test:e2e: PASS, 1 passed
python3 -m py_compile: PASS
Docker Compose up -d --build: PASS
```

상세 테스트 이력은 [docs/development/TEST_REPORT.md](docs/development/TEST_REPORT.md)를 참고합니다.

## 🧭 9. 남은 작업

```text
제출용 최종 시연 리허설
필요 시 스크린샷/영상 캡처
이용약관/개인정보처리방침 기관 최종 검토
운영 DB 백업/복원 운영 환경 리허설
운영 전 ENABLE_REVIEW_ADMIN=false 확인
```

## 🚫 10. 제외 기능

```text
자유 채팅형 챗봇
수업안/평가계획 생성기
교육과정 파일 분석
학생 개인정보 처리
생성형 AI 계정 실제 사용량 자동 조회
생성형 AI 계정 로그인 통제
공용 계정 ID/PW 저장
PostgreSQL 운영 전환
OCI Managed DB
네이버웍스 API
방과후 관리
정보화기기/IP 관리
```

## 🚀 11. 배포 요약

```text
OCI Ubuntu 배포 완료
Docker Compose 운영 완료
Gunicorn 적용 완료
Nginx reverse proxy 적용 완료
Cloudflare/DNS 연결 완료
HTTPS 도메인 연결 완료
SQLite ./instance bind mount 확인 완료
```
