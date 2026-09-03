"""
Quick Verification Script for Incident Triage Agent
"""

from agent_graph import triage_pipeline
from db_store import save_incident

sample_logs = [
    "2026-09-02 12:00:00 [CRITICAL] org.postgresql.util.PSQLException: ConnectionPoolExhausted max limit 100 reached.",
    "2026-09-02 12:05:00 [EMERGENCY] java.lang.OutOfMemoryError: Java heap space. Container killed by Linux kernel OOMKilled signal.",
    "2026-09-02 12:10:00 [ERROR] 504 Gateway Timeout: Call to payment-gateway.service.internal timed out after 15000ms.",
    "2026-09-02 12:15:00 [ERROR] NullPointerException: Cannot invoke \"com.user.Profile.getId()\" because \"userProfile\" is null.",
    "2026-09-02 12:20:00 [WARN] Unhandled stack trace in AuthMicroservice.py line 88: Kafka consumer connection reset by peer."
]


def run_tests():
    print("🚀 Running Autonomous Incident Triage Agent (LangGraph StateGraph Verification)...\n")
    for i, log in enumerate(sample_logs, 1):
        print(f"--- Test Case {i} ---")
        print(f"Input Log: {log}")
        result = triage_pipeline.run(log)
        inc_id = save_incident(result)
        print(f"Saved Incident ID: #{inc_id}")
        print(f"Severity: {result['severity']}")
        print(f"Diagnosis: {result['diagnosis']}")
        if result.get("escalation_status"):
            print(f"Routing Outcome: {result['escalation_status']}")
        elif result.get("patch_recommendation"):
            print(f"Routing Outcome: {result['patch_recommendation']}")
        print(f"Final Pipeline Status: {result['status']}")
        print(f"RCA Report Preview:\n{result['rca_report'][:300]}...\n")
        print("="*60 + "\n")

if __name__ == "__main__":
    run_tests()

