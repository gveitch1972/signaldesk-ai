import streamlit as st
from src.config import ENABLE_HEAVY_CONTEXT_FOR_BRIEFING, ENABLE_HEAVY_CONTEXT_FOR_QA
from src.briefing.generate_briefing import generate_briefing
from src.briefing.context_builder import build_context, clear_context_cache
from src.briefing.chat import ask_question


st.set_page_config(page_title="SignalDesk AI", layout="wide")

st.title("SignalDesk AI")
st.caption("AI & Databricks-powered market, FX, macro, and risk-regime briefing")

with st.sidebar:
    st.subheader("Cost Controls")
    include_heavy_for_qa = st.checkbox(
        "Include heavy context for Q&A",
        value=ENABLE_HEAVY_CONTEXT_FOR_QA,
        help="When off, skips coverage/history queries that scan larger datasets.",
    )
    include_heavy_for_briefing = st.checkbox(
        "Include heavy context for briefing",
        value=ENABLE_HEAVY_CONTEXT_FOR_BRIEFING,
        help="When on, briefing includes coverage/history sections.",
    )
    if st.button("Refresh cached context now"):
        clear_context_cache()
        st.success("Context cache cleared.")

st.subheader("Ask SignalDesk")

with st.form("ask_form", clear_on_submit=False):
    question = st.text_input("Ask a question about the data")
    ask_submitted = st.form_submit_button("Ask")

if ask_submitted and question.strip():
    with st.spinner("Thinking..."):
        answer = ask_question(question, include_heavy=include_heavy_for_qa)
    st.markdown(answer)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Generate Briefing"):
        with st.spinner("Generating briefing..."):
            briefing = generate_briefing(include_heavy=include_heavy_for_briefing)
        st.session_state["briefing"] = briefing

with col2:
    if st.button("Show Raw Context"):
        st.session_state["context"] = build_context(
            include_heavy=include_heavy_for_briefing
        )

if "briefing" in st.session_state:
    st.subheader("Briefing")
    st.markdown(st.session_state["briefing"])

if "context" in st.session_state:
    st.subheader("Raw Context")
    st.code(st.session_state["context"])
