# Release Checklist

## 1. RC 기준

```text
RC 목표일: 2026-07-02
현재 상태: RC 운영 검증 완료
운영 도메인: https://dev-gpt.memilmuk82.com
pytest: 50 passed
Docker Compose rebuild: PASS
```

## 2. 완료 조건

```text
[x] 로컬 Docker Compose 실행 성공
[x] OCI Docker Compose 실행 성공
[x] /healthz 응답 확인
[x] 로컬 로그인 확인
[x] Google OAuth Redirect URI 운영 도메인 기준 설정 확인
[x] Gemini API Key 등록/삭제 확인
[x] 프롬프트 점검 테스트 mock 통과
[x] 예약 생성/취소/완료 확인
[x] 오늘 예약 화면 확인
[x] 사용 로그 작성 확인
[x] 관리자 대시보드 확인
[x] 보조관리자 관리자 화면 접근 확인
[x] pytest 통과
[x] README 실행 방법 확인
[x] .env.example 최신화
[x] 도메인 HTTPS 응답 확인
```

## 3. 2026-07-03 Freeze 원칙

허용:

```text
최종 테스트
README/문서 오타 수정
시연 순서 정리
스크린샷 추가
제출 파일 정리
운영 DB 백업
```

금지:

```text
신규 기능 추가
리팩토링
DB 구조 변경
인증 정책 변경
Gemini 호출 구조 변경
UI 대규모 변경
```

## 4. 최종 테스트 시나리오

```text
1. 새 브라우저/시크릿 창에서 https://dev-gpt.memilmuk82.com 접속
2. 로컬 로그인 또는 Google OAuth 로그인
3. 홈 화면 확인
4. 사용 신청으로 예약 생성
5. 예약 충돌 테스트
6. 오늘 예약 화면 확인
7. 사용 로그 작성
8. Gemini API Key 등록
9. 프롬프트 점검 실행
10. 결과 확인
11. 로그아웃
12. 관리자 또는 보조관리자 계정 로그인
13. 사용자 승인 화면 확인
14. uv run pytest 실행
15. docker compose down/up 후 데이터 유지 확인
```

## 5. 제출 설명 핵심 문장

```text
이 프로젝트는 공용 생성형 AI 계정 사용을 직접 통제하는 앱이 아니라, 공용 AI 사용 예약·기록·프롬프트 개선을 지원하는 운영 관리 앱입니다. Gemini API는 자유 채팅이 아니라 프롬프트 점검 기능에 제한적으로 사용해 비용과 보안 위험을 줄였습니다.
```
