# OCI Dev Server 설정 절차

작성 목적: Codex와 연결해 사용할 **항상 켜져 있는 OCI 개발 서버**를 빠르게 구축하기 위함.

현재 목표는 완벽한 운영 서버가 아니라, **SSH 접속 + Docker Compose + Git + Codex Remote 연결**이 가능한 최소 개발 환경을 만드는 것이다.

---

## 0. 이번 작업의 목표

```text
목표:
- OCI Ubuntu 서버 생성
- SSH 접속 가능
- Docker / Docker Compose 설치
- Git 사용 가능
- Codex에서 SSH 원격 프로젝트로 연결 가능

이번에 하지 않는 것:
- 도메인 연결
- HTTPS 설정
- Nginx / Caddy 설정
- PostgreSQL 설치
- 백업 자동화
- 모니터링
- 로컬 LLM 설치
```

---

## 1. OCI 인스턴스 생성

OCI 콘솔에서 Compute Instance를 생성한다.

권장 설정:

```text
OS: Ubuntu 24.04 LTS
Shape: Ampere A1 가능하면 2 OCPU / 12GB 이상
Boot Volume: 100GB 이상 권장
접속 방식: SSH Key
사용자명: ubuntu
```

주의:

```text
- SSH private key는 절대 공유하지 않는다.
- public key만 OCI 인스턴스 생성 화면에 등록한다.
- 무료 한도 또는 PAYG 사용량을 확인한다.
```

---

## 2. OCI 네트워크 보안 규칙

VCN의 Security List 또는 NSG에서 다음 인바운드 포트를 허용한다.

```text
22   SSH
80   HTTP
443  HTTPS
```

개발 테스트용 Flask 포트 `5000`은 가급적 외부에 열지 않는다.
필요하면 임시로만 열고, 테스트 후 닫는다.

---

## 3. 로컬 PC SSH 설정

로컬 PC의 SSH 설정 파일을 편집한다.

Windows 기준 예시:

```text
C:\Users\<사용자명>\.ssh\config
```

WSL 기준 예시:

```text
~/.ssh/config
```

예시:

```sshconfig
Host oci-dev
  HostName <OCI_PUBLIC_IP>
  User ubuntu
  IdentityFile ~/.ssh/<your_oci_private_key>
```

접속 확인:

```bash
ssh oci-dev
```

정상 접속되면 다음 단계로 이동한다.

---

## 4. 서버 기본 패키지 설치

OCI 서버에 SSH 접속 후 실행한다.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl unzip ca-certificates gnupg ufw htop tree
```

시간대 설정:

```bash
sudo timedatectl set-timezone Asia/Seoul
timedatectl
```

---

## 5. Ubuntu 방화벽 설정

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
```

주의:

```text
OCI 네트워크 보안 규칙과 Ubuntu ufw는 별개다.
둘 다 허용되어야 외부 접속이 가능하다.
```

---

## 6. Docker 설치

Docker 공식 설치 스크립트를 사용한다.

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

설치 확인:

```bash
docker --version
docker compose version
```

테스트:

```bash
docker run hello-world
```

---

## 7. 프로젝트 작업 폴더 생성

```bash
mkdir -p ~/workspace
cd ~/workspace
```

권장 구조:

```text
~/workspace/
├── gpt-share-manager-next/
├── eduplan-ai/
└── sandbox/
```

현재 제출 프로젝트는 하나의 폴더에서만 작업한다.

---

## 8. Git 기본 설정

```bash
git config --global user.name "<Your Name>"
git config --global user.email "<your-email@example.com>"
git config --global init.defaultBranch main
```

확인:

```bash
git config --global --list
```

---

## 9. GitHub SSH 키 설정 선택

OCI 서버에서 GitHub에 SSH로 push/pull하려면 서버용 SSH 키를 만든다.

```bash
ssh-keygen -t ed25519 -C "oci-dev" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

출력된 public key를 GitHub SSH Keys에 등록한다.

접속 확인:

```bash
ssh -T git@github.com
```

GitHub HTTPS 방식으로만 clone할 예정이면 이 단계는 생략 가능하다.

---

## 10. Codex Remote SSH 연결

로컬 PC에서 먼저 아래 명령이 성공해야 한다.

```bash
ssh oci-dev
```

성공하면 Codex에서 SSH 원격 프로젝트를 열 때 `oci-dev` 호스트를 선택한다.

Codex에서 열 프로젝트 경로 예시:

```text
/home/ubuntu/workspace/gpt-share-manager-next
```

주의:

```text
- 운영 서버 파일을 바로 수정하는 구조가 될 수 있으므로, 프로젝트별 Git commit을 자주 남긴다.
- Codex가 제안한 변경은 테스트 전 배포하지 않는다.
- .env, SSH key, API key는 Git에 올리지 않는다.
```

---

## 11. Python / uv 설치 선택

Docker 기반 개발이면 Python을 서버에 직접 설치하지 않아도 된다.
다만 간단한 스크립트 실행을 위해 uv를 설치해도 좋다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

이번 제출용 프로젝트는 Docker Compose 실행을 우선한다.

---

## 12. Docker Compose 프로젝트 실행 예시

프로젝트 폴더에서 실행한다.

```bash
cd ~/workspace/<project-name>
docker compose up -d --build
docker compose ps
docker compose logs -f
```

중지:

```bash
docker compose down
```

DB 파일을 SQLite로 사용할 경우 `./instance` 디렉터리를 반드시 볼륨 마운트한다.

현재 프로젝트의 `compose.yaml` 기준 예시:

```yaml
services:
  web:
    build: .
    ports:
      - "127.0.0.1:5000:5000"
    env_file:
      - .env
    volumes:
      - ./instance:/app/instance
```

외부 공개 시연에서 80/443 리버스 프록시를 붙이지 않는다면, OCI Security List/NSG와 Ubuntu ufw에서 사용할 포트를 명시적으로 허용해야 한다. 개발 테스트용 5000 포트는 임시로만 열고 테스트 후 닫는다.

### 시연용 AI 리소스 준비

fresh DB에서는 예약에 사용할 AI 리소스가 자동 생성되지 않는다. 앱 실행 후 아래 명령으로 최소 1개의 리소스를 추가한다.

```bash
docker compose exec web python -c "from app import create_app; from app.extensions import db; from app.models import AiResource; app=create_app(); ctx=app.app_context(); ctx.push(); AiResource.query.filter_by(name='학교 공용 생성형 AI 계정 A').first() or db.session.add(AiResource(name='학교 공용 생성형 AI 계정 A', provider='OpenAI', description='Shared AI resource')); db.session.commit(); ctx.pop()"
```


---

## 13. .env 관리 원칙

`.env` 파일은 Git에 올리지 않는다.

필수 예시:

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-secret>
DATABASE_URL=sqlite:///instance/app.db
APP_TITLE=생성형 AI 계정 공동 사용 지원 시스템
ORGANIZATION_NAME=학교
APP_ENCRYPTION_KEY=<fernet-key>
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://<your-domain>/auth/google/callback
ALLOWED_GOOGLE_DOMAIN=senedu.kr
ADMIN_EMAILS=admin@senedu.kr
ASSISTANT_ADMIN_EMAILS=
GEMINI_MODEL=gemini-3.5-flash
GEMINI_MAX_INPUT_CHARS=3000
GEMINI_MAX_OUTPUT_TOKENS=1200
MAX_DAILY_AI_CALLS_PER_USER=50
```

`APP_ENCRYPTION_KEY`는 Fernet 키 형식으로 생성한다.

로컬/서버에 `uv sync`가 완료된 경우:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Docker만 사용하는 경우:

```bash
docker compose run --rm web python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Google OAuth Redirect URI 설정은 `docs/deployment/GOOGLE_OAUTH_REDIRECT_URI.md`를 기준으로 확인한다.

`.gitignore`에 반드시 포함한다.

```gitignore
.env
*.db
data/*.db
data/*.sqlite
data/*.sqlite3
__pycache__/
.venv/
```

---

## 14. 오늘 성공 기준

다음이 모두 되면 OCI Dev Server 구축 완료로 본다.

```text
□ 로컬 PC에서 ssh oci-dev 접속 성공
□ OCI 서버에서 git 사용 가능
□ OCI 서버에서 docker --version 확인 성공
□ OCI 서버에서 docker compose version 확인 성공
□ docker run hello-world 성공
□ ~/workspace 생성 완료
□ Codex에서 OCI 원격 프로젝트 폴더 열기 성공
```

---

## 15. 이번 제출 프로젝트에서 하지 않을 작업

시간 절약을 위해 아래 작업은 제출 이후로 미룬다.

```text
- PostgreSQL 컨테이너 전환
- 자동 백업
- 모니터링
- 로그 수집 시스템
- 서버 보안 강화 전체 작업
```

단, 제출 전에 외부 접속 시연이 꼭 필요하면 `80/443`과 리버스 프록시만 최소로 추가한다.

---

## 16. 운영 원칙

```text
1. OCI는 항상 켜져 있는 개인 Dev Server로 사용한다.
2. 실제 구현은 Codex에서 하되, 기능 단위로 Git commit을 남긴다.
3. TDD 통과 전에는 다음 기능으로 넘어가지 않는다.
4. .env와 인증 키는 Git에 올리지 않는다.
5. SQLite DB는 ./instance에 저장하고, 필요 시 수동 백업한다.
6. 제출 전날인 7월 2일에는 RC1을 만들고, 7월 3일에는 기능 추가를 하지 않는다.
```


---

## 17. 현재 운영 도메인 검증 결과

```text
도메인: dev-gpt.memilmuk82.com
DNS: 129.154.221.2
HTTPS /: 200 OK
HTTP /: 301 -> HTTPS
/healthz: 200 {"status":"ok"}
/terms: 200 OK
/privacy: 200 OK
Nginx: reverse proxy 적용
Docker Compose: gpt-manager-web-1 Up
컨테이너 포트: 127.0.0.1:5000 -> 5000
```

운영 재배포 기본 명령:

```bash
git pull
docker compose down
docker compose up -d --build
curl http://127.0.0.1:5000/healthz
curl https://dev-gpt.memilmuk82.com/healthz
curl https://dev-gpt.memilmuk82.com/terms
curl https://dev-gpt.memilmuk82.com/privacy
```
