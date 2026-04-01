import src.briefing.context_builder as context_builder


def _base_payload():
    return {
        "latest_dates": {
            "regime_as_of_date": "2026-03-31",
            "market_snapshot_date": "2026-03-31",
            "fx_rate_date": "2026-03-31",
            "movers_as_of_date": "2026-03-31",
        },
        "regime": [{"risk_regime": "calm"}],
        "market_breadth": [{"k": 1}],
        "market_stress": [{"k": 1}],
        "fx_watchlist": [{"k": 1}],
        "macro_trends": [{"k": 1}],
        "top_movers": [{"symbol": "AAA", "why_summary": "Reason"}],
        "heavy": {
            "market_coverage": [{"k": 1}],
            "fx_coverage": [{"k": 1}],
            "fx_history_summary": [{"k": 1}],
            "macro_coverage": [{"k": 1}],
        },
    }


def test_build_context_fast_mode_avoids_heavy_sections(monkeypatch):
    calls = []

    def fake_run_context_job(include_heavy: bool):
        calls.append(include_heavy)
        return _base_payload()

    monkeypatch.setattr(context_builder, "run_context_job", fake_run_context_job)
    context_builder.clear_context_cache()
    result = context_builder.build_context(include_heavy=False, force_refresh=True)

    assert calls == [False]
    assert "TOP MOVERS + WHY" in result
    assert "MARKET COVERAGE" not in result


def test_build_context_handles_empty_payload(monkeypatch):
    monkeypatch.setattr(context_builder, "run_context_job", lambda include_heavy: {})
    context_builder.clear_context_cache()

    result = context_builder.build_context(include_heavy=True, force_refresh=True)

    assert "Regime data unavailable" in result
    assert "Top movers explainability unavailable" in result


def test_prompt_includes_top_movers_section(monkeypatch):
    monkeypatch.setattr(context_builder, "run_context_job", lambda include_heavy: _base_payload())
    context_builder.clear_context_cache()

    result = context_builder.build_context(include_heavy=False, force_refresh=True)

    assert "TOP MOVERS + WHY" in result
    assert "AAA" in result


def test_get_latest_dates_falls_back_on_failure(monkeypatch):
    def raise_failure(include_heavy: bool):
        raise RuntimeError("boom")

    monkeypatch.setattr(context_builder, "run_context_job", raise_failure)
    context_builder.clear_context_cache()

    latest = context_builder.get_latest_dates()

    assert latest == {
        "regime_as_of_date": "",
        "market_snapshot_date": "",
        "fx_rate_date": "",
        "movers_as_of_date": "",
    }
