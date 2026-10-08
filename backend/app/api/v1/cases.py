from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    CaseStatusUpdate,
    CaseEventCreate,
    CaseEventResponse,
)
from app.services.case_service import (
    create_case,
    get_cases,
    update_case_status,     
)

from app.services.case_event_service import (
    create_case_event,
    get_case_events,
)


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post(
    "",
    response_model=CaseResponse,
    status_code=201,
)
def create_case_endpoint(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
):
    return create_case(db, case_data)


@router.get(
    "",
    response_model=list[CaseResponse],
)
def get_cases_endpoint(
    severity: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    db: Session = Depends(get_db),
):
    return get_cases(
        db,
        severity=severity,
        status=status,
        assignee=assignee,
    )


@router.patch(
    "/{case_id}/status",
    response_model=CaseResponse,
)
def update_case_status_endpoint(
    case_id: int,
    status_data: CaseStatusUpdate,
    db: Session = Depends(get_db),
):
    case = update_case_status(
        db,
        case_id,
        status_data.status,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return case

@router.post(
    "/{case_id}/timeline",
    response_model=CaseEventResponse,
    status_code=201,
)
def create_case_event_endpoint(
    case_id: int,
    event_data: CaseEventCreate,
    db: Session = Depends(get_db),
):
    event = create_case_event(
        db,
        case_id,
        event_data,
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    return event
@router.get(
    "/{case_id}/timeline",
    response_model=list[CaseEventResponse],
)
def get_case_events_endpoint(
    case_id: int,
    db: Session = Depends(get_db),
):
    return get_case_events(
        db,
        case_id,
    )