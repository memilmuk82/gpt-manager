from app import create_app


def test_app_factory_creates_app():
    app = create_app()

    assert app is not None
    assert app.name == "app"


def test_index_page_returns_200():
    app = create_app()

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "생성형 AI 계정 공동 사용 지원 시스템" in response.get_data(as_text=True)
