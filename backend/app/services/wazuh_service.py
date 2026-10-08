import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.alert import Alert

load_dotenv()


WAZUH_INDEXER_URL = os.getenv(
    "WAZUH_INDEXER_URL",
    "https://192.168.1.101:9200"
)

WAZUH_USERNAME = os.getenv("WAZUH_USERNAME", "admin")
WAZUH_PASSWORD = os.getenv("WAZUH_PASSWORD", "admin")


def get_wazuh_alerts(size: int = 20):
    url = f"{WAZUH_INDEXER_URL}/wazuh-alerts-4.x-*/_search"

    query = {
        "size": size,
        "sort": [
            {
                "timestamp": {
                    "order": "desc"
                }
            }
        ]
    }

    response = requests.get(
        url,
        auth=(WAZUH_USERNAME, WAZUH_PASSWORD),
        json=query,
        verify=False,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return [
        hit["_source"]
        for hit in data.get("hits", {}).get("hits", [])
    ]


def import_latest_failed_login(db: Session):
    url = f"{WAZUH_INDEXER_URL}/wazuh-alerts-4.x-*/_search"

    query = {
        "size": 1,
        "sort": [
            {
                "timestamp": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "match": {
                "rule.id": "60122"
            }
        }
    }

    response = requests.get(
        url,
        auth=(WAZUH_USERNAME, WAZUH_PASSWORD),
        json=query,
        verify=False,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()
    hits = data.get("hits", {}).get("hits", [])

    if not hits:
        return None

    wazuh_alert = hits[0]["_source"]

    # Unique ID assigned to this alert by the Wazuh Indexer.
    wazuh_id = hits[0].get("_id")

    # Prevent the same Wazuh alert from being imported twice.
    existing_alert = (
        db.query(Alert)
        .filter(Alert.wazuh_id == wazuh_id)
        .first()
    )

    if existing_alert:
        return existing_alert

    rule = wazuh_alert.get("rule", {})
    agent = wazuh_alert.get("agent", {})

    rule_level = int(rule.get("level", 5))

    if rule_level >= 12:
        severity = "critical"
    elif rule_level >= 7:
        severity = "high"
    elif rule_level >= 4:
        severity = "medium"
    else:
        severity = "low"

    alert = Alert(
        wazuh_id=wazuh_id,
        title=rule.get(
            "description",
            "Wazuh Security Alert"
        ),
        severity=severity,
        status="new",
        source="wazuh",
        description=(
            f"Wazuh Rule ID: {rule.get('id', 'unknown')} | "
            f"Agent: {agent.get('name', 'unknown')} | "
            f"Timestamp: {wazuh_alert.get('timestamp', 'unknown')}"
        ),
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert

def import_new_wazuh_alerts(db: Session, size: int = 20):
    url = f"{WAZUH_INDEXER_URL}/wazuh-alerts-4.x-*/_search"

    query = {
        "size": size,
        "sort": [
            {
                "timestamp": {
                    "order": "desc"
                }
            }
        ]
    }

    response = requests.get(
        url,
        auth=(WAZUH_USERNAME, WAZUH_PASSWORD),
        json=query,
        verify=False,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()
    hits = data.get("hits", {}).get("hits", [])

    imported = []

    for hit in hits:
        wazuh_alert = hit.get("_source", {})
        wazuh_id = hit.get("_id")

        if not wazuh_id:
            continue

        # Skip alerts already imported into CyGRC.
        existing_alert = (
            db.query(Alert)
            .filter(Alert.wazuh_id == wazuh_id)
            .first()
        )

        if existing_alert:
            continue

        rule = wazuh_alert.get("rule", {})
        agent = wazuh_alert.get("agent", {})

        rule_level = int(rule.get("level", 5))

        if rule_level >= 12:
            severity = "critical"
        elif rule_level >= 7:
            severity = "high"
        elif rule_level >= 4:
            severity = "medium"
        else:
            severity = "low"

        alert = Alert(
            wazuh_id=wazuh_id,
            title=rule.get(
                "description",
                "Wazuh Security Alert"
            ),
            severity=severity,
            status="new",
            source="wazuh",
            description=(
                f"Wazuh Rule ID: {rule.get('id', 'unknown')} | "
                f"Agent: {agent.get('name', 'unknown')} | "
                f"Timestamp: {wazuh_alert.get('timestamp', 'unknown')}"
            ),
        )

        db.add(alert)
        imported.append(alert)

    db.commit()

    return imported