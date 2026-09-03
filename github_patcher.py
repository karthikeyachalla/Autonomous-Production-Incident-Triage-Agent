"""
Automated GitHub Pull Request & Code Patch Generator
Generates git branch names, unified diff code patches, and Pull Request payloads for P2/P3 application exceptions.
"""

from typing import Dict, Any

class GitHubPatchGenerator:
    """Generates structured GitHub PR payloads and automated hotfix branches."""

    @staticmethod
    def generate_pull_request(error_type: str, raw_log: str, patch_recommendation: str, incident_id: int = 0) -> Dict[str, Any]:
        """Formulates a GitHub Pull Request template and automated patch code."""
        branch_name = f"hotfix/inc-{incident_id if incident_id else 'auto'}-{error_type.lower().replace(' ', '-')}"
        pr_title = f"fix(auto-remediation): resolve {error_type} in production stack"
        
        pr_body = f"""## 🤖 Automated Remediation PR

**Associated Incident ID:** `#{incident_id}`  
**Trigger Error:** `{error_type}`  

### 🔍 Error Details
```text
{raw_log[:200]}
```

### 🛠️ Proposed Hotfix Patch
{patch_recommendation}

---
*Generated automatically by Autonomous Production Incident Triage Agent (LangGraph).*
"""
        return {
            "branch_name": branch_name,
            "pr_title": pr_title,
            "pr_body": pr_body,
            "status": "PR_DRAFTED"
        }
