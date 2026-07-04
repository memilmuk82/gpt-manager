from datetime import datetime, timedelta, timezone

from flask import Response, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import PromptReview, UserApiKey
from app.prompts import prompts_bp
from app.services.encryption_service import EncryptionError, decrypt_llm_key
from app.services.llm.errors import LLMProviderError
from app.services.llm.registry import (
    PROVIDER_DEFINITIONS,
    default_model,
    get_adapter,
    normalize_provider,
    provider_choices,
    recommended_models,
)
from app.services.prompt_review_service import build_review_prompt


PROMPT_TEMPLATES = [
    {
        "name": "수업자료",
        "goal": "수업자료 제작 요청을 실행 가능한 프롬프트로 정리",
        "prompt": "대상 학년과 교과, 수업 목표, 활동 시간, 필요한 산출물을 포함해 수업자료 제작 요청을 정리합니다.",
    },
    {
        "name": "행정문서",
        "goal": "행정문서 작성 요청을 핵심 항목과 제약 조건 중심으로 정리",
        "prompt": "수신 대상, 목적, 필수 포함 항목, 톤앤매너를 포함해 행정문서 초안 작성 요청을 정리합니다.",
    },
    {
        "name": "코드 수정",
        "goal": "코드 수정 요청을 파일 구조, 재현 방법, 완료 기준 중심으로 정리",
        "prompt": "수정 대상 파일, 현재 증상, 원하는 동작, 실행 방법, 테스트 기준을 포함해 코드 작업 지시문을 정리합니다.",
    },
    {
        "name": "Codex 작업 지시문",
        "goal": "Codex가 바로 수행할 수 있는 작업 지시문으로 정리",
        "prompt": "목표, 변경 범위, 금지 사항, 검증 방법, 커밋/푸시 여부를 포함해 Codex 작업 지시문을 정리합니다.",
    },
]

SYSTEM_PROMPT = """한국어로 답변하세요. 결론과 판정을 먼저 제시하세요.
당신은 사용자의 의견에 무조건 동의하지 않는 비판적 사고 파트너입니다.
좋은 아이디어는 구체적으로 인정하고, 약한 아이디어는 근거를 들어 반박하세요.
반대를 위한 반대, 냉소, 인신공격은 금지합니다.
수업, 코드, 문서 작업은 실행 가능한 형태로 제시하세요.
코드 작업은 파일 구조, 설치 명령어, 실행 방법, 흔한 오류와 해결 방법을 포함하세요.
선택지가 많으면 추천 1순위와 버릴 선택지를 분명히 제시하세요.
최신 정보, 가격, 정책, 제품, 라이브러리 버전은 확인 필요로 표시하세요.
학교 현장과 학생 수준에 맞는 실용성을 우선하고, 비효율적이거나 교육적으로 약한 방향은 분명히 지적하세요.
""".strip()


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
                PromptReview.provider.ilike(like),
            )
        )
    reviews = query.order_by(PromptReview.created_at.desc()).all()
    return render_template("prompts/index.html", reviews=reviews, query_text=query_text)


@prompts_bp.get("/new")
@login_required
def new():
    provider = _selected_provider()
    return _render_new(provider)


@prompts_bp.post("")
@login_required
def create():
    provider = _selected_provider()
    source_prompt = request.form.get("source_prompt", "").strip()
    review_goal = request.form.get("review_goal", "").strip() or "요청 의도 명확화와 실행 가능한 프롬프트 정리"
    max_input_chars = current_app.config["GEMINI_MAX_INPUT_CHARS"]

    if not source_prompt:
        flash("정리할 요청을 입력하세요.", "error")
        return _render_new(provider), 400
    if len(source_prompt) > max_input_chars:
        flash(f"요청은 {max_input_chars}자 이하로 입력하세요.", "error")
        return _render_new(provider), 400

    limit_message = _usage_limit_message()
    if limit_message:
        flash(limit_message, "error")
        return _render_new(provider), 429

    selected_model = request.form.get("model", "").strip()
    raw_api_key = request.form.get("runtime_api_key", "").strip()
    user_api_key = _get_user_api_key(provider)
    used_stored_key = False

    if not raw_api_key:
        if user_api_key is None or not user_api_key.is_active:
            flash("저장하지 않는 모드에서는 이 화면에서 API Key를 일회성으로 입력하거나, 사용자 설정에서 Provider별 키를 암호화 저장하세요.", "error")
            return redirect(url_for("settings.api_key", provider=provider))
        try:
            raw_api_key = decrypt_llm_key(user_api_key.encrypted_api_key)
        except EncryptionError as exc:
            flash(str(exc), "error")
            return redirect(url_for("settings.api_key", provider=provider))
        used_stored_key = True

    model = selected_model or (user_api_key.selected_model if user_api_key else "") or default_model(provider)
    assembled_prompt = build_review_prompt(source_prompt, review_goal)
    try:
        review_result = get_adapter(provider).generate_text(
            api_key=raw_api_key,
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": assembled_prompt},
            ],
            options={"max_output_tokens": current_app.config["GEMINI_MAX_OUTPUT_TOKENS"]},
        )
    except LLMProviderError as exc:
        flash(str(exc), "error")
        return _render_new(provider), 502

    review = PromptReview(
        user_id=current_user.id,
        provider=provider,
        source_prompt=source_prompt,
        review_goal=review_goal,
        assembled_prompt=assembled_prompt,
        review_result=review_result,
        model_name=model,
    )
    db.session.add(review)
    if used_stored_key and user_api_key is not None:
        user_api_key.last_used_at = datetime.now(timezone.utc)
    db.session.commit()

    flash("프롬프트 정리 결과를 저장했습니다.", "success")
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


def _render_new(provider: str):
    user_api_keys = UserApiKey.query.filter_by(user_id=current_user.id).order_by(UserApiKey.provider.asc()).all()
    selected_key = _get_user_api_key(provider)
    selected_model = (selected_key.selected_model if selected_key else "") or default_model(provider)
    model_options = recommended_models(provider)
    if selected_model not in model_options:
        model_options = [selected_model, *model_options]
    return render_template(
        "prompts/new.html",
        prompt_templates=PROMPT_TEMPLATES,
        providers=provider_choices(),
        provider_definitions=PROVIDER_DEFINITIONS,
        selected_provider=provider,
        selected_key=selected_key,
        user_api_keys=user_api_keys,
        model_options=model_options,
        selected_model=selected_model,
    )


def _selected_provider() -> str:
    try:
        return normalize_provider(request.values.get("provider") or "gemini")
    except ValueError:
        flash("지원하지 않는 AI Provider입니다.", "error")
        return "gemini"


def _get_user_api_key(provider: str) -> UserApiKey | None:
    return UserApiKey.query.filter_by(user_id=current_user.id, provider=provider).first()


def _review_markdown(review: PromptReview) -> str:
    provider_label = PROVIDER_DEFINITIONS.get(review.provider, PROVIDER_DEFINITIONS["gemini"]).label
    return "\n".join(
        [
            f"# 프롬프트 정리 결과 #{review.id}",
            "",
            f"- 생성일: {review.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"- Provider: {provider_label}",
            f"- 모델: {review.model_name}",
            f"- 정리 목표: {review.review_goal}",
            "",
            "## 원본 요청",
            "",
            review.source_prompt,
            "",
            "## 정리 결과",
            "",
            review.review_result,
            "",
        ]
    )


def _usage_limit_message() -> str:
    now = datetime.now(timezone.utc)
    daily_limit = current_app.config.get("MAX_DAILY_AI_CALLS_PER_USER", 20)
    if daily_limit > 0 and _count_reviews_since(now - timedelta(days=1)) >= daily_limit:
        return "오늘 사용할 수 있는 AI 프롬프트 정리 횟수를 모두 사용했습니다."

    monthly_limit = current_app.config.get("MAX_MONTHLY_AI_CALLS_PER_USER", 500)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    if monthly_limit > 0 and _count_reviews_since(month_start) >= monthly_limit:
        return "이번 달 사용할 수 있는 AI 프롬프트 정리 횟수를 모두 사용했습니다."

    cooldown = current_app.config.get("AI_REQUEST_COOLDOWN_SECONDS", 5)
    latest = PromptReview.query.filter_by(user_id=current_user.id).order_by(PromptReview.created_at.desc()).first()
    if latest is not None and cooldown > 0:
        latest_at = _aware(latest.created_at)
        if latest_at >= now - timedelta(seconds=cooldown):
            return f"{cooldown}초 이내 연속 요청은 차단됩니다. 잠시 후 다시 시도하세요."
    return ""


def _count_reviews_since(cutoff: datetime) -> int:
    count = 0
    for review in PromptReview.query.filter_by(user_id=current_user.id).all():
        if _aware(review.created_at) >= cutoff:
            count += 1
    return count


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
