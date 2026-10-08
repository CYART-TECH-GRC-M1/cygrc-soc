from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.schemas.alert import AlertCreate


def create_alert(db: Session, alert_data: AlertCreate) -> Alert:
    alert = Alert(
        title=alert_data.title,
        severity=alert_data.severity,
        status=alert_data.status,
        source=alert_data.source,
        description=alert_data.description,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def get_alerts(
    db: Session,
    severity: str | None = None,
    status: str | None = None,
) -> list[Alert]:
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)

    if status:
        query = query.filter(Alert.status == status)

    return query.order_by(Alert.id.desc()).all()
def update_alert_status(
    db: Session,
    alert_id: int,
    status: str,
) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        return None

    alert.status = status

    db.commit()
    db.refresh(alert)

    return alert