# Contextual Help MVP

Lightweight tooltips and a global Help toggle that work with the current `ui/` globals (no build changes).

## Goals
- Surface short, contextual hints where users need them
- Keep implementation simple and resilient to our globals
- Meet basic accessibility: keyboard focus, ESC to dismiss, ARIA roles

## Scope
- Global Help toggle button (bottom-right "?")
- Tooltips on hover/focus for elements with `data-help` or `data-help-key`
- One shared tooltip element positioned near the target
- MutationObserver to bind help for dynamically added DOM
- No walkthroughs, no code splitting

## Authoring model
- Prefer `data-help` for inline copy
- Use `data-help-key` to reference centralized strings in `window.HelpContent`
- Copy rules:
  - 10–120 chars
  - Action-first (e.g., "Run move quality analysis for the current board")
  - Avoid jargon

### Examples
- Navigation tab: `data-help="Switch between workspaces (Analysis, Research, Learning, Competitive)"`
- Analyze button: `data-help="Run move quality analysis for the current board"`
- Advanced toggles: `data-help="Show expert-only configuration options"`

## Engineering steps
1. Add files: `ui/styles/help.css`, `ui/utils/help.js`
2. Wire in `ui/index.html`: include CSS + JS and add a floating button `<button id="help-toggle" class="help-toggle">?</button>`
3. Accessibility: tooltip has `role="tooltip"`; targets get `tabindex` if missing and `aria-describedby`; ESC hides
4. Initial annotations: Navigation tabs, Move Quality Analyze button, Advanced Analysis toggles, Game Controls "Retry Analysis"

## Acceptance criteria
- Help toggle visible and works across pages
- Hover/focus shows tooltip with correct copy
- Keyboard accessible; ESC dismisses; ARIA set
- No layout shift; no console errors
- Minimal perf impact; no new deps

## Coverage (initial targets)
- Navigation: all top-level tabs, workspace label
- Game Controls: header, panel toolbar actions, panel headers
- Move Quality: analyze buttons, header “Move Quality Assessment”
- Pattern tools: Comprehensive, Scoring Optimization, Strategic Analysis headers

## Manual test checklist
- Toggle help on/off via the "?" button
- Hover/focus Navigation, Analyze button, Advanced toggles -> tooltip shows/hides
- Tab/Shift+Tab navigation works; ESC hides
- Tooltip positioning respects viewport and does not obscure key UI
- Mobile tap shows tooltip; tap elsewhere hides

## Robustness notes
- Works without a bundler; no dependency changes
- Resilient to dynamic DOM updates via MutationObserver
- Single shared tooltip to reduce DOM churn and memory
- Defensive event binding avoids double-binding on nodes
- Fails safe if `window.HelpContent` is absent; falls back to `data-help`

## Content centralization (optional)
Define in `ui/utils/help.js`:
```javascript
window.HelpContent = {
  'move-quality.analyze': 'Run move quality analysis for the current board',
  // ...
};
```
Use `data-help-key="move-quality.analyze"` on elements.

## Rollout
1. Land CSS/JS and wire in HTML (no annotations)
2. Annotate Navigation + Move Quality Analyze
3. Annotate Advanced Analysis controls
4. Announce in docs and changelog

## Future phases (out of scope)
- Walkthroughs
- Contextual, state-driven suggestions
- Searchable inline documentation
- Per-user help preferences/persistence

### Future extensions (design sketch)
- Interactive hotspots: subtle "i" badges next to complex controls, toggled by Help mode
- Per-tool inline mini-guides: small, dismissible cards with 2–3 bullets and a "Learn more" link
- Help search palette: Cmd/Ctrl+? opens searchable help mapped from `window.HelpContent`
- Analytics hooks: optional counters for which help items are viewed to guide content improvements
- Persistence: remember Help mode on/off in localStorage

Status: Ready to implement (no build changes required)
