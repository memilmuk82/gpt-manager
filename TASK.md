# 🧭 TASK - Current Codex Work

## ✅ 현재 작업

```text
문서 구조 점검, 최신 상태 반영, 테스트 메뉴 설명 강화, BYOK 모델 정책 정리 완료
```

## 📌 현재 상태

```text
기준 브랜치: master
운영 도메인: https://dev-gpt.memilmuk82.com
최근 검증 기준: 2026-07-04
uv run pytest: 88 passed
npm run test:e2e: 1 passed
Docker Compose 재빌드: PASS, gpt-manager-web-1 Up
```

## 📚 문서 역할

```text
README.md: 프로젝트 포털과 실행 가이드
PROJECT_STATUS.md: 현재 상태와 검증 결과
TASK.md: 현재 작업 메모
SYSTEM_DESIGN.md: 시스템 구조와 데이터/라우트 설계
PROJECT_INSTRUCTIONS.md: 개발 원칙과 Codex 작업 규칙
DEVELOPMENT_LOG.md: 시간순 변경 이력
TEST_REPORT.md: 테스트 이력
EDUCATION.md: 교육 철학과 기술 선정 이유
```

## 🧩 최근 정리 내용

```text
README 포털 구조 유지 및 현재 상태 최신화
PROJECT_STATUS 최신 검증 결과 반영
PROJECT_INSTRUCTIONS에 구현된 기능은 패스하고 미구현만 처리하는 원칙 반영
관리자 테스트 실행 화면에 테스트 파일별 설명/상태 표시 추가
Anthropic Claude 기본 추천 모델을 Opus 4.8 기준으로 정리
SYSTEM_DESIGN 섹션 번호와 향후 확장 목록 정리
RELEASE_CHECKLIST, TEST_REPORT, DEVELOPMENT_LOG 최신화
```

## 🧪 최근 검증 기준

```text
uv run pytest: PASS, 88 passed
npm run test:e2e: PASS, 1 passed
운영 /healthz: 200 {"status":"ok"}
/terms, /privacy: 200 OK
```

## 📎 다음 운영 TODO

```text
제출용 최종 시연 리허설
필요 시 스크린샷/영상 캡처
이용약관/개인정보처리방침 기관 최종 검토
운영 DB 백업/복원 운영 환경 리허설
운영 전 ENABLE_REVIEW_ADMIN=false 확인
```
