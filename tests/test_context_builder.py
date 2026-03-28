import src.briefing.context_builder as context_builder


def test_build_context_fast_mode_avoids_heavy_loaders(monkeypatch):
    monkeypatch.setattr(context_builder, "load_latest_regime", lambda: [{"risk_regime": "calm"}])
    monkeypatch.setattr(context_builder, "load_market_breadth", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_market_stress", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_fx_watchlist", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_macro_trends", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_top_movers_why", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "get_latest_dates", lambda: {"market": "2026-03-25"})
    monkeypatch.setattr(context_builder, "_load_latest_dates_signature", lambda: ("1", "2", "3", "4"))

    def should_not_run():
        raise AssertionError("heavy loader should not run")

    monkeypatch.setattr(context_builder, "load_market_coverage", should_not_run)
    monkeypatch.setattr(context_builder, "load_fx_coverage", should_not_run)
    monkeypatch.setattr(context_builder, "load_fx_history_summary", should_not_run)
    monkeypatch.setattr(context_builder, "load_macro_coverage", should_not_run)

    context_builder.clear_context_cache()
    result = context_builder.build_context(include_heavy=False, force_refresh=True)

    assert "TOP MOVERS + WHY" in result
    assert "MARKET COVERAGE" not in result


def test_build_context_handles_empty_sources(monkeypatch):
    monkeypatch.setattr(context_builder, "load_latest_regime", lambda: [])
    monkeypatch.setattr(context_builder, "load_market_breadth", lambda: [])
    monkeypatch.setattr(context_builder, "load_market_stress", lambda: [])
    monkeypatch.setattr(context_builder, "load_fx_watchlist", lambda: [])
    monkeypatch.setattr(context_builder, "load_macro_trends", lambda: [])
    monkeypatch.setattr(context_builder, "load_top_movers_why", lambda: [])
    monkeypatch.setattr(context_builder, "load_market_coverage", lambda: [])
    monkeypatch.setattr(context_builder, "load_fx_coverage", lambda: [])
    monkeypatch.setattr(context_builder, "load_fx_history_summary", lambda: [])
    monkeypatch.setattr(context_builder, "load_macro_coverage", lambda: [])
    monkeypatch.setattr(context_builder, "get_latest_dates", lambda: {})
    monkeypatch.setattr(context_builder, "_load_latest_dates_signature", lambda: ("", "", "", ""))

    context_builder.clear_context_cache()
    result = context_builder.build_context(include_heavy=True, force_refresh=True)

    assert "Regime data unavailable" in result
    assert "Top movers explainability unavailable" in result


def test_prompt_includes_top_movers_section(monkeypatch):
    monkeypatch.setattr(context_builder, "load_latest_regime", lambda: [{"risk_regime": "elevated"}])
    monkeypatch.setattr(context_builder, "load_market_breadth", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_market_stress", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_fx_watchlist", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_macro_trends", lambda: [{"k": 1}])
    monkeypatch.setattr(context_builder, "load_top_movers_why", lambda: [{"symbol": "AAA", "why_summary": "Reason"}])
    monkeypatch.setattr(context_builder, "get_latest_dates", lambda: {"market": "2026-03-25"})
    monkeypatch.setattr(context_builder, "_load_latest_dates_signature", lambda: ("1", "2", "3", "4"))

    context_builder.clear_context_cache()
    result = context_builder.build_context(include_heavy=False, force_refresh=True)

    assert "TOP MOVERS + WHY" in result
    assert "AAA" in result
