from app.extensions import db
from app.models import ApprovalStatus, User


def test_google_login_redirects_to_google(client):
    response = client.get("/auth/google/login")

    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["Location"]
    assert "hd=" not in response.headers["Location"]


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
        assert user.role == "admin"


def test_google_callback_approves_external_account_when_domain_limit_is_disabled(client, app, monkeypatch):
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
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="external@gmail.com").one()
        assert user.auth_provider == "google"
        assert user.approval_status == ApprovalStatus.APPROVED
        assert user.role == "admin"


def test_google_callback_promotes_existing_local_user_to_admin(client, app, monkeypatch):
    with app.app_context():
        user = User(email="local@example.com", name="Local", role="user", approval_status=ApprovalStatus.PENDING)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-4",
            "email": "local@example.com",
            "email_verified": True,
            "name": "Local",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="local@example.com").one()
        assert user.google_sub == "google-sub-4"
        assert user.auth_provider == "google"
        assert user.approval_status == ApprovalStatus.APPROVED
        assert user.role == "admin"


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
