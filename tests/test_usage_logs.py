from datetime import datetime

from app.extensions import db
from app.models import AiResource, Reservation, UsageLog, User


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


def create_resource(name="GPT Pro 공용 계정 A") -> AiResource:
    resource = AiResource(name=name, provider="OpenAI")
    db.session.add(resource)
    db.session.commit()
    return resource


def test_usage_log_can_be_created_from_reservation(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        reservation = Reservation(
            user_id=user.id,
            resource_id=resource.id,
            start_at=datetime(2026, 7, 2, 9, 0),
            end_at=datetime(2026, 7, 2, 10, 0),
            purpose="수업 준비",
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id
        resource_id = resource.id

    login(client)
    response = client.post(
        "/logs",
        data={
            "reservation_id": reservation_id,
            "resource_id": "",
            "work_type": "수업 자료",
            "summary": "프롬프트 초안 작성",
            "prompt_text": "자료를 요약해줘",
            "result_note": "활동지에 반영",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        usage_log = UsageLog.query.one()
        assert usage_log.reservation_id == reservation_id
        assert usage_log.resource_id == resource_id
        assert usage_log.prompt_text == "자료를 요약해줘"


def test_usage_log_can_be_created_with_resource_only(client, app):
    with app.app_context():
        create_user()
        resource = create_resource()
        resource_id = resource.id

    login(client)
    response = client.post(
        "/logs",
        data={
            "reservation_id": "",
            "resource_id": resource_id,
            "work_type": "행정",
            "summary": "가정통신문 초안 작성",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        usage_log = UsageLog.query.one()
        assert usage_log.reservation_id is None
        assert usage_log.resource_id == resource_id


def test_new_usage_log_preselects_reservation_from_query(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        reservation = Reservation(
            user_id=user.id,
            resource_id=resource.id,
            start_at=datetime(2026, 7, 2, 9, 0),
            end_at=datetime(2026, 7, 2, 10, 0),
            purpose="수업 준비",
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id

    login(client)
    response = client.get(f"/logs/new?reservation_id={reservation_id}")

    assert response.status_code == 200
    assert f'value="{reservation_id}" selected' in response.get_data(as_text=True)


def test_usage_log_requires_owned_reservation(client, app):
    with app.app_context():
        create_user()
        other = create_user(email="other@example.com", name="Other")
        resource = create_resource()
        reservation = Reservation(
            user_id=other.id,
            resource_id=resource.id,
            start_at=datetime(2026, 7, 2, 9, 0),
            end_at=datetime(2026, 7, 2, 10, 0),
            purpose="다른 사용자 예약",
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id

    login(client)
    response = client.post(
        "/logs",
        data={
            "reservation_id": reservation_id,
            "resource_id": "",
            "work_type": "수업 자료",
            "summary": "권한 없는 예약",
        },
    )

    assert response.status_code == 400
    with app.app_context():
        assert UsageLog.query.count() == 0


def test_user_cannot_view_another_users_usage_log(client, app):
    with app.app_context():
        create_user()
        other = create_user(email="other@example.com", name="Other")
        resource = create_resource()
        db.session.add(
            UsageLog(
                user_id=other.id,
                resource_id=resource.id,
                work_type="수업",
                summary="다른 사용자 로그",
            )
        )
        db.session.commit()

    login(client)
    index_response = client.get("/logs")
    show_response = client.get("/logs/1")

    assert index_response.status_code == 200
    assert "다른 사용자 로그" not in index_response.get_data(as_text=True)
    assert show_response.status_code == 404


def test_usage_log_filters_by_keyword_work_type_and_resource(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        other_resource = create_resource(name="GPT Pro 공용 계정 B")
        db.session.add_all([
            UsageLog(user_id=user.id, resource_id=resource.id, work_type="수업", summary="활동지 작성", prompt_text="활동지"),
            UsageLog(user_id=user.id, resource_id=other_resource.id, work_type="행정", summary="가정통신문 작성"),
        ])
        db.session.commit()
        resource_id = resource.id

    login(client)
    response = client.get(f"/logs?q=활동지&work_type=수업&resource_id={resource_id}")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "활동지 작성" in body
    assert "가정통신문 작성" not in body
