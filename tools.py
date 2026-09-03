"""
Incident Triage Tools & Utility Functions
Provides helper utilities for log parsing, stack trace analysis,
severity assignment, and structured Root Cause Analysis (RCA) creation.
"""

import re
from typing import Dict, Any, List, Optional

class LogParserTool:
    """Parses raw server log strings and extracts critical diagnostic details."""
    
    @staticmethod
    def parse_log(raw_log: str) -> Dict[str, Any]:
        """Extracts error type, HTTP status code, timestamp, and stack trace snippet."""
        error_type = "Unknown Error"
        status_code = 500
        severity = "P2"
        
        if "Out of Memory" in raw_log or "OOMKilled" in raw_log or "MemoryLimitExceeded" in raw_log or "heap space" in raw_log:
            error_type = "Memory Exhaustion (OOM)"
            severity = "P0"
        elif "Database Connection Timeout" in raw_log or "Deadlock" in raw_log or "ConnectionPoolExhausted" in raw_log or "PSQLException" in raw_log:
            error_type = "Database Connection Deadlock"
            severity = "P0"
        elif "NullPointerException" in raw_log or "AttributeError" in raw_log:
            error_type = "Application Runtime Exception"
            severity = "P2"
        elif "504 Gateway Timeout" in raw_log or "ETIMEDOUT" in raw_log:
            error_type = "Upstream Service Timeout"
            severity = "P1"
            status_code = 504
        elif "404 Not Found" in raw_log:
            error_type = "Resource Missing"
            severity = "P3"
            status_code = 404

        # Extract HTTP status code if present
        status_match = re.search(r'\b(4\d\d|5\d\d)\b', raw_log)
        if status_match:
            status_code = int(status_match.group(1))
            
        return {
            "error_type": error_type,
            "status_code": status_code,
            "severity": severity,
            "raw_log_length": len(raw_log),
            "snippet": raw_log[:200]
        }

class RCAGeneratorTool:
    """Generates structured markdown RCA report for engineering teams."""
    
    @staticmethod
    def generate_rca(
        parsed_info: Dict[str, Any],
        diagnosis: str,
        action_plan: List[str],
        escalation_msg: Optional[str] = None,
        patch_msg: Optional[str] = None
    ) -> str:
        actions_formatted = "\n".join([f"- [ ] {action}" for action in action_plan])
        
        routing_section = ""
        if escalation_msg:
            routing_section = f"### 🚨 Escalation Workflow Triggered\n> {escalation_msg}\n"
        elif patch_msg:
            routing_section = f"### 🛠️ Automated Hotfix Generated\n> {patch_msg}\n"

        return f"""# 🚨 INCIDENT ROOT CAUSE ANALYSIS (RCA) REPORT

**Severity Level:** `{parsed_info.get('severity', 'P2')}`  
**Error Type:** {parsed_info.get('error_type', 'Unknown')}  
**HTTP Status:** `{parsed_info.get('status_code', 500)}`  

---

### 🔍 Diagnosis Summary
{diagnosis}

{routing_section}
### 🛠️ Recommended Action Items & Remediation Checklist
{actions_formatted}

---
*Report generated automatically by Autonomous Incident Triage Agent (LangGraph).*
"""
