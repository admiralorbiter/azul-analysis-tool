# API Reference Index

Quick links to category pages for the REST API.

- Core
  - Health: `GET /api/v1/health`
  - Stats: `GET /api/v1/stats`
- Positions: CRUD, stats, search, bulk import/export
- Analyses: `POST /api/v1/analyze`, `POST /api/v1/hint`, stats/search
- Move Quality: see `move-quality-endpoints.md`
- Pattern Detection: see `pattern-detection-endpoints.md`
- Neural: see `neural-endpoints.md`
- Comprehensive Analysis (exhaustive): see `exhaustive-analysis-endpoints.md`

## Category Pages
- [Pattern Detection](pattern-detection-endpoints.md)
- [Move Quality](move-quality-endpoints.md)
- [Neural](neural-endpoints.md)
- [Exhaustive Analysis](exhaustive-analysis-endpoints.md)

Notes
- Use `X-Session-ID` where required by endpoint; some read-only endpoints are public.
- For a complete list of registered endpoints, see the code under `api/routes/` and the API info at `GET /api` when the server is running.
 
—
Last Reviewed: 2025-08-08
