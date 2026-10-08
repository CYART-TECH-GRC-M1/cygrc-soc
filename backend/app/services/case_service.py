from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.case import Case
from app.schemas.case import CaseCreate


def create_case(db: Session, case_data: CaseCreate) -> Case:
    case = Case(
        title=case_data.title,
        severity=case_data.severity,
        status=case_data.status,
        assignee=case_data.assignee,
        description=case_data.description,
        alert_id=case_data.alert_id,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def get_cases(
    db: Session,
    severity: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
) -> list[Case]:
    query = db.query(Case)

    if severity:
        query = query.filter(Case.severity == severity)

    if status:
        query = query.filter(Case.status == status)

    if assignee:
        query = query.filter(Case.assignee == assignee)

    return query.order_by(Case.id.desc()).all()
def update_case_status(
    db: Session,
    case_id: int,
    status: str,
) -> Case | None:
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        return None

    case.status = status

    db.commit()
    db.refresh(case)

    return case

def create_case_from_alert(db: Session, alert: Alert) -> Case | None:
    if alert.severity not in ("high", "critical"):
        return None

    existing_case = (
        db.query(Case)
        .filter(Case.alert_id == alert.id)
        .first()
    )

    if existing_case:
        return existing_case

    case = Case(
        title=f"Auto Case: {alert.title}",
        severity=alert.severity,
        status="new",
        description=alert.description,
        alert_id=alert.id,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case