from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.extensions import db
from app.models import ApprovalStatus, User
from app.services.access_policy import initial_approval_status, initial_role, normalize_email
from app.services.oauth_service import OAuthError, build_google_authorization_url, fetch_google_userinfo


def _normalize_email(email: str) -> str:
    return normalize_email(email)


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
    department = request.form.get("department", "").strip()
    extension = request.form.get("extension", "").strip()

    if not email or not name or not password:
        flash("이름, 이메일, 비밀번호를 모두 입력하세요.", "error")
        return render_template("auth/register.html"), 400

    if len(password) < 8:
        flash("비밀번호는 8자 이상이어야 합니다.", "error")
        return render_template("auth/register.html"), 400

    if User.query.filter_by(email=email).first():
        flash("이미 사용할 수 없는 이메일입니다.", "error")
        return render_template("auth/register.html"), 400

    user = User(
        email=email,
        name=name,
        department=department,
        extension=extension,
        role=initial_role(email),
        auth_provider="local",
        approval_status=initial_approval_status(email),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    if user.is_approved:
        flash("회원가입이 완료되었습니다.", "success")
        return redirect(url_for("main.dashboard"))

    flash("가입 요청이 접수되었습니다. 관리자 승인 후 사용할 수 있습니다.", "warning")
    return redirect(url_for("auth.pending"))


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
    if user.approval_status == ApprovalStatus.SUSPENDED:
        flash("정지된 계정입니다. 관리자에게 문의하세요.", "error")
        return render_template("auth/login.html"), 403

    login_user(user)
    if not user.is_approved:
        flash("관리자 승인 대기 중입니다.", "warning")
        return redirect(url_for("auth.pending"))

    flash("로그인되었습니다.", "success")
    next_url = request.args.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    return redirect(url_for("main.dashboard"))


@auth_bp.get("/google/login")
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if not current_app.config["GOOGLE_CLIENT_ID"] or not current_app.config["GOOGLE_CLIENT_SECRET"]:
        flash("Google OAuth 설정이 필요합니다.", "error")
        return redirect(url_for("auth.login"))
    return redirect(build_google_authorization_url())


@auth_bp.get("/google/callback")
def google_callback():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    code = request.args.get("code", "")
    state = request.args.get("state", "")
    if not code:
        flash("Google 인증 코드가 없습니다.", "error")
        return redirect(url_for("auth.login"))

    try:
        userinfo = fetch_google_userinfo(code, state)
    except OAuthError as exc:
        flash(str(exc), "error")
        return redirect(url_for("auth.login"))

    email = _normalize_email(userinfo.get("email", ""))
    google_sub = userinfo.get("sub")
    email_verified = userinfo.get("email_verified") in (True, "true", "True", "1")
    if not email or not google_sub or not email_verified:
        flash("검증된 Google 계정 정보를 확인할 수 없습니다.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(google_sub=google_sub).first() or User.query.filter_by(email=email).first()
    if user is None:
        user = User(
            email=email,
            name=userinfo.get("name") or email.split("@", 1)[0],
            google_sub=google_sub,
            auth_provider="google",
            role="admin",
            approval_status=ApprovalStatus.APPROVED,
        )
        db.session.add(user)
    else:
        user.google_sub = user.google_sub or google_sub
        user.auth_provider = "google"
        if user.approval_status == ApprovalStatus.PENDING:
            user.approval_status = ApprovalStatus.APPROVED
        if user.role != "admin":
            user.role = "admin"
    db.session.commit()

    if user.approval_status == ApprovalStatus.SUSPENDED:
        flash("정지된 계정입니다. 관리자에게 문의하세요.", "error")
        return redirect(url_for("auth.login"))

    login_user(user)
    if not user.is_approved:
        flash("Google 로그인 요청이 접수되었습니다. 관리자 승인 후 사용할 수 있습니다.", "warning")
        return redirect(url_for("auth.pending"))

    flash("Google 계정으로 로그인되었습니다.", "success")
    return redirect(url_for("main.dashboard"))


@auth_bp.get("/pending")
@login_required
def pending():
    if current_user.is_approved:
        return redirect(url_for("main.dashboard"))
    return render_template("auth/pending.html")


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("로그아웃되었습니다.", "success")
    return redirect(url_for("main.index"))
