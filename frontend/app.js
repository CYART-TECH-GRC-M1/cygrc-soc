const API_BASE_URL = "http://127.0.0.1:8000/api/v1";


/* =========================================================
   ALERTS
   ========================================================= */

async function loadAlerts() {
    const severity = document.getElementById("severityFilter").value;
    const status = document.getElementById("statusFilter").value;

    let url = `${API_BASE_URL}/alerts`;

    const params = new URLSearchParams();

    if (severity) {
        params.append("severity", severity);
    }

    if (status) {
        params.append("status", status);
    }

    if (params.toString()) {
        url += `?${params.toString()}`;
    }

    const tableBody = document.getElementById("alertsTableBody");

    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="loading">
                Loading alerts...
            </td>
        </tr>
    `;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const alerts = await response.json();

        displayAlerts(alerts);
        updateStatistics(alerts);

    } catch (error) {
        console.error("Failed to load alerts:", error);

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Failed to load alerts.
                </td>
            </tr>
        `;
    }
}


function displayAlerts(alerts) {
    const tableBody = document.getElementById("alertsTableBody");

    if (alerts.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    No alerts found.
                </td>
            </tr>
        `;

        return;
    }

    tableBody.innerHTML = alerts.map(alert => {

        const createdAt =
            new Date(alert.created_at).toLocaleString();

        return `
            <tr>

                <td>${alert.id}</td>

                <td>
                    <strong>
                        ${escapeHtml(alert.title)}
                    </strong>

                    <br>

                    <small>
                        ${escapeHtml(alert.description || "")}
                    </small>
                </td>

                <td>
                    ${escapeHtml(alert.severity)}
                </td>

                <td>

                    <select
                        class="alert-status"
                        data-alert-id="${alert.id}"
                        onchange="updateAlertStatus(this)"
                    >

                        <option value="new"
                            ${alert.status === "new" ? "selected" : ""}>
                            New
                        </option>

                        <option value="assigned"
                            ${alert.status === "assigned" ? "selected" : ""}>
                            Assigned
                        </option>

                        <option value="investigating"
                            ${alert.status === "investigating" ? "selected" : ""}>
                            Investigating
                        </option>

                        <option value="contained"
                            ${alert.status === "contained" ? "selected" : ""}>
                            Contained
                        </option>

                        <option value="closed"
                            ${alert.status === "closed" ? "selected" : ""}>
                            Closed
                        </option>

                    </select>

                </td>

                <td>
                    ${escapeHtml(alert.source)}
                </td>

                <td>
                    ${createdAt}
                </td>

                <td>

                    <button
                        onclick="openCaseModal(
                            ${alert.id},
                            '${escapeHtml(alert.title).replace(/'/g, "\\'")}',
                            '${alert.severity}'
                        )"
                    >
                        Create Case
                    </button>

                </td>

            </tr>
        `;

    }).join("");
}


function updateStatistics(alerts) {

    document.getElementById("totalAlerts").textContent =
        alerts.length;

    document.getElementById("highAlerts").textContent =
        alerts.filter(a => a.severity === "high").length;

    document.getElementById("mediumAlerts").textContent =
        alerts.filter(a => a.severity === "medium").length;

    document.getElementById("lowAlerts").textContent =
        alerts.filter(a => a.severity === "low").length;
}


/* =========================================================
   CASES
   ========================================================= */

async function loadCases() {

    const tableBody =
        document.getElementById("casesTableBody");

    tableBody.innerHTML = `
        <tr>
            <td colspan="7" class="loading">
                Loading cases...
            </td>
        </tr>
    `;

    try {

        const response =
            await fetch(`${API_BASE_URL}/cases`);

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}`
            );
        }

        const cases =
            await response.json();

        displayCases(cases);

    } catch (error) {

        console.error(
            "Failed to load cases:",
            error
        );

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Failed to load cases.
                </td>
            </tr>
        `;
    }
}


function displayCases(cases) {
    const tableBody = document.getElementById("casesTableBody");

    if (cases.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="loading">
                    No incident cases found.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = cases.map(caseItem => {
        const createdAt = new Date(caseItem.created_at).toLocaleString();

        return `
            <tr>
                <td>${caseItem.id}</td>

                <td>
                    <strong>${escapeHtml(caseItem.title)}</strong>
                    <br>
                    <small>${escapeHtml(caseItem.description || "")}</small>
                </td>

                <td>${escapeHtml(caseItem.severity)}</td>

                <td>
                    <select
                        class="case-status"
                        data-case-id="${caseItem.id}"
                        onchange="updateCaseStatus(this)"
                    >
                        <option value="new" ${caseItem.status === "new" ? "selected" : ""}>New</option>
                        <option value="assigned" ${caseItem.status === "assigned" ? "selected" : ""}>Assigned</option>
                        <option value="investigating" ${caseItem.status === "investigating" ? "selected" : ""}>Investigating</option>
                        <option value="contained" ${caseItem.status === "contained" ? "selected" : ""}>Contained</option>
                        <option value="eradicated" ${caseItem.status === "eradicated" ? "selected" : ""}>Eradicated</option>
                        <option value="recovered" ${caseItem.status === "recovered" ? "selected" : ""}>Recovered</option>
                        <option value="closed" ${caseItem.status === "closed" ? "selected" : ""}>Closed</option>
                    </select>
                </td>

                <td>${escapeHtml(caseItem.assignee || "Unassigned")}</td>

                <td>
                    ${caseItem.alert_id !== null ? `#${caseItem.alert_id}` : "-"}
                </td>

                <td>${createdAt}</td>

                <td>
                    <button
                        class="timeline-button"
                        onclick="openTimelineModal(${caseItem.id}, '${escapeHtml(caseItem.title).replace(/'/g, "\\'")}')"
                    >
                        View Timeline
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}


async function updateCaseStatus(selectElement) {

    const caseId =
        selectElement.dataset.caseId;

    const newStatus =
        selectElement.value;

    try {

        const response = await fetch(
            `${API_BASE_URL}/cases/${caseId}/status`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );
        }

        const updatedCase =
            await response.json();

        console.log(
            `Case #${updatedCase.id} status updated to ${updatedCase.status}`
        );

    } catch (error) {

        console.error(
            "Failed to update case status:",
            error
        );

        alert(
            "Failed to update case status."
        );

        loadCases();
    }
}


/* =========================================================
   CASE CREATION MODAL
   ========================================================= */

function openCaseModal(
    alertId,
    alertTitle,
    alertSeverity
) {

    document.getElementById(
        "caseAlertId"
    ).value = alertId;

    document.getElementById(
        "caseTitle"
    ).value =
        `${alertTitle} Investigation`;

    document.getElementById(
        "caseSeverity"
    ).value = alertSeverity;

    document.getElementById(
        "caseAssignee"
    ).value = "SOC Analyst";

    document.getElementById(
        "caseDescription"
    ).value =
        `Investigation opened for alert #${alertId}: ${alertTitle}`;

    document.getElementById(
        "caseMessage"
    ).textContent = "";

    document.getElementById(
        "caseModal"
    ).classList.remove("hidden");
}


function closeCaseModal() {

    document.getElementById(
        "caseModal"
    ).classList.add("hidden");
}


async function createCase(event) {

    event.preventDefault();

    const alertId =
        Number(
            document.getElementById(
                "caseAlertId"
            ).value
        );

    const title =
        document.getElementById(
            "caseTitle"
        ).value;

    const severity =
        document.getElementById(
            "caseSeverity"
        ).value;

    const assignee =
        document.getElementById(
            "caseAssignee"
        ).value;

    const description =
        document.getElementById(
            "caseDescription"
        ).value;

    const message =
        document.getElementById(
            "caseMessage"
        );

    message.textContent =
        "Creating case...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/cases`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    title,

                    severity,

                    status: "new",

                    assignee:
                        assignee || null,

                    description:
                        description || null,

                    alert_id:
                        alertId
                })
            }
        );

        if (!response.ok) {

            const errorData =
                await response.text();

            throw new Error(
                `API returned ${response.status}: ${errorData}`
            );
        }

        const createdCase =
            await response.json();

        message.textContent =
            `Case #${createdCase.id} created successfully.`;

        message.style.color =
            "#16a34a";

        /*
         * Refresh the case table immediately
         * so the newly created case appears.
         */
        loadCases();

        setTimeout(
            () => closeCaseModal(),
            1200
        );

    } catch (error) {

        console.error(
            "Failed to create case:",
            error
        );

        message.textContent =
            "Failed to create case.";

        message.style.color =
            "#dc2626";
    }
}


/* =========================================================
   ALERT STATUS UPDATE
   ========================================================= */

async function updateAlertStatus(
    selectElement
) {

    const alertId =
        selectElement.dataset.alertId;

    const newStatus =
        selectElement.value;

    try {

        const response = await fetch(
            `${API_BASE_URL}/alerts/${alertId}/status`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );
        }

        const updatedAlert =
            await response.json();

        console.log(
            `Alert #${updatedAlert.id} status updated to ${updatedAlert.status}`
        );

    } catch (error) {

        console.error(
            "Failed to update alert status:",
            error
        );

        alert(
            "Failed to update alert status."
        );

        loadAlerts();
    }
}


/* =========================================================
   HTML SAFETY
   ========================================================= */

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


/* =========================================================
   EVENT LISTENERS
   ========================================================= */

document
    .getElementById("refreshBtn")
    .addEventListener(
        "click",
        loadAlerts
    );


document
    .getElementById("filterBtn")
    .addEventListener(
        "click",
        loadAlerts
    );


document
    .getElementById("refreshCasesBtn")
    .addEventListener(
        "click",
        loadCases
    );


document
    .getElementById("closeModal")
    .addEventListener(
        "click",
        closeCaseModal
    );


document
    .getElementById("caseForm")
    .addEventListener(
        "submit",
        createCase
    );


/* =========================================================
   INITIAL LOAD
   ========================================================= */

loadAlerts();
loadCases();

let currentTimelineCaseId = null;

async function openTimelineModal(caseId, caseTitle) {
    currentTimelineCaseId = caseId;

    document.getElementById("timelineCaseTitle").textContent =
        `Case #${caseId}: ${caseTitle}`;

    document.getElementById("timelineMessage").textContent = "";

    document.getElementById("timelineModal").classList.remove("hidden");

    await loadCaseTimeline(caseId);
}


function closeTimelineModal() {
    document.getElementById("timelineModal").classList.add("hidden");

    currentTimelineCaseId = null;
}


async function loadCaseTimeline(caseId) {
    const timelineList = document.getElementById("timelineList");

    timelineList.innerHTML = "Loading timeline...";

    try {
        const response = await fetch(
            `${API_BASE_URL}/cases/${caseId}/timeline`
        );

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const events = await response.json();

        displayCaseTimeline(events);

    } catch (error) {

        console.error("Failed to load timeline:", error);

        timelineList.innerHTML =
            "Failed to load timeline.";
    }
}


function displayCaseTimeline(events) {
    const timelineList =
        document.getElementById("timelineList");

    if (events.length === 0) {

        timelineList.innerHTML = `
            <div class="timeline-empty">
                No timeline events yet.
            </div>
        `;

        return;
    }

    timelineList.innerHTML = events.map(event => {

        const createdAt =
            new Date(event.created_at).toLocaleString();

        return `
            <div class="timeline-item">

                <div class="timeline-marker">
                    ●
                </div>

                <div class="timeline-content">

                    <div class="timeline-event-header">

                        <strong>
                            ${escapeHtml(event.event_type)}
                        </strong>

                        <span>
                            ${createdAt}
                        </span>

                    </div>

                    <p>
                        ${escapeHtml(event.description)}
                    </p>

                    <small>
                        Actor:
                        ${escapeHtml(event.actor || "Unknown")}
                    </small>

                </div>

            </div>
        `;

    }).join("");
}


async function createTimelineEvent(event) {

    event.preventDefault();

    if (!currentTimelineCaseId) {
        return;
    }

    const eventType =
        document.getElementById("timelineEventType").value;

    const description =
        document.getElementById("timelineDescription").value;

    const actor =
        document.getElementById("timelineActor").value;

    const message =
        document.getElementById("timelineMessage");

    message.textContent = "Adding event...";


    try {

        const response = await fetch(
            `${API_BASE_URL}/cases/${currentTimelineCaseId}/timeline`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    event_type: eventType,
                    description: description,
                    actor: actor || null
                })
            }
        );


        if (!response.ok) {

            const errorData =
                await response.text();

            throw new Error(
                `API returned ${response.status}: ${errorData}`
            );
        }


        message.textContent =
            "Timeline event added.";

        message.style.color = "#16a34a";


        document.getElementById(
            "timelineDescription"
        ).value = "";


        await loadCaseTimeline(
            currentTimelineCaseId
        );


    } catch (error) {

        console.error(
            "Failed to add timeline event:",
            error
        );

        message.textContent =
            "Failed to add timeline event.";

        message.style.color = "#dc2626";
    }
}


document
    .getElementById("closeTimelineModal")
    .addEventListener(
        "click",
        closeTimelineModal
    );


document
    .getElementById("timelineForm")
    .addEventListener(
        "submit",
        createTimelineEvent
    );

/* =========================================================
   ATT&CK COVERAGE
   ========================================================= */

async function loadAttackCoverage() {
    const heatmap = document.getElementById("attackHeatmap");
    heatmap.innerHTML = '<div class="loading">Loading ATT&CK coverage...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/attack-coverage`);
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        displayAttackCoverage(await response.json());
    } catch (error) {
        console.error("Failed to load ATT&CK coverage:", error);
        heatmap.innerHTML = '<div class="loading">Failed to load ATT&CK coverage.</div>';
    }
}

function displayAttackCoverage(coverage) {
    document.getElementById("attackCoveragePercent").textContent =
        coverage.coverage_percent === null ? "—" : `${coverage.coverage_percent}%`;
    document.getElementById("coveredTechniques").textContent = coverage.covered_techniques;
    document.getElementById("totalTechniques").textContent = coverage.total_techniques;
    document.getElementById("mappedRules").textContent = coverage.mapped_rules;

    const heatmap = document.getElementById("attackHeatmap");
    if (!coverage.tactics.length) {
        heatmap.innerHTML = '<div class="table-container"><div class="loading">No ATT&CK catalog techniques are loaded yet. Add the ATT&CK catalog, then sync the Sigma mappings.</div></div>';
        return;
    }

    heatmap.innerHTML = coverage.tactics.map(tactic => `
        <section class="attack-tactic">
            <div class="attack-tactic-header">
                <h3>${escapeHtml(tactic.tactic)}</h3>
                <span>${tactic.covered_techniques}/${tactic.total_techniques} covered (${tactic.coverage_percent}%)</span>
            </div>
            <div class="attack-techniques">
                ${tactic.techniques.map(technique => `
                    <div class="attack-cell ${technique.covered ? "covered" : "uncovered"}" title="${escapeHtml(technique.rules.join(", "))}">
                        <div class="attack-cell-id">${escapeHtml(technique.technique_id)}</div>
                        <div class="attack-cell-name">${escapeHtml(technique.name)}</div>
                        <div class="attack-cell-rules">${technique.covered ? `${technique.rule_count} rule${technique.rule_count === 1 ? "" : "s"}` : "No mapped rule"}</div>
                    </div>
                `).join("")}
            </div>
        </section>
    `).join("");
}

async function syncAttackMappings() {
    const message = document.getElementById("attackMessage");
    message.textContent = "Syncing Sigma ATT&CK tags...";

    try {
        const response = await fetch(`${API_BASE_URL}/attack-coverage/sync-sigma`, { method: "POST" });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        const result = await response.json();
        message.textContent = `Sigma sync complete: ${result.rules} rule(s), ${result.mappings} ATT&CK mapping(s).`;
        await loadAttackCoverage();
    } catch (error) {
        console.error("Failed to sync ATT&CK mappings:", error);
        message.textContent = "Failed to sync Sigma ATT&CK mappings.";
    }
}

document.getElementById("refreshAttackBtn").addEventListener("click", loadAttackCoverage);
document.getElementById("syncAttackBtn").addEventListener("click", syncAttackMappings);
loadAttackCoverage();
