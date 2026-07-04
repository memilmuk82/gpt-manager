from app.extensions import db
from app.models import PromptReview, User, UserApiKey
from app.services.encryption_service import encrypt_llm_key
from app.services.prompt_review_service import build_review_prompt


class FakeAdapter:
    def __init__(self, calls):
        self.calls = calls

    def generate_text(self, **kwargs):
        self.calls.append(kwargs)
        return "판정: 수정 후 채택\n\n1. 정리된 요청\n- 요청이 정리되었습니다."


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


def save_api_key(user: User, raw_api_key="gemini-secret-key-9999", provider="gemini", model="gemini-3.1-flash-lite") -> UserApiKey:
    user_api_key = UserApiKey(
        user_id=user.id,
        provider=provider,
        encrypted_api_key=encrypt_llm_key(raw_api_key),
        key_last4=raw_api_key[-4:],
        selected_model=model,
        is_active=True,
    )
    db.session.add(user_api_key)
    db.session.commit()
    return user_api_key


def test_prompt_review_requires_login(client):
    response = client.get("/prompt-reviews/new")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_prompt_review_requires_api_key_when_no_runtime_key(client, app):
    with app.app_context():
        create_user()

    login(client)
    response = client.post(
        "/prompt-reviews",
        data={"provider": "gemini", "source_prompt": "수업 안내문을 작성해줘", "review_goal": "명확성 개선"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/settings/api-key?provider=gemini")
    with app.app_context():
        assert PromptReview.query.count() == 0


def test_prompt_review_menu_and_pages_match_current_design(client, app):
    with app.app_context():
        create_user()

    login(client)
    dashboard_response = client.get("/dashboard")
    index_response = client.get("/prompt-reviews")
    new_response = client.get("/prompt-reviews/new")

    dashboard_html = dashboard_response.get_data(as_text=True)
    index_html = index_response.get_data(as_text=True)
    new_html = new_response.get_data(as_text=True)

    assert dashboard_response.status_code == 200
    assert index_response.status_code == 200
    assert new_response.status_code == 200
    assert "프롬프트 정리" in dashboard_html
    assert "구조화된 프롬프트로 정리" in index_html
    assert "✓ 새 프롬프트 정리" in new_html
    assert "PROMPT REVIEWS" not in index_html


def test_prompt_review_create_saves_mocked_result_with_stored_key(client, app, monkeypatch):
    calls = []
    monkeypatch.setattr("app.prompts.routes.get_adapter", lambda provider: FakeAdapter(calls))

    with app.app_context():
        user = create_user()
        save_api_key(user, "gemini-secret-key-9999")

    login(client)
    response = client.post(
        "/prompt-reviews",
        data={
            "provider": "gemini",
            "model": "gemini-3.1-flash-lite",
            "source_prompt": "5학년 과학 수업 활동을 만들어줘",
            "review_goal": "수업 활용성 개선",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        review = PromptReview.query.one()
        api_key = UserApiKey.query.one()
        assert review.provider == "gemini"
        assert review.review_goal == "수업 활용성 개선"
        assert review.model_name == "gemini-3.1-flash-lite"
        assert "5학년 과학 수업" in review.source_prompt
        assert "점검 목표: 수업 활용성 개선" in review.assembled_prompt
        assert "판정" in review.review_result
        assert api_key.last_used_at is not None

    assert calls[0]["api_key"] == "gemini-secret-key-9999"
    assert calls[0]["model"] == "gemini-3.1-flash-lite"
    assert calls[0]["messages"][0]["role"] == "system"
    assert "5학년 과학 수업" in calls[0]["messages"][1]["content"]


def test_prompt_review_create_uses_runtime_key_without_storing(client, app, monkeypatch):
    calls = []
    monkeypatch.setattr("app.prompts.routes.get_adapter", lambda provider: FakeAdapter(calls))

    with app.app_context():
        create_user()

    login(client)
    response = client.post(
        "/prompt-reviews",
        data={
            "provider": "openai",
            "model": "gpt-5.5",
            "runtime_api_key": "runtime-openai-key-1234",
            "source_prompt": "회의록을 정리해줘",
            "review_goal": "문서 작성 요청 정리",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        assert UserApiKey.query.count() == 0
        review = PromptReview.query.one()
        assert review.provider == "openai"
        assert review.model_name == "gpt-5.5"
    assert calls[0]["api_key"] == "runtime-openai-key-1234"


def test_prompt_review_rejects_too_long_input(client, app):
    app.config["GEMINI_MAX_INPUT_CHARS"] = 5
    with app.app_context():
        user = create_user()
        save_api_key(user)

    login(client)
    response = client.post(
        "/prompt-reviews",
        data={"provider": "gemini", "source_prompt": "123456", "review_goal": "길이 제한"},
    )

    assert response.status_code == 400
    with app.app_context():
        assert PromptReview.query.count() == 0


def test_prompt_review_enforces_daily_limit(client, app, monkeypatch):
    app.config["MAX_DAILY_AI_CALLS_PER_USER"] = 1
    app.config["AI_REQUEST_COOLDOWN_SECONDS"] = 0
    calls = []
    monkeypatch.setattr("app.prompts.routes.get_adapter", lambda provider: FakeAdapter(calls))

    with app.app_context():
        user = create_user()
        save_api_key(user)

    login(client)
    first_response = client.post(
        "/prompt-reviews",
        data={"provider": "gemini", "source_prompt": "첫 번째 프롬프트", "review_goal": "점검"},
        follow_redirects=False,
    )
    second_response = client.post(
        "/prompt-reviews",
        data={"provider": "gemini", "source_prompt": "두 번째 프롬프트", "review_goal": "점검"},
        follow_redirects=False,
    )

    assert first_response.status_code == 302
    assert second_response.status_code == 429
    assert "오늘 사용할 수 있는 AI" in second_response.get_data(as_text=True)
    with app.app_context():
        assert PromptReview.query.count() == 1


def test_prompt_review_enforces_cooldown(client, app, monkeypatch):
    app.config["MAX_DAILY_AI_CALLS_PER_USER"] = 20
    app.config["AI_REQUEST_COOLDOWN_SECONDS"] = 5
    calls = []
    monkeypatch.setattr("app.prompts.routes.get_adapter", lambda provider: FakeAdapter(calls))

    with app.app_context():
        user = create_user()
        save_api_key(user)

    login(client)
    first_response = client.post("/prompt-reviews", data={"provider": "gemini", "source_prompt": "첫 번째", "review_goal": "점검"})
    second_response = client.post("/prompt-reviews", data={"provider": "gemini", "source_prompt": "두 번째", "review_goal": "점검"})

    assert first_response.status_code == 302
    assert second_response.status_code == 429
    assert "연속 요청" in second_response.get_data(as_text=True)


def test_user_cannot_view_another_users_prompt_review(client, app):
    with app.app_context():
        create_user()
        other = create_user(email="other@example.com", name="Other")
        db.session.add(
            PromptReview(
                user_id=other.id,
                provider="gemini",
                source_prompt="다른 사용자 프롬프트",
                review_goal="비공개",
                assembled_prompt="assembled",
                review_result="secret",
                model_name="gemini-3.1-flash-lite",
            )
        )
        db.session.commit()

    login(client)
    index_response = client.get("/prompt-reviews")
    show_response = client.get("/prompt-reviews/1")

    assert index_response.status_code == 200
    assert "다른 사용자 프롬프트" not in index_response.get_data(as_text=True)
    assert show_response.status_code == 404


def test_build_review_prompt_contains_required_sections():
    assembled = build_review_prompt("자료를 요약해줘", "안전성 점검")

    assert "점검 목표: 안전성 점검" in assembled
    assert "원본 프롬프트:" in assembled
    assert "판정: 채택 / 수정 후 채택 / 보류 / 폐기" in assembled
    assert "최종 프롬프트" in assembled


def test_prompt_review_markdown_download_and_search(client, app):
    with app.app_context():
        user = create_user()
        db.session.add(
            PromptReview(
                user_id=user.id,
                provider="gemini",
                source_prompt="행정 안내문 작성",
                review_goal="행정 문서 개선",
                assembled_prompt="assembled",
                review_result="개선 결과",
                model_name="gemini-3.1-flash-lite",
            )
        )
        db.session.commit()

    login(client)
    index_response = client.get("/prompt-reviews?q=행정")
    download_response = client.get("/prompt-reviews/1/download.md")

    assert index_response.status_code == 200
    assert "행정 문서 개선" in index_response.get_data(as_text=True)
    assert download_response.status_code == 200
    assert "text/markdown" in download_response.headers["Content-Type"]
    body = download_response.get_data(as_text=True)
    assert "# 프롬프트 정리 결과 #1" in body
    assert "Provider: Google Gemini" in body
    assert "행정 안내문 작성" in body
    assert "개선 결과" in body


def test_prompt_review_new_page_shows_templates_and_providers(client, app):
    with app.app_context():
        create_user()

    login(client)
    response = client.get("/prompt-reviews/new")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "정리 템플릿" in body
    assert "수업자료" in body
    assert "행정문서" in body
    assert "코드 수정" in body
    assert "OpenAI" in body
    assert "Anthropic Claude" in body
