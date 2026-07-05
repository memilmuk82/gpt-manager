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
    from datetime import datetime, timedelta

    from app.extensions import db
    from app.models import AiResource, Reservation, ReservationStatus, User

    now = datetime.now()
    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
        user.set_password("password123")
        resource = AiResource(name="GPT Pro", provider="OpenAI")
        db.session.add_all([user, resource])
        db.session.flush()
        db.session.add_all([
            Reservation(
                user_id=user.id,
                resource_id=resource.id,
                start_at=now - timedelta(days=1, hours=1),
                end_at=now - timedelta(days=1),
                purpose="로그 미작성 예약",
                status=ReservationStatus.COMPLETED,
            ),
            Reservation(
                user_id=user.id,
                resource_id=resource.id,
                start_at=now - timedelta(days=45, hours=1),
                end_at=now - timedelta(days=45),
                purpose="오래된 로그 미작성 예약",
                status=ReservationStatus.COMPLETED,
            ),
        ])
        db.session.commit()

    client.post("/auth/login", data={"email": "teacher@example.com", "password": "password123"})
    response = client.get("/dashboard")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "사용 로그 작성 필요" in body
    assert "로그 미작성 예약" in body
    assert "오래된 로그 미작성 예약" not in body
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


def test_profile_shows_account_summary_and_recent_activity(client, app):
    from datetime import datetime, timedelta

    from app.extensions import db
    from app.models import AiResource, PromptReview, Reservation, UsageLog, User, UserApiKey

    now = datetime.now()
    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher", department="정보부", extension="1234")
        user.set_password("password123")
        resource = AiResource(name="GPT Pro", provider="OpenAI")
        db.session.add_all([user, resource])
        db.session.flush()
        reservation = Reservation(
            user_id=user.id,
            resource_id=resource.id,
            start_at=now + timedelta(days=1),
            end_at=now + timedelta(days=1, hours=1),
            purpose="프로필 예약",
            work_type="수업",
        )
        db.session.add(reservation)
        db.session.flush()
        db.session.add_all([
            UsageLog(user_id=user.id, reservation_id=reservation.id, resource_id=resource.id, work_type="수업", summary="프로필 로그"),
            PromptReview(user_id=user.id, provider="gemini", source_prompt="원본", review_goal="프로필 정리", assembled_prompt="조립", review_result="결과", model_name="gemini-test"),
            UserApiKey(user_id=user.id, provider="gemini", encrypted_api_key="encrypted", key_last4="1234", selected_model="gemini-test"),
        ])
        db.session.commit()

    client.post("/auth/login", data={"email": "teacher@example.com", "password": "password123"})
    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "내 프로필" in body
    assert "Teacher" in body
    assert "정보부" in body
    assert "프로필 예약" in body
    assert "프로필 로그" in body
    assert "프로필 정리" in body
    assert "저장됨: •••• 1234" in body


def test_header_user_badge_links_to_profile(client, app):
    from app.extensions import db
    from app.models import User

    with app.app_context():
        user = User(email="teacher@example.com", name="Teacher")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    client.post("/auth/login", data={"email": "teacher@example.com", "password": "password123"})
    response = client.get("/dashboard")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'href="/profile"' in body
    assert 'title="내 프로필"' in body
