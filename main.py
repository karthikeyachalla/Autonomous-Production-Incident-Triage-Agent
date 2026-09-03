"""
FastAPI Server Entrypoint for Autonomous Incident Triage Agent
Exposes production REST API endpoints to run triage workflows.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from agent_graph import triage_pipeline
from db_store import save_incident, get_recent_incidents

app = FastAPI(
    title="Autonomous Incident Triage Agent API",
    description="Multi-Agent LangGraph system for automated production log triage, diagnosis, and RCA generation.",
    version="1.0.0"
)

# Request Models
class TriageRequest(BaseModel):
    raw_log: str = Field(..., example="2026-09-02 12:00:00 [ERROR] java.lang.OutOfMemoryError: Java heap space. OOMKilled by Linux kernel.")

# Response Models
class TriageResponse(BaseModel):
    incident_id: Optional[int] = None
    status: str
    severity: str
    parsed_metadata: Dict[str, Any]
    diagnosis: str
    escalation_status: Optional[str] = None
    patch_recommendation: Optional[str] = None
    action_plan: List[str]
    rca_report: str

@app.get("/")
def root():
    return {
        "message": "Autonomous Production Incident Triage Agent API is running.",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "incident_triage_agent"}

@app.get("/api/v1/incidents")
def list_incidents(limit: int = 10):
    return {"incidents": get_recent_incidents(limit)}

@app.post("/api/v1/triage", response_model=TriageResponse)
def run_triage(request: TriageRequest):
    if not request.raw_log.strip():
        raise HTTPException(status_code=400, detail="raw_log cannot be empty")
        
    result_state = triage_pipeline.run(request.raw_log)
    incident_id = save_incident(result_state)
    
    return TriageResponse(
        incident_id=incident_id,
        status=result_state["status"],
        severity=result_state["severity"],
        parsed_metadata=result_state["parsed_metadata"],
        diagnosis=result_state["diagnosis"],
        escalation_status=result_state.get("escalation_status"),
        patch_recommendation=result_state.get("patch_recommendation"),
        action_plan=result_state["action_plan"],
        rca_report=result_state["rca_report"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
