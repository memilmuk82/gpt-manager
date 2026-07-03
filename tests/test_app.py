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
    assert "사용자 인증" in response.get_data(as_text=True)


def test_dashboard_shows_missing_usage_log_alert_and_metrics(client, app):
    from datetime import datetime

    from app.extensions import db
    from app.models import AiResource, Reservation, ReservationStatus, User

    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
        user.set_password("password123")
        resource = AiResource(name="GPT Pro", provider="OpenAI")
        db.session.add_all([user, resource])
        db.session.flush()
        db.session.add(
            Reservation(
                user_id=user.id,
                resource_id=resource.id,
                start_at=datetime(2026, 7, 2, 9, 0),
                end_at=datetime(2026, 7, 2, 10, 0),
                purpose="로그 미작성 예약",
                status=ReservationStatus.COMPLETED,
            )
        )
        db.session.commit()

    client.post("/auth/login", data={"email": "teacher@example.com", "password": "password123"})
    response = client.get("/dashboard")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "사용 로그 작성 필요" in body
    assert "로그 미작성 예약" in body
    assert "내 월간 예약" in body


def test_notice_banner_renders_when_enabled(client, app):
    from app.extensions import db
    from app.models import AppSetting, User

    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
        user.set_password("password123")
        db.session.add_all([
            user,
            AppSetting(key="notice_enabled", value="true", label="공지 배너 사용", help_text="", sort_order=1),
            AppSetting(key="notice_title", value="긴급 공지", label="공지 제목", help_text="", sort_order=2),
            AppSetting(key="notice_body", value="오늘은 점검일입니다.", label="공지 내용", help_text="", sort_order=3),
        ])
        db.session.commit()

    client.post("/auth/login", data={"email": "teacher@example.com", "password": "password123"})
    response = client.get("/dashboard")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "긴급 공지" in body
    assert "오늘은 점검일입니다." in body
