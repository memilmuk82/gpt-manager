#!/usr/bin/env python3
"""Seed review/demo data for the GPT manager app.

The script is intentionally idempotent for the built-in demo tag. It removes
previous records created for the same tag, then recreates a realistic set of
users, AI resources, reservations, usage logs, prompt reviews, API keys, and
audit logs.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import (
    AiResource,
    AppSetting,
    AuditLog,
    ApprovalStatus,
    PromptReview,
    Reservation,
    ReservationStatus,
    UsageLog,
    User,
    UserApiKey,
    WorkType,
)
from app.services.encryption_service import encrypt_text

TAG = "RC 운영 CRUD 검증 1782896313"
DEMO_PASSWORD = "DemoUser!2026"
DEMO_EMAILS = {
    "admin": "rc.admin.1782896313@senedu.kr",
    "assistant": "rc.assistant.1782896313@senedu.kr",
    "kim": "rc.teacher.kim.1782896313@senedu.kr",
    "lee": "rc.teacher.lee.1782896313@senedu.kr",
    "park": "rc.teacher.park.1782896313@senedu.kr",
    "suspended": "rc.suspended.1782896313@senedu.kr",
}


@dataclass(frozen=True)
class DemoUserSpec:
    key: str
    name: str
    department: str
    extension: str
    role: str = "user"
    active: bool = True
    approval_status: str = ApprovalStatus.APPROVED
    is_auth_manager: bool = False
    sort_order: int = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed RC demo data.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Base date for today/calendar demo data. Default: today.",
    )
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="Remove demo data for the built-in tag without recreating it.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_date = date.fromisoformat(args.date)
    app = create_app()
    with app.app_context():
        clear_demo_data()
        if args.clear_only:
            db.session.commit()
            print(f"seed_tag={TAG}")
            print("cleared=true")
            return
        users = seed_users()
        resources = seed_resources()
        work_types = seed_work_types()
        seed_settings()
        reservations = seed_reservations(base_date, users, resources, work_types)
        seed_usage_logs(base_date, users, resources, work_types, reservations)
        seed_prompt_reviews(base_date, users)
        seed_api_keys(users)
        seed_audit_logs(base_date, users)
        db.session.commit()
        print_summary(base_date, users, resources, reservations)


def clear_demo_data() -> None:
    demo_users = User.query.filter(User.email.in_(DEMO_EMAILS.values())).all()
    demo_user_ids = [user.id for user in demo_users]

    if demo_user_ids:
        PromptReview.query.filter(PromptReview.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
        UserApiKey.query.filter(UserApiKey.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
        UsageLog.query.filter(UsageLog.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
        Reservation.query.filter(Reservation.user_id.in_(demo_user_ids)).delete(synchronize_session=False)
        AuditLog.query.filter(AuditLog.actor_user_id.in_(demo_user_ids)).delete(synchronize_session=False)

    UsageLog.query.filter(UsageLog.summary.ilike(f"%{TAG}%")).delete(synchronize_session=False)
    PromptReview.query.filter(PromptReview.source_prompt.ilike(f"%{TAG}%")).delete(synchronize_session=False)
    Reservation.query.filter(Reservation.purpose.ilike(f"%{TAG}%")).delete(synchronize_session=False)
    AuditLog.query.filter(AuditLog.summary.ilike(f"%{TAG}%")).delete(synchronize_session=False)

    if demo_user_ids:
        User.query.filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)

    AiResource.query.filter(AiResource.name.ilike(f"%{TAG}%")).delete(synchronize_session=False)
    WorkType.query.filter(WorkType.name.ilike(f"%{TAG}%")).delete(synchronize_session=False)
    db.session.flush()


def seed_users() -> dict[str, User]:
    specs = [
        DemoUserSpec("admin", "RC 관리자", "AI컴퓨터과", "2101", "admin", True, ApprovalStatus.APPROVED, False, 1),
        DemoUserSpec("assistant", "RC 보조관리자", "교육정보부", "2102", "assistant_admin", True, ApprovalStatus.APPROVED, True, 2),
        DemoUserSpec("kim", "김도연", "AI컴퓨터과", "2311", "user", True, ApprovalStatus.APPROVED, True, 10),
        DemoUserSpec("lee", "이서준", "스마트팩토리과", "2412", "user", True, ApprovalStatus.APPROVED, False, 20),
        DemoUserSpec("park", "박민지", "콘텐츠디자인과", "2513", "user", True, ApprovalStatus.APPROVED, False, 30),
        DemoUserSpec("suspended", "정지사용자", "테스트부서", "2999", "user", False, ApprovalStatus.SUSPENDED, False, 99),
    ]
    users = {}
    for spec in specs:
        user = User(
            email=DEMO_EMAILS[spec.key],
            name=spec.name,
            department=spec.department,
            extension=spec.extension,
            role=spec.role,
            auth_provider="local",
            approval_status=spec.approval_status,
            is_active=spec.active,
            is_auth_manager=spec.is_auth_manager,
            sort_order=spec.sort_order,
        )
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
        users[spec.key] = user
    db.session.flush()
    return users


def seed_resources() -> dict[str, AiResource]:
    specs = {
        "gpt": (f"{TAG} - GPT Pro 5X", "OpenAI", "장시간 추론과 코드 검토 시연용 리소스"),
        "gemini": (f"{TAG} - Gemini Education Plus", "Google", "프롬프트 점검과 수업자료 검토 시연용 리소스"),
        "notebook": (f"{TAG} - NotebookLM Plus", "Google", "복수 문서 종합 분석 시연용 리소스"),
        "backup": (f"{TAG} - 예비 공용 계정", "OpenAI", "장애 대응과 예비 예약 시나리오용 리소스"),
    }
    resources = {}
    for key, (name, provider, description) in specs.items():
        resource = AiResource(name=name, provider=provider, description=description, is_active=True)
        db.session.add(resource)
        resources[key] = resource
    db.session.flush()
    return resources


def seed_work_types() -> list[str]:
    names = [
        f"{TAG} - 장시간 추론",
        f"{TAG} - 수업자료 검토",
        f"{TAG} - 코드/DB 설계 검토",
        f"{TAG} - 월간 운영 보고서 점검",
    ]
    for index, name in enumerate(names, start=1):
        db.session.add(WorkType(name=name, sort_order=900 + index, is_active=True))
    return names


def seed_settings() -> None:
    updates = {
        "notice_enabled": "true",
        "notice_title": f"{TAG} 시연 데이터 적용",
        "notice_body": "오늘 예약, 내 예약, 월간 캘린더, 사용 로그, 프롬프트 점검, 관리자 통계에서 더미데이터를 확인할 수 있습니다.",
    }
    for key, value in updates.items():
        setting = db.session.get(AppSetting, key)
        if setting:
            setting.value = value


def dt(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(day, time(hour, minute))


def seed_reservations(
    base_date: date,
    users: dict[str, User],
    resources: dict[str, AiResource],
    work_types: list[str],
) -> list[Reservation]:
    now = datetime.now().replace(second=0, microsecond=0)
    if now.date() != base_date:
        now = dt(base_date, 10, 30)
    current_start = now - timedelta(minutes=30)
    current_end = now + timedelta(minutes=60)

    specs = [
        (users["kim"], resources["gpt"], current_start, current_end, work_types[0], "현재 사용중 예약", "대시보드 현재 사용중 카드 확인", ReservationStatus.RESERVED),
        (users["assistant"], resources["gemini"], dt(base_date, 9), dt(base_date, 10), work_types[1], "오전 수업자료 검토", "오늘 예약 오전 시간대 표시", ReservationStatus.RESERVED),
        (users["lee"], resources["notebook"], dt(base_date, 11), dt(base_date, 12, 30), work_types[1], "완료된 수업자료 분석", "오늘 예약 완료 상태와 사용 로그 연결", ReservationStatus.COMPLETED),
        (users["park"], resources["gemini"], dt(base_date, 14), dt(base_date, 16), work_types[2], "오후 코드 리뷰", "오늘 예약 오후 시간대 표시", ReservationStatus.RESERVED),
        (users["kim"], resources["backup"], dt(base_date, 17), dt(base_date, 18), work_types[3], "취소된 예비 예약", "내 예약 취소 상태 필터 확인", ReservationStatus.CANCELLED),
        (users["admin"], resources["notebook"], dt(base_date, 19), dt(base_date, 20, 30), work_types[3], "야간 운영 보고서 검토", "오늘 예약 저녁 시간대 표시", ReservationStatus.RESERVED),
        (users["kim"], resources["gpt"], dt(base_date + timedelta(days=1), 10), dt(base_date + timedelta(days=1), 12), work_types[0], "내일 장시간 추론 예약", "내 예약 예정 상태 확인", ReservationStatus.RESERVED),
        (users["lee"], resources["gemini"], dt(base_date + timedelta(days=2), 13), dt(base_date + timedelta(days=2), 15), work_types[1], "미래 수업자료 점검", "월간 캘린더 미래 예약 표시", ReservationStatus.RESERVED),
        (users["kim"], resources["notebook"], dt(base_date - timedelta(days=1), 10), dt(base_date - timedelta(days=1), 11), work_types[2], "완료 로그 미작성 예약", "홈 미작성 로그 알림 확인", ReservationStatus.COMPLETED),
        (users["kim"], resources["gemini"], dt(base_date - timedelta(days=3), 15), dt(base_date - timedelta(days=3), 16, 30), work_types[1], "완료 로그 작성 예약", "내 예약 완료와 사용 로그 연결", ReservationStatus.COMPLETED),
        (users["park"], resources["backup"], dt(base_date - timedelta(days=7), 9), dt(base_date - timedelta(days=7), 10), work_types[0], "지난주 취소 예약", "취소 예약 검색/필터 확인", ReservationStatus.CANCELLED),
        (users["assistant"], resources["gpt"], dt(base_date.replace(day=1), 13), dt(base_date.replace(day=1), 14), work_types[3], "월초 운영 점검", "월간 캘린더 월초 데이터", ReservationStatus.COMPLETED),
    ]

    reservations = []
    for user, resource, start_at, end_at, work_type, title, description, status in specs:
        reservation = Reservation(
            user_id=user.id,
            resource_id=resource.id,
            start_at=start_at,
            end_at=end_at,
            work_type=work_type,
            purpose=f"{TAG} - {title}",
            description=f"{TAG} / {description}",
            safety_confirmed=True,
            consent_version="2026-07-04-demo",
            status=status,
        )
        db.session.add(reservation)
        reservations.append(reservation)
    db.session.flush()
    return reservations


def seed_usage_logs(
    base_date: date,
    users: dict[str, User],
    resources: dict[str, AiResource],
    work_types: list[str],
    reservations: list[Reservation],
) -> None:
    reservation_by_title = {reservation.purpose: reservation for reservation in reservations}
    linked = [
        (users["lee"], reservation_by_title[f"{TAG} - 완료된 수업자료 분석"], "수업자료 분석 완료", "자료 구조와 활동 흐름을 점검했습니다."),
        (users["kim"], reservation_by_title[f"{TAG} - 완료 로그 작성 예약"], "코드 설계 검토 완료", "DB 모델과 예약 충돌 흐름을 검토했습니다."),
        (users["assistant"], reservation_by_title[f"{TAG} - 월초 운영 점검"], "월초 운영 점검 완료", "예약 현황과 로그 작성률을 확인했습니다."),
    ]
    for user, reservation, title, note in linked:
        db.session.add(
            UsageLog(
                user_id=user.id,
                reservation_id=reservation.id,
                resource_id=reservation.resource_id,
                work_type=reservation.work_type,
                summary=f"{TAG} - {title}",
                prompt_text=f"{TAG} 프롬프트: 개인정보 없이 {title}을 점검하는 요청",
                result_note=f"{TAG} 결과 메모: {note}",
                created_at=reservation.end_at + timedelta(minutes=10),
            )
        )
    db.session.add(
        UsageLog(
            user_id=users["kim"].id,
            reservation_id=None,
            resource_id=resources["backup"].id,
            work_type=work_types[3],
            summary=f"{TAG} - 예약 없이 작성한 운영 메모",
            prompt_text=f"{TAG} 월간 운영 보고서 체크리스트를 정리해 주세요.",
            result_note=f"{TAG} 관리자 보고서 메뉴와 로그 검색 필터 확인용 독립 로그입니다.",
            created_at=dt(base_date, 18, 40),
        )
    )


def seed_prompt_reviews(base_date: date, users: dict[str, User]) -> None:
    specs = [
        (users["kim"], "수업자료", "활동 가능성과 개인정보 위험 점검"),
        (users["kim"], "행정문서", "문체와 누락 항목 점검"),
        (users["assistant"], "월간 보고서", "운영 보고서 구성 점검"),
        (users["lee"], "평가문항 검토", "평가 보안 자료 없이 품질 관점 점검"),
    ]
    for index, (user, category, goal) in enumerate(specs, start=1):
        source_prompt = f"{TAG} - {category} 프롬프트 초안 #{index}\n학생 개인정보 없이 {category} 작업 요청을 점검합니다."
        db.session.add(
            PromptReview(
                user_id=user.id,
                source_prompt=source_prompt,
                review_goal=goal,
                assembled_prompt=f"{TAG} 조립 프롬프트: {goal}\n{source_prompt}",
                review_result=f"{TAG} 점검 결과: 목적, 입력 제한, 산출물 형식을 더 명확히 쓰는 것이 좋습니다.",
                model_name="gemini-demo-model",
                created_at=datetime.combine(base_date, time(9 + index, 15)),
            )
        )


def seed_api_keys(users: dict[str, User]) -> None:
    for user in [users["kim"], users["assistant"], users["lee"]]:
        db.session.add(
            UserApiKey(
                user_id=user.id,
                provider="gemini",
                encrypted_api_key=encrypt_text(f"demo-gemini-key-{TAG}-{user.email}"),
                key_last4="DEMO",
            )
        )


def seed_audit_logs(base_date: date, users: dict[str, User]) -> None:
    entries = [
        ("demo.seed", "system", "demo", "시연 더미데이터를 생성했습니다."),
        ("users.update", "user", DEMO_EMAILS["kim"], "김도연 사용자 정보를 확인했습니다."),
        ("reservations.review", "reservation", "today", "오늘 예약 현황을 검토했습니다."),
        ("exports.download", "usage_log", "csv", "사용 로그 CSV 내보내기를 시연했습니다."),
    ]
    for index, (action, target_type, target_id, summary) in enumerate(entries):
        db.session.add(
            AuditLog(
                actor_user_id=users["admin"].id,
                action=action,
                target_type=target_type,
                target_id=str(target_id),
                summary=f"{TAG} - {summary}",
                ip_address=f"10.10.178.{20 + index}",
                created_at=datetime.combine(base_date, time(8 + index, 30)),
            )
        )


def print_summary(
    base_date: date,
    users: dict[str, User],
    resources: dict[str, AiResource],
    reservations: list[Reservation],
) -> None:
    print(f"seed_tag={TAG}")
    print(f"base_date={base_date.isoformat()}")
    print(f"demo_password={DEMO_PASSWORD}")
    print("demo_users=" + ", ".join(f"{key}:{user.email}" for key, user in users.items()))
    print(f"resources={len(resources)}")
    print(f"reservations={len(reservations)}")
    print("done")


if __name__ == "__main__":
    main()
