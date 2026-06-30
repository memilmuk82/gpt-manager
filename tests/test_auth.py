from app.extensions import db
from app.models import User


def register(client, email="teacher@example.com", name="Teacher", password="password123"):
    return client.post(
        "/auth/register",
        data={"email": email, "name": name, "password": password},
        follow_redirects=False,
    )


def login(client, email="teacher@example.com", password="password123"):
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
        user = User.query.filter_by(email="teacher@example.com").one()
        assert user.name == "Teacher"
        assert user.password_hash != "password123"


def test_register_rejects_duplicate_email(client, app):
    register(client)
    client.post("/auth/logout")

    response = register(client, name="Other Teacher")

    assert response.status_code == 400
    with app.app_context():
        assert User.query.filter_by(email="teacher@example.com").count() == 1


def test_login_success_allows_dashboard_access(client, app):
    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = login(client)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "teacher@example.com" in dashboard.get_data(as_text=True)


def test_login_failure_uses_generic_message(client, app):
    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
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
