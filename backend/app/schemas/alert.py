from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
    title: str
    severity: str = "medium"
    status: str = "new"
    source: str = "wazuh"
    description: str | None = None

class AlertStatusUpdate(BaseModel):
    status: str

class AlertResponse(BaseModel):
    id: int
    title: str
    severity: str
    status: str
    source: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)