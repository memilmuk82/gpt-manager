import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


class EncryptionError(ValueError):
    pass


def encrypt_text(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise EncryptionError("암호화 키가 일치하지 않아 저장된 값을 읽을 수 없습니다.") from exc


def _fernet() -> Fernet:
    configured_key = current_app.config.get("APP_ENCRYPTION_KEY", "").strip()
    key = configured_key.encode("utf-8") if configured_key else _derive_dev_key()
    try:
        return Fernet(key)
    except ValueError as exc:
        raise EncryptionError("APP_ENCRYPTION_KEY는 Fernet 키 형식이어야 합니다.") from exc


def _derive_dev_key() -> bytes:
    secret_key = current_app.config.get("SECRET_KEY", "dev-change-me")
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)
