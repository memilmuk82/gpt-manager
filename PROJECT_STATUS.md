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
현재 Phase: Phase 2 완료
상태: 로컬 회원가입/로그인/로그아웃 및 보호된 대시보드 구현 완료 / Phase 3 예약·로그 착수 준비
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
Auth: Flask-Login + Authlib Google OAuth
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
```

## 6. Phase 2 결과

```text
Flask-Login 의존성 추가
LoginManager 초기화
User 모델 추가
Werkzeug password hash 적용
/auth/register GET/POST 구현
/auth/login GET/POST 구현
/auth/logout POST 구현
/dashboard 로그인 보호 적용
인증 템플릿 작성
테스트 DB fixture 작성
인증/비밀번호/설정 테스트 작성
SQLite 상대 경로를 ./data 기준 절대 경로로 정규화
```

검증 결과:

```text
uv run pytest: 14 passed
리팩토링 검토 후 uv run pytest 재실행: 14 passed
docker compose up --build -d: image build success, host 5000 port already in use
docker run -p 5001:5000 gpt-manager-web:latest: success
curl http://localhost:5001/healthz: 200 {"status":"ok"}
curl http://localhost:5001/: 200
curl http://localhost:5001/dashboard: 302 /auth/login?next=%2Fdashboard
```

주의:

```text
현재 개발 환경에서 127.0.0.1:5000은 별도 flask 프로세스가 점유 중임
Compose 실행 자체는 5000 포트가 비어 있을 때 정상 실행 가능
```

## 7. 진행 예정

### Phase 3

```text
AI 리소스
예약 CRUD
예약 충돌 검증
사용 로그 CRUD
```

### Phase 4

```text
Gemini API Key 설정
암호화 저장
삭제/마스킹
```

### Phase 5

```text
프롬프트 점검기
Gemini 호출
결과 저장
```

### Phase 6

```text
관리자 대시보드
가능하면 운영 보고서 생성
```

### Phase 7

```text
OCI 배포
README
최종 테스트
제출
```

## 8. 제외 기능

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

## 9. 현재 위험 요소

```text
OAuth Redirect URI 설정 지연 가능성
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
