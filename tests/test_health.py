from app import create_app


def test_healthz_returns_200():
    app = create_app()

    with app.test_client() as client:
        response = client.get("/healthz")

    assert response.status_code == 200


def test_healthz_contains_status_ok():
    app = create_app()

    with app.test_client() as client:
        response = client.get("/healthz")

    assert response.get_json() == {"status": "ok"}
