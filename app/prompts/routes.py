from datetime import datetime, time

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import PromptReview, UserApiKey
from app.prompts import prompts_bp
from app.services.encryption_service import EncryptionError, decrypt_text
from app.services.prompt_review_service import GeminiReviewError, build_review_prompt, call_gemini_review


PROVIDER = "gemini"


@prompts_bp.get("")
@login_required
def index():
    reviews = (
        PromptReview.query.filter_by(user_id=current_user.id)
        .order_by(PromptReview.created_at.desc())
        .all()
    )
    return render_template("prompts/index.html", reviews=reviews)


@prompts_bp.get("/new")
@login_required
def new():
    return render_template("prompts/new.html")


@prompts_bp.post("")
@login_required
def create():
    source_prompt = request.form.get("source_prompt", "").strip()
    review_goal = request.form.get("review_goal", "").strip() or "명확성, 안전성, 수업 활용성 개선"
    max_input_chars = current_app.config["GEMINI_MAX_INPUT_CHARS"]

    if not source_prompt:
        flash("점검할 프롬프트를 입력하세요.", "error")
        return render_template("prompts/new.html"), 400
    if len(source_prompt) > max_input_chars:
        flash(f"프롬프트는 {max_input_chars}자 이하로 입력하세요.", "error")
        return render_template("prompts/new.html"), 400
    if _daily_review_limit_exceeded():
        flash("오늘 사용할 수 있는 Gemini 프롬프트 점검 횟수를 모두 사용했습니다.", "error")
        return render_template("prompts/new.html"), 429

    user_api_key = _get_user_api_key()
    if user_api_key is None:
        flash("먼저 Gemini API Key를 설정하세요.", "error")
        return redirect(url_for("settings.api_key"))

    try:
        api_key = decrypt_text(user_api_key.encrypted_api_key)
    except EncryptionError as exc:
        flash(str(exc), "error")
        return redirect(url_for("settings.api_key"))

    model = current_app.config["GEMINI_MODEL"]
    assembled_prompt = build_review_prompt(source_prompt, review_goal)
    try:
        review_result = call_gemini_review(
            api_key=api_key,
            model=model,
            prompt=assembled_prompt,
            max_output_tokens=current_app.config["GEMINI_MAX_OUTPUT_TOKENS"],
        )
    except GeminiReviewError as exc:
        flash(str(exc), "error")
        return render_template("prompts/new.html"), 502

    review = PromptReview(
        user_id=current_user.id,
        source_prompt=source_prompt,
        review_goal=review_goal,
        assembled_prompt=assembled_prompt,
        review_result=review_result,
        model_name=model,
    )
    db.session.add(review)
    db.session.commit()

    flash("프롬프트 점검 결과를 저장했습니다.", "success")
    return redirect(url_for("prompts.show", review_id=review.id))


@prompts_bp.get("/<int:review_id>")
@login_required
def show(review_id: int):
    review = PromptReview.query.filter_by(id=review_id, user_id=current_user.id).first_or_404()
    return render_template("prompts/show.html", review=review)


def _get_user_api_key() -> UserApiKey | None:
    return UserApiKey.query.filter_by(user_id=current_user.id, provider=PROVIDER).first()


def _daily_review_limit_exceeded() -> bool:
    limit = current_app.config.get("MAX_DAILY_AI_CALLS_PER_USER", 50)
    if limit <= 0:
        return False
    today_start = datetime.combine(datetime.now().date(), time.min)
    reviews_today = PromptReview.query.filter(
        PromptReview.user_id == current_user.id,
        PromptReview.created_at >= today_start,
    ).count()
    return reviews_today >= limit
