from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import UserApiKey
from app.services.encryption_service import EncryptionError, decrypt_text, encrypt_text
from app.settings import settings_bp


PROVIDER = "gemini"


@settings_bp.get("/api-key")
@login_required
def api_key():
    user_api_key = _get_user_api_key()
    return render_template("settings/api_key.html", user_api_key=user_api_key)


@settings_bp.post("/api-key")
@login_required
def save_api_key():
    raw_api_key = request.form.get("api_key", "").strip()
    if not raw_api_key:
        flash("API Key를 입력하세요.", "error")
        return render_template("settings/api_key.html", user_api_key=_get_user_api_key()), 400

    try:
        encrypted_api_key = encrypt_text(raw_api_key)
    except EncryptionError as exc:
        flash(str(exc), "error")
        return render_template("settings/api_key.html", user_api_key=_get_user_api_key()), 500

    user_api_key = _get_user_api_key()
    if user_api_key is None:
        user_api_key = UserApiKey(user_id=current_user.id, provider=PROVIDER)
        db.session.add(user_api_key)

    user_api_key.encrypted_api_key = encrypted_api_key
    user_api_key.key_last4 = raw_api_key[-4:]
    db.session.commit()

    flash("Gemini API Key가 암호화되어 저장되었습니다.", "success")
    return redirect(url_for("settings.api_key"))


@settings_bp.post("/api-key/test")
@login_required
def test_api_key():
    user_api_key = _get_user_api_key()
    if user_api_key is None:
        flash("저장된 API Key가 없습니다.", "error")
        return redirect(url_for("settings.api_key"))

    try:
        decrypt_text(user_api_key.encrypted_api_key)
    except EncryptionError as exc:
        flash(str(exc), "error")
        return redirect(url_for("settings.api_key"))

    flash("저장된 API Key 복호화 확인을 완료했습니다.", "success")
    return redirect(url_for("settings.api_key"))


@settings_bp.post("/api-key/delete")
@login_required
def delete_api_key():
    user_api_key = _get_user_api_key()
    if user_api_key is not None:
        db.session.delete(user_api_key)
        db.session.commit()
        flash("Gemini API Key를 삭제했습니다.", "success")
    else:
        flash("삭제할 API Key가 없습니다.", "warning")
    return redirect(url_for("settings.api_key"))


def _get_user_api_key() -> UserApiKey | None:
    return UserApiKey.query.filter_by(user_id=current_user.id, provider=PROVIDER).first()
