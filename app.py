"""
Autonomous Production Incident Triage Agent — Clean Minimal Dashboard
"""
import streamlit as st
import time
import plotly.graph_objects as go
from agent_graph import triage_pipeline
from db_store import save_incident, get_recent_incidents, get_sre_metrics

st.set_page_config(
    page_title="Incident Triage Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: #0A0A0F !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 1200px !important; }

/* Top Nav */
.top-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 0; border-bottom: 1px solid #1F1F2E;
    margin-bottom: 2.5rem;
}
.logo { font-size: 1.3rem; font-weight: 800; color: #fff; letter-spacing: -0.03em; }
.logo span { color: #7C3AED; }
.nav-badge {
    background: #7C3AED22; color: #A78BFA;
    border: 1px solid #7C3AED44; border-radius: 20px;
    padding: 0.3rem 0.9rem; font-size: 0.78rem; font-weight: 600;
}

/* Section title */
.section-title { font-size: 1.05rem; font-weight: 700; color: #E2E8F0; margin-bottom: 1rem; }

/* Input card */
.input-card {
    background: #111118; border: 1px solid #1F1F2E;
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;
}

/* Textarea */
textarea {
    background: #0D0D14 !important; color: #E2E8F0 !important;
    border: 1px solid #2D2D40 !important; border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.88rem !important;
    line-height: 1.6 !important;
}
textarea:focus { border-color: #7C3AED !important; box-shadow: 0 0 0 3px #7C3AED22 !important; }

/* Button */
.stButton > button, div[st-form-submit-button] button {
    background: #7C3AED !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px #7C3AED44 !important;
}
.stButton > button:hover { background: #6D28D9 !important; transform: translateY(-1px) !important; }

/* Result metric cards */
.metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
.metric-card {
    flex: 1; background: #111118; border: 1px solid #1F1F2E;
    border-radius: 12px; padding: 1.2rem 1.4rem;
}
.metric-label { font-size: 0.78rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
.metric-value { font-size: 1.4rem; font-weight: 800; color: #E2E8F0; }

/* Severity colors */
.sev-p0 { color: #F87171 !important; }
.sev-p1 { color: #FBBF24 !important; }
.sev-p2 { color: #34D399 !important; }

/* Alert boxes */
.alert-critical {
    background: #F8717115; border: 1px solid #F8717140;
    border-left: 4px solid #F87171; border-radius: 10px;
    padding: 1rem 1.2rem; margin: 1rem 0; color: #FCA5A5; font-size: 0.9rem;
}
.alert-ok {
    background: #34D39915; border: 1px solid #34D39940;
    border-left: 4px solid #34D399; border-radius: 10px;
    padding: 1rem 1.2rem; margin: 1rem 0; color: #6EE7B7; font-size: 0.9rem;
}
.alert-info {
    background: #7C3AED15; border: 1px solid #7C3AED40;
    border-left: 4px solid #7C3AED; border-radius: 10px;
    padding: 1rem 1.2rem; margin: 1rem 0; color: #C4B5FD; font-size: 0.9rem;
}

/* Action plan */
.action-item {
    display: flex; align-items: flex-start; gap: 0.7rem;
    background: #111118; border: 1px solid #1F1F2E;
    border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    color: #CBD5E1; font-size: 0.9rem;
}
.action-num {
    background: #7C3AED22; color: #A78BFA; border-radius: 6px;
    padding: 0.1rem 0.5rem; font-size: 0.78rem; font-weight: 700; min-width: 24px; text-align: center;
}

/* Download button */
.stDownloadButton > button {
    background: #111118 !important; color: #A78BFA !important;
    border: 1px solid #7C3AED44 !important; border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Tabs */
button[data-baseweb="tab"] { color: #6B7280 !important; font-weight: 600 !important; }
button[aria-selected="true"] { color: #A78BFA !important; border-bottom-color: #7C3AED !important; }

/* Metrics */
div[data-testid="stMetricValue"] { color: #A78BFA !important; font-weight: 800 !important; }
div[data-testid="stMetricLabel"] { color: #6B7280 !important; font-size: 0.8rem !important; }

/* Expander */
details { background: #111118 !important; border: 1px solid #1F1F2E !important; border-radius: 10px !important; }
summary { color: #CBD5E1 !important; font-weight: 600 !important; }

/* Selectbox / Input */
div[data-testid="stSelectbox"] > div, div[data-testid="stTextInput"] > div > div {
    background: #0D0D14 !important; border-color: #2D2D40 !important;
    border-radius: 8px !important; color: #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)

# Top Nav
st.markdown("""
<div class="top-nav">
    <div class="logo">🛡️ Incident<span>AI</span></div>
    <div class="nav-badge">LangGraph · Groq Llama-3.3 · FastAPI</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["⚡ Triage", "📊 Analytics", "📜 Logs"])

# ── TAB 1: TRIAGE ─────────────────────────────────────────────────────────────
with tabs[0]:
    preset_map = {
        "Custom Input": "",
        "P0 · DB Deadlock": "2026-09-02 12:00:00 [CRITICAL] org.postgresql.util.PSQLException: ConnectionPoolExhausted max limit 100 reached.",
        "P0 · OOM Crash": "2026-09-02 12:05:00 [EMERGENCY] java.lang.OutOfMemoryError: Java heap space. OOMKilled.",
        "P1 · 504 Timeout": "2026-09-02 12:10:00 [ERROR] 504 Gateway Timeout: payment-gateway timed out after 15000ms.",
        "P2 · NullPointer": "2026-09-02 12:15:00 [ERROR] NullPointerException: Cannot invoke Profile.getId() — userProfile is null.",
    }

    col_a, col_b = st.columns([3, 2], gap="large")

    with col_a:
        choice = st.selectbox("Preset logs", list(preset_map.keys()), label_visibility="collapsed")
        with st.form("triage"):
            log_input = st.text_area(
                "log", value=preset_map[choice], height=150,
                placeholder="Paste any raw production crash log or stack trace here...",
                label_visibility="collapsed"
            )
            run = st.form_submit_button("⚡  Run Triage Pipeline")

    with col_b:
        st.markdown('<div class="section-title">Agent Execution Pipeline</div>', unsafe_allow_html=True)
        steps = [
            "Log Ingestion & Parsing",
            "Groq LLM Diagnosis",
            "Severity Routing",
            "Webhook / PR Dispatch",
            "RCA Generation & Storage"
        ]
        for i, s in enumerate(steps):
            st.markdown(f"""
            <div class="action-item">
                <span class="action-num">{i+1}</span> {s}
            </div>""", unsafe_allow_html=True)

    if run:
        if not log_input.strip():
            st.warning("Please paste a log first.")
        else:
            bar = st.progress(0, text="Running agent graph...")
            for p in range(0, 101, 20):
                time.sleep(0.04)
                bar.progress(p, text=f"Executing node {p//20 + 1}/5...")

            result = triage_pipeline.run(log_input)
            inc_id = save_incident(result)
            bar.progress(100, text="✅ Done")

            sev = result.get("severity", "P2")
            sev_class = {"P0": "sev-p0", "P1": "sev-p1"}.get(sev, "sev-p2")
            sev_label = {"P0": "P0 — Critical", "P1": "P1 — High", "P2": "P2 — Moderate", "P3": "P3 — Low"}.get(sev, sev)
            err = result["parsed_metadata"].get("error_type", "Unknown")
            status_code = result["parsed_metadata"].get("status_code", "—")

            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card"><div class="metric-label">Severity</div><div class="metric-value {sev_class}">{sev_label}</div></div>
                <div class="metric-card"><div class="metric-label">Error Type</div><div class="metric-value">{err}</div></div>
                <div class="metric-card"><div class="metric-label">Incident ID</div><div class="metric-value"># {inc_id}</div></div>
            </div>
            """, unsafe_allow_html=True)

            if result.get("escalation_status"):
                st.markdown(f'<div class="alert-critical">🚨 {result["escalation_status"]}</div>', unsafe_allow_html=True)
            elif result.get("patch_recommendation"):
                st.markdown(f'<div class="alert-ok">🛠️ {result["patch_recommendation"]}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="alert-info">🔍 {result.get("diagnosis","")}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title" style="margin-top:1.5rem">Remediation Actions</div>', unsafe_allow_html=True)
            for i, item in enumerate(result.get("action_plan", []), 1):
                st.markdown(f'<div class="action-item"><span class="action-num">{i}</span>{item}</div>', unsafe_allow_html=True)

            rca = result.get("rca_report", "")
            st.download_button("📥  Download RCA Report", rca, f"RCA_{sev}_#{inc_id}.md", "text/markdown")

# ── TAB 2: ANALYTICS ──────────────────────────────────────────────────────────
with tabs[1]:
    m = get_sre_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", m["total_incidents"])
    c2.metric("MTTR Reduction", f"{m['mttr_reduction_pct']}%")
    c3.metric("Agent Speed", f"{m['mttr_agent_minutes']} min")
    c4.metric("Automation Rate", m["automation_rate"])

    st.markdown("---")
    g1, g2 = st.columns(2)

    with g1:
        fig = go.Figure(go.Pie(
            labels=["P0 Critical", "P1 High", "P2 Moderate", "P3 Low"],
            values=[m["p0_critical"], m["p1_high"], m["p2_moderate"], m["p3_low"]],
            hole=0.6,
            marker_colors=["#F87171", "#FBBF24", "#34D399", "#60A5FA"]
        ))
        fig.update_layout(
            title=dict(text="Severity Distribution", font=dict(color="#CBD5E1", size=14)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1", family="Inter"),
            margin=dict(t=40, b=10, l=10, r=10), showlegend=True,
            legend=dict(font=dict(color="#9CA3AF"))
        )
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        fig2 = go.Figure(go.Bar(
            x=["Manual SRE", "Autonomous Agent"],
            y=[m["mttr_manual_minutes"], m["mttr_agent_minutes"]],
            marker_color=["#F87171", "#7C3AED"],
            text=[f"{m['mttr_manual_minutes']} min", f"{m['mttr_agent_minutes']} min"],
            textposition="auto", textfont=dict(color="#fff", family="Inter", size=13)
        ))
        fig2.update_layout(
            title=dict(text="MTTR Comparison", font=dict(color="#CBD5E1", size=14)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1", family="Inter"),
            yaxis=dict(title="Minutes", gridcolor="#1F1F2E", color="#6B7280"),
            xaxis=dict(gridcolor="#1F1F2E", color="#6B7280"),
            margin=dict(t=40, b=10, l=10, r=10)
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── TAB 3: LOGS ───────────────────────────────────────────────────────────────
with tabs[2]:
    f1, f2 = st.columns([1, 2])
    with f1:
        sev_f = st.selectbox("Severity", ["All", "P0", "P1", "P2", "P3"])
    with f2:
        kw = st.text_input("Search", placeholder="Postgres, OOM, Timeout...")

    data = get_recent_incidents(50)
    if sev_f != "All":
        data = [d for d in data if d["severity"] == sev_f]
    if kw:
        q = kw.lower()
        data = [d for d in data if any(q in str(d[k]).lower() for k in ["raw_log","error_type","diagnosis"])]

    st.caption(f"{len(data)} records")
    icons = {"P0": "🔴", "P1": "🟠", "P2": "🔵", "P3": "🟢"}
    for inc in data:
        icon = icons.get(inc["severity"], "⚪")
        with st.expander(f"{icon}  #{inc['id']} · {inc['error_type']} · {inc['timestamp']}"):
            st.code(inc["raw_log"], language="text")
            st.markdown(inc["rca_report"])
