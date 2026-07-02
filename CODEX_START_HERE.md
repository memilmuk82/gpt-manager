# Codex Start Here - 생성형 AI 계정 공동 사용 지원 시스템

## 0. 프로젝트 한 줄 정의

`생성형 AI 계정 공동 사용 지원 시스템`는 공용 AI 계정 사용을 예약·기록하고, Gemini 경량 모델을 이용해 사용자가 작성한 프롬프트를 점검·개선하는 Flask 기반 웹앱이다.

이 프로젝트는 새 교육 생성기를 만드는 것이 아니다. 기존 GPT 공유앱의 운영 철학을 Flask + Docker + OCI 구조로 재설계하고, Gemini API는 필수 기능인 "프롬프트 점검기"에 사용한다. "운영 보고서 생성"은 시간이 남을 때만 구현하는 선택 기능이다.

## 1. Codex가 먼저 읽을 문서 순서

아래 순서로 읽고, 파일 수정 전에 구현 계획을 보고한다.

```text
1. PROJECT_INSTRUCTIONS.md
2. PRD.md
3. SYSTEM_DESIGN.md
4. DEVELOPMENT_PLAN.md
5. TASK.md
6. PROJECT_STATUS.md
```

선택적으로 읽을 문서:

```text
docs/architecture/REPOSITORY_STRUCTURE.md
docs/decisions/TECH_STACK_DECISIONS.md
docs/decisions/SECURITY_DECISIONS.md
docs/development/TEST_REPORT.md
docs/deployment/OCI_DEV_SERVER_SETUP.md
```

## 2. 현재 최우선 목표

```text
2026-07-02까지 OCI에서 실행 가능한 RC1 완성
2026-07-03에는 기능 추가·리팩토링 없이 최종 테스트와 제출만 수행
```

## 3. 첫 작업 지시

Codex는 지금 바로 코드를 생성하지 말고, 먼저 다음을 보고한다.

```text
1. 이해한 프로젝트 목표
2. MVP 기능 범위
3. 생성할 파일/폴더 목록
4. Phase 1에서 실제로 수행할 작업
5. 예상 위험 요소
6. 테스트 방법
7. 사용자 승인이 필요한 항목
```

사용자가 `Phase 1 진행` 또는 이에 준하는 명시적 승인을 하면 파일을 생성한다.

## 4. 이번 프로젝트에서 절대 하지 말 것

```text
- GPT 계정 ID/PW 저장
- GPT 실제 사용량 자동 조회 시도
- GPT 로그인 제어/강제 로그아웃 기능 구현
- 자유 채팅형 AI 챗봇 구현
- 학생 개인정보 입력 기능 구현
- PDF/HWP/HWPX 업로드·분석 기능 구현
- PostgreSQL/OCI Managed DB 선행 도입
- React/Vue/Svelte 임의 도입
- 기능 완성 없이 구조만 과도하게 확장
- 테스트 없이 다음 Phase 진행
- 2026-07-02 RC1 이후 신규 기능 추가
```
