from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UEBAAnomaly(Base):
    __tablename__ = "ueba_anomalies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    activity_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    baseline_mean: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    baseline_stddev: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    z_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=3.0,
    )

    is_anomaly: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )