# 2026-07-03 운영 보안 및 사용 흐름 보완

## 변경 요약

```text
CSRF 토큰 기반 POST 요청 보호 추가
Google OAuth 도메인 콜백 검증 및 자동 관리자 승격 제거
리뷰용 관리자 계정 자동 생성 opt-in 전환
완료 예약의 사용 로그 작성 유도 및 예약 자동 선택
사용자별 일일 Gemini 프롬프트 점검 호출 제한 적용
SQLite 백업/복원 스크립트 추가
README/PROJECT_STATUS 문서 갱신
```

## 운영 설정

```text
WTF_CSRF_ENABLED=true
ENABLE_REVIEW_ADMIN=false
ALLOWED_GOOGLE_DOMAIN=<필요 시 Google Workspace 도메인>
MAX_DAILY_AI_CALLS_PER_USER=50
```

리뷰용 임시 관리자 계정은 제출 또는 외부 검토가 필요한 경우에만 `ENABLE_REVIEW_ADMIN=true`와 강한 `REVIEW_ADMIN_PASSWORD`를 같이 지정한다.

## DB 백업

```bash
bash scripts/backup_sqlite.sh instance/app.db backups
```

## DB 복원

```bash
docker compose down
bash scripts/restore_sqlite.sh backups/app-YYYYmmdd-HHMMSS.db instance/app.db
docker compose up -d --build
```
