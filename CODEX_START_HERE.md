# 🤖 Codex Start Here - 생성형 AI 계정 공동 사용 지원 시스템

## 🧭 0. 프로젝트 한 줄 정의

`생성형 AI 계정 공동 사용 지원 시스템`은 학교 공용 생성형 AI 계정 사용을 예약·기록하고, Gemini 경량 모델로 사용자가 작성한 프롬프트를 점검·개선하는 Flask 기반 업무 시스템입니다.

이 프로젝트는 교육용 예제이면서 실제 학교 운영 문제를 해결하기 위한 기준 프로젝트입니다. Codex와 ChatGPT는 요구사항 정리, 구현 보조, 코드 리뷰, 테스트 점검, 문서 작성에 협업 도구로 활용합니다.

## 📚 1. Codex가 먼저 읽을 문서 순서

파일 수정 전 아래 순서로 현재 맥락을 확인합니다.

1. 🧭 [README.md](README.md)
2. ✅ [PROJECT_STATUS.md](PROJECT_STATUS.md)
3. 🧾 [TASK.md](TASK.md)
4. 🏗️ [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md)
5. 🧑‍🏫 [PROJECT_INSTRUCTIONS.md](PROJECT_INSTRUCTIONS.md)
6. 📝 [docs/development/DEVELOPMENT_LOG.md](docs/development/DEVELOPMENT_LOG.md)

선택적으로 읽을 문서:

```text
docs/EDUCATION.md
docs/architecture/REPOSITORY_STRUCTURE.md
docs/decisions/TECH_STACK_DECISIONS.md
docs/decisions/SECURITY_DECISIONS.md
docs/development/TEST_REPORT.md
docs/deployment/OCI_DEV_SERVER_SETUP.md
```

## ✅ 2. 현재 최우선 목표

```text
운영 기능 구현 완료 상태 유지
문서와 실제 코드의 불일치 제거
중복 설명은 README에서 줄이고 전문 문서로 분리
기능 변경은 사용자 요청이 있을 때만 수행
변경 후 테스트 또는 문서 검증 결과를 명확히 남김
```

## 🛠️ 3. 작업 시작 전 확인 항목

```text
1. 현재 사용자 요청
2. 변경 대상 파일
3. 실제 코드와 문서의 충돌 여부
4. 테스트 또는 검증 방법
5. 커밋/푸시 필요 여부
```

단순 문서 최신화와 검증은 요청 범위 안에서 진행합니다. 인증, 예약, 권한, DB 스키마, 배포 구조 변경은 사용자 요청 없이 임의로 변경하지 않습니다.

## 🚫 4. 이번 프로젝트에서 절대 하지 말 것

```text
GPT 계정 ID/PW 저장
GPT 실제 사용량 자동 조회 시도
GPT 로그인 제어/강제 로그아웃 기능 구현
자유 채팅형 AI 챗봇 구현
학생 개인정보 입력 기능 구현
PDF/HWP/HWPX 업로드·분석 기능 구현
PostgreSQL/OCI Managed DB 선행 도입
React/Vue/Svelte 임의 도입
기능 완성 없이 구조만 과도하게 확장
테스트 또는 문서 검증 없이 완료 보고
```
