from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.attack_coverage import AttackTechnique
from app.schemas.attack_coverage import AttackTechniqueCreate, RuleTechniqueMappingCreate
from app.services.attack_coverage_service import add_mapping, calculate_coverage, sync_sigma_rules, upsert_technique


def make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_coverage_calculation():
    db = make_db()
    upsert_technique(db, AttackTechniqueCreate(technique_id="T1059", name="Command and Scripting Interpreter", tactic="Execution"))
    upsert_technique(db, AttackTechniqueCreate(technique_id="T1105", name="Ingress Tool Transfer", tactic="Command and Control"))
    upsert_technique(db, AttackTechniqueCreate(technique_id="T1021", name="Remote Services", tactic="Lateral Movement"))

    add_mapping(db, RuleTechniqueMappingCreate(rule_id="rule-1", technique_id="T1059"))
    add_mapping(db, RuleTechniqueMappingCreate(rule_id="rule-2", technique_id="T1059"))
    add_mapping(db, RuleTechniqueMappingCreate(rule_id="rule-2", technique_id="T1105"))

    result = calculate_coverage(db)
    assert result["total_techniques"] == 3
    assert result["covered_techniques"] == 2
    assert result["uncovered_techniques"] == 1
    assert result["coverage_percent"] == 66.67
    assert result["total_rules"] == 2


def test_sigma_sync_extracts_attack_tags(tmp_path: Path):
    rules_dir = tmp_path / "detection_rules" / "sigma"
    rules_dir.mkdir(parents=True)
    (rules_dir / "rule.yml").write_text(
        "id: test-rule\ntitle: Test Rule\ntags:\n  - attack.execution\n  - attack.t1059\n  - attack.t1059.001\n",
        encoding="utf-8",
    )

    db = make_db()
    result = sync_sigma_rules(db, rules_dir)
    assert result == {"files": 1, "rules": 1, "mappings": 2}
    assert {m.technique_id for m in db.query(__import__('app.models.attack_coverage', fromlist=['RuleTechniqueMapping']).RuleTechniqueMapping).all()} == {"T1059", "T1059.001"}
