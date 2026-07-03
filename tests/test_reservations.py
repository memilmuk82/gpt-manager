from datetime import datetime

from app.extensions import db
from app.models import AiResource, Reservation, ReservationStatus, User


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
    resource = AiResource(name=name, provider="OpenAI", description="Shared resource")
    db.session.add(resource)
    db.session.commit()
    return resource


def test_reservation_create_and_cancel_flow(client, app):
    with app.app_context():
        create_user()
        resource = create_resource()
        resource_id = resource.id

    login(client)
    response = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T09:00",
            "end_at": "2026-07-02T10:00",
            "purpose": "수업 자료 준비",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/reservations")

    with app.app_context():
        reservation = Reservation.query.one()
        assert reservation.purpose == "수업 자료 준비"
        assert reservation.start_at == datetime(2026, 7, 2, 9, 0)
        assert reservation.status == ReservationStatus.RESERVED

    cancel_response = client.post("/reservations/1/cancel", follow_redirects=False)

    assert cancel_response.status_code == 302
    with app.app_context():
        assert Reservation.query.one().status == ReservationStatus.CANCELLED


def test_user_cannot_see_another_users_reservation(client, app):
    with app.app_context():
        owner = create_user()
        other = create_user(email="other@example.com", name="Other")
        resource = create_resource()
        db.session.add(
            Reservation(
                user_id=other.id,
                resource_id=resource.id,
                start_at=datetime(2026, 7, 2, 9, 0),
                end_at=datetime(2026, 7, 2, 10, 0),
                purpose="다른 사용자 예약",
            )
        )
        db.session.commit()
        assert owner.id != other.id

    login(client)
    response = client.get("/reservations")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "다른 사용자 예약" not in body


def test_reservation_conflict_rejects_overlap_on_same_resource(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        resource_id = resource.id
        db.session.add(
            Reservation(
                user_id=user.id,
                resource_id=resource_id,
                start_at=datetime(2026, 7, 2, 9, 0),
                end_at=datetime(2026, 7, 2, 10, 0),
                purpose="기존 예약",
            )
        )
        db.session.commit()

    login(client)
    response = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T09:30",
            "end_at": "2026-07-02T10:30",
            "purpose": "겹치는 예약",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 400
    assert "이미 겹치는 예약이 있습니다." in body
    with app.app_context():
        assert Reservation.query.count() == 1


def test_reservation_allows_back_to_back_and_different_resource(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        other_resource = create_resource(name="GPT Pro 공용 계정 B")
        resource_id = resource.id
        other_resource_id = other_resource.id
        db.session.add(
            Reservation(
                user_id=user.id,
                resource_id=resource_id,
                start_at=datetime(2026, 7, 2, 9, 0),
                end_at=datetime(2026, 7, 2, 10, 0),
                purpose="기존 예약",
            )
        )
        db.session.commit()

    login(client)
    back_to_back = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T10:00",
            "end_at": "2026-07-02T11:00",
            "purpose": "바로 이어지는 예약",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )
    different_resource = client.post(
        "/reservations",
        data={
            "resource_id": other_resource_id,
            "start_at": "2026-07-02T09:30",
            "end_at": "2026-07-02T10:30",
            "purpose": "다른 리소스 예약",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )

    assert back_to_back.status_code == 302
    assert different_resource.status_code == 302
    with app.app_context():
        assert Reservation.query.count() == 3


def test_cancelled_reservation_does_not_block_new_reservation(client, app):
    with app.app_context():
        user = create_user()
        resource = create_resource()
        resource_id = resource.id
        db.session.add(
            Reservation(
                user_id=user.id,
                resource_id=resource_id,
                start_at=datetime(2026, 7, 2, 9, 0),
                end_at=datetime(2026, 7, 2, 10, 0),
                purpose="취소된 예약",
                status=ReservationStatus.CANCELLED,
            )
        )
        db.session.commit()

    login(client)
    response = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T09:30",
            "end_at": "2026-07-02T10:30",
            "purpose": "새 예약",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        assert Reservation.query.count() == 2


def test_inactive_resource_cannot_be_reserved(client, app):
    with app.app_context():
        create_user()
        resource = AiResource(name="비활성 리소스", provider="OpenAI", is_active=False)
        db.session.add(resource)
        db.session.commit()
        resource_id = resource.id

    login(client)
    response = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T09:00",
            "end_at": "2026-07-02T10:00",
            "purpose": "비활성 예약",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )

    assert response.status_code == 400
    assert "예약 가능한 AI 리소스를 선택하세요." in response.get_data(as_text=True)


def test_reservation_end_must_be_after_start(client, app):
    with app.app_context():
        create_user()
        resource = create_resource()
        resource_id = resource.id

    login(client)
    response = client.post(
        "/reservations",
        data={
            "resource_id": resource_id,
            "start_at": "2026-07-02T10:00",
            "end_at": "2026-07-02T10:00",
            "purpose": "잘못된 시간",
            "work_type": "워크북 개발",
            "safety_confirmed": "on",
        },
    )

    assert response.status_code == 400
    assert "예약 종료 시간은 시작 시간보다 늦어야 합니다." in response.get_data(as_text=True)


def test_today_reservations_show_shared_daily_schedule(client, app):
    with app.app_context():
        create_user()
        other = create_user(email="other@example.com", name="Other")
        resource = create_resource()
        db.session.add_all(
            [
                Reservation(
                    user_id=other.id,
                    resource_id=resource.id,
                    start_at=datetime(2026, 7, 2, 9, 0),
                    end_at=datetime(2026, 7, 2, 10, 0),
                    purpose="다른 사용자 예약",
                ),
                Reservation(
                    user_id=other.id,
                    resource_id=resource.id,
                    start_at=datetime(2026, 7, 3, 9, 0),
                    end_at=datetime(2026, 7, 3, 10, 0),
                    purpose="다른 날짜 예약",
                ),
                Reservation(
                    user_id=other.id,
                    resource_id=resource.id,
                    start_at=datetime(2026, 7, 2, 11, 0),
                    end_at=datetime(2026, 7, 2, 12, 0),
                    purpose="취소된 예약",
                    status=ReservationStatus.CANCELLED,
                ),
            ]
        )
        db.session.commit()

    login(client)
    response = client.get("/reservations/today?date=2026-07-02")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "다른 사용자 예약" in body
    assert "Other" in body
    assert "다른 날짜 예약" not in body
    assert "취소된 예약" not in body
