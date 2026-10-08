from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UEBAAnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    activity_count: int
    baseline_mean: float
    baseline_stddev: float
    z_score: float
    threshold: float
    is_anomaly: bool
    detected_at: datetime