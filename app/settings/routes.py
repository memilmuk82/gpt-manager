from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import UserApiKey
from app.services.encryption_service import EncryptionError, decrypt_llm_key, encrypt_llm_key
from app.services.llm.errors import LLMProviderError
from app.services.llm.registry import (
    PROVIDER_DEFINITIONS,
    default_model,
    list_models_with_fallback,
    normalize_provider,
    provider_choices,
    recommended_models,
    test_provider_connection,
)
from app.settings import settings_bp


def _provider_from_request() -> str:
    try:
        return normalize_provider(request.values.get("provider") or "gemini")
    except ValueError:
        flash("지원하지 않는 AI Provider입니다.", "error")
        return "gemini"


@settings_bp.get("/api-key")
@login_required
def api_key():
    provider = _provider_from_request()
    return _render_settings(provider)


@settings_bp.post("/api-key")
@login_required
def save_api_key():
    provider = _provider_from_request()
    raw_api_key = request.form.get("api_key", "").strip()
    selected_model = request.form.get("selected_model", "").strip() or default_model(provider)
    is_active = request.form.get("is_active") == "on"
    user_api_key = _get_user_api_key(provider)

    if not raw_api_key and user_api_key is None:
        flash("서버에 저장할 API Key를 입력하세요. 저장하지 않는 모드는 프롬프트 정리 실행 화면에서 일회성으로 사용할 수 있습니다.", "error")
        return _render_settings(provider, status_code=400)

    if user_api_key is None:
        user_api_key = UserApiKey(user_id=current_user.id, provider=provider)
        db.session.add(user_api_key)

    if raw_api_key:
        try:
            user_api_key.encrypted_api_key = encrypt_llm_key(raw_api_key)
        except EncryptionError as exc:
            db.session.rollback()
            flash(str(exc), "error")
            return _render_settings(provider, status_code=500)
        user_api_key.key_last4 = raw_api_key[-4:]

    user_api_key.selected_model = selected_model
    user_api_key.is_active = is_active
    db.session.commit()

    flash(f"{PROVIDER_DEFINITIONS[provider].label} API Key 설정을 암호화 저장했습니다.", "success")
    return redirect(url_for("settings.api_key", provider=provider))


@settings_bp.post("/api-key/test")
@login_required
def test_api_key():
    provider = _provider_from_request()
    selected_model = request.form.get("selected_model", "").strip() or default_model(provider)
    raw_api_key = request.form.get("api_key", "").strip()
    if not raw_api_key:
        user_api_key = _get_user_api_key(provider)
        if user_api_key is None:
            flash("저장된 API Key가 없습니다. 테스트할 키를 입력하거나 서버에 암호화 저장하세요.", "error")
            return redirect(url_for("settings.api_key", provider=provider))
        try:
            raw_api_key = decrypt_llm_key(user_api_key.encrypted_api_key)
        except EncryptionError as exc:
            flash(str(exc), "error")
            return redirect(url_for("settings.api_key", provider=provider))

    try:
        response_text = test_provider_connection(provider, raw_api_key, selected_model)
    except LLMProviderError as exc:
        flash(str(exc), "error")
        return redirect(url_for("settings.api_key", provider=provider))

    snippet = response_text[:80].replace("\n", " ")
    flash(f"연결 테스트 성공: {PROVIDER_DEFINITIONS[provider].label} / {selected_model} / {snippet}", "success")
    return redirect(url_for("settings.api_key", provider=provider))


@settings_bp.post("/api-key/models")
@login_required
def refresh_models():
    provider = _provider_from_request()
    raw_api_key = request.form.get("api_key", "").strip()
    if not raw_api_key:
        user_api_key = _get_user_api_key(provider)
        if user_api_key is not None:
            try:
                raw_api_key = decrypt_llm_key(user_api_key.encrypted_api_key)
            except EncryptionError:
                raw_api_key = ""

    models, refreshed, message = list_models_with_fallback(provider, raw_api_key or None)
    flash(message, "success" if refreshed else "warning")
    return _render_settings(provider, refreshed_models=models)


@settings_bp.post("/api-key/delete")
@login_required
def delete_api_key():
    provider = _provider_from_request()
    user_api_key = _get_user_api_key(provider)
    if user_api_key is not None:
        db.session.delete(user_api_key)
        db.session.commit()
        flash(f"{PROVIDER_DEFINITIONS[provider].label} API Key를 삭제했습니다.", "success")
    else:
        flash("삭제할 API Key가 없습니다.", "warning")
    return redirect(url_for("settings.api_key", provider=provider))


def _render_settings(provider: str, refreshed_models: list[str] | None = None, status_code: int = 200):
    user_api_key = _get_user_api_key(provider)
    models = refreshed_models or recommended_models(provider)
    selected_model = (user_api_key.selected_model if user_api_key else "") or default_model(provider)
    if selected_model not in models:
        models = [selected_model, *models]
    response = render_template(
        "settings/api_key.html",
        providers=provider_choices(),
        provider_definitions=PROVIDER_DEFINITIONS,
        selected_provider=provider,
        user_api_key=user_api_key,
        user_api_keys=UserApiKey.query.filter_by(user_id=current_user.id).order_by(UserApiKey.provider.asc()).all(),
        model_options=models,
        selected_model=selected_model,
    )
    return response, status_code


def _get_user_api_key(provider: str) -> UserApiKey | None:
    return UserApiKey.query.filter_by(user_id=current_user.id, provider=provider).first()
