# Project Status - 생성형 AI 계정 공동 사용 지원 시스템

## 1. 프로젝트 개요

```text
프로젝트명: gpt-share-manager-vnext
표시명: 생성형 AI 계정 공동 사용 지원 시스템
목적: 공용 생성형 AI 계정 예약·사용 기록 관리 + Gemini 기반 프롬프트 점검기
제출 목표: 2026-07-03 오후
운영 도메인: https://dev-gpt.memilmuk82.com
```

## 2. 현재 상태

```text
상태: Release Candidate 운영 검증 완료
최근 배포 커밋: 95f51ca ui: add today reservations and assistant admin
pytest: PASS, 50 passed
Docker Compose rebuild: PASS
운영 Health Check: PASS, /healthz 200 {"status":"ok"}
HTTPS 도메인: PASS, dev-gpt.memilmuk82.com 200 OK
HTTP -> HTTPS: PASS, 301 redirect
오늘 예약 화면: 구현 완료
보조관리자 권한: 구현 완료
Google OAuth Redirect URI: https://dev-gpt.memilmuk82.com/auth/google/callback 로 설정 확인
```

## 3. 확정된 방향

```text
Flask + SQLite + Docker Compose + OCI 단일 인스턴스
Gunicorn 컨테이너 + Nginx HTTPS reverse proxy
Gemini API는 프롬프트 점검/개선에만 제한적으로 사용
자유 채팅형 챗봇은 만들지 않음
생성형 AI 계정 실제 사용량 자동 조회는 하지 않음
공용 계정 ID/PW 저장하지 않음
```

## 4. 확정 기술 스택

```text
Backend: Flask
DB: SQLite ./instance/app.db
ORM: SQLAlchemy
Auth: Flask-Login + Google OAuth
API Key Encryption: cryptography.Fernet
Frontend: Jinja2 + Tailwind CDN
Package: uv
Test: pytest
Deploy: Docker Compose + Gunicorn + Nginx + OCI Ubuntu
```

## 5. 완료된 작업

```text
Phase 1 Flask 기본 골격 생성
Phase 2 로컬 회원가입/로그인/로그아웃 구현
Phase 3 AiResource/Reservation/UsageLog 모델 및 예약/로그 기능 구현
Phase 4 Gemini API Key 암호화 저장/삭제/마스킹/복호화 확인 구현
Phase 5 PromptReview 모델 및 Gemini 프롬프트 점검 기능 구현
Phase 6 관리자 대시보드, 사용자 승인/정지, Google OAuth 기본 흐름 구현
Phase 7 README/.env.example/OAuth Redirect URI/OCI 문서 정리
Release Candidate Playwright E2E 검증
SQLite 운영 DB 호환성 보정
OCI 운영 배포
Nginx reverse proxy 및 HTTPS 도메인 연결
Apps Script 기준 UI 문구 일반화 및 홈/사용 안내 화면 정리
오늘 예약 화면 추가
보조관리자 권한 추가
Docker Compose 재빌드 및 도메인 응답 확인
```

## 6. 현재 구현 기능

```text
비로그인 시작 화면
로컬 로그인/회원가입/로그아웃
Google OAuth 로그인
승인 대기 화면
승인 사용자 홈 화면
사용 신청/내 예약/오늘 예약
사용 로그
Gemini API Key 설정
프롬프트 점검
사용 안내
관리자/보조관리자 대시보드
사용자 승인/정지 관리
```

## 7. 권한 정책

```text
비로그인: 시작 화면, 로그인, 회원가입, Google OAuth 시작 가능
승인 대기 사용자: pending 화면으로 제한
일반 사용자: 본인 예약/로그/API Key/프롬프트 점검, 오늘 예약 전체 현황 조회
보조관리자 assistant_admin: 일반 사용자 기능 + /admin 및 /admin/users 접근
관리자 admin: 보조관리자와 동일한 운영 관리 접근
정지 사용자: 로그인/기능 접근 차단
```

보조관리자 자동 지정:

```text
ASSISTANT_ADMIN_EMAILS=<comma-separated-emails>
```

## 8. 운영 검증 결과

```text
DNS: dev-gpt.memilmuk82.com -> 129.154.221.2
HTTPS: 200 OK
HTTP: 301 -> HTTPS
/healthz: 200 {"status":"ok"}
/reservations/today: 비로그인 302 /auth/login?next=...
Docker container: gpt-manager-web-1 Up
Port binding: 127.0.0.1:5000 -> container 5000
```

## 9. 테스트 결과

```text
명령: uv run pytest
결과: PASS
PASS: 50
FAIL: 0
```

추가 검증:

```text
python3 -m py_compile: PASS
Docker Compose down/up --build: PASS
curl http://127.0.0.1:5000/: 200 OK
curl https://dev-gpt.memilmuk82.com/: 200 OK
curl https://dev-gpt.memilmuk82.com/healthz: 200 OK
```

## 10. 남은 작업

```text
제출용 최종 시연 리허설
필요 시 스크린샷/영상 캡처
운영 DB 백업 절차 수동 정리
CSRF 보호는 제출 이후 보완 과제로 유지
```

## 11. 제외 기능

```text
자유 채팅형 챗봇
수업안/평가계획 생성기
교육과정 파일 분석
학생 개인정보 처리
생성형 AI 계정 실제 사용량 자동 조회
생성형 AI 계정 로그인 통제
공용 계정 ID/PW 저장
PostgreSQL
OCI Managed DB
네이버웍스 API
방과후 관리
정보화기기/IP 관리
```

## 12. Release Candidate 배포 요약

```text
OCI Ubuntu 배포 완료
Docker Compose 운영 완료
Gunicorn 적용 완료
Nginx reverse proxy 적용 완료
Cloudflare/DNS 연결 완료
HTTPS 도메인 연결 완료
SQLite ./instance bind mount 확인 완료
Release Candidate 환경 구축 완료
```
