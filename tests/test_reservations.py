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
