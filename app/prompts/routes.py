from datetime import datetime, timedelta, timezone

from flask import Response, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import PromptReview, UserApiKey
from app.prompts import prompts_bp
from app.services.encryption_service import EncryptionError, decrypt_text
from app.services.prompt_review_service import GeminiReviewError, build_review_prompt, call_gemini_review


PROVIDER = "gemini"

PROMPT_TEMPLATES = [
    {
        "name": "수업자료",
        "goal": "수업자료의 명확성, 활동 가능성, 안전성 개선",
        "prompt": "대상 학년과 교과, 수업 목표, 활동 시간, 필요한 산출물을 포함해 수업자료 제작 프롬프트를 작성합니다.",
    },
    {
        "name": "행정문서",
        "goal": "행정문서의 문체, 핵심 항목, 개인정보 노출 위험 점검",
        "prompt": "수신 대상, 목적, 필수 포함 항목, 톤앤매너를 포함해 행정문서 초안 작성 프롬프트를 작성합니다.",
    },
    {
        "name": "평가문항 검토",
        "goal": "평가 보안 자료 없이 문항 품질 점검 관점만 개선",
        "prompt": "실제 문항이나 정답을 넣지 않고 평가 기준, 난이도, 사고 과정, 오류 가능성 점검 요청을 작성합니다.",
    },
    {
        "name": "가정통신문",
        "goal": "학부모 안내문의 이해도, 누락 항목, 민감정보 위험 점검",
        "prompt": "행사명, 일시, 장소, 준비물, 문의처, 유의사항을 포함해 가정통신문 초안 요청을 작성합니다.",
    },
]


@prompts_bp.get("")
@login_required
def index():
    query_text = request.args.get("q", "").strip()
    query = PromptReview.query.filter_by(user_id=current_user.id)
    if query_text:
        like = f"%{query_text}%"
        query = query.filter(
            or_(
                PromptReview.review_goal.ilike(like),
                PromptReview.source_prompt.ilike(like),
                PromptReview.review_result.ilike(like),
            )
        )
    reviews = query.order_by(PromptReview.created_at.desc()).all()
    return render_template("prompts/index.html", reviews=reviews, query_text=query_text)


@prompts_bp.get("/new")
@login_required
def new():
    return render_template("prompts/new.html", prompt_templates=PROMPT_TEMPLATES)


@prompts_bp.post("")
@login_required
def create():
    source_prompt = request.form.get("source_prompt", "").strip()
    review_goal = request.form.get("review_goal", "").strip() or "명확성, 안전성, 수업 활용성 개선"
    max_input_chars = current_app.config["GEMINI_MAX_INPUT_CHARS"]

    if not source_prompt:
        flash("점검할 프롬프트를 입력하세요.", "error")
        return render_template("prompts/new.html", prompt_templates=PROMPT_TEMPLATES), 400
    if len(source_prompt) > max_input_chars:
        flash(f"프롬프트는 {max_input_chars}자 이하로 입력하세요.", "error")
        return render_template("prompts/new.html", prompt_templates=PROMPT_TEMPLATES), 400
    if _daily_review_limit_exceeded():
        flash("오늘 사용할 수 있는 Gemini 프롬프트 점검 횟수를 모두 사용했습니다.", "error")
        return render_template("prompts/new.html", prompt_templates=PROMPT_TEMPLATES), 429

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
        return render_template("prompts/new.html", prompt_templates=PROMPT_TEMPLATES), 502

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


@prompts_bp.get("/<int:review_id>/download.md")
@login_required
def download(review_id: int):
    review = PromptReview.query.filter_by(id=review_id, user_id=current_user.id).first_or_404()
    filename = f"prompt-review-{review.id}.md"
    return Response(
        _review_markdown(review),
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _get_user_api_key() -> UserApiKey | None:
    return UserApiKey.query.filter_by(user_id=current_user.id, provider=PROVIDER).first()


def _review_markdown(review: PromptReview) -> str:
    return "\n".join(
        [
            f"# 프롬프트 점검 결과 #{review.id}",
            "",
            f"- 생성일: {review.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"- 모델: {review.model_name}",
            f"- 점검 목표: {review.review_goal}",
            "",
            "## 원본 프롬프트",
            "",
            review.source_prompt,
            "",
            "## Gemini 점검 결과",
            "",
            review.review_result,
            "",
        ]
    )


def _daily_review_limit_exceeded() -> bool:
    limit = current_app.config.get("MAX_DAILY_AI_CALLS_PER_USER", 50)
    if limit <= 0:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    recent_reviews = 0
    for review in PromptReview.query.filter_by(user_id=current_user.id).all():
        created_at = review.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if created_at >= cutoff:
            recent_reviews += 1
    return recent_reviews >= limit
