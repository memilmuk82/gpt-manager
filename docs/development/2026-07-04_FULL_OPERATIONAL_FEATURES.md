# 2026-07-04 전체 운영 편의 기능 보완 기록

## 목적

리뷰와 실제 운영 점검에서 바로 확인할 수 있도록 남은 편의 기능을 한 번에 보완했다. 핵심 방향은 관리자가 데이터와 백업을 직접 확인할 수 있게 하고, 일반 사용자는 예약 후 사용 로그를 빠뜨리지 않게 하는 것이다.

## 구현 기능

```text
관리자 DB 백업 생성 및 다운로드
관리자 사용자 CSV 내보내기
관리자 예약 CSV 내보내기
관리자 사용 로그 CSV 내보내기
홈 KPI 카드 추가
완료 예약의 미작성 사용 로그 알림
월간 예약 캘린더
운영 공지 배너 설정값 및 표시
프롬프트 정리 템플릿 선택과 자동 채우기
예약별 사용 규칙 동의 버전 기록
BYOK 프롬프트 정리 제한을 최근 24시간 기준으로 안정화
```

## 변경 파일

```text
app/admin/routes.py
app/defaults.py
app/models/__init__.py
app/prompts/routes.py
app/reservations/routes.py
app/routes/main.py
app/templates/admin/dashboard.html
app/templates/base.html
app/templates/dashboard.html
app/templates/prompts/new.html
app/templates/reservations/calendar.html
app/templates/reservations/new.html
tests/test_admin.py
tests/test_app.py
tests/test_prompt_reviews.py
tests/test_reservations.py
README.md
PROJECT_STATUS.md
```

## 검증

```text
uv run pytest: PASS, 88 passed
```

Docker Compose 리빌드, E2E, 컨테이너 health check, 로컬-원격 저장소 대조는 최종 커밋 전후로 별도 실행한다.
