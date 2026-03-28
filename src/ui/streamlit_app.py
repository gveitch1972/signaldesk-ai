import streamlit as st

from src.config import ENABLE_HEAVY_CONTEXT_FOR_BRIEFING, ENABLE_HEAVY_CONTEXT_FOR_QA
from src.briefing.chat import ask_question
from src.briefing.context_builder import build_context, clear_context_cache, get_latest_dates
from src.briefing.generate_briefing import generate_briefing
from src.queries.fx import load_fx_watchlist
from src.queries.macro import load_macro_trends
from src.queries.regime import load_latest_regime
from src.queries.top_movers import load_top_movers_why


st.set_page_config(page_title="SignalDesk AI", layout="wide")


def _safe_rows(loader, fallback=None):
    if fallback is None:
        fallback = []
    try:
        rows = loader()
        return rows if rows else fallback
    except Exception:
        return fallback


st.title("SignalDesk AI")
st.caption("AI + Databricks market intelligence with explainable movers")

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

latest_dates = _safe_rows(get_latest_dates, fallback={})
st.caption(
    "Freshness: "
    f"regime={latest_dates.get('regime_as_of_date') or 'n/a'} | "
    f"market={latest_dates.get('market_snapshot_date') or 'n/a'} | "
    f"fx={latest_dates.get('fx_rate_date') or 'n/a'} | "
    f"movers={latest_dates.get('movers_as_of_date') or 'n/a'}"
)

regime_rows = _safe_rows(load_latest_regime, fallback=[{}])
latest_regime = regime_rows[0] if regime_rows else {}

k1, k2, k3, k4 = st.columns(4)
k1.metric("Risk Regime", str(latest_regime.get("risk_regime", "unknown")))
k2.metric("Market Stress", str(latest_regime.get("market_stress_symbols", "n/a")))
k3.metric("FX Stress", str(latest_regime.get("fx_stress_pairs", "n/a")))
k4.metric(
    "Macro Balance",
    f"{latest_regime.get('macro_up_indicators', 'n/a')}↑ / {latest_regime.get('macro_down_indicators', 'n/a')}↓",
)

st.subheader("Top Movers + Why")
top_movers = _safe_rows(load_top_movers_why, fallback=[])
if top_movers:
    st.dataframe(top_movers, use_container_width=True)
else:
    st.info("Top movers explainability is unavailable right now.")

left, right = st.columns(2)
with left:
    st.subheader("FX Watch")
    fx_rows = _safe_rows(load_fx_watchlist, fallback=[])
    if fx_rows:
        st.dataframe(fx_rows, use_container_width=True)
    else:
        st.info("FX watchlist unavailable.")

with right:
    st.subheader("Macro Pulse")
    macro_rows = _safe_rows(load_macro_trends, fallback=[])
    if macro_rows:
        st.dataframe(macro_rows, use_container_width=True)
    else:
        st.info("Macro trends unavailable.")

st.subheader("Ask SignalDesk")
with st.form("ask_form", clear_on_submit=False):
    question = st.text_input("Ask a question about the data")
    ask_submitted = st.form_submit_button("Ask")

if ask_submitted and question.strip():
    with st.spinner("Thinking..."):
        answer = ask_question(question, include_heavy=include_heavy_for_qa)
    st.session_state["answer"] = answer

if "answer" in st.session_state:
    st.markdown(st.session_state["answer"])

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    if st.button("Generate Briefing"):
        with st.spinner("Generating briefing..."):
            st.session_state["briefing"] = generate_briefing(include_heavy=include_heavy_for_briefing)

with c2:
    if st.button("Regenerate Briefing"):
        with st.spinner("Regenerating briefing..."):
            st.session_state["briefing"] = generate_briefing(include_heavy=include_heavy_for_briefing)

with c3:
    if st.button("Show Raw Context"):
        st.session_state["context"] = build_context(include_heavy=include_heavy_for_briefing)

if "briefing" in st.session_state:
    st.subheader("Executive Briefing")
    st.markdown(st.session_state["briefing"])
    st.download_button(
        "Copy Briefing",
        data=st.session_state["briefing"],
        file_name="signaldesk_briefing.txt",
        mime="text/plain",
    )

if "context" in st.session_state:
    st.subheader("Raw Context")
    st.code(st.session_state["context"])
