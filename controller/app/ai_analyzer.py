"""AI Incident Root-Cause Analyzer for Vigil Controller.

Analyzes incident alerts, pod logs, Kubernetes events, and recent diffs using
Google Gemini API to generate structured root-cause analyses and remediation
reports with strict secret redaction.
"""

import os
import re
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# Common secret patterns for pre-flight redaction
SECRET_PATTERNS = [
    r"(?i)(api[_-]?key|apikey|secret|password|passwd|token|auth[_-]?token|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.\~]{8,})['\"]?",
    r"(?i)(bearer\s+)([a-zA-Z0-9_\-\.]{16,})",
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access tokens
    r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth tokens
    r"AKIA[0-9A-Z]{16}",     # AWS access key
    r"AIza[0-9A-Za-z\-_]{35}", # Google API Key
]


def redact_secrets(text: str) -> str:
    """Redacts passwords, tokens, API keys and credentials before sending to LLM."""
    if not text:
        return ""
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = re.sub(pattern, r"[REDACTED_SECRET]", redacted)
    return redacted


class GeminiIncidentAnalyzer:
    """Uses Google Gemini API to analyze deployment failures and generate postmortems."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        from .config import settings
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("VIGIL_GEMINI_API_KEY")
            or settings.GEMINI_API_KEY
        )
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-flash-lite-latest")
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def analyze_incident(
        self,
        alert: Dict[str, Any],
        pod_logs: str = "",
        events: str = "",
        action_taken: str = "",
    ) -> Dict[str, Any]:
        """Analyzes an incident using Gemini or falls back to rule-based postmortem."""
        labels = alert.get("labels", {})
        alertname = labels.get("alertname", "UnknownIncident")
        target = labels.get("pod") or labels.get("deployment") or "workload"
        namespace = labels.get("namespace", "default")
        annotations = alert.get("annotations", {})
        summary = annotations.get("summary", "Unspecified failure")

        safe_logs = redact_secrets(pod_logs)
        safe_events = redact_secrets(events)

        if not self.is_enabled:
            return self._generate_fallback_summary(
                alertname=alertname,
                target=target,
                namespace=namespace,
                summary=summary,
                action_taken=action_taken,
            )

        prompt = f"""You are a Principal Site Reliability Engineer analyzing an automated Kubernetes incident for the Vigil self-healing platform.
Analyze the following incident telemetry and generate a concise, professional postmortem summary.

Incident Telemetry:
- Alert: {alertname}
- Target: {target} (Namespace: {namespace})
- Alert Summary: {summary}
- Action Taken by Vigil: {action_taken or 'Remediation dispatched'}
- Pod Logs (Redacted):
{safe_logs or 'No critical stack traces captured'}
- Kubernetes Events:
{safe_events or 'Pod unhealthy / CrashLoopBackOff detected'}

Format your response exactly using these Markdown sections:
### 🔍 Root Cause Analysis
Explain the primary cause based on the alert and logs.

### 💥 Impact & Blast Radius
Detail the user and service impact.

### 🛠️ Self-Healing Remediation
Describe the action taken (restart, rollback, scale) and why it stabilized the workload.

### 🛡️ Recommended Prevention
Provide 2-3 concrete developer actions (e.g. increase memory limit, fix null pointer, add readiness probe).

Always include this footer tag at the end:
> [!NOTE]
> 🤖 AI-Generated Incident Summary by Vigil (powered by Gemini)
"""

        try:
            with httpx.Client(timeout=35.0) as client:
                response = client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    json={
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": prompt}],
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.2,
                            "maxOutputTokens": 800,
                        },
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return {
                            "status": "ai_generated",
                            "model": self.model,
                            "summary": text,
                            "redacted": True,
                        }
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error calling Gemini API for incident analysis: {e}")

        # Fallback if API call fails
        return self._generate_fallback_summary(
            alertname=alertname,
            target=target,
            namespace=namespace,
            summary=summary,
            action_taken=action_taken,
        )

    def _generate_fallback_summary(
        self,
        alertname: str,
        target: str,
        namespace: str,
        summary: str,
        action_taken: str,
    ) -> Dict[str, Any]:
        """Deterministic rule-based summary when Gemini API key is not supplied."""
        report = f"""### 🔍 Root Cause Analysis
Workload `{target}` in namespace `{namespace}` triggered `{alertname}`: {summary}.

### 💥 Impact & Blast Radius
Automated telemetry identified pod instability. Traffic was contained by Vigil to prevent cascading outages.

### 🛠️ Self-Healing Remediation
Vigil automatically executed: **{action_taken or 'Automated recovery sequence'}**. Target state was restored.

### 🛡️ Recommended Prevention
- Validate resource limits and readiness probes in Helm chart.
- Inspect pre-deploy test coverage for edge case regressions.

> [!NOTE]
> ℹ️ Rule-Based Incident Summary by Vigil. Set `GEMINI_API_KEY` to activate full Gemini AI root-cause analysis.
"""
        return {
            "status": "rule_based",
            "model": "deterministic-rules",
            "summary": report,
            "redacted": True,
        }


gemini_analyzer = GeminiIncidentAnalyzer()
