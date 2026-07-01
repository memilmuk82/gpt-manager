import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.extensions import db
from app.models import AiResource

DB_PATH = Path('/tmp/gpt-manager-e2e.db')
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ.setdefault('DATABASE_URL', f'sqlite:///{DB_PATH}')
os.environ.setdefault('SECRET_KEY', 'e2e-secret-key')
os.environ.setdefault('APP_ENCRYPTION_KEY', '')
os.environ.setdefault('ALLOWED_GOOGLE_DOMAIN', 'senedu.kr')
os.environ.setdefault('ADMIN_EMAILS', 'admin@senedu.kr')

app = create_app()
with app.app_context():
    if AiResource.query.filter_by(name='GPT Pro 공용 계정 A').first() is None:
        db.session.add(
            AiResource(
                name='GPT Pro 공용 계정 A',
                provider='OpenAI',
                description='E2E shared AI resource',
            )
        )
        db.session.commit()
