from app.extensions import db
from app.models import User, UserApiKey
from app.services.encryption_service import decrypt_text


def create_user(email="teacher@example.com", name="Teacher") -> User:
    user = User(email=email, name=name)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email="teacher@example.com", password="password123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_api_key_settings_requires_login(client):
    response = client.get("/settings/api-key")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_approved_user_badge_links_to_personal_api_key_settings(client, app):
    with app.app_context():
        create_user(name="이진선")

    login(client)
    dashboard_response = client.get("/dashboard")
    settings_response = client.get("/settings/api-key")

    dashboard_body = dashboard_response.get_data(as_text=True)
    settings_body = settings_response.get_data(as_text=True)

    assert dashboard_response.status_code == 200
    assert settings_response.status_code == 200
    assert 'href="/settings/api-key"' in dashboard_body
    assert "이진선" in dashboard_body
    assert "개인 설정" in settings_body
    assert "♙ Gemini API Key" in settings_body
    assert "SETTINGS" not in settings_body


def test_api_key_is_encrypted_and_roundtrips(client, app):
    raw_api_key = "gemini-secret-key-1234"
    with app.app_context():
        create_user()

    login(client)
    response = client.post(
        "/settings/api-key",
        data={"api_key": raw_api_key},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/settings/api-key")
    with app.app_context():
        user_api_key = UserApiKey.query.one()
        assert user_api_key.provider == "gemini"
        assert user_api_key.key_last4 == "1234"
        assert user_api_key.encrypted_api_key != raw_api_key
        assert raw_api_key not in user_api_key.encrypted_api_key
        assert decrypt_text(user_api_key.encrypted_api_key) == raw_api_key


def test_api_key_page_masks_saved_key(client, app):
    raw_api_key = "gemini-secret-key-5678"
    with app.app_context():
        create_user()

    login(client)
    client.post("/settings/api-key", data={"api_key": raw_api_key})
    response = client.get("/settings/api-key")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "5678" in body
    assert raw_api_key not in body


def test_api_key_can_be_replaced_and_deleted(client, app):
    with app.app_context():
        create_user()

    login(client)
    first_response = client.post("/settings/api-key", data={"api_key": "first-key-1111"})
    second_response = client.post("/settings/api-key", data={"api_key": "second-key-2222"})

    assert first_response.status_code == 302
    assert second_response.status_code == 302
    with app.app_context():
        assert UserApiKey.query.count() == 1
        assert UserApiKey.query.one().key_last4 == "2222"

    delete_response = client.post("/settings/api-key/delete", follow_redirects=False)

    assert delete_response.status_code == 302
    with app.app_context():
        assert UserApiKey.query.count() == 0


def test_saved_api_key_decrypt_check(client, app):
    with app.app_context():
        create_user()

    login(client)
    client.post("/settings/api-key", data={"api_key": "decrypt-check-3333"})
    response = client.post("/settings/api-key/test", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/settings/api-key")
