# TASK - Current Codex Work

## 현재 작업

```text
Phase 6: 관리자 대시보드 및 Google OAuth senedu.kr 제한 구현 준비
```

## 추론 수준

```text
높음
```

## 현재 상태

```text
Phase 1 기본 골격 완료
Phase 2 인증 완료
Phase 3 예약/사용 로그 완료
Phase 4 Gemini API Key 암호화 설정 완료
Phase 5 프롬프트 점검기 완료
uv run pytest: 36 passed
```

## Phase 6 목표

```text
관리자가 전체 운영 현황을 확인할 수 있게 하고, Google OAuth 로그인은 senedu.kr 계정만 허용되도록 제한한다.
```

## Phase 6 구현 범위

```text
1. 관리자 대시보드 추가
2. 전체 예약/사용 로그/프롬프트 점검 결과 조회
3. Google OAuth 로그인 라우트 추가
4. ALLOWED_GOOGLE_DOMAIN=senedu.kr 정책 적용
5. Google callback에서 email/hd claim 검증
6. senedu.kr 허용 및 외부 도메인 거부 테스트 추가
7. 필요 시 로컬 회원가입 도메인 제한 여부 결정
```

## Phase 6 제외 범위

```text
복잡한 권한 체계
Google Workspace Admin API 연동
실제 GPT 계정 로그인 통제
실사용량 자동 조회
```

## Phase 6 완료 조건

```text
uv run pytest 통과
관리자 화면 접근 제어 동작
Google OAuth senedu.kr 도메인 제한 테스트 통과
PROJECT_STATUS.md 갱신
DEVELOPMENT_LOG.md 갱신
docs/development/TEST_REPORT.md 갱신
```
