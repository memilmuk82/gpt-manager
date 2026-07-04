#!/usr/bin/env bash
set -euo pipefail

export DATABASE_URL="sqlite:////tmp/gpt-manager-e2e.db"
export SECRET_KEY="e2e-secret-key"
export APP_ENCRYPTION_KEY=""
export LLM_KEY_ENCRYPTION_SECRET="e2e-llm-secret"
export ALLOWED_GOOGLE_DOMAIN=""
export ADMIN_EMAILS="admin@senedu.kr"
export FLASK_ENV="testing"

uv run python tests/e2e/prepare_e2e.py
exec uv run flask --app run run --host 127.0.0.1 --port 5100
