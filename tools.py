import os
import re
import json
import urllib.request
from typing import Dict, Any, List, Optional

# Load environment variables from .env if python-dotenv is present, or parse .env manually
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v



class LLMDiagnosisTool:
    """Uses Groq / Gemini LLM API to analyze unformatted crash logs and generate real AI root-cause analysis."""
    
    @staticmethod
    def analyze_unformatted_log(raw_log: str) -> Dict[str, Any]:
        """Queries Groq LLM API (llama-3.3-70b-versatile / llama3-8b-8192) for real-time AI log diagnosis."""
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                prompt = f"""You are an Expert DevOps / Site Reliability Engineer AI Agent.
Analyze this production crash log:
"{raw_log}"

Return ONLY a valid JSON object (no code block formatting, no markdown) with exact keys:
{{
  "error_type": "Short 2-4 word error category",
  "severity": "P0, P1, P2, or P3",
  "status_code": 500,
  "root_cause": "Detailed 1-2 sentence root cause explanation",
  "custom_patch": "Recommended code hotfix or infrastructure patch"
}}
"""
                payload = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are a DevOps Incident Analysis AI that outputs raw JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                }).encode("utf-8")
                
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "AutonomousIncidentAgent/1.0"
                    },
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = response.read().decode("utf-8")
                    res_json = json.loads(res_body)
                    content_str = res_json["choices"][0]["message"]["content"]
                    parsed_res = json.loads(content_str)
                    return parsed_res
            except Exception as e:
                pass
                
        # Smart Heuristic Fallback if offline or API key unreachable
        return {
            "error_type": "Deep Telemetry Exception",
            "severity": "P1" if ("Timeout" in raw_log or "Connection" in raw_log) else "P2",
            "status_code": 500,
            "root_cause": "Unstructured stack trace analysis detected unhandled runtime exception in log signature.",
            "custom_patch": "Apply defensive error boundary and wrap call stack in try-except block with fallback logging."
        }


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
        else:
            # Fallback to LLM analysis for unrecognized stack trace signatures
            llm_res = LLMDiagnosisTool.analyze_unformatted_log(raw_log)
            error_type = llm_res.get("error_type", "Unstructured Runtime Exception")
            severity = llm_res.get("severity", "P2")
            status_code = llm_res.get("status_code", 500)

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
