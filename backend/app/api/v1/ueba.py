from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.ueba import UEBAAnomaly
from app.schemas.ueba import UEBAAnomalyResponse
from app.services.ueba_service import analyze_all_agents


router = APIRouter(
    prefix="/ueba",
    tags=["UEBA"],
)


@router.post(
    "/analyze",
    response_model=list[UEBAAnomalyResponse],
)
def run_ueba_analysis(
    db: Session = Depends(get_db),
):
    """
    Run statistical UEBA analysis for all active agents.
    """

    return analyze_all_agents(db)


@router.get(
    "/anomalies",
    response_model=list[UEBAAnomalyResponse],
)
def get_ueba_anomalies(
    db: Session = Depends(get_db),
):
    return (
        db.query(UEBAAnomaly)
        .order_by(UEBAAnomaly.detected_at.desc())
        .all()
    )


@router.get(
    "/anomalies/{anomaly_id}",
    response_model=UEBAAnomalyResponse,
)
def get_ueba_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db),
):
    anomaly = (
        db.query(UEBAAnomaly)
        .filter(UEBAAnomaly.id == anomaly_id)
        .first()
    )

    if not anomaly:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="UEBA anomaly not found",
        )

    return anomaly