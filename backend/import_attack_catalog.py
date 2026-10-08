"""Import an Enterprise ATT&CK STIX JSON export into the CyGRC catalog.

Usage:
    python scripts/import_attack_catalog.py /path/to/enterprise-attack.json

The source JSON should be the Enterprise ATT&CK STIX bundle selected by the team.
"""

import json
import sys
from pathlib import Path

# Allow running this file directly from backend/scripts.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.database import SessionLocal, init_db  # noqa: E402
from app.schemas.attack_coverage import AttackTechniqueCreate  # noqa: E402
from app.services.attack_coverage_service import upsert_technique  # noqa: E402


def tactic_name(phase_name: str) -> str:
    return phase_name.replace("-", " ").title()


def import_catalog(path: Path) -> int:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    objects = bundle.get("objects", [])
    imported = 0

    db = SessionLocal()
    try:
        for obj in objects:
            if obj.get("type") != "attack-pattern":
                continue
            if obj.get("revoked") or obj.get("x_mitre_deprecated"):
                continue

            external_id = next(
                (
                    ref.get("external_id")
                    for ref in obj.get("external_references", [])
                    if ref.get("source_name") == "mitre-attack"
                ),
                None,
            )
            if not external_id or not external_id.startswith("T"):
                continue

            phases = [
                tactic_name(phase.get("phase_name", "Uncategorized"))
                for phase in obj.get("kill_chain_phases", [])
                if phase.get("kill_chain_name") == "mitre-attack"
            ]
            tactic = phases[0] if phases else "Uncategorized"

            upsert_technique(
                db,
                AttackTechniqueCreate(
                    technique_id=external_id,
                    name=obj.get("name", external_id),
                    tactic=tactic,
                    description=obj.get("description"),
                    sort_order=0,
                ),
            )
            imported += 1
    finally:
        db.close()

    return imported


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/import_attack_catalog.py /path/to/enterprise-attack.json")

    init_db()
    count = import_catalog(Path(sys.argv[1]))
    print(f"Imported/updated {count} ATT&CK techniques.")
