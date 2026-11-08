/*
 * Dailies runtime: a deterministic timeline for HTML compositions.
 *
 * A composition is a pure function of time: render(t) must put the page into
 * the exact state for second t, no matter what was rendered before. That is
 * what lets scripts/render.mjs capture any frame in any order, and what makes a
 * styleframe identical to the same moment in the final video.
 *
 * Modes (URL query):
 *   (none)        live preview with play/pause, scrubber and keyboard stepping
 *   ?render=1     headless capture: no UI, exact pixel size, driven by render.mjs
 *   ?t=4.2        open the preview at a time
 *   ?guides=1     draw title-safe / platform safe-area guides
 *   ?bg=<url>     show an image under the stage (overlay mockups on real frames)
 *   ?alpha=1      transparent stage background (overlays rendered with alpha)
 *   ?tokens=<url> load a different tokens.json (design variants)
 *   ?w=&h=        override the composition size (multi-format export)
 */
(function () {
  "use strict";

  const params = new URLSearchParams(location.search);
  const RENDER = params.has("render");

  // ---------------------------------------------------------------- easing
  const ease = {
    linear: (p) => p,
    inQuad: (p) => p * p,
    outQuad: (p) => 1 - (1 - p) * (1 - p),
    inOutQuad: (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2),
    inCubic: (p) => p * p * p,
    outCubic: (p) => 1 - Math.pow(1 - p, 3),
    inOutCubic: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    inQuart: (p) => p * p * p * p,
    outQuart: (p) => 1 - Math.pow(1 - p, 4),
    inOutQuart: (p) => (p < 0.5 ? 8 * p ** 4 : 1 - Math.pow(-2 * p + 2, 4) / 2),
    inExpo: (p) => (p === 0 ? 0 : Math.pow(2, 10 * p - 10)),
    outExpo: (p) => (p === 1 ? 1 : 1 - Math.pow(2, -10 * p)),
    inOutExpo: (p) =>
      p === 0 ? 0 : p === 1 ? 1 : p < 0.5 ? Math.pow(2, 20 * p - 10) / 2 : (2 - Math.pow(2, -20 * p + 10)) / 2,
    outBack: (p) => {
      const c1 = 1.70158, c3 = c1 + 1;
      return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
    },
    inOutSine: (p) => -(Math.cos(Math.PI * p) - 1) / 2,
  };

  // Damped spring step response. Unlike the curves above it runs in seconds,
  // so a spring keeps its physical feel regardless of the tween's length.
  function spring(stiffness = 170, damping = 18, mass = 1) {
    const w0 = Math.sqrt(stiffness / mass);
    const zeta = damping / (2 * Math.sqrt(stiffness * mass));
    const fn = (p, durSeconds = 1) => {
      const t = p * durSeconds;
      if (zeta < 1) {
        const wd = w0 * Math.sqrt(1 - zeta * zeta);
        return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + ((zeta * w0) / wd) * Math.sin(wd * t));
      }
      return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
    };
    fn.physical = true;
    return fn;
  }

  function resolveEase(e) {
    if (!e) return ease.linear;
    if (typeof e === "function") return e;
    const m = /^spring\(([\d.]+)\s*,\s*([\d.]+)\)$/.exec(e);
    if (m) return spring(+m[1], +m[2]);
    return ease[e] || ease.linear;
  }

  // ---------------------------------------------------------------- math
  const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  // 0..1 progress of t through [start, start+dur]
  const range = (t, start, dur) => (dur <= 0 ? (t >= start ? 1 : 0) : clamp((t - start) / dur));
  // Quantize time for a stop-motion feel ("on twos" at 30 fps -> stepped(t, 15))
  const stepped = (t, rate) => Math.floor(t * rate) / rate;

  // Deterministic value noise in [-1, 1]; same inputs always give same output.
  function hash(n) {
    const s = Math.sin(n * 127.1 + 311.7) * 43758.5453123;
    return s - Math.floor(s);
  }
  function noise1(x, seed = 0) {
    const i = Math.floor(x), f = x - i;
    const u = f * f * (3 - 2 * f);
    return lerp(hash(i + seed * 101.3), hash(i + 1 + seed * 101.3), u) * 2 - 1;
  }
  const wiggle = (t, freq = 2, amp = 1, seed = 0) => noise1(t * freq, seed) * amp;

  // ---------------------------------------------------------------- keyframes
  /*
   * kf(t, [[0.2, {opacity: 0, y: 40}], [0.8, {opacity: 1, y: 0}, "outExpo"]])
   * Each keyframe is [time, values, easeIntoThisKeyframe]. Before the first
   * keyframe the first values hold; after the last, the last values hold.
   */
  function kf(t, frames) {
    if (!frames.length) return {};
    if (t <= frames[0][0]) return { ...frames[0][1] };
    for (let i = 1; i < frames.length; i++) {
      const [t1, v1, e] = frames[i];
      const [t0, v0] = frames[i - 1];
      if (t <= t1) {
        const fn = resolveEase(e);
        const dur = t1 - t0;
        const p = fn(range(t, t0, dur), dur);
        const out = { ...v0 };
        for (const k of Object.keys(v1)) {
          const a = v0[k] ?? v1[k], b = v1[k];
          out[k] = typeof a === "number" && typeof b === "number" ? lerp(a, b, p) : p < 1 ? a : b;
        }
        return out;
      }
    }
    return { ...frames[frames.length - 1][1] };
  }

  const TRANSFORM_KEYS = ["x", "y", "scale", "scaleX", "scaleY", "rotate", "skewX"];
  // Apply a value object to an element. Known keys map to transform/filter;
  // anything else is set as a style property (use CSS names, e.g. "letterSpacing").
  function apply(el, v) {
    if (typeof el === "string") el = document.querySelectorAll(el);
    if (el instanceof NodeList || Array.isArray(el)) return el.forEach((e) => apply(e, v));
    if (!el) return;
    const tf = [];
    if (v.x != null || v.y != null) tf.push(`translate(${v.x || 0}px, ${v.y || 0}px)`);
    if (v.scale != null) tf.push(`scale(${v.scale})`);
    if (v.scaleX != null) tf.push(`scaleX(${v.scaleX})`);
    if (v.scaleY != null) tf.push(`scaleY(${v.scaleY})`);
    if (v.rotate != null) tf.push(`rotate(${v.rotate}deg)`);
    if (v.skewX != null) tf.push(`skewX(${v.skewX}deg)`);
    if (tf.length) el.style.transform = tf.join(" ");
    if (v.opacity != null) el.style.opacity = v.opacity;
    if (v.blur != null) el.style.filter = v.blur > 0.01 ? `blur(${v.blur}px)` : "none";
    // clip: 0 = hidden, 1 = fully revealed (wipe from the left)
    if (v.clip != null) el.style.clipPath = `inset(0 ${(1 - v.clip) * 100}% 0 0)`;
    for (const [k, val] of Object.entries(v)) {
      if (TRANSFORM_KEYS.includes(k) || ["opacity", "blur", "clip"].includes(k)) continue;
      el.style[k] = typeof val === "number" && !/opacity|zIndex|fontWeight/.test(k) ? `${val}px` : val;
    }
  }

  const animate = (el, t, frames) => apply(el, kf(t, frames));

  // Stroke draw-on for SVG paths/lines/polylines. p: 0..1
  function draw(el, p) {
    if (typeof el === "string") el = document.querySelectorAll(el);
    if (el instanceof NodeList) return el.forEach((e) => draw(e, p));
    const len = el.__len || (el.__len = el.getTotalLength ? el.getTotalLength() : 1000);
    el.style.strokeDasharray = `${len}`;
    el.style.strokeDashoffset = `${len * (1 - clamp(p))}`;
  }

  // Reveal characters of text. p: 0..1
  function typewriter(el, text, p) {
    if (typeof el === "string") el = document.querySelector(el);
    el.textContent = text.slice(0, Math.round(text.length * clamp(p)));
  }

  function countUp(el, from, to, p, fmt = (n) => Math.round(n).toLocaleString()) {
    if (typeof el === "string") el = document.querySelector(el);
    el.textContent = fmt(lerp(from, to, clamp(p)));
  }

  // Split an element's text into spans (once) for per-word / per-letter animation.
  // Nested markup (e.g. <span class="accent">) is kept; its words are split inside it.
  function split(el, by = "word") {
    if (typeof el === "string") el = document.querySelector(el);
    if (el.__parts) return el.__parts;
    const parts = [];
    const walk = (node) => {
      for (const child of [...node.childNodes]) {
        if (child.nodeType === Node.ELEMENT_NODE) { walk(child); continue; }
        if (child.nodeType !== Node.TEXT_NODE) continue;
        const frag = document.createDocumentFragment();
        const pieces = by === "char" ? [...child.textContent] : child.textContent.split(/(\s+)/);
        for (const piece of pieces) {
          if (!piece) continue;
          if (/^\s+$/.test(piece)) { frag.appendChild(document.createTextNode(piece)); continue; }
          const s = document.createElement("span");
          s.textContent = piece;
          s.style.display = "inline-block";
          frag.appendChild(s);
          parts.push(s);
        }
        child.replaceWith(frag);
      }
    };
    walk(el);
    el.__parts = parts;
    return parts;
  }

  // Show a scene element only inside [start, end); returns local time or null.
  function scene(el, t, start, end) {
    if (typeof el === "string") el = document.querySelector(el);
    const on = t >= start && t < end;
    el.style.visibility = on ? "visible" : "hidden";
    return on ? t - start : null;
  }

  // ---------------------------------------------------------------- tokens
  async function loadTokens() {
    const url = params.get("tokens") || "../tokens.json";
    let tokens;
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) return null;
      tokens = await res.json();
    } catch {
      return null; // file:// preview or no tokens file: CSS defaults stay
    }
    const root = document.documentElement.style;
    for (const [k, v] of Object.entries(tokens.color || {})) root.setProperty(`--color-${k}`, v);
    const faces = [];
    for (const [role, f] of Object.entries(tokens.font || {})) {
      if (!f) continue;
      root.setProperty(`--font-${role}`, `"${f.family}", system-ui, sans-serif`);
      if (f.weight) root.setProperty(`--font-${role}-weight`, f.weight);
      if (f.file) {
        const src = new URL(f.file, new URL(url, location.href)).href;
        faces.push(new FontFace(f.family, `url("${src}")`, { weight: "100 900" }).load().then((ff) => document.fonts.add(ff)).catch(() => console.warn("font failed", src)));
      }
    }
    if (tokens.radius != null) root.setProperty("--radius", `${tokens.radius}px`);
    for (const [k, v] of Object.entries(tokens.motion || {})) if (typeof v === "number") root.setProperty(`--dur-${k}`, `${v}s`);
    if (tokens.texture?.grain != null) root.setProperty("--grain", tokens.texture.grain);
    await Promise.all(faces);
    return tokens;
  }

  // ---------------------------------------------------------------- media
  // <video data-start="2" data-in="10.5" muted> plays source time 10.5 at composition time 2.
  function syncVideos(t, exact) {
    const waits = [];
    document.querySelectorAll("video[data-start]").forEach((v) => {
      const start = parseFloat(v.dataset.start || "0");
      const inPt = parseFloat(v.dataset.in || "0");
      const rate = parseFloat(v.dataset.rate || "1");
      const target = Math.max(0, inPt + (t - start) * rate);
      if (exact) {
        v.pause();
        if (Math.abs(v.currentTime - target) > 0.001) {
          waits.push(new Promise((res) => { v.addEventListener("seeked", res, { once: true }); setTimeout(res, 5000); }));
          v.currentTime = target;
        }
      } else if (Math.abs(v.currentTime - target) > 0.25) {
        v.currentTime = target;
      }
    });
    return Promise.all(waits);
  }

  function mediaReady() {
    const imgs = [...document.images].map((i) => (i.complete ? i.decode().catch(() => {}) : new Promise((r) => { i.onload = i.onerror = r; })));
    const vids = [...document.querySelectorAll("video")].map((v) =>
      v.readyState >= 2 ? null : new Promise((r) => { v.addEventListener("loadeddata", r, { once: true }); v.addEventListener("error", r, { once: true }); }));
    return Promise.all([...imgs, ...vids]);
  }

  // ---------------------------------------------------------------- composition
  function composition(cfg) {
    // ?w=&h= render the same composition at another size (multi-format export)
    const width = +params.get("w") || cfg.width || 1920;
    const height = +params.get("h") || cfg.height || 1080;
    const { fps = 30, duration = 10 } = cfg;
    const stage = document.getElementById("stage");
    stage.style.width = `${width}px`;
    stage.style.height = `${height}px`;
    document.documentElement.style.setProperty("--w", `${width}px`);
    document.documentElement.style.setProperty("--h", `${height}px`);
    if (params.has("alpha")) document.documentElement.classList.add("alpha");
    if (params.get("bg")) {
      const bg = document.createElement("img");
      bg.id = "dailies-bg";
      bg.src = params.get("bg");
      stage.prepend(bg);
    }
    if (params.has("guides")) addGuides(stage, width, height);

    let current = 0;
    const ready = (async () => {
      await loadTokens();
      if (cfg.setup) await cfg.setup();
      await document.fonts.ready;
      await mediaReady();
      cfg.render(0);
    })();

    const api = {
      width, height, fps, duration, ready,
      async seek(t) {
        current = t;
        await syncVideos(t, true);
        cfg.render(t);
        // let layout, fonts and decoding settle before the frame is captured
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
      },
    };
    window.__dailies = api;

    if (RENDER) {
      document.documentElement.classList.add("render");
    } else {
      ready.then(() => previewUI(api, cfg, (t) => { current = t; syncVideos(t, false); cfg.render(t); }, parseFloat(params.get("t") || "0")));
    }
    return api;
  }

  function addGuides(stage, w, h) {
    const g = document.createElement("div");
    g.id = "dailies-guides";
    const vertical = h > w;
    // 16:9 title-safe 90%; 9:16 platform UI: top 12%, bottom 22%, right 15%
    const boxes = vertical
      ? [{ l: 6, t: 12, r: 15, b: 22, c: "#00E5FF", label: "9:16 platform safe" }]
      : [{ l: 5, t: 5, r: 5, b: 5, c: "#00E5FF", label: "title safe 90%" }, { l: 3.5, t: 3.5, r: 3.5, b: 3.5, c: "#FF3D7F", label: "action safe 93%" }];
    for (const b of boxes) {
      const d = document.createElement("div");
      Object.assign(d.style, { position: "absolute", left: `${b.l}%`, top: `${b.t}%`, right: `${b.r}%`, bottom: `${b.b}%`, border: `2px dashed ${b.c}`, pointerEvents: "none", zIndex: 9999 });
      const s = document.createElement("span");
      s.textContent = b.label;
      Object.assign(s.style, { position: "absolute", top: "4px", left: "6px", font: "600 18px system-ui", color: b.c });
      d.appendChild(s);
      g.appendChild(d);
    }
    stage.appendChild(g);
  }

  function previewUI(api, cfg, renderAt, startT) {
    const bar = document.createElement("div");
    bar.id = "dailies-bar";
    bar.innerHTML = `<button id="dl-play">Play</button><input id="dl-scrub" type="range" min="0" max="${api.duration}" step="${1 / api.fps}" value="0"><span id="dl-time"></span>`;
    document.body.appendChild(bar);
    const play = bar.querySelector("#dl-play"), scrub = bar.querySelector("#dl-scrub"), label = bar.querySelector("#dl-time");
    let t = clamp(startT, 0, api.duration), playing = false, last = 0;
    const fit = () => {
      const s = Math.min(innerWidth / api.width, (innerHeight - 56) / api.height);
      document.getElementById("stage").style.transform = `scale(${s})`;
    };
    const show = () => { renderAt(t); scrub.value = t; label.textContent = `${t.toFixed(2)}s / ${api.duration}s  ·  frame ${Math.round(t * api.fps)}`; };
    const tick = (now) => {
      if (!playing) return;
      t += (now - last) / 1000; last = now;
      if (t >= api.duration) t = 0;
      show(); requestAnimationFrame(tick);
    };
    const toggle = () => {
      playing = !playing; play.textContent = playing ? "Pause" : "Play";
      document.querySelectorAll("video[data-start]").forEach((v) => (playing ? v.play().catch(() => {}) : v.pause()));
      if (playing) { last = performance.now(); requestAnimationFrame(tick); }
    };
    play.onclick = toggle;
    scrub.oninput = () => { t = parseFloat(scrub.value); show(); };
    addEventListener("keydown", (e) => {
      if (e.code === "Space") { e.preventDefault(); toggle(); }
      if (e.code === "ArrowRight") { t = Math.min(api.duration, t + 1 / api.fps); show(); }
      if (e.code === "ArrowLeft") { t = Math.max(0, t - 1 / api.fps); show(); }
    });
    addEventListener("resize", fit);
    fit(); show();
  }

  window.Dailies = { composition, ease, spring, kf, apply, animate, range, clamp, lerp, stepped, wiggle, noise: noise1, draw, typewriter, countUp, split, scene };
})();
