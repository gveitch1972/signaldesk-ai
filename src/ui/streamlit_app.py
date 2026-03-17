import streamlit as st
from src.briefing.generate_briefing import generate_briefing
from src.briefing.context_builder import build_context

st.set_page_config(page_title="SignalDesk AI", layout="wide")

st.title("SignalDesk AI")
st.caption("AI & Databricks-powered market, FX, macro, and risk-regime briefing")
# st.metric("Current Regime:", regime_flag)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Generate Briefing"):
        with st.spinner("Generating briefing..."):
            briefing = generate_briefing()
        st.session_state["briefing"] = briefing

with col2:
    if st.button("Show Raw Context"):
        st.session_state["context"] = build_context()

if "briefing" in st.session_state:
    st.subheader("Briefing")
    st.markdown(st.session_state["briefing"])

if "context" in st.session_state:
    st.subheader("Raw Context")
    st.code(st.session_state["context"])
