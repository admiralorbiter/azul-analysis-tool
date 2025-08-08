import os
import sys
import json

# Ensure project root is on sys.path like other tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.app import create_test_app


def test_exhaustive_analysis_includes_insights(monkeypatch):
    app = create_test_app()
    client = app.test_client()

    # Monkeypatch database access to return a deterministic analysis row
    from api.routes import comprehensive_analysis as ca

    class DummyRow(dict):
        def __getattr__(self, item):
            return self[item]

    class DummyCursor:
        def __init__(self, rows):
            self._rows = rows
            self._idx = 0
        def fetchone(self):
            return self._rows[0] if self._rows else None
        def fetchall(self):
            return self._rows

    class DummyConn:
        def __init__(self, rows):
            self._rows = rows
        def execute(self, *_args, **_kwargs):
            return DummyCursor(self._rows)
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    def fake_get_connection():
        # Minimal single analysis row with JSON fields
        row = DummyRow({
            'id': 1,
            'game_phase': 'mid',
            'total_moves_analyzed': 10,
            'quality_distribution': json.dumps({'!': 3, '=': 7}),
            'average_quality_score': 72.5,
            'best_move_score': 88.0,
            'worst_move_score': 30.0,
            'engine_consensus': json.dumps({'alpha_beta': 0.7}),
            'disagreement_level': 0.2,
            'position_complexity': 0.6,
            'strategic_themes': json.dumps(["Factory control pressure", "Endgame setup"]),
            'tactical_opportunities': json.dumps(["Immediate block on blue", "Double-score setup"]),
            'analysis_time': 1.23,
            'created_at': '2025-01-01T00:00:00Z'
        })
        return DummyConn([row])

    monkeypatch.setattr(ca.db, 'get_position_id', lambda _fen: 42)
    monkeypatch.setattr(ca.db, 'get_connection', fake_get_connection)
    monkeypatch.setattr(ca.db, 'get_comprehensive_move_analyses', lambda _id: [])

    resp = client.get('/api/v1/exhaustive-analysis/some_fen_key')
    payload = None
    try:
        payload = resp.get_json()
    except Exception:
        payload = {'raw': resp.data.decode('utf-8', errors='ignore')}
    # Helpful debug on failure
    assert resp.status_code == 200, f"status={resp.status_code}, payload={payload}"
    assert payload.get('success') is True
    analysis = payload.get('analysis')
    assert isinstance(analysis, dict)
    assert 'strategic_themes' in analysis
    assert 'tactical_opportunities' in analysis
    assert analysis['strategic_themes'] == ["Factory control pressure", "Endgame setup"]
    assert analysis['tactical_opportunities'] == ["Immediate block on blue", "Double-score setup"]


