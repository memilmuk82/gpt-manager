from app import create_app
from app.services import legal_markdown_service


def test_footer_links_and_manager_info_are_visible(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Copyright © 2026 GPT Share Manager vNext" in body
    assert "이용약관" in body
    assert "개인정보처리방침" in body
    assert "정보관리책임자" in body
    assert "이진선" in body
    assert "070-4390-8235" in body
    assert "memilmuk82@senedu.kr" in body
    assert "/terms" in body
    assert "/privacy" in body


def test_terms_page_renders_markdown_document(client):
    response = client.get("/terms")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "이용약관" in body
    assert "GPT Share Manager vNext" in body
    assert "공용 AI 계정 예약 서비스" in body or "공용 생성형 AI 계정" in body
    assert "AI 결과에 대한 면책" in body


def test_privacy_page_renders_markdown_document(client):
    response = client.get("/privacy")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "개인정보처리방침" in body
    assert "Google OAuth" in body
    assert "Gemini API" in body
    assert "비밀번호 해시" in body
    assert "이진선" in body


def test_pending_user_can_access_legal_pages(client, app):
    from app.extensions import db
    from app.models import User

    with app.app_context():
        user = User(email="pending@example.com", name="Pending", approval_status="pending")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    client.post(
        "/auth/login",
        data={"email": "pending@example.com", "password": "password123"},
        follow_redirects=False,
    )

    assert client.get("/terms").status_code == 200
    assert client.get("/privacy").status_code == 200


def test_markdown_changes_are_reflected_and_html_is_escaped(client, tmp_path, monkeypatch):
    legal_file = tmp_path / "TERMS.md"
    legal_file.write_text("# 테스트 약관\n\n<script>alert('xss')</script>\n\n- 변경된 항목", encoding="utf-8")
    monkeypatch.setattr(legal_markdown_service, "LEGAL_DOCUMENTS", {"terms": legal_file})

    response = client.get("/terms")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "테스트 약관" in body
    assert "변경된 항목" in body
    assert "<script>alert" not in body
    assert "&lt;script&gt;alert" in body
