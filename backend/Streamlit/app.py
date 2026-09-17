import streamlit as st
import requests
import os
import base64
import streamlit.components.v1 as components


# ===============================
# Page Config
# ===============================
st.set_page_config(
    page_title="Lion Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===============================
# Session State Init
# ===============================

if "main_query" not in st.session_state:
    st.session_state.main_query = ""

if "pending_fill" not in st.session_state:
    st.session_state.pending_fill = None


# ===============================
# Global CSS
# ===============================
st.markdown("""
<style>

div[data-baseweb="input"] {
    max-width: 850px;
    margin: 0 auto;
}

.stApp {
    background-color: #ffffff;
}

.main .block-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 2.5rem;
    margin-top: 1.5rem;
}

/* Default button style */
.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 0.55rem 1.3rem;  /* slightly tighter for consistent height */
    font-weight: 600;
    border: none;
}

.stButton > button:hover {
    background: #1d4ed8;
}

/* Card style */
.card {
    background: #f9fafb;
    padding: 1.4rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
}

/* ✅ Category buttons: same height + no ugly wrapping */
.category-btn button {
    height: 58px !important;
    padding: 0 14px !important;   /* keep them consistent */
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    font-size: 16px !important;
}

</style>
""", unsafe_allow_html=True)


# ===============================
# Sidebar
# ===============================
st.sidebar.title("Lion Agent")

st.sidebar.markdown("### Navigation")
st.sidebar.page_link("app.py", label=" Home")
st.sidebar.page_link("pages/1_Launch_Query.py", label=" Launch Query")
st.sidebar.page_link("pages/2_Manage_Docs.py", label=" Manage Docs")
st.sidebar.divider()

USE_MOCK = False
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.sidebar.markdown("Backend:")
st.sidebar.code(BACKEND_URL)



# ===============================
# Mock Response
# ===============================
def mock_response(question: str):

    return {
        "checklist": [
            "Review Columbia policy documentation",
            "Prepare appeal materials",
            "Submit request via official portal",
            "Follow up with advisor",
        ],
        "templates": [
            "Dear Office,\n\nI am writing to request...\n\nBest regards",
            "Hello,\n\nI would like to appeal...\n\nThank you"
        ],
        "risks": [
            "Missing deadline",
            "Incomplete documentation"
        ],
        "citations": [
            "Columbia Student Handbook 2025",
            "GS Policy Manual Section 4"
        ]
    }


# ===============================
# Header
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "assets", "logo.jpg")

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

components.html(
    f"""
    <div style="text-align:center; margin-top:40px;">
        <div style="
            font-size:44px;
            font-weight:700;
            display:flex;
            justify-content:center;
            align-items:center;
            gap:12px;
        ">
            <img src="data:image/png;base64,{logo_base64}" style="height:45px;" />
            <span>Lion Agent</span>
        </div>

        <div style="
            margin-top:12px;
            font-size:18px;
            color:#6b7280;
        ">
            Chat about Columbia.
        </div>
    </div>
    """,
    height=160,
)

st.divider()


# ===============================
# Input Area
# ===============================


if st.session_state.pending_fill:
    st.session_state.main_query = st.session_state.pending_fill
    st.session_state.pending_fill = None


st.markdown("<br>", unsafe_allow_html=True)

query = st.text_input(
    label="Ask a question",
    placeholder="Ask me anything about Columbia...",
    value=st.session_state.main_query,
    key="main_query"
)


c1, c2, c3 = st.columns([3, 1, 3])
with c2:
    run = st.button("Ask")

st.markdown("<br>", unsafe_allow_html=True)


# ===============================
# Backend Call
# ===============================
if run and query.strip():
    st.write("✅ button clicked")
    st.write("query =", query)

    st.markdown("### Your Question")
    st.info(query)

    st.markdown("### AI Response")

    with st.spinner("Thinking..."):

        try:

            if USE_MOCK:
                data = mock_response(query)

            else:
                res = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": query},
                    timeout=180
                )

                if res.status_code != 200:
                    st.error("Backend error.")
                    st.stop()

                data = res.json()

        except Exception as e:

            st.error(f"Connection failed: {e}")
            st.stop()


    tabs = st.tabs([" Checklist", " Templates", " Risks", " Citations"])

    with tabs[0]:
        for i, step in enumerate(data.get("checklist", []), 1):
            st.write(f"{i}. {step}")

    with tabs[1]:
        for t in data.get("templates", []):
            st.code(t)

    with tabs[2]:
        for r in data.get("risks", []):
            st.warning(r)

    with tabs[3]:
        for c in data.get("citations", []):
            st.caption(c)


st.divider()

st.markdown("## Supported Categories")

import random

def quick_fill(text):
    st.session_state.pending_fill = text


# Random questions for "Others"
others_questions = [
    "Where is the dining hall?",
    "How do I reset my Columbia password?",
    "What campus policies should I know?",
    "How do I request official documents?",
    "Do I need an ID to enter buildings?"
]

cols = st.columns(6)

categories = [
    ("📘 Course", "I want to appeal a course waitlist or credit issue.", "Waitlists, credits, appeals."),
    ("💳 Billing", "I have a billing or refund dispute.", "Fees, refunds, disputes."),
    ("🏠 Housing", "I have a housing eligibility or lease issue.", "Eligibility, leases."),
    ("🎓 Financial Aid", "I have a financial aid or FAFSA related question.", "FAFSA, awards, deadlines."),
    ("🚇 Transportation", "How can I commute to campus or use campus transportation?", "Transit, shuttle, parking."),
    ("📂 Others", random.choice(others_questions), "Random common questions.")
]

for col, (title, text, caption) in zip(cols, categories):
    with col:
        st.markdown('<div class="category-btn">', unsafe_allow_html=True)

        clicked = st.button(title, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.caption(caption)

        if clicked:
            quick_fill(text)



# ===============================
# Footer
# ===============================
st.divider()

st.caption("Built for Columbia Hackathon • Lion Agent • Offline AI Assistant")
