from app.extensions import db
from app.models import User


def register(client, email="teacher@senedu.kr", name="Teacher", password="password123"):
    return client.post(
        "/auth/register",
        data={"email": email, "name": name, "password": password},
        follow_redirects=False,
    )


def login(client, email="teacher@senedu.kr", password="password123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_register_creates_user_and_redirects_to_dashboard(client, app):
    response = register(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    with app.app_context():
        user = User.query.filter_by(email="teacher@senedu.kr").one()
        assert user.name == "Teacher"
        assert user.password_hash != "password123"


def test_register_rejects_duplicate_email(client, app):
    register(client)
    client.post("/auth/logout")

    response = register(client, name="Other Teacher")

    assert response.status_code == 400
    with app.app_context():
        assert User.query.filter_by(email="teacher@senedu.kr").count() == 1


def test_login_success_allows_dashboard_access(client, app):
    with app.app_context():
        user = User(email="teacher@senedu.kr", name="Teacher")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = login(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "teacher@senedu.kr" in dashboard.get_data(as_text=True)


def test_login_failure_uses_generic_message(client, app):
    with app.app_context():
        user = User(email="teacher@senedu.kr", name="Teacher")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = login(client, password="wrong-password")
    body = response.get_data(as_text=True)

    assert response.status_code == 401
    assert "이메일 또는 비밀번호를 확인하세요." in body
    assert "wrong-password" not in body


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_logout_blocks_dashboard_access(client):
    register(client)

    logout_response = client.post("/auth/logout", follow_redirects=False)
    dashboard_response = client.get("/dashboard")

    assert logout_response.status_code == 302
    assert dashboard_response.status_code == 302
    assert "/auth/login" in dashboard_response.headers["Location"]


def test_external_local_registration_is_approved_without_domain_limit(client, app):
    response = register(client, email="external@gmail.com")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="external@gmail.com").one()
        assert user.approval_status == "approved"

    dashboard_response = client.get("/dashboard", follow_redirects=False)
    assert dashboard_response.status_code == 200


def test_admin_email_registration_gets_admin_role(client, app):
    response = register(client, email="admin@senedu.kr")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="admin@senedu.kr").one()
        assert user.role == "admin"
        assert user.approval_status == "approved"


def test_assistant_admin_email_registration_gets_assistant_admin_role(client, app):
    response = register(client, email="assistant@senedu.kr")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with app.app_context():
        user = User.query.filter_by(email="assistant@senedu.kr").one()
        assert user.role == "assistant_admin"
        assert user.approval_status == "approved"


def test_suspended_user_cannot_login(client, app):
    with app.app_context():
        user = User(email="blocked@senedu.kr", name="Blocked", approval_status="suspended")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = login(client, email="blocked@senedu.kr")

    assert response.status_code == 403
