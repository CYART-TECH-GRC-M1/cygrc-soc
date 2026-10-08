from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.case_event import CaseEvent
from app.schemas.case import CaseEventCreate


def create_case_event(
    db: Session,
    case_id: int,
    event_data: CaseEventCreate,
) -> CaseEvent | None:

    case = (
        db.query(Case)
        .filter(Case.id == case_id)
        .first()
    )

    if not case:
        return None

    event = CaseEvent(
        case_id=case_id,
        event_type=event_data.event_type,
        description=event_data.description,
        actor=event_data.actor,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_case_events(
    db: Session,
    case_id: int,
) -> list[CaseEvent]:

    return (
        db.query(CaseEvent)
        .filter(CaseEvent.case_id == case_id)
        .order_by(CaseEvent.created_at.asc())
        .all()
    )