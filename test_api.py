"""
Standard Library Test Suite for Autonomous Production Incident Triage Agent API
Tests all endpoints directly via FastAPI ASGI / internal router with zero external dependencies.
"""

import unittest
from main import app

class TestFastAPIEndpoints(unittest.TestCase):
    
    def test_root_endpoint(self):
        """Verify root GET endpoint returns status 200."""
        from main import root
        res = root()
        self.assertIn("Autonomous Production Incident Triage Agent API", res["message"])
        self.assertEqual(res["docs_url"], "/docs")

    def test_health_check_endpoint(self):
        """Verify health check endpoint status."""
        from main import health
        res = health()
        self.assertEqual(res["status"], "healthy")
        self.assertEqual(res["service"], "incident_triage_agent")

    def test_incidents_list_endpoint(self):
        """Verify incidents history listing endpoint."""
        from main import list_incidents
        res = list_incidents(limit=5)
        self.assertIn("incidents", res)
        self.assertIsInstance(res["incidents"], list)

    def test_triage_post_p0_deadlock(self):
        """Verify triage endpoint with P0 Database Deadlock log."""
        from main import run_triage, TriageRequest
        req = TriageRequest(raw_log="2026-09-02 12:00:00 [CRITICAL] org.postgresql.util.PSQLException: ConnectionPoolExhausted max limit 100 reached.")
        res = run_triage(req)
        self.assertEqual(res.severity, "P0")
        self.assertEqual(res.status, "TRIAGE_COMPLETE")
        self.assertIsNotNone(res.escalation_status)

    def test_triage_post_p2_runtime_exception(self):
        """Verify triage endpoint with P2 NullPointer log."""
        from main import run_triage, TriageRequest
        req = TriageRequest(raw_log="2026-09-02 12:15:00 [ERROR] NullPointerException: Cannot invoke 'getId()' because 'userProfile' is null.")
        res = run_triage(req)
        self.assertEqual(res.severity, "P2")
        self.assertEqual(res.status, "TRIAGE_COMPLETE")
        self.assertIsNotNone(res.patch_recommendation)

if __name__ == "__main__":
    unittest.main(verbosity=2)
