import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app, session, url_for


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class OAuthError(RuntimeError):
    pass


def build_google_authorization_url() -> str:
    state = secrets.token_urlsafe(24)
    session["google_oauth_state"] = state
    params = {
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "redirect_uri": current_app.config["GOOGLE_REDIRECT_URI"],
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    allowed_domain = current_app.config.get("ALLOWED_GOOGLE_DOMAIN", "").strip()
    if allowed_domain:
        params["hd"] = allowed_domain
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def fetch_google_userinfo(code: str, state: str) -> dict:
    expected_state = session.pop("google_oauth_state", None)
    if not expected_state or state != expected_state:
        raise OAuthError("Google 로그인 상태값이 올바르지 않습니다.")

    token_payload = {
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": current_app.config["GOOGLE_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }
    token_response = _post_form(GOOGLE_TOKEN_URL, token_payload)
    access_token = token_response.get("access_token")
    if not access_token:
        raise OAuthError("Google access token을 받지 못했습니다.")

    request = urllib.request.Request(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OAuthError("Google 사용자 정보를 가져오지 못했습니다.") from exc


def _post_form(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OAuthError("Google OAuth 토큰 요청이 실패했습니다.") from exc
