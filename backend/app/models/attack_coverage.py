from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AttackTechnique(Base):
    __tablename__ = "attack_techniques"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    technique_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tactic: Mapped[str] = mapped_column(String(100), nullable=False, default="Uncategorized")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RuleTechniqueMapping(Base):
    __tablename__ = "rule_technique_mappings"
    __table_args__ = (
        UniqueConstraint("rule_id", "technique_id", name="uq_rule_technique_mapping"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rule_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rule_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    technique_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="sigma")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
