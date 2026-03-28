import src.queries.top_movers as top_movers


def test_top_movers_query_returns_rows(monkeypatch):
    rows = [{"symbol": "AAA", "why_summary": "Reason"}]

    def fake_run_query(_query):
        return rows

    monkeypatch.setattr(top_movers, "run_query", fake_run_query)

    result = top_movers.load_top_movers_why(limit=5)

    assert result == rows


def test_top_movers_query_handles_missing_table(monkeypatch):
    def fake_run_query(_query):
        raise RuntimeError("table not found")

    monkeypatch.setattr(top_movers, "run_query", fake_run_query)

    result = top_movers.load_top_movers_why(limit=5)

    assert result == []
