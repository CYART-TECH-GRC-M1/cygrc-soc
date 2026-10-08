from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttackTechniqueCreate(BaseModel):
    technique_id: str = Field(pattern=r"^T\d{4}(?:\.\d{3})?$")
    name: str
    tactic: str = "Uncategorized"
    description: str | None = None
    sort_order: int = 0


class AttackTechniqueResponse(AttackTechniqueCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleTechniqueMappingCreate(BaseModel):
    rule_id: str
    rule_title: str | None = None
    technique_id: str = Field(pattern=r"^T\d{4}(?:\.\d{3})?$")
    source: str = "sigma"


class RuleTechniqueMappingResponse(RuleTechniqueMappingCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttackCoverageTechnique(BaseModel):
    technique_id: str
    name: str
    tactic: str
    covered: bool
    rule_count: int
    rules: list[str]


class AttackCoverageTactic(BaseModel):
    tactic: str
    covered_techniques: int
    total_techniques: int
    coverage_percent: float
    techniques: list[AttackCoverageTechnique]


class AttackCoverageResponse(BaseModel):
    total_techniques: int
    covered_techniques: int
    uncovered_techniques: int
    coverage_percent: float | None
    total_rules: int
    mapped_rules: int
    tactics: list[AttackCoverageTactic]
