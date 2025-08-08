/**
 * PatternInsights Component
 * 
 * Displays strategic themes and tactical opportunities for the current position
 * by querying the comprehensive analysis endpoint.
 * 
 * Props:
 * - fenString: FEN-like string identifying the current position
 */

const { useState, useEffect } = React;

const PatternInsights = ({ fenString }) => {
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [themes, setThemes] = useState([]);
    const [opportunities, setOpportunities] = useState([]);

    useEffect(() => {
        let cancelled = false;
        async function fetchInsights() {
            if (!fenString) {
                setThemes([]);
                setOpportunities([]);
                setError(null);
                setLoading(false);
                return;
            }
            setLoading(true);
            setError(null);
            try {
                const apiBase = window.API_CONSTANTS?.API_BASE || '/api/v1';
                const url = `${apiBase}/exhaustive-analysis/${encodeURIComponent(fenString)}`;
                const resp = await fetch(url);
                if (!resp.ok) {
                    // 404 or other errors mean insights not available for this position
                    throw new Error(`HTTP ${resp.status}`);
                }
                const data = await resp.json();
                const analysis = data?.analysis || {};
                const sThemes = Array.isArray(analysis.strategic_themes) ? analysis.strategic_themes : [];
                const tOpps = Array.isArray(analysis.tactical_opportunities) ? analysis.tactical_opportunities : [];
                if (!cancelled) {
                    setThemes(sThemes);
                    setOpportunities(tOpps);
                }
            } catch (e) {
                if (!cancelled) {
                    setThemes([]);
                    setOpportunities([]);
                    setError(e?.message || 'Failed to load insights');
                }
            } finally {
                if (!cancelled) setLoading(false);
            }
        }
        fetchInsights();
        return () => {
            cancelled = true;
        };
    }, [fenString]);

    // Hide the panel entirely if there is neither data nor loading/error and not expanded
    const hasData = (themes && themes.length > 0) || (opportunities && opportunities.length > 0);
    if (!fenString || (!hasData && !expanded && !loading && !error)) {
        return null;
    }

    return (
        <div className="pattern-insights" style={{ marginBottom: '12px' }}>
            <button
                onClick={() => setExpanded(!expanded)}
                style={{
                    width: '100%',
                    padding: '6px 8px',
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '11px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    color: '#495057',
                    fontWeight: 500
                }}
                data-help="Show strategic themes and tactical opportunities identified for this position"
            >
                <span>Pattern Insights</span>
                <span>{expanded ? '▼' : '▶'}</span>
            </button>

            {expanded && (
                <div style={{
                    marginTop: '8px',
                    padding: '10px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    fontSize: '11px',
                    lineHeight: 1.4,
                    color: '#495057'
                }}>
                    {loading && (
                        <div style={{ color: '#6c757d' }}>Loading insights…</div>
                    )}
                    {!loading && error && (
                        <div style={{ color: '#6c757d' }}>No insights available for this position.</div>
                    )}
                    {!loading && !error && !hasData && (
                        <div style={{ color: '#6c757d' }}>No insights available for this position.</div>
                    )}

                    {!loading && !error && hasData && (
                        <div style={{ display: 'grid', gap: '10px' }}>
                            {themes && themes.length > 0 && (
                                <div>
                                    <div style={{ fontWeight: 600, color: '#333', marginBottom: '6px' }}>Strategic Themes</div>
                                    <ul style={{ margin: 0, paddingLeft: '16px' }}>
                                        {themes.map((t, idx) => (
                                            <li key={idx} style={{ marginBottom: '4px' }}>{t}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            {opportunities && opportunities.length > 0 && (
                                <div>
                                    <div style={{ fontWeight: 600, color: '#333', marginBottom: '6px' }}>Tactical Opportunities</div>
                                    <ul style={{ margin: 0, paddingLeft: '16px' }}>
                                        {opportunities.map((o, idx) => (
                                            <li key={idx} style={{ marginBottom: '4px' }}>{o}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

// Export to window for global access
window.PatternInsights = PatternInsights;

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatternInsights;
}


