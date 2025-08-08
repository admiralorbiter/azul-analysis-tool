(function () {
  const state = { enabled: false, tooltip: null, current: null };

  function ensureTooltip() {
    if (state.tooltip) return state.tooltip;
    const el = document.createElement('div');
    el.className = 'help-tooltip';
    el.setAttribute('role', 'tooltip');
    el.id = 'contextual-help';
    el.style.display = 'none';
    document.body.appendChild(el);
    state.tooltip = el;
    return el;
  }

  function getHelpText(target) {
    const key = target.getAttribute('data-help-key');
    if (key && window.HelpContent && window.HelpContent[key]) return window.HelpContent[key];
    return target.getAttribute('data-help');
  }

  function positionTooltip(tt, rect) {
    const offset = 8;
    const top = Math.max(8, rect.bottom + offset + window.scrollY);
    const left = Math.max(8, rect.left + window.scrollX);
    tt.style.top = top + 'px';
    tt.style.left = left + 'px';
  }

  function showTooltip(target) {
    const text = getHelpText(target);
    if (!text) return;
    const tt = ensureTooltip();
    tt.textContent = text;
    tt.style.display = 'block';
    positionTooltip(tt, target.getBoundingClientRect());
    target.classList.add('help-highlight');
    state.current = target;
  }

  function hideTooltip() {
    const tt = ensureTooltip();
    tt.style.display = 'none';
    if (state.current) state.current.classList.remove('help-highlight');
    state.current = null;
  }

  function attach(el) {
    if (el.__helpBound) return;
    el.__helpBound = true;
    el.addEventListener('mouseenter', () => state.enabled && showTooltip(el));
    el.addEventListener('mouseleave', hideTooltip);
    el.addEventListener('focus', () => state.enabled && showTooltip(el));
    el.addEventListener('blur', hideTooltip);
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
    el.setAttribute('aria-describedby', 'contextual-help');
  }

  function scan(root = document) {
    root.querySelectorAll('[data-help], [data-help-key]').forEach(attach);
  }

  function toggleHelp(on) {
    state.enabled = typeof on === 'boolean' ? on : !state.enabled;
    const btn = document.getElementById('help-toggle');
    if (btn) btn.setAttribute('aria-pressed', String(state.enabled));
    if (!state.enabled) hideTooltip();
  }

  // Global controls
  window.Help = {
    toggle: toggleHelp,
    rescan: scan
  };

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') hideTooltip();
  });

  // Attach toggle button listener when available
  window.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('help-toggle');
    if (btn) btn.addEventListener('click', () => toggleHelp());
    scan();
  });

  // Observe dynamic UI
  const mo = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const n of m.addedNodes) {
        if (n.nodeType === 1) scan(n);
      }
    }
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();


