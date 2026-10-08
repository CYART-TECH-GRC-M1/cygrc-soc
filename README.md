# CyGRC SOC

Cyber Defense Operations — SOC backend and frontend foundation.

## Step 1

Initial project architecture and FastAPI health endpoint.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## Teammate 3 — ATT&CK Coverage

The `feature/attack-coverage` implementation adds rule-to-technique mappings, coverage calculation, and an ATT&CK heat map. See `ATTACK_COVERAGE.md` for the API and integration notes.
