"""
LangGraph Multi-Agent State Machine for Production Incident Triage
Defines state schemas, agent nodes, conditional edge routers, and graph compilation.
"""

from typing import TypedDict, List, Dict, Any, Optional
from tools import LogParserTool, RCAGeneratorTool

# Try importing native LangGraph; fallback to lightweight StateGraph engine if offline
try:
    from langgraph.graph import StateGraph, START, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    START = "START"
    END = "END"
    
    class StateGraph:
        def __init__(self, state_schema):
            self.state_schema = state_schema
            self.nodes = {}
            self.edges = []
            self.conditional_edges = []

        def add_node(self, name, func):
            self.nodes[name] = func

        def add_edge(self, start, end):
            self.edges.append((start, end))

        def add_conditional_edges(self, source, router, path_map):
            self.conditional_edges.append((source, router, path_map))

        def compile(self):
            return CompiledGraph(self)

    class CompiledGraph:
        def __init__(self, graph):
            self.graph = graph

        def invoke(self, initial_state):
            state = dict(initial_state)
            state.update(self.graph.nodes["log_ingestion_node"](state))
            state.update(self.graph.nodes["diagnosis_node"](state))
            router = self.graph.conditional_edges[0][1]
            target_node = router(state)
            state.update(self.graph.nodes[target_node](state))
            state.update(self.graph.nodes["rca_generation_node"](state))
            return state


# 1. State Definition
class IncidentState(TypedDict):
    raw_log: str
    parsed_metadata: Optional[Dict[str, Any]]
    diagnosis: Optional[str]
    severity: Optional[str]
    escalation_status: Optional[str]
    patch_recommendation: Optional[str]
    action_plan: Optional[List[str]]
    rca_report: Optional[str]
    current_node: str
    status: str

# 2. Agent Node Functions
def log_ingestion_node(state: IncidentState) -> Dict[str, Any]:
    """Ingests raw production log and parses basic metadata."""
    raw_log = state["raw_log"]
    parsed = LogParserTool.parse_log(raw_log)
    
    return {
        "parsed_metadata": parsed,
        "severity": parsed["severity"],
        "current_node": "log_ingestion_node",
        "status": "LOG_PARSED"
    }

def diagnosis_node(state: IncidentState) -> Dict[str, Any]:
    """Analyzes log context to form diagnostic conclusions."""
    meta = state.get("parsed_metadata", {})
    error_type = meta.get("error_type", "Unknown")
    severity = state.get("severity", "P2")
    
    if severity in ["P0", "P1"]:
        diagnosis = f"CRITICAL SYSTEM IMPACT ({severity}): Detected {error_type}. High risk to system availability and data throughput."
    else:
        diagnosis = f"MODERATE APPLICATION EXCEPTION ({severity}): Detected {error_type}. Standard runtime failure isolate to application stack."
        
    return {
        "diagnosis": diagnosis,
        "current_node": "diagnosis_node",
        "status": "DIAGNOSED"
    }

def escalation_node(state: IncidentState) -> Dict[str, Any]:
    """Node executed for P0/P1 critical outages requiring engineering escalation."""
    severity = state.get("severity", "P0")
    meta = state.get("parsed_metadata", {})
    error_type = meta.get("error_type", "Unknown")
    
    escalation_msg = f"🚨 PAGERDUTY DISPATCH: Escalated {severity} {error_type} incident to Senior DevOps On-Call Team & Infrastructure Leads."
    
    action_plan = [
        "Trigger immediate PagerDuty / Slack #incidents channel notification.",
        "Isolate degraded pod instances / restart connection pools.",
        "Initiate automated failover to secondary database read-replica if latency > 5000ms.",
        "Schedule post-mortem sync with Lead SRE within 24 hours."
    ]
    
    return {
        "escalation_status": escalation_msg,
        "action_plan": action_plan,
        "current_node": "escalation_node",
        "status": "ESCALATED_TO_ONCALL"
    }

def patch_remediation_node(state: IncidentState) -> Dict[str, Any]:
    """Node executed for P2/P3 standard application errors for auto-remediation."""
    meta = state.get("parsed_metadata", {})
    error_type = meta.get("error_type", "Unknown")
    
    patch_msg = f"🛠️ AUTO-PATCH GENERATED: Formulated automated code patch and null-check pull request for {error_type}."
    
    action_plan = [
        "Generate automated bug hotfix branch in GitHub repository.",
        "Add null-coalescing guard clauses around affected variable pointers.",
        "Trigger CI/CD regression test suite on Staging environment.",
        "Auto-merge hotfix PR upon 100% test pass rate."
    ]
    
    return {
        "patch_recommendation": patch_msg,
        "action_plan": action_plan,
        "current_node": "patch_remediation_node",
        "status": "HOTFIX_PATCH_READY"
    }

def rca_generation_node(state: IncidentState) -> Dict[str, Any]:
    """Generates structured Root Cause Analysis (RCA) and action items."""
    meta = state.get("parsed_metadata", {})
    diagnosis = state.get("diagnosis", "")
    action_plan = state.get("action_plan", [])
    escalation = state.get("escalation_status")
    patch = state.get("patch_recommendation")
    
    rca_md = RCAGeneratorTool.generate_rca(
        parsed_info=meta,
        diagnosis=diagnosis,
        action_plan=action_plan,
        escalation_msg=escalation,
        patch_msg=patch
    )
    
    return {
        "rca_report": rca_md,
        "current_node": "rca_generation_node",
        "status": "TRIAGE_COMPLETE"
    }

# 3. Conditional Router Function
def route_by_severity(state: IncidentState) -> str:
    """Routes state based on severity: P0/P1 -> Escalation Node, P2/P3 -> Patch Node."""
    severity = state.get("severity", "P2")
    if severity in ["P0", "P1"]:
        return "escalation_node"
    return "patch_remediation_node"

# 4. LangGraph StateGraph Assembly
builder = StateGraph(IncidentState)

# Add Nodes
builder.add_node("log_ingestion_node", log_ingestion_node)
builder.add_node("diagnosis_node", diagnosis_node)
builder.add_node("escalation_node", escalation_node)
builder.add_node("patch_remediation_node", patch_remediation_node)
builder.add_node("rca_generation_node", rca_generation_node)

# Add Edges
builder.add_edge(START, "log_ingestion_node")
builder.add_edge("log_ingestion_node", "diagnosis_node")

# Conditional Edge Branching
builder.add_conditional_edges(
    "diagnosis_node",
    route_by_severity,
    {
        "escalation_node": "escalation_node",
        "patch_remediation_node": "patch_remediation_node"
    }
)

builder.add_edge("escalation_node", "rca_generation_node")
builder.add_edge("patch_remediation_node", "rca_generation_node")
builder.add_edge("rca_generation_node", END)

# Compile Graph
incident_graph = builder.compile()

# Pipeline Wrapper Class for simple execution
class IncidentTriagePipeline:
    """Coordinates execution of the compiled LangGraph StateGraph."""
    
    def run(self, raw_log: str) -> IncidentState:
        initial_state: IncidentState = {
            "raw_log": raw_log,
            "parsed_metadata": None,
            "diagnosis": None,
            "severity": None,
            "escalation_status": None,
            "patch_recommendation": None,
            "action_plan": None,
            "rca_report": None,
            "current_node": "init",
            "status": "INITIALIZED"
        }
        
        final_state = incident_graph.invoke(initial_state)
        return final_state

# Instantiated Singleton for API & App usage
triage_pipeline = IncidentTriagePipeline()
