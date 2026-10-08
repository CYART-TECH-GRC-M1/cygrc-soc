from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.attack_coverage import (
    AttackCoverageResponse,
    AttackTechniqueCreate,
    AttackTechniqueResponse,
    RuleTechniqueMappingCreate,
    RuleTechniqueMappingResponse,
)
from app.services.attack_coverage_service import (
    add_mapping,
    calculate_coverage,
    list_mappings,
    list_techniques,
    sync_sigma_rules,
    upsert_technique,
)

router = APIRouter(prefix="/attack-coverage", tags=["ATT&CK Coverage"])


@router.get("/techniques", response_model=list[AttackTechniqueResponse])
def get_attack_techniques(db: Session = Depends(get_db)):
    return list_techniques(db)


@router.post("/techniques", response_model=AttackTechniqueResponse, status_code=201)
def create_attack_technique(data: AttackTechniqueCreate, db: Session = Depends(get_db)):
    return upsert_technique(db, data)


@router.get("/mappings", response_model=list[RuleTechniqueMappingResponse])
def get_attack_mappings(db: Session = Depends(get_db)):
    return list_mappings(db)


@router.post("/mappings", response_model=RuleTechniqueMappingResponse, status_code=201)
def create_attack_mapping(data: RuleTechniqueMappingCreate, db: Session = Depends(get_db)):
    if not data.rule_id.strip():
        raise HTTPException(status_code=400, detail="rule_id cannot be empty")
    return add_mapping(db, data)


@router.post("/sync-sigma")
def sync_sigma_attack_mappings(db: Session = Depends(get_db)):
    repo_root = Path(__file__).resolve().parents[4]
    rules_dir = repo_root / "detection_rules" / "sigma"
    return sync_sigma_rules(db, rules_dir)


@router.get("", response_model=AttackCoverageResponse)
def get_attack_coverage(db: Session = Depends(get_db)):
    return calculate_coverage(db)
