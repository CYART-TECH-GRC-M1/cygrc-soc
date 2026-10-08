from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.wazuh_service import get_wazuh_alerts, import_latest_failed_login, import_new_wazuh_alerts
from app.database.database import get_db
from app.schemas.alert import AlertCreate, AlertResponse, AlertStatusUpdate
from app.services.alert_service import (
    create_alert,
    get_alerts,
    update_alert_status,
)


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post(
    "",
    response_model=AlertResponse,
    status_code=201,
)
def create_alert_endpoint(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
):
    return create_alert(db, alert_data)


@router.get(
    "",
    response_model=list[AlertResponse],
)
def get_alerts_endpoint(
    severity: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return get_alerts(
        db,
        severity=severity,
        status=status,
    )


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse,
)
def update_alert_status_endpoint(
    alert_id: int,
    status_data: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    alert = update_alert_status(
        db,
        alert_id,
        status_data.status,
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return alert

@router.get("/wazuh")
def get_wazuh_alerts_endpoint():
    return get_wazuh_alerts()

@router.post("/wazuh/import")
def import_wazuh_alert(db: Session = Depends(get_db)):
    alert = import_latest_failed_login(db)

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="No Wazuh rule 60122 alert found"
        )

    return alert
@router.post("/wazuh/import-all")
def import_all_wazuh_alerts(
    db: Session = Depends(get_db),
):
    imported = import_new_wazuh_alerts(db)

    return {
        "imported": imported,
        "source": "wazuh",
    }