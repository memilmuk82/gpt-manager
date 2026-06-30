from app.extensions import db
from app.models import User


def test_user_password_hash_roundtrip(app):
    user = User(email="teacher@example.com", name="Teacher")
    user.set_password("correct-password")

    assert user.check_password("correct-password") is True
    assert user.check_password("wrong-password") is False


def test_user_password_is_not_stored_in_plaintext(app):
    password = "very-secret-password"
    user = User(email="teacher@example.com", name="Teacher")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    saved = User.query.filter_by(email="teacher@example.com").one()

    assert saved.password_hash != password
    assert password not in saved.password_hash
