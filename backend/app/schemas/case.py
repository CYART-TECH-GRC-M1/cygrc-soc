from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    title: str
    severity: str = "medium"
    status: str = "new"
    assignee: str | None = None
    description: str | None = None
    alert_id: int | None = None

class CaseStatusUpdate(BaseModel):
    status: str
class CaseEventCreate(BaseModel):
    event_type: str
    description: str
    actor: str | None = None


class CaseEventResponse(BaseModel):
    id: int
    case_id: int
    event_type: str
    description: str
    actor: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseResponse(BaseModel):
    id: int
    title: str
    severity: str
    status: str
    assignee: str | None
    description: str | None
    alert_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)