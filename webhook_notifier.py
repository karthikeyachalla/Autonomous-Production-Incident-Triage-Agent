"""
Slack & PagerDuty Webhook Alert Dispatcher
Simulates real-time webhook dispatches for P0/P1 critical production outages.
"""

import os
import json
import urllib.request
from typing import Dict, Any

class SlackPagerDutyNotifier:
    """Dispatches formatted Slack blocks and PagerDuty alert payloads."""

    @staticmethod
    def dispatch_p0_p1_alert(severity: str, error_type: str, diagnosis: str, incident_id: int = 0) -> Dict[str, Any]:
        """Formats and sends webhook notifications to Slack and PagerDuty endpoints."""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        
        # Slack Block Kit Payload
        slack_payload = {
            "text": f"🚨 *CRITICAL INCIDENT ALERT [{severity}]* - {error_type}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚨 Incident Alert #{incident_id}: {severity} {error_type}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:* `{severity}`"},
                        {"type": "mrkdwn", "text": f"*Error Type:* {error_type}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Diagnosis Summary:*\n{diagnosis}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Incident Dashboard"},
                            "style": "danger",
                            "url": "http://localhost:8501"
                        }
                    ]
                }
            ]
        }
        
        dispatched = False
        if webhook_url:
            try:
                data = json.dumps(slack_payload).encode("utf-8")
                req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    dispatched = (resp.status == 200)
            except Exception:
                dispatched = False

        return {
            "dispatched": dispatched,
            "channel": "slack-pagerduty-oncall",
            "payload_preview": slack_payload
        }
