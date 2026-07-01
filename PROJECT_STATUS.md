# Project Status - GPT Share Manager vNext

## 1. 프로젝트 개요

```text
프로젝트명: gpt-share-manager-vnext
목적: 공용 AI 계정 예약·사용 기록 관리 + Gemini 기반 프롬프트 점검기
마감: 2026-07-03 오후 제출
RC1 목표: 2026-07-02
```

## 2. 현재 Phase

```text
현재 Phase: Phase 5 완료
상태: 프롬프트 점검기 구현 완료 / Phase 6 관리자 대시보드 및 Google OAuth senedu.kr 제한 착수 준비
추론 수준: 높음
```

## 3. 확정된 방향

```text
기존 GPT 공유앱의 구조 개선/재설계 방향
Flask + SQLite + Docker Compose + OCI
Gemini API는 프롬프트 점검/개선에만 제한적으로 사용
자유 채팅형 챗봇은 만들지 않음
GPT 계정 실제 사용량 자동 조회는 하지 않음
GPT 계정 ID/PW 저장하지 않음
```

## 4. 확정 기술 스택

```text
Backend: Flask
DB: SQLite ./data/app.db
ORM: SQLAlchemy
Auth: Flask-Login + Authlib Google OAuth 구조
API Key Encryption: cryptography.Fernet
Frontend: Jinja2 + Vanilla JS + Tailwind CDN
Package: uv
Test: pytest
Deploy: Docker Compose + OCI 단일 인스턴스
```

## 5. 완료된 작업

```text
아이디어 브레인스토밍
교육 생성 앱 폐기
정보화기기/IP 관리 앱 장기 과제로 분리
방과후 관리 앱 폐기
기존 GPT 공유앱 재설계 방향 채택
Gemini 경량 모델 기반 프롬프트 점검기 채택
SQLite + Docker Compose + OCI 단일 인스턴스 전략 채택
Release Freeze 원칙 확정
Phase 1 Flask 기본 골격 생성
Phase 1 Docker Compose 빌드/실행 확인
Phase 1 pytest 통과
Phase 2 User 모델 추가
Phase 2 로컬 회원가입/로그인/로그아웃 구현
Phase 2 /dashboard 로그인 보호 구현
Phase 2 인증 pytest 통과
Phase 3 AiResource/Reservation/UsageLog 모델 구현
Phase 3 예약 생성/취소/완료 및 충돌 검증 구현
Phase 3 사용 로그 생성/조회 구현
Phase 3 예약/로그 pytest 통과
Phase 4 UserApiKey 모델 구현
Phase 4 Gemini API Key 암호화 저장/삭제/마스킹/복호화 확인 구현
Phase 4 API Key pytest 통과
Phase 5 PromptReview 모델 구현
Phase 5 프롬프트 점검 입력/저장/조회 구현
Phase 5 Gemini 호출 service 및 mock 테스트 구현
Phase 5 프롬프트 점검 pytest 통과
```

## 6. Phase 3 결과

```text
AiResource 모델 추가
Reservation 모델 및 reserved/cancelled/completed 상태 추가
UsageLog 모델 추가
/reservations 목록/생성/취소/완료 구현
예약 시간 파싱 및 충돌 검증 service 분리
취소된 예약은 충돌 대상에서 제외
/logs 목록/생성/상세 조회 구현
사용 로그는 예약 또는 AI 리소스에 연결 가능
사용자별 예약/로그 접근 제한 구현
```

## 7. Phase 4 결과

```text
cryptography 의존성 추가
UserApiKey 모델 추가
Fernet 기반 암호화/복호화 service 추가
APP_ENCRYPTION_KEY가 없을 때 개발용 키를 SECRET_KEY에서 파생
/settings/api-key 화면 추가
Gemini API Key 등록/교체/삭제 구현
저장 상태는 마지막 4자리만 표시
저장된 키 복호화 확인 기능 추가
```

검증 결과:

```text
uv run pytest: 30 passed
```

주의:

```text
운영 배포 전 APP_ENCRYPTION_KEY는 Fernet.generate_key() 형식의 안정적인 값으로 설정해야 함
현재 개발 환경에서 127.0.0.1:5000은 별도 flask 프로세스가 점유 중일 수 있음
Compose 실행 자체는 5000 포트가 비어 있을 때 정상 실행 가능
CSRF 보호는 후속 보완 필요
```

## 8. Phase 5 결과

```text
PromptReview 모델 추가
프롬프트 점검 목록/입력/상세 화면 추가
점검 프롬프트 조립 service 추가
Gemini REST 호출 service 추가
테스트에서는 Gemini 호출을 mock 처리
저장된 사용자 Gemini API Key를 복호화해 호출에 사용
입력 길이 제한 적용
사용자별 점검 결과 접근 제한 구현
GEMINI_MODEL 기본값을 gemini-3.5-flash로 갱신
```

검증 결과:

```text
uv run pytest: 36 passed
```

## 9. 진행 예정

### Phase 6

```text
관리자 대시보드
전체 예약/로그/프롬프트 점검 결과 확인
Google OAuth 로그인 구현
senedu.kr 계정만 Google 로그인 가능하도록 제한
로컬 회원가입 도메인 제한 여부 최종 결정
가능하면 운영 보고서 생성
```

### Phase 7

```text
OCI 배포
README
최종 테스트
제출
```

## 10. 제외 기능

```text
자유 채팅형 챗봇
수업안/평가계획 생성기
교육과정 파일 분석
학생 개인정보
GPT 실제 사용량 자동 조회
GPT 로그인 통제
PostgreSQL
OCI Managed DB
네이버웍스 API
방과후 관리
정보화기기/IP 관리
```

## 11. 현재 위험 요소

```text
OAuth Redirect URI 설정 지연 가능성
Google OAuth senedu.kr 도메인 제한 구현/검증 필요
Gemini 모델명/SDK 확인 필요
OCI 배포 시간 부족 가능성
UI 완성도 부족 가능성
CSRF 보호는 후속 보완 필요
```

대응:

```text
로컬 로그인과 Docker 이미지 실행 가능성 확보
Gemini 호출부를 service로 격리
모델명은 환경변수로 관리
상태 변경 요청은 POST로 제한
7월 2일 RC1 이후 신규 기능 금지
```
