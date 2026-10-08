from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean, pstdev

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.ueba import UEBAAnomaly


DEFAULT_THRESHOLD = 3.0
DEFAULT_WINDOW_MINUTES = 60
DEFAULT_BASELINE_HOURS = 24


def calculate_z_score(
    current_value: float,
    baseline_mean: float,
    baseline_stddev: float,
) -> float:
    """
    Calculate the statistical z-score.

    z = (current value - baseline mean) / standard deviation
    """

    if baseline_stddev == 0:
        return 0.0

    return (
        current_value - baseline_mean
    ) / baseline_stddev


def extract_agent_name(alert: Alert) -> str:
    """
    Extract the Wazuh agent name from the existing
    alert description.
    """

    description = alert.description or ""

    if "Agent:" in description:
        return (
            description
            .split("Agent:", 1)[1]
            .split("|", 1)[0]
            .strip()
        )

    return "unknown"


def get_current_activity(
    db: Session,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
) -> dict[str, int]:
    """
    Count alerts for each agent during the current
    activity window.
    """

    cutoff = datetime.utcnow() - timedelta(
        minutes=window_minutes
    )

    alerts = (
        db.query(Alert)
        .filter(
            Alert.source == "wazuh",
            Alert.created_at >= cutoff,
        )
        .all()
    )

    activity = defaultdict(int)

    for alert in alerts:
        agent_name = extract_agent_name(alert)
        activity[agent_name] += 1

    return dict(activity)


def get_historical_activity(
    db: Session,
    subject: str,
    baseline_hours: int = DEFAULT_BASELINE_HOURS,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
) -> list[int]:
    """
    Build historical activity counts using fixed time windows.

    Example:
        baseline_hours = 24
        window_minutes = 60

    This produces up to 24 historical hourly activity
    values for the selected agent.
    """

    now = datetime.utcnow()

    baseline_start = now - timedelta(
        hours=baseline_hours
    )

    alerts = (
        db.query(Alert)
        .filter(
            Alert.source == "wazuh",
            Alert.created_at >= baseline_start,
            Alert.created_at < now - timedelta(
                minutes=window_minutes
            ),
        )
        .all()
    )

    buckets = defaultdict(int)

    window_seconds = window_minutes * 60

    for alert in alerts:
        if extract_agent_name(alert) != subject:
            continue

        seconds_from_start = (
            alert.created_at - baseline_start
        ).total_seconds()

        bucket_index = int(
            seconds_from_start // window_seconds
        )

        buckets[bucket_index] += 1

    total_windows = (
        baseline_hours * 60
    ) // window_minutes

    return [
        buckets.get(index, 0)
        for index in range(total_windows)
    ]


def calculate_baseline(
    historical_counts: list[int],
) -> tuple[float, float]:
    """
    Calculate baseline mean and population standard deviation.
    """

    if not historical_counts:
        return 0.0, 0.0

    baseline_mean = mean(historical_counts)

    if len(historical_counts) == 1:
        baseline_stddev = 0.0
    else:
        baseline_stddev = pstdev(historical_counts)

    return baseline_mean, baseline_stddev


def detect_anomaly(
    current_activity: int,
    baseline_mean: float,
    baseline_stddev: float,
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[float, bool]:
    """
    Calculate z-score and determine whether activity
    is anomalous.
    """

    z_score = calculate_z_score(
        current_activity,
        baseline_mean,
        baseline_stddev,
    )

    is_anomaly = abs(z_score) >= threshold

    return z_score, is_anomaly


def analyze_agent(
    db: Session,
    subject: str,
    historical_counts: list[int],
    current_activity: int,
    threshold: float = DEFAULT_THRESHOLD,
) -> UEBAAnomaly:
    """
    Analyze one behavioral subject and store the result.

    If the subject already has a UEBA result, update the
    existing result instead of creating a duplicate.
    """

    baseline_mean, baseline_stddev = calculate_baseline(
        historical_counts
    )

    z_score, is_anomaly = detect_anomaly(
        current_activity,
        baseline_mean,
        baseline_stddev,
        threshold,
    )

    # Check whether this subject already has a UEBA result.
    anomaly = (
        db.query(UEBAAnomaly)
        .filter(
            UEBAAnomaly.subject == subject
        )
        .order_by(
            UEBAAnomaly.detected_at.desc()
        )
        .first()
    )

    if anomaly:
        # Update the existing record.
        anomaly.activity_count = current_activity
        anomaly.baseline_mean = baseline_mean
        anomaly.baseline_stddev = baseline_stddev
        anomaly.z_score = z_score
        anomaly.threshold = threshold
        anomaly.is_anomaly = is_anomaly
        anomaly.detected_at = datetime.utcnow()

    else:
        # Create a new record for a new subject.
        anomaly = UEBAAnomaly(
            subject=subject,
            activity_count=current_activity,
            baseline_mean=baseline_mean,
            baseline_stddev=baseline_stddev,
            z_score=z_score,
            threshold=threshold,
            is_anomaly=is_anomaly,
        )

        db.add(anomaly)

    db.commit()
    db.refresh(anomaly)

    return anomaly


def analyze_all_agents(
    db: Session,
    threshold: float = DEFAULT_THRESHOLD,
    baseline_hours: int = DEFAULT_BASELINE_HOURS,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
) -> list[UEBAAnomaly]:
    """
    Run UEBA analysis for all agents with current activity.

    For each agent:
        1. Collect current activity.
        2. Build historical baseline.
        3. Calculate mean and standard deviation.
        4. Calculate z-score.
        5. Determine anomaly status.
        6. Store or update the result.
    """

    current_activity = get_current_activity(
        db,
        window_minutes=window_minutes,
    )

    results = []

    for subject, activity_count in current_activity.items():

        historical_counts = get_historical_activity(
            db,
            subject=subject,
            baseline_hours=baseline_hours,
            window_minutes=window_minutes,
        )

        anomaly = analyze_agent(
            db=db,
            subject=subject,
            historical_counts=historical_counts,
            current_activity=activity_count,
            threshold=threshold,
        )

        results.append(anomaly)

    return results