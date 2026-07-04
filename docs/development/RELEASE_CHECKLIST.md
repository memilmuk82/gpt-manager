# 🚀 Release Checklist

## 🔗 관련 문서

[README](../../README.md) · [현재 상태](../../PROJECT_STATUS.md) · [테스트 리포트](TEST_REPORT.md)

## ✅ 1. 현재 릴리스 기준

```text
상태: 운영 편의 기능 보완 및 문서화 완료
기준일: 2026-07-04
운영 도메인: https://dev-gpt.memilmuk82.com
pytest: 84 passed
Playwright E2E: 1 passed
Docker Compose rebuild: PASS
```

이 문서는 제출·시연·운영 전 최종 점검용입니다. 과거 RC 일정과 결정 배경은 [docs/adr/0003-release-freeze.md](../adr/0003-release-freeze.md)와 [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md)에 기록으로 보존합니다.

## 🧩 2. 완료 조건

```text
[x] 로컬 Docker Compose 실행 성공
[x] OCI Docker Compose 실행 성공
[x] /healthz 응답 확인
[x] 로컬 로그인 확인
[x] Google OAuth Redirect URI 운영 도메인 기준 설정 확인
[x] BYOK Provider별 API Key 등록/삭제 확인
[x] 프롬프트 정리 adapter mock 테스트 통과
[x] 예약 생성/취소/완료 확인
[x] 오늘 예약 화면 확인
[x] 월간 예약 캘린더 확인
[x] 완료 예약의 미작성 로그 알림 확인
[x] 사용 로그 작성/검색/필터 확인
[x] 관리자 대시보드 확인
[x] 관리자 설정/안내문구/주요 화면 문구/신청 항목/사용자/통계/월간 보고서/감사 로그 확인
[x] DB 백업과 CSV 내보내기 확인
[x] 프롬프트 정리 메뉴와 화면 최신 UI 확인
[x] 개인 AI Provider 설정 화면과 사용자 badge 링크 확인
[x] 보조관리자 관리자 화면 접근 확인
[x] pytest 통과
[x] Playwright E2E 통과
[x] README 실행 방법 확인
[x] .env.example 최신화
[x] 도메인 HTTPS 응답 확인
[x] Footer 이용약관/개인정보처리방침 링크 확인
[x] /terms, /privacy HTTPS 200 확인
[x] Markdown 법적 문서 raw HTML escape 테스트 확인
```

## 🔒 3. 운영 전 확인

```text
[ ] 제출/리뷰가 끝난 뒤 ENABLE_REVIEW_ADMIN=false 확인
[ ] 운영 SECRET_KEY와 APP_ENCRYPTION_KEY가 고정값인지 확인
[ ] Google OAuth Redirect URI가 운영 도메인과 일치하는지 확인
[ ] 운영 DB 백업 파일 생성 및 복원 절차 리허설
[ ] 이용약관/개인정보처리방침 기관 최종 검토
[ ] 필요한 경우 주요 화면 스크린샷 또는 시연 영상 캡처
```

## 🎬 4. 최종 테스트 시나리오

```text
1. 새 브라우저/시크릿 창에서 https://dev-gpt.memilmuk82.com 접속
2. 리뷰용 테스트 계정 또는 Google OAuth로 로그인
3. 홈 화면 KPI와 미작성 로그 알림 확인
4. 사용 신청으로 예약 생성
5. 예약 충돌 테스트
6. 오늘 예약과 월간 예약 캘린더 확인
7. 예약 완료 후 사용 로그 작성
8. AI Provider/API Key 설정
9. 프롬프트 정리 실행 및 Markdown 다운로드 확인
10. Footer에서 이용약관과 개인정보처리방침 페이지 이동 확인
11. 로그아웃
12. 관리자 또는 보조관리자 계정 로그인
13. 관리자 설정/안내문구/주요 화면 문구/신청 항목/사용자/통계/월간 보고서/감사 로그 확인
14. 사용자/예약/로그 CSV 내보내기와 DB 백업 확인
15. uv run pytest 실행
16. npm run test:e2e 실행
17. docker compose up -d --build 후 /healthz 확인
```

## 🗣️ 5. 제출 설명 핵심 문장

```text
이 프로젝트는 공용 생성형 AI 계정 사용을 직접 통제하는 앱이 아니라, 공용 AI 사용 예약·기록·프롬프트 개선을 지원하는 학교 업무 관리 앱입니다. AI API는 자유 채팅이 아니라 BYOK 프롬프트 정리 기능에 제한적으로 사용해 비용과 보안 위험을 줄였습니다. 관리자는 공용 API Key를 제공하지 않습니다.
```
