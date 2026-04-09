import os

import pandas as pd
import streamlit as st

from src.briefing.chat import ask_question
from src.disruption.signals import DISRUPTION_THEMES, SCRAPED_DATE
from src.briefing.context_builder import (
    clear_context_cache,
    get_context_payload,
    get_latest_dates,
)
from src.config import (
    ENABLE_HEAVY_CONTEXT_FOR_BRIEFING,
    ENABLE_HEAVY_CONTEXT_FOR_QA,
    ENABLE_SERVERLESS_COMPUTE,
    ENABLE_UI_DEBUG,
)


st.set_page_config(page_title="SignalDesk AI", layout="wide")


def _safe_rows(loader, fallback=None, debug_label: str = "", show_debug: bool = False):
    if fallback is None:
        fallback = []
    try:
        rows = loader()
        return rows if rows else fallback
    except Exception as exc:
        if show_debug:
            label = debug_label or "data loader"
            st.error(f"Debug: `{label}` failed with `{type(exc).__name__}`: {exc}")
        return fallback


def _to_frame(rows) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def _append_chat(role: str, content: str) -> None:
    history = st.session_state.setdefault("chat_history", [])
    history.append({"role": role, "content": content})


def _render_chat_history() -> None:
    history = st.session_state.get("chat_history", [])
    if not history:
        st.info("No Q&A history yet. Ask a question to start a running thread.")
        return
    for item in history:
        with st.chat_message(item.get("role", "assistant")):
            st.markdown(item.get("content", ""))


st.title("SignalDesk AI")
st.caption("Databricks lakehouse + Foundry AI for market monitoring and executive briefing")

with st.sidebar:
    st.subheader("Controls")
    previous_serverless_mode = st.session_state.get(
        "use_serverless_compute", ENABLE_SERVERLESS_COMPUTE
    )
    use_serverless_compute = st.checkbox(
        "Use Serverless Compute",
        value=previous_serverless_mode,
        help="When on, skips single-node compute validation for serverless-backed jobs.",
    )
    st.session_state["use_serverless_compute"] = use_serverless_compute
    os.environ["USE_SERVERLESS_COMPUTE"] = "true" if use_serverless_compute else "false"
    if previous_serverless_mode != use_serverless_compute:
        clear_context_cache()
        st.info("Compute mode changed. Context cache cleared.")

    show_debug = st.checkbox("Debug mode", value=ENABLE_UI_DEBUG)
    include_heavy_for_qa = st.checkbox(
        "Include heavy context for Q&A", value=ENABLE_HEAVY_CONTEXT_FOR_QA
    )
    include_heavy_for_briefing = st.checkbox(
        "Include heavy context for briefing", value=ENABLE_HEAVY_CONTEXT_FOR_BRIEFING
    )
    if st.button("Refresh cached context"):
        clear_context_cache()
        st.success("Context cache cleared.")
    if st.button("Clear chat history"):
        st.session_state["chat_history"] = []
        st.success("Chat history cleared.")

latest_dates = _safe_rows(
    lambda: get_latest_dates(raise_on_error=show_debug),
    fallback={},
    debug_label="latest_dates",
    show_debug=show_debug,
)
st.caption(
    "Freshness: "
    f"regime={latest_dates.get('regime_as_of_date') or 'n/a'} | "
    f"market={latest_dates.get('market_snapshot_date') or 'n/a'} | "
    f"fx={latest_dates.get('fx_rate_date') or 'n/a'} | "
    f"movers={latest_dates.get('movers_as_of_date') or 'n/a'}"
)

payload = _safe_rows(
    lambda: get_context_payload(include_heavy=False, raise_on_error=show_debug),
    fallback={},
    debug_label="context_payload_fast",
    show_debug=show_debug,
)
regime_rows = payload.get("regime") or [{}]
latest_regime = regime_rows[0] if regime_rows else {}

movers_df = _to_frame(payload.get("top_movers") or [])
fx_df = _to_frame(payload.get("fx_watchlist") or [])
macro_df = _to_frame(payload.get("macro_trends") or [])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Risk Regime", str(latest_regime.get("risk_regime", "unknown")))
k2.metric("Market Stress", str(latest_regime.get("market_stress_symbols", "n/a")))
k3.metric("FX Stress", str(latest_regime.get("fx_stress_pairs", "n/a")))
k4.metric(
    "Macro Balance",
    f"{latest_regime.get('macro_up_indicators', 'n/a')}↑ / {latest_regime.get('macro_down_indicators', 'n/a')}↓",
)

st.subheader("Top Movers")
if not movers_df.empty:
    preferred_cols = [
        "symbol",
        "latest_price",
        "day_change_pct",
        "return_30d_pct",
        "stress_flag",
        "why_summary",
    ]
    table_cols = [col for col in preferred_cols if col in movers_df.columns]
    st.dataframe(movers_df[table_cols] if table_cols else movers_df, use_container_width=True)
else:
    st.info("Top movers explainability is unavailable right now.")

left, right = st.columns(2)
with left:
    st.subheader("FX Watch")
    if fx_df.empty:
        st.info("FX watchlist unavailable.")
    else:
        st.dataframe(fx_df, use_container_width=True)

with right:
    st.subheader("Macro Pulse")
    if macro_df.empty:
        st.info("Macro trends unavailable.")
    else:
        st.dataframe(macro_df, use_container_width=True)

st.subheader("Disruption Intelligence")
st.caption(f"Key themes from EY, Deloitte, McKinsey & KPMG — sourced {SCRAPED_DATE}")

for theme in DISRUPTION_THEMES:
    with st.expander(f"{theme['icon']}  {theme['theme']}"):
        st.markdown(f"_{theme['summary']}_")
        st.divider()
        cols = st.columns(len(theme["firms"]))
        for col, (firm, points) in zip(cols, theme["firms"].items()):
            with col:
                st.markdown(f"**{firm}**")
                for point in points:
                    st.markdown(f"- {point}")

st.subheader("Ask SignalDesk")
with st.form("ask_form", clear_on_submit=False):
    question = st.text_input("Ask a question about the data")
    ask_submitted = st.form_submit_button("Ask")

if ask_submitted and question.strip():
    _append_chat("user", question.strip())
    with st.spinner("Thinking..."):
        answer = ask_question(question.strip(), include_heavy=include_heavy_for_qa)
    _append_chat("assistant", answer)

_render_chat_history()

st.subheader("Executive Briefing")
default_prompt = (
    "Write a concise senior market briefing with sections for: "
    "(1) what changed, (2) why it matters, (3) what to watch next."
)
briefing_prompt = st.text_area(
    "Briefing instruction",
    value=st.session_state.get("briefing_prompt", default_prompt),
    height=110,
)
st.session_state["briefing_prompt"] = briefing_prompt

b1, b2, b3 = st.columns([1, 1, 2])
with b1:
    if st.button("Generate Briefing"):
        with st.spinner("Generating briefing..."):
            st.session_state["briefing"] = ask_question(
                briefing_prompt, include_heavy=include_heavy_for_briefing
            )
with b2:
    if st.button("Regenerate Briefing"):
        with st.spinner("Regenerating briefing..."):
            st.session_state["briefing"] = ask_question(
                briefing_prompt, include_heavy=include_heavy_for_briefing
            )
with b3:
    if not movers_df.empty and "symbol" in movers_df.columns:
        symbols = [str(s) for s in movers_df["symbol"].dropna().tolist()]
        selected_symbol = st.selectbox("Explain This Spike", symbols, key="spike_symbol")
        if st.button("Analyze Selected Symbol"):
            user_prompt = (
                f"Explain the latest spike for {selected_symbol}. "
                "Use concrete datapoints, likely drivers, and key risks to monitor."
            )
            _append_chat("user", user_prompt)
            with st.spinner("Analyzing spike..."):
                spike_response = ask_question(
                    user_prompt, include_heavy=include_heavy_for_qa
                )
            _append_chat("assistant", spike_response)

if "briefing" in st.session_state:
    st.markdown(st.session_state["briefing"])
    st.download_button(
        "Download Briefing",
        data=st.session_state["briefing"],
        file_name="signaldesk_briefing.txt",
        mime="text/plain",
    )
else:
    st.info("Generate a briefing to populate this section.")
