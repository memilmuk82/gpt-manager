# Google OAuth Redirect URI 설정

## 관련 문서

[README](../../README.md) · [OCI 서버 설정](OCI_DEV_SERVER_SETUP.md) · [보안 결정](../decisions/SECURITY_DECISIONS.md)


이 프로젝트의 Google OAuth callback route는 고정입니다.

```text
/auth/google/callback
```

## 1. 현재 운영 값

```text
운영 도메인: https://dev-gpt.memilmuk82.com
운영 Redirect URI: https://dev-gpt.memilmuk82.com/auth/google/callback
```

Google Cloud Console의 Authorized redirect URI와 `.env`의 `GOOGLE_REDIRECT_URI`는 위 값과 일치해야 합니다.

## 2. 로컬 개발 값

```text
http://localhost:5000/auth/google/callback
```

## 3. Google Cloud Console 설정

```text
1. Google Cloud Console 접속
2. APIs & Services > Credentials 이동
3. OAuth 2.0 Client IDs에서 Web application 클라이언트 생성 또는 선택
4. Authorized redirect URIs에 실제 Redirect URI 추가
5. Client ID와 Client Secret 복사
6. 프로젝트 .env에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI 입력
7. docker compose down && docker compose up -d --build 또는 컨테이너 재시작
```

`.env` 예시:

```env
GOOGLE_CLIENT_ID=<client-id>
GOOGLE_CLIENT_SECRET=<client-secret>
GOOGLE_REDIRECT_URI=https://dev-gpt.memilmuk82.com/auth/google/callback
ALLOWED_GOOGLE_DOMAIN=
```

## 4. 승인 정책

```text
Google 계정: 이메일 도메인과 관계없이 자동 승인
관리자가 필요 시 사용자 관리에서 비활성화 가능
email_verified가 false인 Google 계정: 로그인 거부
ADMIN_EMAILS 포함 이메일: admin role
ASSISTANT_ADMIN_EMAILS 포함 이메일: assistant_admin role
```

관리자 또는 보조관리자는 `/admin/users`에서 pending 사용자를 승인합니다.

## 5. 점검 방법

```text
1. https://dev-gpt.memilmuk82.com/auth/login 접속
2. Google 로그인 클릭
3. Google 동의 화면으로 이동하는지 확인
4. callback 후 /dashboard 또는 /auth/pending으로 이동하는지 확인
5. 외부 계정은 /admin/users에서 pending으로 보이는지 확인
```

오류가 나면 아래 값을 대조합니다.

```text
Google Cloud Console Authorized redirect URI
.env GOOGLE_REDIRECT_URI
브라우저에서 실제 접속한 scheme/host/port
컨테이너 재시작 여부
Nginx HTTPS proxy 상태
```
