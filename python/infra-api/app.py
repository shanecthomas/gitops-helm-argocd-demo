"""
infra_api.py — Internal Infrastructure Status API
Because someone has to keep the lights on.
"""

from flask import Flask, jsonify
import time
import os
import random

app = Flask(__name__)

START_TIME = time.time()
REQUEST_COUNT = 0

EXCUSES_DEV = [
    "The on-call engineer is 'investigating'.",
    "Have you tried turning it off and on again?",
    "It worked in dev. This is dev. So technically it's working.",
    "That's not a bug, it's an undocumented feature.",
    "The intern pushed to main again.",
    "Mercury is in retrograde.",
    "The JIRA ticket is in the backlog.",
    "We're waiting on change control board approval.",
    "DNS. It's always DNS.",
    "The Ansible playbook skipped that task. No idea why.",
    "Kubernetes decided to reschedule everything at 3am.",
    "The pipeline is green. The deployment is not. We don't talk about it.",
    "It's a known issue. It is not being fixed.",
    "The runbook says to restart the service. The service does not restart.",
    "We have 47 Slack messages about this and zero solutions.",
]

EXCUSES_PROD = [
    "We are aware of the issue and actively investigating.",
    "A root cause analysis is in progress; updates to follow.",
    "The incident has been escalated to the appropriate team.",
    "A fix has been identified and is pending deployment review.",
    "This is being tracked under our standard incident response process.",
    "Engineering has been notified and is assessing impact.",
    "A postmortem will be published following resolution.",
    "Mitigations are in place while a permanent fix is developed.",
]

DEPLOYMENT_AFFIRMATIONS = [
    "You deployed on a Friday. Bold.",
    "The build passed. Shipping is another matter entirely.",
    "LGTM. (Nobody reviewed this.)",
    "Deployed to prod. Prayers sent.",
    "Green pipeline. Godspeed.",
    "Zero test coverage. Full send.",
    "This is fine.",
]

LINUX_FORTUNES = [
    "Today's kernel panic brought to you by an unsigned module.",
    "Your crontab is running. You don't remember writing it.",
    "rm -rf is just aggressive housekeeping.",
    "The man page has the answer. Nobody reads the man page.",
    "sudo fix me.",
    "Your SSH key expired. In prod. On Friday.",
    "There are 47 zombie processes. Nobody knows whose they are.",
    "The disk is full. It has been full for three weeks.",
    "uptime: 847 days. Don't touch it.",
]


@app.before_request
def count_requests():
    global REQUEST_COUNT
    REQUEST_COUNT += 1


@app.route("/health")
def health():
    """Standard liveness check. We're alive. Barely."""
    return jsonify({
        "status": "ok",
        "message": "Service is up. Whether it's working is a separate question.",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "requests_served": REQUEST_COUNT,
    })


@app.route("/version")
def version():
    """Returns deployment metadata. Useful for knowing what you just broke."""
    return jsonify({
        "app": "infra-api",
        "version": os.getenv("APP_VERSION", "0.0.1-whoknows"),
        "git_sha": os.getenv("GIT_SHA", "c0ffee"),
        "environment": os.getenv("APP_ENV", "unknown"),
        "built_by": "GitHub Actions (probably fine)",
        "deployed_on": "a Friday, most likely",
    })


@app.route("/excuse")
def excuse():
    """
    Returns an incident excuse — tone depends on environment.
    Dev gets brutal honesty. Prod gets professionalism.
    """
    env = os.getenv("APP_ENV", "unknown")
    excuse_pool = EXCUSES_PROD if env == "prod" else EXCUSES_DEV

    response = {
        "incident_excuse": random.choice(excuse_pool),
        "environment": env,
    }

    if env == "prod":
        response.update({
            "status": "Under active investigation",
            "next_update": "Within 30 minutes",
            "incident_id": f"INC-{random.randint(10000, 99999)}",
        })
    else:
        response.update({
            "confidence": f"{random.randint(12, 97)}%",
            "estimated_resolution": "soon-ish",
            "jira_ticket": f"OPS-{random.randint(1000, 9999)} (unassigned)",
        })

    return jsonify(response)


@app.route("/deploy")
def deploy():
    """
    Deployment status affirmation endpoint.
    For when you need moral support before merging to main.
    """
    return jsonify({
        "status": random.choice(DEPLOYMENT_AFFIRMATIONS),
        "pipeline": "green",
        "tests": "passing",
        "coverage": f"{random.randint(0, 12)}%",
        "reviewed_by": "the merge queue",
        "rollback_plan": "lol",
    })


@app.route("/fortune")
def fortune():
    """
    Daily Linux wisdom.
    Like a fortune cookie, but with more kernel panics.
    """
    return jsonify({
        "fortune": random.choice(LINUX_FORTUNES),
        "source": "years of trauma",
    })


@app.route("/oncall")
def oncall():
    """
    On-call status endpoint.
    Dev is unfiltered. Prod maintains plausible deniability.
    """
    env = os.getenv("APP_ENV", "unknown")
    aware = random.choice([True, False, False, False])

    if env == "prod":
        return jsonify({
            "oncall_status": "Engaged",
            "acknowledged": True,
            "response_time_sla": "15 minutes",
            "escalation_policy": "Standard",
            "environment": env,
        })

    return jsonify({
        "oncall_engineer": "someone brave",
        "aware_of_situation": aware,
        "pagerduty_ack": aware,
        "last_seen": "Slack, 11 minutes ago, then went quiet",
        "status": "investigating" if aware else "also investigating (has not looked yet)",
        "estimated_response": "5 minutes" if aware else "5 business days",
        "environment": env,
    })


@app.route("/metrics")
def metrics():
    """
    Application metrics.
    These numbers are real. Their meaning is up for debate.
    """
    return jsonify({
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "requests_served": REQUEST_COUNT,
        "errors_today": random.randint(0, 3),
        "alerts_firing": random.randint(0, 12),
        "alerts_acknowledged": 0,
        "dashboards_with_red_panels": random.randint(1, 5),
        "dashboards_anyone_checks": 0,
        "open_jira_tickets": random.randint(40, 400),
        "tickets_marked_wontfix": random.randint(20, 200),
        "runbooks_up_to_date": False,
    })


@app.route("/")
def index():
    """API root — available endpoints."""
    return jsonify({
        "service": "Internal Infrastructure API",
        "tagline": "If it's in prod, it's fine. Probably.",
        "endpoints": {
            "GET /health":  "Liveness check",
            "GET /version": "Deployment metadata",
            "GET /metrics": "Application metrics (use loosely)",
            "GET /excuse":  "Industry-standard incident excuse",
            "GET /deploy":  "Pre-deployment moral support",
            "GET /fortune": "Daily Linux wisdom",
            "GET /oncall":  "On-call engineer status",
        },
        "support": "have you tried the runbook",
        "runbook_url": "http://confluence/runbooks/good-luck",
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5050)),
        debug=os.getenv("APP_ENV") == "dev"
    )
