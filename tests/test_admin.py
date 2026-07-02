from app.extensions import db
from app.models import ApprovalStatus, User


def create_user(email="teacher@senedu.kr", name="Teacher", role="user", approval_status="approved") -> User:
    user = User(email=email, name=name, role=role, approval_status=approval_status)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email="teacher@senedu.kr", password="password123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_admin_dashboard_requires_admin_role(client, app):
    with app.app_context():
        create_user()

    login(client)
    response = client.get("/admin")

    assert response.status_code == 403


def test_admin_can_view_and_approve_pending_user(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        pending = create_user(email="external@gmail.com", name="External", approval_status="pending")
        pending_id = pending.id

    login(client, email="admin@senedu.kr")
    users_response = client.get("/admin/users")

    assert users_response.status_code == 200
    assert "external@gmail.com" in users_response.get_data(as_text=True)

    approve_response = client.post(f"/admin/users/{pending_id}/approve", follow_redirects=False)

    assert approve_response.status_code == 302
    with app.app_context():
        assert db.session.get(User, pending_id).approval_status == ApprovalStatus.APPROVED


def test_admin_cannot_suspend_self(client, app):
    with app.app_context():
        admin = create_user(email="admin@senedu.kr", name="Admin", role="admin")
        admin_id = admin.id

    login(client, email="admin@senedu.kr")
    response = client.post(f"/admin/users/{admin_id}/suspend", follow_redirects=False)

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(User, admin_id).approval_status == ApprovalStatus.APPROVED


def test_assistant_admin_can_access_admin_dashboard(client, app):
    with app.app_context():
        create_user(email="assistant@senedu.kr", name="Assistant", role="assistant_admin")

    login(client, email="assistant@senedu.kr")

    dashboard_response = client.get("/admin")
    users_response = client.get("/admin/users")

    assert dashboard_response.status_code == 200
    assert users_response.status_code == 200
