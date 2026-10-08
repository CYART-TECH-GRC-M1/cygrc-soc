import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.orm import Session

from app.models.attack_coverage import AttackTechnique, RuleTechniqueMapping
from app.schemas.attack_coverage import AttackTechniqueCreate, RuleTechniqueMappingCreate

ATTACK_ID_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$", re.IGNORECASE)
ATTACK_TAG_RE = re.compile(r"^attack\.(t\d{4}(?:\.\d{3})?)$", re.IGNORECASE)


def _normalise_attack_id(value: str) -> str:
    return value.strip().upper()


def list_techniques(db: Session) -> list[AttackTechnique]:
    return db.query(AttackTechnique).order_by(AttackTechnique.sort_order, AttackTechnique.technique_id).all()


def upsert_technique(db: Session, data: AttackTechniqueCreate) -> AttackTechnique:
    technique_id = _normalise_attack_id(data.technique_id)
    technique = db.query(AttackTechnique).filter(AttackTechnique.technique_id == technique_id).first()

    if technique is None:
        technique = AttackTechnique(technique_id=technique_id)
        db.add(technique)

    technique.name = data.name
    technique.tactic = data.tactic
    technique.description = data.description
    technique.sort_order = data.sort_order
    db.commit()
    db.refresh(technique)
    return technique


def add_mapping(db: Session, data: RuleTechniqueMappingCreate) -> RuleTechniqueMapping:
    technique_id = _normalise_attack_id(data.technique_id)
    existing = (
        db.query(RuleTechniqueMapping)
        .filter(
            RuleTechniqueMapping.rule_id == data.rule_id,
            RuleTechniqueMapping.technique_id == technique_id,
        )
        .first()
    )
    if existing:
        existing.rule_title = data.rule_title
        existing.source = data.source
        db.commit()
        db.refresh(existing)
        return existing

    mapping = RuleTechniqueMapping(
        rule_id=data.rule_id,
        rule_title=data.rule_title,
        technique_id=technique_id,
        source=data.source,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def list_mappings(db: Session) -> list[RuleTechniqueMapping]:
    return db.query(RuleTechniqueMapping).order_by(RuleTechniqueMapping.rule_id, RuleTechniqueMapping.technique_id).all()


def _extract_attack_ids(tags: Any) -> list[str]:
    if not isinstance(tags, list):
        tags = [tags] if tags else []
    result: list[str] = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        match = ATTACK_TAG_RE.match(tag.strip())
        if match:
            result.append(_normalise_attack_id(match.group(1)))
        elif ATTACK_ID_RE.match(tag.strip()):
            result.append(_normalise_attack_id(tag))
    return sorted(set(result))


def sync_sigma_rules(db: Session, rules_dir: Path) -> dict[str, int]:
    """Import ATT&CK tags from Sigma YAML rules without requiring the Sigma engine module."""
    if not rules_dir.exists():
        return {"files": 0, "rules": 0, "mappings": 0}

    files = sorted([*rules_dir.rglob("*.yml"), *rules_dir.rglob("*.yaml")])
    rules = 0
    mappings = 0

    for path in files:
        try:
            with path.open("r", encoding="utf-8") as handle:
                document = yaml.safe_load(handle) or {}
        except (OSError, yaml.YAMLError):
            continue

        if not isinstance(document, dict):
            continue

        rule_id = str(document.get("id") or path.stem)
        title = document.get("title")
        technique_ids = _extract_attack_ids(document.get("tags", []))
        if not technique_ids:
            continue

        rules += 1
        for technique_id in technique_ids:
            add_mapping(
                db,
                RuleTechniqueMappingCreate(
                    rule_id=rule_id,
                    rule_title=title,
                    technique_id=technique_id,
                    source="sigma",
                ),
            )
            mappings += 1

    return {"files": len(files), "rules": rules, "mappings": mappings}


def calculate_coverage(db: Session) -> dict[str, Any]:
    techniques = list_techniques(db)
    mappings = list_mappings(db)

    rules_by_technique: dict[str, set[str]] = defaultdict(set)
    rules = set()
    for mapping in mappings:
        rules_by_technique[mapping.technique_id].add(mapping.rule_id)
        rules.add(mapping.rule_id)

    # A catalog is deliberately required for a meaningful ATT&CK percentage.
    # If the project has no catalog yet, return null instead of presenting a
    # misleading 100% based only on the mapped techniques.
    catalog_ids = {t.technique_id for t in techniques}
    covered_ids = catalog_ids.intersection(rules_by_technique)
    total = len(catalog_ids)
    covered = len(covered_ids)
    coverage_percent = round((covered / total) * 100, 2) if total else None

    grouped: dict[str, list[AttackTechnique]] = defaultdict(list)
    for technique in techniques:
        grouped[technique.tactic].append(technique)

    tactics = []
    for tactic in sorted(grouped):
        tactic_techniques = grouped[tactic]
        tactic_covered = sum(1 for t in tactic_techniques if t.technique_id in rules_by_technique)
        tactic_total = len(tactic_techniques)
        tactics.append({
            "tactic": tactic,
            "covered_techniques": tactic_covered,
            "total_techniques": tactic_total,
            "coverage_percent": round((tactic_covered / tactic_total) * 100, 2) if tactic_total else 0.0,
            "techniques": [
                {
                    "technique_id": t.technique_id,
                    "name": t.name,
                    "tactic": t.tactic,
                    "covered": t.technique_id in rules_by_technique,
                    "rule_count": len(rules_by_technique.get(t.technique_id, set())),
                    "rules": sorted(rules_by_technique.get(t.technique_id, set())),
                }
                for t in tactic_techniques
            ],
        })

    return {
        "total_techniques": total,
        "covered_techniques": covered,
        "uncovered_techniques": max(total - covered, 0),
        "coverage_percent": coverage_percent,
        "total_rules": len(rules),
        "mapped_rules": len(rules),
        "tactics": tactics,
    }
