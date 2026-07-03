from app.extensions import db
from app.models import ApprovalStatus, User


def test_google_login_redirects_to_google(client):
    response = client.get("/auth/google/login")

    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["Location"]
    assert "hd=" not in response.headers["Location"]


def test_google_callback_auto_approves_senedu_account_without_admin_role(client, app, monkeypatch):
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
        assert user.role == "user"


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
        assert user.role == "user"


def test_google_callback_links_existing_local_user_without_admin_promotion(client, app, monkeypatch):
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
        assert user.role == "user"


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


def test_google_callback_rejects_disallowed_domain(client, app, monkeypatch):
    app.config["ALLOWED_GOOGLE_DOMAIN"] = "senedu.kr"

    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-5",
            "email": "external@gmail.com",
            "email_verified": True,
            "name": "External",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")
    with app.app_context():
        assert User.query.filter_by(email="external@gmail.com").count() == 0


def test_google_callback_preserves_admin_email_role(client, app, monkeypatch):
    def fake_fetch_google_userinfo(code, state):
        return {
            "sub": "google-sub-6",
            "email": "admin@senedu.kr",
            "email_verified": True,
            "name": "Admin",
        }

    monkeypatch.setattr("app.auth.routes.fetch_google_userinfo", fake_fetch_google_userinfo)

    response = client.get("/auth/google/callback?code=ok&state=test", follow_redirects=False)

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email="admin@senedu.kr").one()
        assert user.role == "admin"
