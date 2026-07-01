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
현재 Phase: Release Candidate 검증 진행 중
상태: pytest PASS, Playwright E2E PASS, OCI 배포 PASS, 운영 Health/로컬 로그인/CRUD/세션 유지 PASS / Google OAuth 운영 설정 미완료로 Release Freeze 보류
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
DB: SQLite ./instance/app.db
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
Phase 6 관리자 대시보드 구현
Phase 6 사용자 승인/정지 관리 구현
Phase 6 senedu.kr 자동 승인 + 외부 계정 관리자 승인제 구현
Phase 6 Google OAuth 기본 로그인 흐름 구현
Phase 6 관리자/OAuth/승인제 pytest 통과
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

## 9. Phase 6 결과

```text
관리자 대시보드 추가
전체 사용자/예약/사용 로그/프롬프트 점검 수 요약 추가
사용자 승인 관리 화면 추가
관리자만 /admin 접근 가능
senedu.kr 계정은 자동 승인
외부 Google 계정과 외부 로컬 이메일 계정은 pending 상태로 등록
관리자가 pending 계정을 승인 가능
관리자가 사용자 계정을 정지 가능
Google OAuth login/callback 기본 흐름 추가
Google callback에서 검증된 email/sub 확인
Google OAuth 테스트는 userinfo fetch를 mock 처리
```

검증 결과:

```text
uv run pytest: 46 passed
```

## 10. 진행 예정

### Phase 7

```text
완료: README 최신화
완료: .env.example 최종 확인 및 주석 보강
완료: Google OAuth Redirect URI 설정 절차 문서화
완료: Docker Compose 로컬 빌드/실행/healthz 확인
완료: uv run pytest 최종 통과 확인
완료: OCI 실제 서버 배포 및 운영 기본 흐름 검증
남음: Google OAuth 운영 Redirect URI 수동 확인
남음: 제출용 최종 시연 리허설
```

## 11. 제외 기능

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

## 12. 현재 위험 요소

```text
OAuth Redirect URI 설정 지연 가능성
Google OAuth 운영 Redirect URI와 실제 Google Cloud 설정 확인 필요
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

## 13. Phase 7 진행 결과

```text
README를 Phase 7 기준으로 최신화
.env.example에 Google OAuth/운영 설정 주석 추가
Google OAuth Redirect URI 설정 문서 추가
OCI Dev Server 문서의 compose/env 예시를 현재 앱 설정과 일치하도록 보완
uv run pytest 최종 통과
Docker Compose build/up/healthz/down 로컬 검증 완료
```

검증 결과:

```text
uv run pytest: 47 passed
docker compose build: success
docker compose up -d: success
curl /healthz: 200 {"status":"ok"}
docker compose down: success
```

남은 작업:

```text
OCI 실제 서버에 Google OAuth 운영값 설정
Google Cloud Console에 운영 Redirect URI 등록
OCI URL에서 Google OAuth 로그인 수동 확인
제출 전 최종 시연 리허설
```

## 14. Release Candidate 검증 결과

```text
pytest: PASS, 47 passed
Playwright E2E: PASS, 1 passed
Docker Build: PASS
OCI 배포: PASS
운영 Health Check: PASS
OAuth 운영 검증: BLOCKED, GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET 미설정
로컬 로그인 운영 검증: PASS
CRUD 운영 검증: PASS
세션 유지 운영 검증: PASS
Release Freeze: 보류, Google OAuth 운영 검증 완료 필요
```

Playwright 검증 범위:

```text
메인 페이지 접속
회원가입/로컬 로그인
예약 목록 조회
예약 추가
예약 상태 변경
API Key 등록/교체/삭제
새로고침 후 데이터 유지
```

운영 SQLite 스키마 호환성 수정:

```text
기존 운영 DB의 user 테이블에 auth_provider/approval_status 컬럼이 없어 회원가입 500 발생
앱 시작 시 SQLite user 테이블 누락 컬럼을 보정하도록 수정
pytest 47 passed
Playwright E2E 1 passed
```

## 15. OCI 운영 검증 결과

```text
git pull: PASS
docker compose build: PASS
docker compose up -d: PASS
/healthz: PASS, 200 {"status":"ok"}
로컬 로그인: PASS
예약 목록/추가/완료: PASS
Gemini API Key 등록/교체/삭제: PASS
세션 유지: PASS
Google OAuth: BLOCKED, 운영 .env에 GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET 미설정
```

Release Freeze:

```text
보류
Google OAuth 운영 설정과 수동 로그인 검증 완료 후 전환
```

## 16. SQLite instance 영속성 검증

```text
SQLite DB 컨테이너 없음
DB 경로: /app/instance/app.db
Host bind mount: ./instance:/app/instance
운영 DATABASE_URL: sqlite:///instance/app.db
compose down/up 후 데이터 유지 확인
users: 3 -> 3
reservations: 2 -> 2
uv run pytest: 47 passed
```

## RC Deployment

- OCI Ubuntu 배포 완료
- Docker Compose 운영
- Gunicorn 적용
- Nginx Reverse Proxy 적용
- Cloudflare DNS 연결
- dev-gpt.memilmuk82.com 연결 완료
- iptables HTTP/HTTPS 허용
- Release Candidate 환경 구축 완료