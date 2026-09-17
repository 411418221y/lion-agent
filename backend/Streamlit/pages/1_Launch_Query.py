import streamlit as st
import requests

# ---------------------------
# Config
# ---------------------------
API = "http://localhost:8000/ask"

st.set_page_config(
    page_title="Launch Query",
    layout="wide"
)

st.title("🚀 Launch Query")
st.caption("Ask questions and get: Checklist + Templates + Risks + Citations (offline)")
st.divider()

# ---------------------------
# Demo questions
# ---------------------------
demos = {
    "Billing - Wrong Fee": "My bill shows a monthly pet fee but my lease says no monthly pet fee. Write an email to waive it.",
    "Billing - Unknown Charge": "I was charged a fee I don’t understand. What steps should I take?",
    "Course - Waitlist Appeal": "Help me write a waitlist appeal email to the professor. I can attend every class.",
    "Course - What to include": "What info should I include in a waitlist request?",
    "Housing - Family eligibility": "Do I qualify for family housing with a domestic partner? What documents do I need?",
    "Housing - Steps": "What steps should I take to apply for family housing?",
    "Fallback (Not covered)": "Can I bring a reptile into housing?"
}

with st.sidebar:
    st.header("🎯 Demo Questions")
    demo_key = st.selectbox("Pick a demo:", list(demos.keys()))
    st.caption("Backend should be running on http://localhost:8000")

# ---------------------------
# Helpers
# ---------------------------
def safe_get(obj, key, default):
    if not isinstance(obj, dict):
        return default
    v = obj.get(key, default)
    return default if v is None else v


def post_ask(q: str) -> dict:
    r = requests.post(API, json={"question": q}, timeout=120)
    r.raise_for_status()
    return r.json()


# ---------------------------
# Input
# ---------------------------
c1, c2 = st.columns([5, 1])
with c1:
    question = st.text_input("Ask:", value=demos.get(demo_key, ""))
with c2:
    run = st.button("🚀 Run", use_container_width=True)

left, right = st.columns([3, 1])

# ---------------------------
# Run query
# ---------------------------
if run and question.strip():
    try:
        with st.spinner("Analyzing offline policies..."):
            res = post_ask(question.strip())
    except Exception as e:
        st.error(f"Failed to call backend /ask at {API}\n\nError: {e}")
        st.info("Make sure backend is running:\n\nuvicorn app:app --reload")
        st.stop()

    checklist = safe_get(res, "checklist", [])
    templates = safe_get(res, "templates", [])
    risks = safe_get(res, "risks", [])
    citations = safe_get(res, "citations", [])
    confidence = float(safe_get(res, "confidence", 0.0))

    # type guards
    if not isinstance(checklist, list):
        checklist = []
    if not isinstance(templates, list):
        templates = []
    if not isinstance(risks, list):
        risks = []
    if not isinstance(citations, list):
        citations = []

    tabs = left.tabs(["📋 Checklist", "✉️ Templates", "⚠️ Risks", "📎 Sources"])

    # ---------------- Checklist ----------------
    with tabs[0]:
        st.subheader("Action Steps")
        if not checklist:
            st.info("No checklist returned.")
        for i, step in enumerate(checklist, 1):
            if not isinstance(step, dict):
                continue
            text = step.get("text", "")
            cites = step.get("citations", []) or []
            if not isinstance(cites, list):
                cites = [str(cites)]

            st.markdown(f"### ✅ Step {i}")
            st.write(text if text else "—")
            st.caption("Sources: " + (", ".join(cites) if cites else "(none)"))

    # ---------------- Templates ----------------
    with tabs[1]:
        st.subheader("Templates")
        if not templates:
            st.info("No templates returned.")
        for idx, t in enumerate(templates, 1):
            if not isinstance(t, dict):
                continue
            ttype = t.get("type", "email")
            subject = t.get("subject", f"Template {idx}")
            body = t.get("body", "")

            st.markdown(f"#### {ttype.upper()} — {subject}")
            st.text_area("Body", value=body, height=220, key=f"tmpl_{idx}")
            st.download_button(
                "📄 Download",
                data=body,
                file_name=f"template_{idx}.txt",
                mime="text/plain",
                key=f"dl_{idx}"
            )
            st.divider()

    # ---------------- Risks ----------------
    with tabs[2]:
        st.subheader("Risks & Mitigations")
        if not risks:
            st.info("No risks returned.")
        for r in risks:
            if not isinstance(r, dict):
                continue
            risk = r.get("risk", "")
            mitigation = r.get("mitigation", "")
            cites = r.get("citations", []) or []
            if not isinstance(cites, list):
                cites = [str(cites)]

            st.warning(risk if risk else "—")
            if mitigation:
                st.caption("Mitigation: " + mitigation)
            if cites:
                st.caption("Sources: " + ", ".join(cites))

    # ---------------- Sources ----------------
    with tabs[3]:
        st.subheader("Evidence Snippets")
        if not citations:
            st.info("No citations returned.")
        else:
            for c in citations:
                if not isinstance(c, dict):
                    continue
                ref = c.get("ref", "(no ref)")
                excerpt = c.get("excerpt", "")
                with st.expander(ref):
                    st.write(excerpt if excerpt else "—")

    # ---------------- Right panel ----------------
    with right:
        st.subheader("📌 Status")
        st.metric("Confidence", f"{int(confidence * 100)}%")
        st.caption(f"API: {API}")
        st.write("Checklist steps:", len(checklist))
        st.write("Templates:", len(templates))
        st.write("Risks:", len(risks))
        st.write("Citations:", len(citations))

else:
    left.info("Pick a demo question or type your own, then click **Run**.")
    right.info("Status will show after you run a query.")
