from datetime import datetime

from app.models import AiResource, Reservation, ReservationStatus


class ReservationValidationError(ValueError):
    pass


def parse_datetime_local(value: str) -> datetime:
    value = value.strip()
    if not value:
        raise ReservationValidationError("예약 시작/종료 시간을 입력하세요.")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReservationValidationError("예약 시간 형식이 올바르지 않습니다.") from exc


def validate_reservation_window(start_at: datetime, end_at: datetime) -> None:
    if end_at <= start_at:
        raise ReservationValidationError("예약 종료 시간은 시작 시간보다 늦어야 합니다.")


def find_reservation_conflict(
    resource_id: int,
    start_at: datetime,
    end_at: datetime,
    exclude_reservation_id: int | None = None,
) -> Reservation | None:
    query = Reservation.query.filter(
        Reservation.resource_id == resource_id,
        Reservation.status != ReservationStatus.CANCELLED,
        Reservation.start_at < end_at,
        Reservation.end_at > start_at,
    )
    if exclude_reservation_id is not None:
        query = query.filter(Reservation.id != exclude_reservation_id)
    return query.order_by(Reservation.start_at.asc()).first()


def validate_reservation_request(
    resource: AiResource | None,
    start_at: datetime,
    end_at: datetime,
) -> None:
    if resource is None or not resource.is_active:
        raise ReservationValidationError("예약 가능한 AI 리소스를 선택하세요.")
    validate_reservation_window(start_at, end_at)
    if find_reservation_conflict(resource.id, start_at, end_at):
        raise ReservationValidationError("이미 겹치는 예약이 있습니다.")
