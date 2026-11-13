(function () {
  const TOKEN_KEY = "ga_stats_token";
  const meta = document.querySelector('meta[name="stats-api"]');
  const API = (meta && meta.getAttribute("content")) || "";
  const $ = (id) => document.getElementById(id);

  function token() { return localStorage.getItem(TOKEN_KEY) || ""; }
  function setToken(value) {
    if (value) localStorage.setItem(TOKEN_KEY, value);
    else localStorage.removeItem(TOKEN_KEY);
  }
  function headers() {
    return { Authorization: "Bearer " + token(), Accept: "application/json" };
  }

  function showGate(message) {
    $("gate").hidden = false;
    $("dash").hidden = true;
    if (message) $("gateError").textContent = message;
    else $("gateError").textContent = "";
    $("token").value = "";
    $("token").focus();
  }
  function showDash() {
    $("gate").hidden = true;
    $("dash").hidden = false;
  }

  function n(value) { return (value || 0).toLocaleString("en-US"); }
  function metric(label, bag, extra) {
    const total = bag && typeof bag === "object" ? bag.total : bag;
    const web = bag && bag.web;
    const android = bag && bag.android;
    const bits = [];
    if (typeof web === "number" || typeof android === "number") {
      bits.push("Web " + n(web || 0) + " · Android " + n(android || 0));
    }
    if (extra) bits.push(extra);
    return '<div class="card"><div class="k">' + label + '</div><div class="v">' + n(total) + '</div>' +
      (bits.length ? '<div class="s">' + bits.join(" · ") + "</div>" : "") + "</div>";
  }
  function period(title, p) {
    const feats = p.features || {};
    const featureRows = [
      ["chat", "Chat / AI Help"],
      ["case_check", "Case check"],
      ["motion_maker", "Motion maker"],
      ["funny_laws", "Funny laws"],
      ["find_legal_help", "Find legal help"],
      ["uploads", "Uploads"],
    ].map(([k, label]) => {
      const bag = feats[k] || { total: 0, web: 0, android: 0 };
      return "<li><span>" + label + "</span><b>" + n(bag.total) + "</b> <small>web " + n(bag.web) + " · Android " + n(bag.android) + "</small></li>";
    }).join("");
    return (
      '<section class="period"><h2>' + title + "</h2>" +
      '<div class="grid">' +
        metric("Opens", p.opens) +
        metric("Sessions", p.sessions) +
        metric("Unique devices", { total: p.unique_devices }) +
        metric("AI questions", p.ai_questions) +
        metric("First opens", p.first_opens) +
        metric("New installs", p.new_installs) +
      "</div>" +
      "<h3>Feature use</h3><ul class='features'>" + featureRows + "</ul></section>"
    );
  }
  function chart(daily) {
    const max = Math.max(1, ...daily.map((d) => d.opens || 0));
    const bars = daily.map((d) => {
      const h = Math.round(((d.opens || 0) / max) * 100);
      const label = d.day.slice(5);
      return '<div class="bar" title="' + d.day + ": " + (d.opens || 0) + " opens, " +
        (d.unique_devices || 0) + ' devices"><div class="col" style="height:' + h + '%"></div><span>' + label + "</span></div>";
    }).join("");
    return '<section class="period"><h2>Daily opens (last 30 days)</h2><div class="chart">' + bars + "</div></section>";
  }
  function stars(rating) {
    if (!rating) return "—";
    return "★".repeat(rating) + "☆".repeat(5 - rating) + " " + rating;
  }
  function feedback(fb) {
    const avg = fb.average_rating == null ? "No ratings yet" : fb.average_rating.toFixed(2) + " / 5";
    const cats = Object.entries(fb.category_labels || {}).map(([k, label]) => {
      return "<li><span>" + label + "</span><b>" + n((fb.by_category || {})[k] || 0) + "</b></li>";
    }).join("");
    const dist = [1, 2, 3, 4, 5].map((i) => {
      return "<li><span>" + i + " star</span><b>" + n((fb.ratings || {})[String(i)] || 0) + "</b></li>";
    }).join("");
    const comments = (fb.recent || []).map((row) => {
      const when = (row.created_at || "").replace("T", " ").slice(0, 16);
      const meta = [row.platform, row.app_version, row.screen, row.category_label || row.category].filter(Boolean).join(" · ");
      const email = row.contact_email ? '<div class="email">Reply: ' + escapeHtml(row.contact_email) + "</div>" : "";
      const body = row.comment ? "<p>" + escapeHtml(row.comment) + "</p>" : "<p class='muted'>No comment</p>";
      return '<article class="comment"><div class="when">' + escapeHtml(when) + " · " + stars(row.rating) +
        '</div><div class="meta">' + escapeHtml(meta) + "</div>" + body + email + "</article>";
    }).join("") || "<p class='muted'>No feedback yet.</p>";
    return (
      '<section class="period"><h2>App feedback</h2>' +
      '<div class="grid">' +
        '<div class="card"><div class="k">Average rating</div><div class="v">' + avg + "</div><div class='s'>" +
          n(fb.rating_count || 0) + " rated · " + n(fb.count || 0) + " submissions</div></div></div>" +
      "<div class='split'><div><h3>By category</h3><ul class='features'>" + cats +
      "</ul></div><div><h3>Star counts</h3><ul class='features'>" + dist + "</ul></div></div>" +
      "<h3>Recent comments</h3><div class='comments'>" + comments + "</div></section>"
    );
  }
  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  async function load() {
    $("status").textContent = "Loading…";
    const res = await fetch(API + "/stats/summary", { headers: headers() });
    if (res.status === 401 || res.status === 403) {
      setToken("");
      showGate("That token was not accepted. Try again.");
      return;
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || "Could not load stats");
    }
    const data = await res.json();
    showDash();
    $("stamp").textContent = "As of " + (data.generated_at || "") + " (" + (data.timezone || "America/New_York") + ")";
    $("content").innerHTML = period("Today", data.today) + period("Last 7 days", data.last_7_days) +
      period("Last 30 days", data.last_30_days) + chart(data.daily || []) + feedback(data.feedback || {});
    $("status").textContent = "";
  }

  async function unlock(event) {
    event.preventDefault();
    const value = $("token").value.trim();
    if (!value) return;
    setToken(value);
    $("gateError").textContent = "";
    const res = await fetch(API + "/stats/session", { method: "POST", headers: headers() });
    if (!res.ok) {
      setToken("");
      $("gateError").textContent = "That token was not accepted.";
      return;
    }
    try { await load(); } catch (err) { showGate(err.message); }
  }

  function logout() { setToken(""); showGate(""); }

  window.addEventListener("DOMContentLoaded", function () {
    $("gateForm").addEventListener("submit", unlock);
    $("logout").addEventListener("click", logout);
    if (token()) load().catch((err) => showGate(err.message));
    else showGate("");
  });
})();
