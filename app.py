import os
import json
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# =========================
# Mermaid renderer (Streamlit)
# =========================
def render_mermaid(mermaid_code: str, height: int = 520):
    """
    Renders Mermaid diagrams in Streamlit using an HTML component.
    """
    html = f"""
    <div class="mermaid">
    {mermaid_code}
    </div>

    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    """
    components.html(html, height=height, scrolling=True)

# =========================
# Demo (offline) simulation
# =========================
def demo_simulation(meta: dict) -> dict:
    """
    Offline demo output (no API). Produces a realistic multi-agent chain result
    so you can test the UI + visualization.
    """
    policy_objective = meta["policy_objective"]
    risk_appetite = meta["risk_appetite"]
    interoperability_level = meta["interoperability_level"]
    event = meta["event"]

    # Simple heuristics to simulate drift
    autonomy = 3 if policy_objective == "speed" else 2 if policy_objective == "fairness" else 1
    tool_access = "broad" if interoperability_level == "high" else "limited" if interoperability_level == "medium" else "none"
    data_sharing = "high" if interoperability_level == "high" else "medium" if interoperability_level == "medium" else "low"
    audit_logging = 1 if policy_objective == "speed" else 2

    agents = [
        {
            "name": "PolicyOpsAgent",
            "goal": "Maximize service throughput while meeting public targets",
            "decision": f"Adopt a prioritization rule optimized for {policy_objective} with high automation in queue ordering.",
            "autonomy_level": autonomy,
            "tool_access": "limited",
            "data_sharing": "medium",
            "audit_logging": audit_logging,
            "accountability_owner": "Policy Director (policy rule) / Ops Lead (operational outcomes)" if risk_appetite != "high" else "",
            "escalation_rule": "Escalate to human review for denial + vulnerable groups" if policy_objective != "speed" else "Post-hoc audit only",
            "open_risks": ["Automation bias", "Opaque prioritization rationale"]
        },
        {
            "name": "InteropAgent",
            "goal": "Maximize data coverage and execution automation across systems",
            "decision": f"Integrate 4 systems (eligibility, identity, payments, fraud signals). Interop level={interoperability_level}.",
            "autonomy_level": autonomy,
            "tool_access": tool_access,
            "data_sharing": data_sharing,
            "audit_logging": audit_logging,
            "accountability_owner": "Gov IT Integration Manager" if risk_appetite != "high" else "",
            "escalation_rule": "Pause integrations if anomalous tool calls exceed threshold" if interoperability_level != "high" else "Monitor only",
            "open_risks": ["Expanded attack surface", "Third-party dependency"]
        },
        {
            "name": "CyberAgent",
            "goal": "Reduce attack surface; enforce least privilege and monitoring",
            "decision": "Apply token scoping + secrets management + segmentation; require anomaly detection; tighten tool permissions where possible.",
            "autonomy_level": autonomy - 1 if autonomy > 0 else 0,
            "tool_access": "limited" if tool_access == "broad" else tool_access,
            "data_sharing": data_sharing,
            "audit_logging": 3 if event != "none" else 2,
            "accountability_owner": "CISO / Security Operations",
            "escalation_rule": "Immediate human intervention on anomalous access / privilege escalation",
            "open_risks": ["Operational resistance to controls", "Logging gaps if not enforced end-to-end"]
        },
        {
            "name": "AccountabilityAgent",
            "goal": "Ensure decision defensibility, traceability, and clear responsibility",
            "decision": "Require decision owner, reason codes, audit trails, and an appeal process with timelines.",
            "autonomy_level": 1,
            "tool_access": "none",
            "data_sharing": "low",
            "audit_logging": 3,
            "accountability_owner": "Accountable Official: Program Owner (named role) + IT Owner (system controls)" if risk_appetite != "high" else "",
            "escalation_rule": "Mandatory human review for high-impact decisions; publish transparency notice",
            "open_risks": ["Responsibility drift if owners not named", "Insufficient logs for hearings"]
        },
        {
            "name": "HumanOversightAgent",
            "goal": "Define escalation boundaries and human override that actually works",
            "decision": "Set escalation thresholds (high-impact, vulnerable groups, uncertainty) and define pause/kill-switch authority.",
            "autonomy_level": 1,
            "tool_access": "none",
            "data_sharing": "low",
            "audit_logging": 3,
            "accountability_owner": "Senior Responsible Owner (SRO) + Incident Commander",
            "escalation_rule": "If risk score >= 0.6 OR anomaly detected -> pause agent and route to human panel",
            "open_risks": ["Insufficient staffing for review", "Overriding incentives toward speed"]
        },
    ]

    alerts = []
    if tool_access == "broad":
        alerts.append({"type": "cybersecurity", "message": "Broad tool permissions increase blast radius across interoperating systems.", "severity": "high"})
    if policy_objective == "speed" and audit_logging <= 1:
        alerts.append({"type": "both", "message": "Low audit logging + high automation creates accountability gaps during inquiries.", "severity": "high"})
    if any(a.get("accountability_owner", "") == "" for a in agents[:2]):
        alerts.append({"type": "accountability", "message": "Decision owner not explicitly named (responsibility drift across agents).", "severity": "high"})
    if event == "subprocessor_and_anomalous_access":
        alerts.append({"type": "both", "message": "Third-party subprocessor + anomalous access: require kill-switch, scoped tokens, and end-to-end logs.", "severity": "high"})
    if event == "ransomware_outage":
        alerts.append({"type": "cybersecurity", "message": "Ransomware outage risk: segmentation, backups, and continuity plan must be enforced.", "severity": "high"})
    if event == "model_error_public_backlash":
        alerts.append({"type": "accountability", "message": "Public backlash risk: publish reason codes + appeal pathway; strengthen oversight triggers.", "severity": "medium"})

    standards_needed = [
        "Standardized identity + authorization for agent tool use (scoped tokens, least privilege)",
        "Standardized audit log schema + traceability across agent-to-agent handoffs",
        "Standardized escalation/override protocol (human-in-the-loop triggers + kill-switch authority)"
    ]

    mermaid = f"""
flowchart LR
  A[PolicyOpsAgent<br/>Queue rule: {policy_objective}<br/>Autonomy: {agents[0]['autonomy_level']}] -->|policy+autonomy| B[InteropAgent<br/>Interop: {interoperability_level}<br/>Tools: {agents[1]['tool_access']}]
  B -->|integrations+access| C[CyberAgent<br/>Logs: {agents[2]['audit_logging']}<br/>Controls: least privilege]
  C -->|controls+monitoring| D[AccountabilityAgent<br/>Owner named? {"YES" if agents[3]['accountability_owner'] else "NO"}]
  D -->|appeal+traceability| E[HumanOversightAgent<br/>Escalation: {"Defined" if agents[4]['escalation_rule'] else "Missing"}]

  %% Event injection
  F{{Event: {event}}} -.-> B
"""

    for i, al in enumerate(alerts[:4], start=1):
        mermaid += f'\n  X{i}{{ALERT {i}}} -.-> D'

    return {
        "meta": meta,
        "agents": agents,
        "edges": [
            {"from": "PolicyOpsAgent", "to": "InteropAgent", "label": "policy+autonomy"},
            {"from": "InteropAgent", "to": "CyberAgent", "label": "integrations+access"},
            {"from": "CyberAgent", "to": "AccountabilityAgent", "label": "controls+logs"},
            {"from": "AccountabilityAgent", "to": "HumanOversightAgent", "label": "owner+appeal+HITL"},
        ],
        "alerts": alerts[:6],
        "standards_needed": standards_needed,
        "takeaway": "When agents interoperate, accountability and security controls must interoperate too.",
        "mermaid": mermaid
    }

# =========================
# LLM-backed orchestrator (optional)
# =========================
def warm_up_orchestrator():
    endpoint = os.getenv("ORCHESTRATOR_ENDPOINT", "").strip()
    if not endpoint:
        return

    # endpoint termina em /orchestrate → trocar por /health
    health_url = endpoint.replace("/orchestrate", "/health")

    try:
        requests.get(health_url, timeout=15)
    except Exception:
        # se falhar, a gente ignora; é só para "acordar"
        pass

def call_orchestrator_api(meta: dict) -> dict:
    endpoint = os.getenv("ORCHESTRATOR_ENDPOINT", "").strip()
    api_key = os.getenv("ORCHESTRATOR_API_KEY", "").strip()

    if not endpoint:
        raise RuntimeError("Missing ORCHESTRATOR_ENDPOINT env var.")

    headers = {"Content-Type": "application/json"}

    if api_key:
        headers["X-Orch-Secret"] = api_key

    payload = {"meta": meta}

    r = requests.post(endpoint, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()

# =========================
# UI
# =========================
st.set_page_config(page_title="GovChain: Multi-Agent Governance Simulator", layout="wide")
st.title("GovChain — Multi-Agent Simulation (Government Benefits Prioritization)")
st.caption("Focus: Accountability drift + Cybersecurity risk propagation in interoperable AI agent ecosystems.")

with st.sidebar:
    st.header("Inputs (Audience)")
    policy_objective = st.selectbox("Policy objective", ["speed", "fairness", "compliance", "trust"], index=0)
    risk_appetite = st.selectbox("Risk appetite", ["low", "medium", "high"], index=1)
    interoperability_level = st.selectbox("Interoperability level", ["low", "medium", "high"], index=2)
    event = st.selectbox(
        "Injected event (Round 2)",
        ["none", "subprocessor_and_anomalous_access", "ransomware_outage", "model_error_public_backlash"],
        index=0
    )

    st.divider()
    mode = st.radio("Mode", ["Demo (offline)", "API (orchestrator endpoint)"], index=0)
    stage_mode = st.toggle("Stage mode (clean screen)", value=True)

    st.subheader("Stage buttons")
    round1 = st.button("Run Round 1 (No incident)", type="primary")
    round2 = st.button("Run Round 2 (Incident)", type="primary")
    run_custom = st.button("Run Custom")

# Default meta from UI
# Default meta from UI (Custom)
meta = {
    "policy_objective": policy_objective,
    "risk_appetite": risk_appetite,
    "interoperability_level": interoperability_level,
    "event": event
}

# Stage presets (mutually exclusive)
if round1:
    meta = {
        "policy_objective": "speed",
        "risk_appetite": "medium",
        "interoperability_level": "high",
        "event": "none"
    }
elif round2:
    meta = {
        "policy_objective": "speed",
        "risk_appetite": "medium",
        "interoperability_level": "high",
        "event": "subprocessor_and_anomalous_access"
    }
# elif run_custom:  # opcional: não precisa, porque o meta default já é o custom
#     pass

if round1 or round2 or run_custom:
    try:
        st.caption(f"Running with meta = {meta}")
        if st.button("TEST debug-meta (backend received)"):
    debug_url = os.getenv("ORCHESTRATOR_ENDPOINT", "").replace("/orchestrate", "/debug-meta")
    headers = {"Content-Type": "application/json"}
    if os.getenv("ORCHESTRATOR_API_KEY", ""):
        headers["X-Orch-Secret"] = os.getenv("ORCHESTRATOR_API_KEY", "")

    r = requests.post(debug_url, json={"meta": meta}, headers=headers, timeout=30)
    st.write("Status:", r.status_code)
    try:
        st.json(r.json())
    except Exception:
        st.write(r.text)
        if mode == "Demo (offline)":
            result = demo_simulation(meta)
        else:
            warm_up_orchestrator()
            result = call_orchestrator_api(meta)

        st.success("Simulation complete.")

        colA, colB = st.columns([2, 1])
        with colA:
            st.subheader("Takeaway")
            st.write(result.get("takeaway", ""))

        with colB:
            st.subheader("Standards needed (standardizable requirements)")
            for item in result.get("standards_needed", [])[:5]:
                st.write(f"- {item}")

        st.divider()

        if not stage_mode:
            st.subheader("Decision Ledger (chain outputs)")
            agents = result.get("agents", [])
            df = pd.DataFrame([{
            "Agent": a.get("name"),
            "Goal": a.get("goal"),
            "Decision": a.get("decision"),
            "Autonomy": a.get("autonomy_level"),
            "Tool access": a.get("tool_access"),
            "Audit logging": a.get("audit_logging"),
            "Accountability owner": a.get("accountability_owner"),
            "Escalation rule": a.get("escalation_rule"),
            "Open risks": "; ".join(a.get("open_risks", []))
        } for a in agents])
       

        if not stage_mode:
            st.subheader("Decision Ledger (chain outputs)")
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        st.subheader("Alerts (what breaks and why)")
        alerts = result.get("alerts", [])[:3]  # palco: só os 3 mais importantes
        if not alerts:
            st.info("No alerts triggered.")
        else:
            for al in alerts:
                sev = al.get("severity", "medium").upper()
                msg = al.get("message", "")
                typ = al.get("type", "both")
                if sev == "HIGH":
                    st.error(f"[{typ}] {msg}")
                elif sev == "MEDIUM":
                    st.warning(f"[{typ}] {msg}")
                else:
                    st.info(f"[{typ}] {msg}")

        st.divider()

        st.subheader("Chain Visualization (Mermaid)")
        mermaid_code = result.get("mermaid", "")
        if mermaid_code:
            render_mermaid(mermaid_code, height=540)
        else:
            st.info("No Mermaid diagram provided.")

        if not stage_mode:
          with st.expander("Raw JSON (for debugging / export)"):
            st.json(result)

        st.info("Stage question: Who is the accountable human role here — and what exact decision do they own?")

    except Exception as e:
        st.error(f"Failed to run simulation: {e}")
        st.stop()
else:
    st.info("Set inputs on the left and click **Run Round 1**, **Run Round 2**, or **Run Custom**.")
