import os

import pandas as pd
import streamlit as st

from src.briefing.chat import ask_question
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


def _fmt_pct(value) -> str:
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def _to_frame(rows) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


st.title("SignalDesk AI")
st.caption("Databricks lakehouse + Foundry AI for senior market briefings")

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

page1, page2 = st.tabs(["Page 1: Signals Snapshot", "Page 2: Senior Briefing"])

with page1:
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Stress",
        str(latest_regime.get("risk_regime", "unknown")),
        _fmt_pct(latest_regime.get("market_avg_day_change_pct")),
    )
    m2.metric(
        "FX",
        str(latest_regime.get("fx_stress_pairs", "n/a")),
        _fmt_pct(latest_regime.get("fx_avg_daily_change_pct")),
    )
    m3.metric(
        "Macro",
        f"{latest_regime.get('macro_up_indicators', 'n/a')}↑/{latest_regime.get('macro_down_indicators', 'n/a')}↓",
        _fmt_pct(latest_regime.get("macro_avg_period_change_pct")),
    )

    st.subheader("Cross-Asset Movers")
    if not movers_df.empty and {"symbol", "return_30d_pct"}.issubset(movers_df.columns):
        chart_df = movers_df[["symbol", "return_30d_pct"]].copy()
        chart_df["return_30d_pct"] = pd.to_numeric(
            chart_df["return_30d_pct"], errors="coerce"
        )
        chart_df = chart_df.dropna().sort_values("return_30d_pct")
        if not chart_df.empty:
            st.bar_chart(chart_df.set_index("symbol"))
        else:
            st.info("Chart unavailable: return values are missing.")
    else:
        st.info("Chart unavailable: top movers data is missing.")

    st.subheader("Top Movers Table")
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
        st.info("Top movers table unavailable right now.")

with page2:
    st.subheader("Prompt")
    default_prompt = (
        "Write a concise senior market briefing with sections for: "
        "(1) what changed, (2) why it matters, (3) what to watch next."
    )
    prompt = st.text_area(
        "Briefing instruction",
        value=st.session_state.get("briefing_prompt", default_prompt),
        height=120,
    )
    st.session_state["briefing_prompt"] = prompt

    b1, b2 = st.columns([1, 3])
    with b1:
        if st.button("Generate AI Briefing", use_container_width=True):
            with st.spinner("Generating briefing..."):
                st.session_state["briefing"] = ask_question(
                    prompt, include_heavy=include_heavy_for_briefing
                )

    with b2:
        st.caption("Use this as the daily senior-ready narrative. Edit the prompt to shift tone or focus.")

    st.subheader("AI-Generated Briefing")
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

    st.subheader("Explain This Spike")
    if not movers_df.empty and "symbol" in movers_df.columns:
        symbols = [str(s) for s in movers_df["symbol"].dropna().tolist()]
        selected_symbol = st.selectbox("Pick a symbol", symbols)
        if st.button("Explain this spike"):
            with st.spinner("Analyzing spike..."):
                st.session_state["spike_explanation"] = ask_question(
                    (
                        f"Explain the latest spike for {selected_symbol}. "
                        "Use concrete datapoints, likely drivers, and key risks to monitor."
                    ),
                    include_heavy=include_heavy_for_qa,
                )
    else:
        st.info("No mover symbols available for spike analysis.")

    if "spike_explanation" in st.session_state:
        st.markdown(st.session_state["spike_explanation"])
