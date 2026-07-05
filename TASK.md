# 🧭 TASK - Current Codex Work

## ✅ 현재 작업

```text
UI 디자인 시스템 실제 적용 완료
개인 프로필 화면과 관리자 테스트 실패 힌트 적용 완료
프로젝트 Markdown 문서 구조와 최신 검증 기준 반영 중
```

## 📌 현재 상태

```text
기준 브랜치: master
운영 도메인: https://dev-gpt.memilmuk82.com
최근 검증 기준: 2026-07-05
uv run pytest: 95 passed
npm run test:e2e: 2 passed
Docker Compose 재빌드: PASS, gpt-manager-web-1 Up, /healthz 200
```

## 📚 문서 역할

```text
README.md: 프로젝트 포털, 시연 계정, 주요 기능, 실행 가이드
PROJECT_STATUS.md: 현재 구현 상태와 검증 결과 요약
TASK.md: 현재 작업 메모와 다음 운영 TODO
SYSTEM_DESIGN.md: 시스템 구조, 데이터/라우트 설계, 보안/배포 기준
PROJECT_INSTRUCTIONS.md: 개발 원칙과 Codex 작업 규칙
DEVELOPMENT_LOG.md: 시간순 변경 이력
TEST_REPORT.md: 테스트 이력과 검증 명령
EDUCATION.md: 교육 철학과 기술 선정 이유
```

## 🧩 최근 정리 내용

```text
예약 생성 화면 자동 충돌 확인과 max_duration_minutes 반영
모바일 내비게이션을 핵심 메뉴와 더보기 구조로 정리
관리자 CSV 내보내기에 기간/사용자/리소스/작업유형/상태/검색어 필터 추가
관리자 SQLite 백업은 최근 20개 보관 정책 적용
관리자/상단 화면의 장식 기호를 줄여 업무 도구 톤으로 정리
Landing/Auth/Dashboard/Reservations/Logs/Prompts/Admin Test Result에 light operational SaaS UI 적용
/profile 개인 프로필 화면 추가 및 헤더 사용자 badge 링크 변경
관리자 Test Result 실패 원인 요약/해결 힌트 추가
docs/ui 3개 문서와 README, PROJECT_STATUS, SYSTEM_DESIGN, RELEASE_CHECKLIST, TEST_REPORT, DEVELOPMENT_LOG 최신화
```

## 🧪 최근 검증 기준

```text
python3 -m py_compile app/admin/routes.py app/reservations/routes.py: PASS
uv run pytest: PASS, 95 passed
npm run test:e2e: PASS, 2 passed
git diff --check: PASS
Playwright Profile/Admin/mobile overflow check: PASS
```

## 📎 다음 운영 TODO

```text
제출용 최종 시연 리허설
필요 시 스크린샷/영상 캡처
이용약관/개인정보처리방침 기관 최종 검토
운영 DB 복원 절차 리허설
제출/리뷰 종료 후 ENABLE_REVIEW_ADMIN=false 확인
```
