"""
Streamlit Web UI for Autonomous Production Incident Triage Agent
Provides a modern visual dashboard to paste crash logs, view agent graph progress,
and browse historical incident triage reports.
"""

import streamlit as st
import time
from agent_graph import triage_pipeline
from db_store import save_incident, get_recent_incidents

# Page Config
st.set_page_config(
    page_title="Incident Triage AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .node-badge {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-family: monospace;
        font-weight: 600;
        display: inline-block;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚨 Autonomous Incident Triage Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">LangGraph Multi-Agent State Machine & Automated RCA Generator</div>', unsafe_allow_html=True)

tabs = st.tabs(["🚀 Live Agent Triage", "📜 Historical Incidents Log", "🏗️ Graph Architecture Blueprint"])

with tabs[0]:
    # Sidebar Preset Selectors
    st.sidebar.header("📋 Preset Crash Logs")
    sample_choice = st.sidebar.selectbox(
        "Choose a preset log or custom input:",
        [
            "Custom Log Input",
            "P0: Out of Memory (OOM) Crash",
            "P0: Database Connection Deadlock",
            "P1: 504 Gateway Upstream Timeout",
            "P2: Application NullPointer Exception"
        ]
    )

    preset_map = {
        "P0: Out of Memory (OOM) Crash": "2026-09-02 12:05:00 [EMERGENCY] java.lang.OutOfMemoryError: Java heap space. Container killed by Linux kernel OOMKilled signal.",
        "P0: Database Connection Deadlock": "2026-09-02 12:00:00 [CRITICAL] org.postgresql.util.PSQLException: ConnectionPoolExhausted max limit 100 reached.",
        "P1: 504 Gateway Upstream Timeout": "2026-09-02 12:10:00 [ERROR] 504 Gateway Timeout: Call to payment-gateway.service.internal timed out after 15000ms.",
        "P2: Application NullPointer Exception": "2026-09-02 12:15:00 [ERROR] NullPointerException: Cannot invoke \"com.user.Profile.getId()\" because \"userProfile\" is null."
    }

    default_log = preset_map.get(sample_choice, "")

    with st.form("triage_form"):
        st.subheader("📥 Production Log / Stack Trace Input")
        raw_log = st.text_area(
            "Paste crash log string below:",
            value=default_log,
            height=130,
            placeholder="e.g. 2026-09-02 12:00:00 [ERROR] Connection pool exhausted..."
        )
        submit_btn = st.form_submit_button("🚀 Run LangGraph Triage Pipeline")

    if submit_btn:
        if not raw_log.strip():
            st.warning("⚠️ Please enter a server log string to analyze.")
        else:
            st.info("⚡ Invoking LangGraph StateGraph: Ingestion → Diagnosis → Router → Remediation Node...")
            progress_bar = st.progress(0)
            
            for pct in range(1, 101, 25):
                time.sleep(0.08)
                progress_bar.progress(pct)
                
            result = triage_pipeline.run(raw_log)
            progress_bar.progress(100)
            
            # Save incident to database
            save_incident(result)
            
            st.success("✅ Multi-Agent Graph Execution Complete & Saved to Incident Store!")
            
            # Display Results Metrics
            col1, col2, col3 = st.columns(3)
            severity = result.get("severity", "P2")
            severity_badge = "🔴 P0 (Critical)" if severity == "P0" else ("🟠 P1 (High)" if severity == "P1" else "🟡 P2 (Moderate)")
            
            col1.metric("Severity Level", severity_badge)
            col2.metric("Error Category", result["parsed_metadata"].get("error_type", "Unknown"))
            col3.metric("HTTP Status", result["parsed_metadata"].get("status_code", 500))
            
            st.markdown("---")
            
            # Dynamic Node Routing Outcome
            st.subheader("🔀 LangGraph Dynamic Routing Execution")
            if result.get("escalation_status"):
                st.error(result["escalation_status"])
            elif result.get("patch_recommendation"):
                st.success(result["patch_recommendation"])
                
            st.info(f"**Diagnosis Summary:** {result.get('diagnosis', '')}")
            
            # Action Plan
            st.subheader("🛠️ Recommended Remediation Action Items")
            for item in result.get("action_plan", []):
                st.checkbox(item, value=False, key=item)
                
            st.markdown("---")
            
            # RCA Report Preview & Download
            st.subheader("📄 Generated RCA Report (Markdown)")
            rca_text = result.get("rca_report", "")
            st.code(rca_text, language="markdown")
            
            st.download_button(
                label="📥 Download RCA Report (.md)",
                data=rca_text,
                file_name=f"RCA_Report_{severity}.md",
                mime="text/markdown"
            )

with tabs[1]:
    st.subheader("📜 Historical Triaged Incidents Log & Search")
    
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        severity_filter = st.selectbox("Filter by Severity:", ["All Severities", "P0", "P1", "P2", "P3"])
    with col_filter2:
        search_query = st.text_input("Search Incidents by Keyword:", placeholder="e.g. Postgres, Memory, Timeout, NullPointer")
        
    incidents = get_recent_incidents(50)
    
    # Apply Filtering
    if severity_filter != "All Severities":
        incidents = [inc for inc in incidents if inc["severity"] == severity_filter]
        
    if search_query.strip():
        q = search_query.lower()
        incidents = [
            inc for inc in incidents
            if q in inc["raw_log"].lower() or q in inc["error_type"].lower() or q in inc["diagnosis"].lower()
        ]
        
    st.write(f"Showing **{len(incidents)}** matching record(s):")
    
    if not incidents:
        st.info("No matching incidents found in database history.")
    else:
        for inc in incidents:
            severity_tag = "🔴 P0" if inc['severity'] == "P0" else ("🟠 P1" if inc['severity'] == "P1" else "🔵 P2")
            with st.expander(f"ID #{inc['id']} | {inc['timestamp']} | Severity: {severity_tag} | {inc['error_type']}"):
                st.write(f"**Raw Crash Log:** `{inc['raw_log']}`")
                st.write(f"**Diagnostic Conclusion:** {inc['diagnosis']}")
                st.markdown("---")
                st.markdown(inc['rca_report'])


with tabs[2]:
    st.subheader("🏗️ System Architecture & LangGraph Flow Diagram")
    st.markdown("""
    ```mermaid
    graph TD
        START((START)) --> A[log_ingestion_node]
        A --> B[diagnosis_node]
        B --> C{route_by_severity}
        C -- Severity P0/P1 --> D[escalation_node]
        C -- Severity P2/P3 --> E[patch_remediation_node]
        D --> F[rca_generation_node]
        E --> F
        F --> END((END))
    ```
    """)
    st.markdown("""
    ### Key Architecture Innovations:
    - **StateGraph Compilation:** Native graph node wiring using LangGraph `StateGraph(IncidentState)`.
    - **Conditional Edge Routing:** Dynamic runtime branching based on incident severity.
    - **Persistent Storage:** SQLite incident database storing structured RCA reports for historical post-mortems.
    """)
