# TASK - Current Codex Work

## 현재 작업

```text
README 및 전체 문서 최신화, GitHub push
```

## 현재 상태

```text
Release Candidate 운영 검증 완료
도메인: https://dev-gpt.memilmuk82.com
Docker Compose 재빌드 완료
uv run pytest: 55 passed
최근 기능 push: 337e677 feat: add legal policy pages
```

## 완료된 주요 기능

```text
로컬 로그인/회원가입/로그아웃
Google OAuth 로그인
승인 대기/정지 계정 접근 제어
관리자 및 보조관리자 권한
사용자 승인/정지 관리
홈 화면 현재 사용중/다음 예약/오늘 예약 요약
사용 신청
내 예약
오늘 예약 날짜별 전체 현황
사용 로그
Gemini API Key 암호화 저장
프롬프트 점검
사용 안내
이용약관/개인정보처리방침 Markdown 법적 고지 페이지
공통 Footer Copyright/정보관리책임자 표시
Docker Compose + Gunicorn + Nginx + HTTPS 운영
```

## 최근 검증

```text
uv run pytest: 55 passed
npm run test:e2e: 1 passed
Docker Compose up -d --build: PASS
https://dev-gpt.memilmuk82.com/: 200 OK
https://dev-gpt.memilmuk82.com/healthz: 200 {"status":"ok"}
https://dev-gpt.memilmuk82.com/terms: 200 OK
https://dev-gpt.memilmuk82.com/privacy: 200 OK
/reservations/today 비로그인 접근: 302 /auth/login?next=...
```

## 남은 작업

```text
README 및 문서 최신화 커밋/푸시
제출용 최종 시연 리허설
필요 시 운영 DB 백업
```
