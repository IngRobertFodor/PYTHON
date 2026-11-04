/**
 * ai_agent.js — AI Asistent chat panel
 * =====================================
 * Floating resizable chat panel pre Land Research Invest.
 * Komunikuje s /api/agent/* endpointmi. Vanilla JS.
 */
const AIAgent = (() => {
  const MAX_CHARS   = 500;
  const LS_HISTORY  = "ai_agent_history_v1";
  const LS_MODEL    = "ai_agent_model_v1";
  const LS_WARN_DIS = "ai_agent_warn_dismiss_v1";
  const CHIPS = [
    { icon: "📊", text: "Súhrn posledného behu" },
    { icon: "🔥", text: "Dražby pod znaleckou cenou" },
    { icon: "📉", text: "Obce s poklesom cien" },
    { icon: "💎", text: "Pozemky do 25 km s indexom nad 70" },
    { icon: "🏘️", text: "Peer analýza — zadaj obec" },
  ];

  let _available = false, _currentModel = null, _panelOpen = false, _loading = false;
  let _history = [], _warnDismissTs = 0;
  let _resizing = false, _rsx, _rsy, _rsw, _rsh;
  let $toggle, $panel, $warnBanner, $warnText, $warnAction, $warnDismiss,
      $messages, $chips, $input, $sendBtn, $charCount, $modelLabel,
      $resizeHandle, $modelModal;

  function init() { _buildDOM(); _bindEvents(); _loadHistory(); _checkStatus(); }

  function _buildDOM() {
    const root = document.getElementById("ai-agent-root");
    if (!root) return;
    root.innerHTML = [
      '<button id="ai-toggle-btn" title="AI asistent">',
        '<span class="ai-toggle-icon">💬</span>',
        '<span>AI asistent</span>',
        '<span class="ai-notify-dot"></span>',
      '</button>',
      '<div id="ai-panel" class="ai-hidden">',
        '<div id="ai-resize-handle"></div>',
        '<div id="ai-panel-header">',
          '<span class="ai-header-title">💬 AI asistent</span>',
          '<span class="ai-header-model" id="ai-model-label"></span>',
          '<button class="ai-btn-icon" id="ai-settings-btn" title="Model">⚙️</button>',
          '<button class="ai-btn-icon" id="ai-clear-btn" title="Vymazať">🗑</button>',
          '<button class="ai-btn-icon" id="ai-close-btn" title="Zatvoriť">✕</button>',
        '</div>',
        '<div id="ai-warn-banner" class="ai-hidden">',
          '<span>⚠️</span>',
          '<span class="ai-warn-text" id="ai-warn-text"></span>',
          '<button class="ai-warn-action" id="ai-warn-action">Vybrať model</button>',
          '<button class="ai-warn-dismiss" id="ai-warn-dismiss">×</button>',
        '</div>',
        '<div id="ai-messages"></div>',
        '<div id="ai-chips"></div>',
        '<div id="ai-input-area">',
          '<textarea id="ai-input" placeholder="Napíš otázku..." rows="1"></textarea>',
          '<span id="ai-char-count">0</span>',
          '<button id="ai-send-btn" title="Odoslať (Enter)">▶</button>',
        '</div>',
      '</div>',
      '<div id="ai-model-modal" class="ai-hidden">',
        '<div id="ai-model-modal-box">',
          '<h3>🧠 Výber AI modelu',
            '<button class="ai-btn-icon" id="ai-modal-close-btn" style="color:#fff">✕</button>',
          '</h3>',
          '<div class="ai-model-modal-body" id="ai-model-list"><p style="color:#aaa;font-size:.8rem">Načítavam...</p></div>',
          '<div id="ai-model-status"></div>',
          '<div class="ai-model-modal-footer">',
            '<button class="ai-btn-secondary" id="ai-modal-cancel-btn">Zrušiť</button>',
            '<button class="ai-btn-primary" id="ai-modal-apply-btn" disabled>Použiť</button>',
          '</div>',
        '</div>',
      '</div>',
    ].join("");

    $toggle       = document.getElementById("ai-toggle-btn");
    $panel        = document.getElementById("ai-panel");
    $warnBanner   = document.getElementById("ai-warn-banner");
    $warnText     = document.getElementById("ai-warn-text");
    $warnAction   = document.getElementById("ai-warn-action");
    $warnDismiss  = document.getElementById("ai-warn-dismiss");
    $messages     = document.getElementById("ai-messages");
    $chips        = document.getElementById("ai-chips");
    $input        = document.getElementById("ai-input");
    $sendBtn      = document.getElementById("ai-send-btn");
    $charCount    = document.getElementById("ai-char-count");
    $modelLabel   = document.getElementById("ai-model-label");
    $resizeHandle = document.getElementById("ai-resize-handle");
    $modelModal   = document.getElementById("ai-model-modal");
  }

  function _bindEvents() {
    if (!$toggle) return;
    $toggle.addEventListener("click", () => { if (_available) _panelOpen ? _closePanel() : _openPanel(); });
    const _g = id => document.getElementById(id);
    _g("ai-close-btn").addEventListener("click", _closePanel);
    _g("ai-clear-btn").addEventListener("click", _clearHistory);
    _g("ai-settings-btn").addEventListener("click", _openModelModal);
    $warnAction.addEventListener("click", _openModelModal);
    $warnDismiss.addEventListener("click", () => {
      _warnDismissTs = Date.now();
      localStorage.setItem(LS_WARN_DIS, String(_warnDismissTs));
      $warnBanner.classList.add("ai-hidden");
    });
    $input.addEventListener("input", _onInputChange);
    $input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); _send(); } });
    $sendBtn.addEventListener("click", _send);
    $resizeHandle.addEventListener("mousedown", _onResizeStart);
    document.addEventListener("mousemove", _onResizeMove);
    document.addEventListener("mouseup", _onResizeEnd);
    _g("ai-modal-cancel-btn").addEventListener("click", _closeModelModal);
    _g("ai-modal-close-btn").addEventListener("click", _closeModelModal);
    _g("ai-modal-apply-btn").addEventListener("click", _applyModel);
    $modelModal.addEventListener("click", e => { if (e.target === $modelModal) _closeModelModal(); });
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") {
        if (!$modelModal.classList.contains("ai-hidden")) { _closeModelModal(); return; }
        if (_panelOpen) _closePanel();
      }
    });
  }

  // ---------------------------------------------------------------
  // Status / health
  // ---------------------------------------------------------------
  function _checkStatus() {
    fetch("/api/agent/status")
      .then(r => r.json())
      .then(d => {
        _available = d.available; _currentModel = d.model || d.default_model || null;
        _updateToggle();
        if (_available) {
          _updateModelLabel(_currentModel);
          const saved = localStorage.getItem(LS_MODEL);
          if (saved && saved !== _currentModel) _selectModel(saved, false);
          _checkHealth();
        }
      })
      .catch(() => { _available = false; _updateToggle(); });
  }

  function _checkHealth() {
    fetch("/api/agent/health")
      .then(r => r.json())
      .then(d => {
        const p = d.primary || {};
        if (p.status && p.status !== "ok" && p.status !== "unknown") {
          const dis = parseInt(localStorage.getItem(LS_WARN_DIS) || "0");
          if (Date.now() - dis > 7 * 86400000) {
            $warnText.textContent = p.message_sk || "Primárny AI model vyžaduje aktualizáciu.";
            $warnBanner.classList.remove("ai-hidden");
            $toggle.classList.add("ai-has-warning");
          }
        }
      })
      .catch(() => {});
  }

  function _updateToggle() {
    if (!$toggle) return;
    $toggle.classList.toggle("ai-unavailable", !_available);
    $toggle.title = _available ? "AI asistent" : "AI asistent — nastav GOOGLE_API_KEY v .env";
  }

  function _updateModelLabel(m) {
    if ($modelLabel && m) $modelLabel.textContent = m.replace("models/", "");
  }

  // ---------------------------------------------------------------
  // Panel / chips
  // ---------------------------------------------------------------
  function _openPanel() {
    _panelOpen = true; $panel.classList.remove("ai-hidden");
    _renderChips(); _scrollToBottom();
    setTimeout(() => $input && $input.focus(), 50);
  }

  function _closePanel() { _panelOpen = false; $panel.classList.add("ai-hidden"); }

  function _renderChips() {
    if (_history.length > 0) { $chips.classList.add("ai-hidden"); return; }
    $chips.classList.remove("ai-hidden");
    $chips.innerHTML = CHIPS.map(c =>
      `<button class="ai-chip" data-text="${_esc(c.text)}">${c.icon} ${_esc(c.text)}</button>`
    ).join("");
    $chips.querySelectorAll(".ai-chip").forEach(btn => {
      btn.addEventListener("click", () => { $input.value = btn.dataset.text; _onInputChange(); _send(); });
    });
  }

  // ---------------------------------------------------------------
  // Input
  // ---------------------------------------------------------------
  function _onInputChange() {
    const len = $input.value.length;
    $charCount.textContent = len;
    $charCount.classList.toggle("ai-warn", len > MAX_CHARS * 0.9);
    $input.style.height = "auto";
    $input.style.height = Math.min($input.scrollHeight, 100) + "px";
  }

  // ---------------------------------------------------------------
  // Send
  // ---------------------------------------------------------------
  function _send() {
    const q = $input.value.trim();
    if (!q || _loading) return;
    if (q.length > MAX_CHARS) { _showError(`Otázka príliš dlhá (max ${MAX_CHARS} znakov).`); return; }
    if (!_available) { _showError("AI nie je k dispozícii."); return; }

    _addBubble("user", q); $input.value = ""; _onInputChange();
    $chips.classList.add("ai-hidden"); _saveHistory();
    _loading = true; $sendBtn.disabled = true;
    const loadId = _addLoading();

    // #5: 60s timeout — ak Gemini neodpovie, zobraz SK chybu
    const controller = new AbortController();
    const timeoutId  = setTimeout(() => controller.abort(), 60000);

    fetch("/api/agent/ask", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
      signal: controller.signal,
    })
      .then(r => r.json())
      .then(data => {
        clearTimeout(timeoutId);
        _removeLoading(loadId); _loading = false; $sendBtn.disabled = false;
        if (data.ok) {
          _addBubble("ai", data.answer, data.tool_calls || []);
          if (data.model_used) { _currentModel = data.model_used; _updateModelLabel(data.model_used); }
        } else {
          _addBubble("error", data.answer || data.error || "Neznáma chyba.");
        }
        _saveHistory(); _scrollToBottom();
      })
      .catch(err => {
        clearTimeout(timeoutId);
        _removeLoading(loadId); _loading = false; $sendBtn.disabled = false;
        const msg = err.name === "AbortError"
          ? "AI neodpovedá (timeout 60s). Skús neskôr."
          : "Nedá sa pripojiť na server.";
        _addBubble("error", msg); _scrollToBottom();
      });
  }


  // ---------------------------------------------------------------
  // Message rendering
  // ---------------------------------------------------------------
  function _addBubble(role, text, toolCalls) {
    _history.push({ role, text, toolCalls: toolCalls || [] });
    _renderLastBubble();
  }

  function _renderLastBubble() {
    const item = _history[_history.length - 1]; if (!item) return;
    const cls = item.role === "user" ? "ai-bubble-user"
              : item.role === "error" ? "ai-bubble-error" : "ai-bubble-ai";
    const div = document.createElement("div");
    div.className = `ai-bubble ${cls}`;
    div.innerHTML = _renderText(item.text, item.role === "ai");
    $messages.appendChild(div);
    if (item.role === "ai" && item.toolCalls && item.toolCalls.length) {
      const chips = document.createElement("div");
      chips.className = "ai-tool-chips";
      chips.innerHTML = item.toolCalls.map(tc => {
        // #6: čitateľný tooltip miesto JSON (napr. "obec=Senec, limit=10")
        const argsText = Object.entries(tc.args || {})
          .map(([k, v]) => `${k}=${v}`)
          .join(", ");
        const tooltip = argsText || "bez argumentov";
        return `<span class="ai-tool-chip" title="${_esc(tooltip)}">🔧 ${_esc(tc.name)}</span>`;
      }).join("");
      $messages.appendChild(chips);
    }
  }

  function _renderText(text, md) {
    let s = _esc(text || "");
    if (md) {
      s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
           .replace(/`([^`]+)`/g, "<code>$1</code>")
           .replace(/\n/g, "<br>")
           .replace(/^\s*[-•]\s(.+)$/gm, "<li>$1</li>")
           .replace(/((<li>.*<\/li>)+)/g, "<ul>$1</ul>");
    } else {
      s = s.replace(/\n/g, "<br>");
    }
    return s;
  }

  function _addLoading() {
    const id = "ai-load-" + Date.now();
    const div = document.createElement("div");
    div.className = "ai-bubble-loading"; div.id = id;
    div.innerHTML = '<div class="ai-dot"></div><div class="ai-dot"></div><div class="ai-dot"></div>';
    $messages.appendChild(div); _scrollToBottom(); return id;
  }

  function _removeLoading(id) { const el = document.getElementById(id); if (el) el.remove(); }

  function _showError(msg) {
    const div = document.createElement("div");
    div.className = "ai-bubble ai-bubble-error"; div.textContent = msg;
    $messages.appendChild(div); _scrollToBottom();
  }

  function _scrollToBottom() { if ($messages) $messages.scrollTop = $messages.scrollHeight; }

  function _esc(s) {
    return String(s || "")
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  }

  // ---------------------------------------------------------------
  // History (localStorage)
  // ---------------------------------------------------------------
  function _loadHistory() {
    try {
      const raw = localStorage.getItem(LS_HISTORY);
      _history = raw ? JSON.parse(raw) : [];
      if ($messages && _history.length) {
        $messages.innerHTML = "";
        const saved = _history.slice();
        _history = [];
        saved.forEach(item => { _history.push(item); _renderLastBubble(); });
      }
    } catch (e) { _history = []; }
  }

  function _saveHistory() {
    try { localStorage.setItem(LS_HISTORY, JSON.stringify(_history.slice(-30))); }
    catch (e) {}
  }

  function _clearHistory() {
    _history = []; $messages.innerHTML = ""; _saveHistory(); _renderChips();
  }


  // ---------------------------------------------------------------
  // Resize (drag ľavý-horný roh panelu)
  // ---------------------------------------------------------------
  function _onResizeStart(e) {
    _resizing = true; e.preventDefault();
    _rsx = e.clientX; _rsy = e.clientY;
    const rect = $panel.getBoundingClientRect();
    _rsw = rect.width; _rsh = rect.height;
  }

  function _onResizeMove(e) {
    if (!_resizing) return;
    const dw = e.clientX - _rsx;
    const dh = e.clientY - _rsy;
    const newW = Math.max(300, Math.min(800, _rsw + dw));
    const newH = Math.max(400, Math.min(window.innerHeight * 0.9, _rsh + dh));
    $panel.style.width  = newW + "px";
    $panel.style.height = newH + "px";
  }

  function _onResizeEnd() { _resizing = false; }

  // ---------------------------------------------------------------
  // Model picker modal
  // ---------------------------------------------------------------
  function _openModelModal() {
    $modelModal.classList.remove("ai-hidden");
    const listEl = document.getElementById("ai-model-list");
    const statusEl = document.getElementById("ai-model-status");
    const applyBtn = document.getElementById("ai-modal-apply-btn");
    listEl.innerHTML = '<p style="color:#aaa;font-size:.8rem">Načítavam modely...</p>';
    statusEl.textContent = "";
    applyBtn.disabled = true;

    fetch("/api/agent/available-models")
      .then(r => r.json())
      .then(data => {
        const models = data.models || [];
        const src = data.source === "google-api" ? "✅ Aktuálny zoznam z Google API"
                  : "⚠️ " + (data.warning || "Lokálny zoznam");
        listEl.innerHTML = `<p class="ai-model-source">${_esc(src)}</p>` +
          models.map(m => `
            <label class="ai-model-option">
              <input type="radio" name="ai-model-radio" value="${_esc(m.id)}"
                     ${m.id === _currentModel ? "checked" : ""}>
              <span class="ai-model-option-label">
                <span class="ai-model-option-id">${_esc(m.id)}</span>
                ${m.recommended ? '<span class="ai-model-option-badge">odporúčaný</span>' : ""}
              </span>
            </label>`).join("");

        listEl.querySelectorAll("input[type=radio]").forEach(r => {
          r.addEventListener("change", () => {
            applyBtn.disabled = false;
            statusEl.textContent = "";
          });
        });
        if (models.length > 0) applyBtn.disabled = false;
      })
      .catch(() => { listEl.innerHTML = '<p style="color:#a02020">Chyba načítania modelov.</p>'; });
  }

  function _closeModelModal() {
    $modelModal.classList.add("ai-hidden");
  }

  function _applyModel() {
    const checked = document.querySelector('input[name="ai-model-radio"]:checked');
    if (!checked) return;
    const model  = checked.value;
    const statusEl = document.getElementById("ai-model-status");
    const applyBtn = document.getElementById("ai-modal-apply-btn");
    statusEl.textContent = "Testujem model...";
    applyBtn.disabled = true;
    _selectModel(model, true, statusEl, applyBtn);
  }

  function _selectModel(model, notify, statusEl, applyBtn) {
    fetch("/api/agent/select-model", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          _currentModel = model; _updateModelLabel(model);
          localStorage.setItem(LS_MODEL, model);
          $warnBanner.classList.add("ai-hidden");
          $toggle.classList.remove("ai-has-warning");
          if (notify) _closeModelModal();
        } else {
          if (statusEl) statusEl.textContent = data.error || "Model nie je dostupný.";
          if (applyBtn) applyBtn.disabled = false;
        }
      })
      .catch(() => {
        if (statusEl) statusEl.textContent = "Chyba spojenia.";
        if (applyBtn) applyBtn.disabled = false;
      });
  }

  // ---------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------
  return { init };

})();

// Autostart po načítaní DOM
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", AIAgent.init);
} else {
  AIAgent.init();
}

