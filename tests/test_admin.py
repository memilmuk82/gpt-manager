from app.extensions import db
from app.models import AiResource, AppSetting, ApprovalStatus, GuideItem, User, WorkType


def create_user(email="teacher@senedu.kr", name="Teacher", role="user", approval_status="approved") -> User:
    user = User(email=email, name=name, role=role, approval_status=approval_status)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email="teacher@senedu.kr", password="password123"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_admin_dashboard_requires_admin_role(client, app):
    with app.app_context():
        create_user()

    login(client)
    response = client.get("/admin")

    assert response.status_code == 403


def test_admin_can_view_and_approve_pending_user(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        pending = create_user(email="external@gmail.com", name="External", approval_status="pending")
        pending_id = pending.id

    login(client, email="admin@senedu.kr")
    users_response = client.get("/admin/users")

    assert users_response.status_code == 200
    assert "external@gmail.com" in users_response.get_data(as_text=True)

    approve_response = client.post(f"/admin/users/{pending_id}/approve", follow_redirects=False)

    assert approve_response.status_code == 302
    with app.app_context():
        assert db.session.get(User, pending_id).approval_status == ApprovalStatus.APPROVED


def test_admin_cannot_suspend_self(client, app):
    with app.app_context():
        admin = create_user(email="admin@senedu.kr", name="Admin", role="admin")
        admin_id = admin.id

    login(client, email="admin@senedu.kr")
    response = client.post(f"/admin/users/{admin_id}/suspend", follow_redirects=False)

    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(User, admin_id).approval_status == ApprovalStatus.APPROVED


def test_assistant_admin_can_access_admin_dashboard(client, app):
    with app.app_context():
        create_user(email="assistant@senedu.kr", name="Assistant", role="assistant_admin")

    login(client, email="assistant@senedu.kr")

    dashboard_response = client.get("/admin")
    users_response = client.get("/admin/users")

    assert dashboard_response.status_code == 200
    assert users_response.status_code == 200


def test_admin_can_manage_resources_and_work_types_for_reservation_form(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        resource = AiResource(name="기존 리소스", provider="OpenAI", is_active=True)
        work_type = WorkType(name="기존 업무", sort_order=10, is_active=True)
        db.session.add_all([resource, work_type])
        db.session.commit()
        resource_id = resource.id
        work_type_id = work_type.id

    login(client, email="admin@senedu.kr")
    resource_response = client.post(
        "/admin/resources",
        data={
            f"resource_{resource_id}_name": "수정 리소스",
            f"resource_{resource_id}_provider": "OpenAI",
            f"resource_{resource_id}_description": "수정 설명",
            f"resource_{resource_id}_is_active": "on",
            "new_resource_name": "새 리소스",
            "new_resource_provider": "OpenAI",
            "new_resource_description": "새 설명",
            "new_resource_is_active": "on",
        },
        follow_redirects=False,
    )
    work_type_response = client.post(
        "/admin/work-types",
        data={
            f"work_type_{work_type_id}_name": "수정 업무",
            f"work_type_{work_type_id}_sort_order": "10",
            f"work_type_{work_type_id}_is_active": "on",
            "new_work_type_name": "새 업무",
            "new_work_type_sort_order": "20",
            "new_work_type_is_active": "on",
        },
        follow_redirects=False,
    )

    assert resource_response.status_code == 302
    assert work_type_response.status_code == 302
    form_response = client.get("/reservations/new")
    body = form_response.get_data(as_text=True)
    assert "수정 리소스 (OpenAI)" in body
    assert "새 리소스 (OpenAI)" in body
    assert "수정 업무" in body
    assert "새 업무" in body


def test_admin_guides_can_update_gpt_access_messages(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        db.session.add_all([
            AppSetting(key="board_reference_message", value="기존 접속 안내", label="접속 안내", help_text="", sort_order=1),
            AppSetting(key="auth_message", value="기존 인증 안내", label="인증 안내", help_text="", sort_order=2),
            AppSetting(key="logout_notice", value="기존 로그아웃 안내", label="로그아웃 안내", help_text="", sort_order=3),
            GuideItem(code="GUIDE_TEST", category="테스트", title="테스트 안내", body="본문", sort_order=1, is_active=True),
        ])
        db.session.commit()
        guide = GuideItem.query.filter_by(code="GUIDE_TEST").one()

    login(client, email="admin@senedu.kr")
    response = client.post(
        "/admin/guides",
        data={
            "setting_board_reference_message": "새 접속 안내",
            "setting_auth_message": "새 인증 안내",
            "setting_logout_notice": "새 로그아웃 안내",
            f"guide_{guide.id}_category": "테스트",
            f"guide_{guide.id}_title": "테스트 안내",
            f"guide_{guide.id}_sort_order": "1",
            f"guide_{guide.id}_is_active": "on",
            f"guide_{guide.id}_body": "본문",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    dashboard = client.get("/dashboard")
    body = dashboard.get_data(as_text=True)
    assert "새 접속 안내" in body
    assert "새 인증 안내" in body
    assert "새 로그아웃 안내" in body


def test_auth_manager_is_limited_to_two_users(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        manager1 = create_user(email="manager1@senedu.kr", name="Manager 1")
        manager1.is_auth_manager = True
        manager1.is_active = True
        manager2 = create_user(email="manager2@senedu.kr", name="Manager 2")
        manager2.is_auth_manager = True
        manager2.is_active = True
        target = create_user(email="manager3@senedu.kr", name="Manager 3")
        db.session.commit()
        target_id = target.id

    login(client, email="admin@senedu.kr")
    response = client.post(
        f"/admin/users/{target_id}/update",
        data={
            "name": "Manager 3",
            "department": "정보부",
            "extension": "333",
            "role": "user",
            "sort_order": "100",
            "is_active": "on",
            "is_auth_manager": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "인증번호 담당자는 최대 2명까지만 지정할 수 있습니다." in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.get(User, target_id).is_auth_manager is False


def test_admin_pytest_command_falls_back_to_uv_when_pytest_module_is_missing(monkeypatch):
    from app.admin import routes

    monkeypatch.setattr(routes.importlib.util, "find_spec", lambda name: None)
    monkeypatch.setattr(routes.shutil, "which", lambda name: "/usr/local/bin/uv" if name == "uv" else None)

    assert routes._pytest_command() == ["/usr/local/bin/uv", "run", "--frozen", "pytest"]


def test_admin_pytest_command_uses_current_python_when_pytest_module_exists(monkeypatch):
    from app.admin import routes

    monkeypatch.setattr(routes.importlib.util, "find_spec", lambda name: object())

    assert routes._pytest_command() == [routes.sys.executable, "-m", "pytest"]


def test_admin_configurable_page_copy_is_rendered(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        db.session.add_all([
            AppSetting(key="auth_info_title", value="공용 GPT 로그인 안내", label="GPT 접속 안내 제목", help_text="", sort_order=1),
            AppSetting(key="reservation_intro_text", value="신청 화면 첫 문구", label="사용 신청 안내 문구", help_text="", sort_order=2),
            AppSetting(key="reservation_helper_text", value="신청 화면 두 번째 문구", label="사용 신청 보조 문구", help_text="", sort_order=3),
            AppSetting(key="guide_intro_text", value="사용 안내 소개 문구", label="사용 안내 소개 문구", help_text="", sort_order=4),
        ])
        db.session.commit()

    login(client, email="admin@senedu.kr")

    dashboard_body = client.get("/dashboard").get_data(as_text=True)
    reservation_body = client.get("/reservations/new").get_data(as_text=True)
    guide_body = client.get("/guide").get_data(as_text=True)

    assert "공용 GPT 로그인 안내" in dashboard_body
    assert "신청 화면 첫 문구" in reservation_body
    assert "신청 화면 두 번째 문구" in reservation_body
    assert "사용 안내 소개 문구" in guide_body


def test_guide_page_shows_quick_links_for_all_active_guides(client, app):
    with app.app_context():
        create_user(email="admin@senedu.kr", name="Admin", role="admin")
        for index, category in enumerate(["적합", "부적합", "민감정보", "평가보안", "학생부"], start=1):
            db.session.add(
                GuideItem(
                    code=f"GUIDE_QUICK_{index}",
                    category=category,
                    title=f"{category} 안내",
                    body="본문",
                    sort_order=index,
                    is_active=True,
                )
            )
        db.session.commit()

    login(client, email="admin@senedu.kr")
    response = client.get("/guide")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    for label in ["적합 상세", "부적합 상세", "민감정보 상세", "평가보안 상세", "학생부 상세"]:
        assert label in body
