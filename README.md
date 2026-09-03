# 🤖 Autonomous Production Incident Triage Agent (LangGraph)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange.svg)](https://python.langchain.com/docs/langgraph)

An autonomous multi-agent system built with **LangGraph** and **FastAPI** designed to automate production incident triage, log parsing, root cause analysis (RCA) generation, and remediation routing in high-scale cloud environments.

---

## 🌟 Key Features
- **Multi-Agent Orchestration:** Manages state transitions across Ingestion, Diagnosis, Router, and RCA generation nodes.
- **Conditional Edge Branching:** P0/P1 outages trigger On-Call Escalation; P2/P3 errors trigger Auto-Hotfix PR recommendations.
- **SQLite Incident Storage:** Persistent database storing all triaged logs and generated markdown RCA reports.
- **Streamlit Dashboard:** Interactive Web UI (`app.py`) for live triage and incident auditing.
- **FastAPI REST Service:** Production-ready endpoints (`/api/v1/triage`) for integration with Sentry/Datadog webhooks or CI/CD pipelines.

---

## 📁 Repository Structure
```text
.
├── main.py              # FastAPI Web API Server
├── app.py               # Streamlit Visual Web UI
├── agent_graph.py       # LangGraph Multi-Agent State Machine & Router
├── db_store.py          # SQLite Incident History Storage
├── tools.py             # Log parsing & RCA generation tools
├── test_triage.py       # Automated verification test script
├── Dockerfile           # Production Docker container definition
├── docker-compose.yml   # Multi-container orchestration
├── requirements.txt     # Python dependencies
├── PROJECT_OVERVIEW.md  # Detailed architecture & interview talking points
└── README.md            # GitHub documentation
```

---

## ⚡ Quick Start & Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Instant Test Verification
```bash
python test_triage.py
```

### 3. Launch Streamlit Web UI
```bash
streamlit run app.py
```
*Access web interface at: **`http://localhost:8501`***

### 4. Launch FastAPI Backend Server
```bash
python main.py
```
*Access interactive API documentation at: **`http://localhost:8000/docs`***

---

## 🎤 Interview Summary
Built to demonstrate end-to-end **Agentic AI**, **Software Engineering (Python OOP)**, and **DevOps Automation** capabilities for AI/ML and Systems Engineering roles.
