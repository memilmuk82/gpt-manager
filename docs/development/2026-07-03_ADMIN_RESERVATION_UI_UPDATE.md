# 2026-07-03 관리자/예약/안내 UI 및 수업 맥락 반영 변경 기록

## 배경

종로산업정보학교 AI컴퓨터과 1년 교육과정과 2학기 개인 프로젝트 수업 흐름을 반영하기 위해 기능과 문서를 정리했다. 학생들은 3월부터 Python, Flask, SQLite를 학습했고, 현재 Flask와 SQLite 기반 CRUD 웹사이트를 직접 구현하는 단계다. 2학기에는 SQLAlchemy를 이용해 백엔드 모델을 구성하고, 칸반보드로 개인 프로젝트를 관리하며, 프론트엔드는 생성형 AI의 도움을 받아 개선하고 백엔드 기본 뼈대는 학생들이 직접 만드는 방향으로 수업을 진행할 예정이다.

배포 흐름은 가능하면 OCI 개인 인스턴스에 올리고, 어려운 경우 학교 서버에 배포해 시연회를 진행하는 구성을 염두에 두었다.

## 주요 변경

```text
README 상단에 리뷰용 관리자 테스트 계정 안내 추가
README에 Flask - SQLite - OCI 선택 이유와 AI컴퓨터과 수업 맥락 추가
기본 앱 제목을 ChatGPT Pro 5X 공동 사용 지원 시스템으로 변경
기본 학교/기관명을 종로산업정보학교로 변경
관리자 설정/안내문구 기본값을 app/defaults.py로 분리
AppSetting 모델 추가
GuideItem 모델 추가
User 모델에 department, extension, is_auth_manager, sort_order 추가
WorkType 모델 추가 및 기본 작업유형 시드 추가
Reservation 모델에 work_type, description, safety_confirmed 추가
SQLite 기존 DB 호환 ALTER TABLE 보정 추가
실행 DB에 기본 설정, 기본 안내문구, 기본 GPT Pro 리소스, 리뷰용 관리자 계정 자동 시드 추가
템플릿 공통 context_processor로 setting_value 제공
미등록 사용자도 /guide 접근 가능하도록 승인 예외 추가
```

## 관리자 기능

```text
/admin 카드형 관리자 허브 디자인 적용
설정 관리: 앱 제목, 학교/부서명, 인증 안내, 업무게시판 안내, 로그아웃 안내, AI 활용 권장 순서, 기본 사용 시간, 장시간 사용 기준 수정
안내 문구 관리: GuideItem 분류, 제목, 정렬 순서, 표시 여부, 본문 수정 및 GPT 접속/인증번호 안내 Settings 수정
사용자 관리: 사용자 추가, 수정, 활성/비활성, 권한 변경, 인증번호 담당자 여부, 부서, 내선, 정렬 순서 관리, 인증번호 담당자 최대 2명 제한
CSV 일괄 등록: email,name,department,extension,role,active,is_auth_manager,sort_order 컬럼 검증 후 일괄 등록, 인증번호 담당자 2명 제한 검증
등록 요청 관리: pending 사용자 승인/반려 분리 표시
통계 조회: 사용자별/작업 유형별 예약 수, 예약 기준 사용 시간, 완료 기준 실제 사용 시간 조회
전체 테스트 실행: 관리자 화면에서 현재 Python pytest 또는 uv run --frozen pytest fallback으로 테스트 실행
```

## 예약/사용 신청 기능

```text
작업 유형 드롭다운을 DB WorkType active 목록 기준으로 표시하고 비어 있으면 DEFAULT_WORK_TYPES fallback
작업명과 작업 설명 입력 UI 정리
사용 전 확인 체크 항목 필수화
시작 시간 + 사용 시간으로 종료 예정 시간 자동 계산
종료 예정 시간을 직접 수정하면 사용 시간이 자동 반영
30분, 1시간, 2시간, 3시간, 직접 입력 사용 시간 지원
/reservations/conflicts API 추가
충돌 확인 버튼이 서버 API를 호출해 동시간대 예약 여부 표시
예약 생성 시 work_type, description, safety_confirmed 저장
```

## 화면 디자인

```text
공통 헤더/네비게이션을 홈, 사용 신청, 오늘 예약, 내 예약, 사용 안내, 관리자 중심으로 정리
상단 학교명과 시스템명은 유지
홈 화면에 현재 사용중, 다음 예약, 인증 안내, 빠른 이동, 오늘 예약 요약 표시
오늘 예약 화면 카드형 목록과 날짜 조회 UI 정리
내 예약 화면 카드형 목록과 상태 변경 버튼 정리
사용 안내 화면은 GuideItem 데이터 기반으로 표시
개인정보 상세, 평가 보안 상세 앵커 링크 추가
미등록 사용자 화면과 등록 요청 화면 디자인 정리
```

## 테스트 변경

```text
tests/test_reservations.py: 새 필수 예약 입력값(work_type, safety_confirmed) 반영
tests/test_app.py: 기본 앱 제목 변경 반영
tests/e2e/rc.spec.ts: 새 등록 요청/사용 신청 UI와 체크박스 흐름 반영
```

## 검증 결과

```text
python3 -m py_compile app/models/__init__.py app/__init__.py app/admin/routes.py app/reservations/routes.py app/routes/main.py app/auth/routes.py app/config.py app/defaults.py: PASS
uv run pytest: PASS, 61 passed
npm run test:e2e: PASS, 1 passed
Flask local server http://127.0.0.1:5001: PASS
주요 화면 HTTP 200 확인: /dashboard, /reservations/new, /reservations/today, /reservations, /guide, /admin, 관리자 각 section
/reservations/conflicts API: PASS, 동시간대 예약 없음 JSON 응답 확인
```

## 운영 주의

```text
리뷰용 관리자 기본 계정은 REVIEW_ADMIN_EMAIL, REVIEW_ADMIN_PASSWORD 환경변수로 변경 가능
실제 운영 전 기본 리뷰 계정 비밀번호 변경 또는 비활성화 필요
관리자 화면의 전체 테스트 실행은 서버 자원을 사용하므로 운영 중 반복 실행은 주의
Docker 이미지는 관리자 테스트 실행을 위해 dev dependency group도 설치
SQLite 호환 보정은 기존 DB에 누락 컬럼을 추가하지만 복잡한 스키마 마이그레이션 도구를 대체하지는 않음
```
