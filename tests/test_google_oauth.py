from app.extensions import db
from app.models import ApprovalStatus, User


def test_google_login_redirects_to_google(client):
    response = client.get("/auth/google/login")

    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["Location"]
    assert "hd=senedu.kr" in response.headers["Location"]


def test_google_callback_auto_approves_senedu_account(client, app, monkeypatch):
    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-1",
            "email": "teacher@senedu.kr",
            "email_verified": True,
            "name": "Teacher",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="teacher@senedu.kr").one()
        assert user.google_sub == "google-sub-1"
        assert user.auth_provider == "google"
        assert user.approval_status == ApprovalStatus.APPROVED


def test_google_callback_keeps_external_account_pending(client, app, monkeypatch):
    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-2",
            "email": "external@gmail.com",
            "email_verified": True,
            "name": "External",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/pending")
    with app.app_context():
        user = User.query.filter_by(email="external@gmail.com").one()
        assert user.auth_provider == "google"
        assert user.approval_status == ApprovalStatus.PENDING


def test_google_callback_rejects_unverified_email(client, app, monkeypatch):
    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-3",
            "email": "external@gmail.com",
            "email_verified": False,
            "name": "External",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")
    with app.app_context():
        assert User.query.count() == 0
