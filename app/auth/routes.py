from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.auth import auth_bp
from app.extensions import db
from app.models import User


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@auth_bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    email = _normalize_email(request.form.get("email", ""))
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")

    if not email or not name or not password:
        flash("이름, 이메일, 비밀번호를 모두 입력하세요.", "error")
        return render_template("auth/register.html"), 400

    if len(password) < 8:
        flash("비밀번호는 8자 이상이어야 합니다.", "error")
        return render_template("auth/register.html"), 400

    if User.query.filter_by(email=email).first():
        flash("이미 사용할 수 없는 이메일입니다.", "error")
        return render_template("auth/register.html"), 400

    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash("회원가입이 완료되었습니다.", "success")
    return redirect(url_for("main.dashboard"))


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    email = _normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    user = User.query.filter_by(email=email).first() if email else None

    if not user or not user.check_password(password):
        flash("이메일 또는 비밀번호를 확인하세요.", "error")
        return render_template("auth/login.html"), 401

    login_user(user)
    flash("로그인되었습니다.", "success")
    next_url = request.args.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    return redirect(url_for("main.dashboard"))


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("main.index"))
