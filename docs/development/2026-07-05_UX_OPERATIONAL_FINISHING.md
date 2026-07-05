# 2026-07-05 UX and Operational Finishing

## 배경

프로젝트가 제출 가능한 완성 단계에 가까워지면서 새 대형 기능을 추가하기보다, 실제 시연과 운영 화면에서 사용자가 덜 헷갈리도록 예약 UX, 모바일 내비게이션, 관리자 CSV/백업 흐름을 마감 보완했다.

## 변경 범위

```text
예약 생성 화면
모바일 및 공통 내비게이션
관리자 CSV 내보내기
관리자 SQLite 백업
관련 테스트와 문서
```

## 예약 UX 보완

```text
AI 리소스, 시작/종료 시간, 사용 시간이 바뀌면 충돌 확인을 자동 실행
충돌 확인 중 또는 충돌 발생 시 예약 등록 버튼 비활성화
관리자 설정의 max_duration_minutes를 직접 입력 max 값과 안내 문구에 반영. 현재 기본값은 8시간(480분)
기존 충돌 확인 버튼은 수동 재확인 용도로 유지
예약 관련 장식 기호 문구를 일반 텍스트 버튼으로 정리
```

## 내비게이션과 화면 정리

```text
데스크톱 메뉴는 기존 전체 메뉴를 유지
모바일 메뉴는 홈, 사용 신청, 오늘 예약을 우선 표시하고 나머지는 더보기로 이동
상단 사용자 badge, 로그아웃 버튼, 관리자 주요 제목의 기호 아이콘을 줄여 업무 도구 톤으로 정리
```

## 관리자 CSV 내보내기 보완

```text
사용자 CSV: 검색어, 사용자, 생성일 기간 필터 지원
예약 CSV: 기간, 사용자, AI 리소스, 작업 유형, 상태, 검색어 필터 지원
사용 로그 CSV: 기간, 사용자, AI 리소스, 작업 유형, 검색어 필터 지원
관리자 화면에서 조건을 한 번 설정한 뒤 사용자/예약/사용 로그 CSV를 각각 다운로드 가능
```

## 관리자 백업 보관 정책

```text
SQLite 백업 생성 시 최근 20개만 보관
오래된 app-*.db 백업은 자동 정리
백업 목록에 생성 시각과 크기 표시
백업 생성 감사 로그에 정리 여부 기록
```

## 테스트 보강

```text
tests/test_reservations.py: max_duration_minutes가 예약 화면 input max와 안내 문구에 반영되는지 검증
tests/test_admin.py: CSV 필터가 예약/로그/사용자 CSV에 적용되는지 검증
tests/test_admin.py: 백업 보관 정책이 최신 20개만 남기는지 검증
```

## 검증

```text
python3 -m py_compile app/admin/routes.py app/reservations/routes.py: PASS
uv run pytest tests/test_reservations.py tests/test_admin.py: PASS, 30 passed
uv run pytest: PASS, 91 passed
npm run test:e2e: PASS, 1 passed
git diff --check: PASS
docker compose up -d --build: PASS, gpt-manager-web-1 Up
GET http://127.0.0.1:5000/healthz: PASS, {"status":"ok"}
```

## 의도적으로 유지한 항목

```text
관리자 생성/CSV 등록 계정의 기본 password123 흐름은 과제 사이트와 시연 편의 목적상 유지
관리자 전체 테스트 실행 기능은 과제 사이트의 검증 설명 기능으로 유지
```
