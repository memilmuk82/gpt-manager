# Google OAuth Redirect URI 설정

Phase 7 제출 준비용 Google OAuth 설정 절차입니다.

## 1. 앱에서 사용하는 callback 경로

이 프로젝트의 Google OAuth callback route는 고정입니다.

```text
/auth/google/callback
```

따라서 Redirect URI는 접속 주소와 위 경로를 합친 값입니다.

로컬 개발:

```text
http://localhost:5000/auth/google/callback
```

OCI/운영 예시:

```text
https://<your-domain>/auth/google/callback
http://<OCI_PUBLIC_IP>/auth/google/callback
http://<OCI_PUBLIC_IP>:5000/auth/google/callback
```

리버스 프록시 없이 현재 `compose.yaml`의 `5000:5000` 포트를 직접 노출해 시연하면 `:5000`이 포함된 Redirect URI를 Google Cloud Console과 `.env`에 모두 등록해야 합니다. Google OAuth 운영 검증은 가능하면 HTTPS 도메인으로 진행합니다. IP와 HTTP만 사용하는 구성은 Google 정책이나 브라우저 보안 조건에 따라 제한될 수 있습니다.

## 2. Google Cloud Console 설정

```text
1. Google Cloud Console 접속
2. APIs & Services > Credentials 이동
3. OAuth 2.0 Client IDs에서 Web application 클라이언트 생성 또는 선택
4. Authorized redirect URIs에 실제 Redirect URI 추가
5. Client ID와 Client Secret을 복사
6. 프로젝트 .env에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI 입력
7. 앱 재시작
```

`.env` 예시:

```env
GOOGLE_CLIENT_ID=<client-id>
GOOGLE_CLIENT_SECRET=<client-secret>
GOOGLE_REDIRECT_URI=https://<your-domain>/auth/google/callback
ALLOWED_GOOGLE_DOMAIN=senedu.kr
```

## 3. 승인 정책

```text
senedu.kr Google 계정: 자동 승인
senedu.kr 외 Google 계정: pending 상태로 등록 후 관리자 승인 필요
email_verified가 false인 Google 계정: 로그인 거부
```

관리자는 `ADMIN_EMAILS`에 포함된 이메일로 가입하거나 로그인한 뒤 `/admin/users`에서 pending 사용자를 승인합니다.

## 4. 점검 방법

```text
1. 앱 실행
2. /auth/login 접속
3. Google로 로그인 클릭
4. Google 동의 화면으로 이동하는지 확인
5. callback 후 dashboard 또는 승인 대기 화면으로 이동하는지 확인
6. 외부 계정은 /admin/users에서 pending으로 보이는지 확인
```

오류가 나면 아래 값을 먼저 대조합니다.

```text
Google Cloud Console Authorized redirect URI
.env GOOGLE_REDIRECT_URI
브라우저에서 실제 접속한 scheme/host/port
리버스 프록시 미사용 시 :5000 포함 여부
컨테이너 재시작 여부
```
