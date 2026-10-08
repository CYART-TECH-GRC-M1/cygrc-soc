# Teammate 3 — ATT&CK Coverage

This implements the Teammate 3 scope from the SOC handover:

- Rule-to-technique mapping
- Coverage calculation
- ATT&CK coverage heat map

## Design

The feature is intentionally separated from the Sigma engine. Teammate 2 can keep creating Sigma rules under `detection_rules/sigma/`; Teammate 3 can then import their `attack.Txxxx` / `attack.Txxxx.xxx` tags with the **Sync Sigma Mappings** action or the API.

The backend stores:

- `attack_techniques`: the ATT&CK catalog used as the denominator for coverage.
- `rule_technique_mappings`: the detection-rule → ATT&CK-technique relationship.

Coverage is calculated as:

```text
covered techniques / total techniques in the loaded ATT&CK catalog × 100
```

If no ATT&CK catalog has been loaded, the API returns `coverage_percent: null` rather than reporting a misleading 100% based only on mapped rules.

## API

### Add/update an ATT&CK technique

`POST /api/v1/attack-coverage/techniques`

```json
{
  "technique_id": "T1059",
  "name": "Command and Scripting Interpreter",
  "tactic": "Execution",
  "description": "...",
  "sort_order": 0
}
```

### Add/update a rule mapping

`POST /api/v1/attack-coverage/mappings`

```json
{
  "rule_id": "my-sigma-rule-id",
  "rule_title": "Example Sigma Rule",
  "technique_id": "T1059.001",
  "source": "sigma"
}
```

The same rule can map to multiple techniques, and the same technique can be covered by multiple rules. Duplicate rule/technique pairs are updated rather than duplicated.

### Sync Sigma tags

`POST /api/v1/attack-coverage/sync-sigma`

The service scans the repository's `detection_rules/sigma/` directory and extracts tags such as:

```yaml
tags:
  - attack.execution
  - attack.t1059
  - attack.t1059.001
```

Tactic tags are ignored; technique tags become mappings.

### Get coverage

`GET /api/v1/attack-coverage`

Returns the overall coverage plus tactic-level and technique-level heat-map data.

### Get raw catalog/mappings

- `GET /api/v1/attack-coverage/techniques`
- `GET /api/v1/attack-coverage/mappings`

## ATT&CK catalog requirement

The supplied ZIP does **not** contain an ATT&CK technique catalog, so this branch does not invent a catalog or claim a coverage percentage that the source project cannot support. Load the Enterprise ATT&CK catalog/version selected by the team into `attack_techniques` using the technique endpoint (or a small import script) before demonstrating the percentage.

The Sigma rules are also not present in the supplied ZIP, so the sync endpoint is ready for Teammate 2's `detection_rules/sigma/` files.

## Frontend

The existing dashboard now has a **MITRE ATT&CK Coverage** section with:

- overall coverage percentage
- covered vs total techniques
- mapped rule count
- tactic sections
- green cells for covered techniques
- red cells for uncovered techniques
- Sigma mapping sync button
- refresh button

## Tests

`backend/tests/test_attack_coverage.py` covers:

1. coverage calculation and percentage
2. multiple rules covering the same technique
3. Sigma ATT&CK tag extraction

For this environment, run tests with a SQLite test database:

```bash
cd backend
DATABASE_URL=sqlite+pysqlite:///:memory: PYTHONPATH=. pytest -q
```

Production remains configured for PostgreSQL through `DATABASE_URL`.

### Optional catalog importer

If the team has selected an Enterprise ATT&CK STIX JSON export, the included helper can load it:

```bash
cd backend
python scripts/import_attack_catalog.py /path/to/enterprise-attack.json
```

This imports non-revoked, non-deprecated Enterprise `attack-pattern` objects and uses their MITRE ATT&CK kill-chain phase as the tactic.
