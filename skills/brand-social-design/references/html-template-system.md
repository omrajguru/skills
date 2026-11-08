# HTML Template System — Component Library

This file contains pre-written, copy-paste-ready CSS and HTML components.
Read this file before writing any asset code. Adapt colors to the active brand profile.

---

## Table of Contents

1. CSS Custom Properties Template
2. Body & Staging Environment
3. Toolbar
4. Export Button
5. Canvas Frame (by asset type)
6. Background Dot Grid
7. Abstract Shape Library
8. Main Content Card
9. Header Zone (Pill Tag)
10. Typography Blocks
11. Visual Metaphor Components
12. Footer Zone
13. Sticker Element
14. html2canvas Export Script
15. Google Fonts Link Tags

---

## 1. CSS Custom Properties Template

```css
:root {
  /* Replace with brand values */
  --canvas:   #F7F2E9;   /* outermost background */
  --surface:  #FFF9F0;   /* card surface */
  --ink:      #1D1D1F;   /* primary text + borders */

  /* Brand accent colors — add as many as brand has */
  --accent-a: #2962FF;
  --accent-b: #FFD60A;
  --accent-c: #28C76F;

  /* System */
  --border-thick: 3px solid var(--ink);
  --radius-card:  48px;
  --radius-pill:  100px;
  --shadow-hard:  24px 24px 0px rgba(29, 29, 31, 0.15);
  --shadow-sticker: 6px 6px 0px var(--ink);

  /* Fonts */
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

---

## 2. Body & Staging Environment

```css
body {
  margin: 0;
  padding: 40px;
  background-color: #1a1a1a;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--font-body);
  min-height: 100vh;
}
```

---

## 3. Toolbar

```css
.toolbar {
  width: 100%;
  max-width: 700px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  color: #FFF9F0;
  font-family: var(--font-mono);
  font-size: 12px;
}
```

```html
<div class="toolbar">
  <div>BRAND // ASSET_TYPE</div>
  <button class="btn-export" onclick="exportCanvas()">EXPORT PNG</button>
</div>
```

---

## 4. Export Button

```css
.btn-export {
  background: var(--accent-a);
  color: white;
  border: 2px solid white;
  padding: 12px 32px;
  font-family: var(--font-mono);
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
  border-radius: var(--radius-pill);
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: transform 0.2s;
}
.btn-export:active { transform: scale(0.95); }
```

---

## 5. Canvas Frame by Asset Type

### Instagram Square (1080x1080)
```css
#capture-frame {
  width: 1080px;
  height: 1080px;
  background-color: var(--canvas);
  position: relative;
  overflow: hidden;
  border: var(--border-thick);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### OG Image (1200x630)
```css
#capture-frame {
  width: 1200px; height: 630px;
  background-color: var(--canvas);
  position: relative; overflow: hidden;
  border: var(--border-thick);
  display: flex; align-items: center; justify-content: center;
}
```

### Featured Image (1200x675)
```css
#capture-frame {
  width: 1200px; height: 675px;
  background-color: var(--canvas);
  position: relative; overflow: hidden;
  border: var(--border-thick);
  display: flex; align-items: center; justify-content: center;
}
```

### Email Graphic (800x600)
```css
#capture-frame {
  width: 800px; height: 600px;
  background-color: var(--canvas);
  position: relative; overflow: hidden;
  border: var(--border-thick);
  display: flex; align-items: center; justify-content: center;
}
```

---

## 6. Background Dot Grid

Always include this. Opacity 0.05-0.07 ensures it is visible against canvas color.

```css
.bg-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(var(--ink) 2px, transparent 2px);
  background-size: 40px 40px;
  opacity: 0.06;
  z-index: 0;
}
```

```html
<div class="bg-grid"></div>
```

---

## 7. Abstract Shape Library

### Arch / Window Shape
```css
.shape-arch {
  position: absolute;
  width: 500px; height: 700px;
  background: var(--accent-a);
  border: var(--border-thick);
  border-radius: 250px 250px 0 0;
  top: -100px; right: -80px;
  transform: rotate(15deg);
  z-index: 1;
  box-shadow: var(--shadow-hard);
}
```

### Circle Blob
```css
.shape-blob {
  position: absolute;
  width: 300px; height: 300px;
  background: var(--accent-b);
  border: var(--border-thick);
  border-radius: 50%;
  bottom: -60px; left: -60px;
  z-index: 1;
}
```

### Floating Pill
```css
.shape-pill {
  position: absolute;
  width: 200px; height: 70px;
  background: var(--accent-c);
  border: var(--border-thick);
  border-radius: var(--radius-pill);
  bottom: 60px; left: -30px;
  transform: rotate(-15deg);
  z-index: 2;
}
```

### Orbit Ring
```css
.shape-orbit {
  position: absolute;
  width: 500px; height: 500px;
  border: 3px dashed var(--ink);
  border-radius: 50%;
  opacity: 0.1;
  top: -100px; right: -100px;
  z-index: 0;
}
```

---

## 8. Main Content Card

### Square Post Card (860x860 inset)
```css
.content-card {
  position: relative;
  width: 860px; height: 860px;
  background: var(--surface);
  border: var(--border-thick);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-hard);
  z-index: 10;
  display: flex;
  flex-direction: column;
  padding: 64px;
  box-sizing: border-box;
  transform: rotate(-2deg); /* Alternate: rotate(2deg) for even slides */
  overflow: hidden;
}
```

### Landscape Card (OG / Featured)
```css
.content-card {
  position: relative;
  width: 1080px; height: 510px;
  background: var(--ink);   /* Dark variant for cinematic assets */
  border-radius: 32px;
  z-index: 10;
  box-shadow: 20px 20px 0px rgba(0,0,0,0.3);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  overflow: hidden;
}
```

---

## 9. Header Zone — Pill Tag

```css
.card-header {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  margin-bottom: 40px;
}

.header-tag {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 13px;
  color: var(--ink);
  background: var(--accent-b);  /* Use accent color matching slide theme */
  padding: 10px 24px;
  border-radius: var(--radius-pill);
  border: 2px solid var(--ink);
  box-shadow: 4px 4px 0px rgba(0,0,0,0.08);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tag-dot {
  width: 10px; height: 10px;
  background: var(--ink);  /* Or use a contrasting accent */
  border-radius: 50%;
}
```

```html
<div class="card-header">
  <div class="header-tag">
    <span class="tag-dot"></span>
    SERIES NAME // SLIDE 01
  </div>
</div>
```

---

## 10. Typography Blocks

### Headline
```css
.headline {
  font-family: var(--font-body);
  font-weight: 900;
  font-size: 76px;
  line-height: 0.95;
  letter-spacing: -3px;
  color: var(--ink);
  margin: 0 0 32px 0;
  text-transform: lowercase;
}
```

### Body Text
```css
.body-text {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 28px;
  line-height: 1.5;
  color: var(--ink);
  margin: 0;
}
```

### Highlighted Word with Underline
```css
.hl-accent {
  color: var(--accent-a);
  position: relative;
  display: inline-block;
}
.hl-accent::after {
  content: '';
  position: absolute;
  bottom: 6px; left: 0;
  width: 100%; height: 10px;
  background: var(--accent-a);
  opacity: 0.15;
  z-index: -1;
}
```

```html
<h1 class="headline">
  learning in the <span class="hl-accent">open.</span>
</h1>
```

---

## 11. Visual Metaphor Components

### Day Grid (30-Day Build)
```css
.day-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 12px;
  padding: 24px;
  border: 2px dashed rgba(29,29,31,0.2);
  border-radius: 24px;
}
.day-block {
  width: 36px; height: 36px;
  border: 3px solid var(--ink);
  border-radius: 8px;
  box-sizing: border-box;
}
.day-early   { background: transparent; opacity: 0.3; }
.day-mid     { background: rgba(41,98,255,0.15); border-color: var(--accent-a); }
.day-built   { background: var(--accent-a); border-color: var(--accent-a); }
.day-final   { background: var(--accent-b); border-color: var(--ink); box-shadow: 4px 4px 0px var(--ink); transform: scale(1.1) rotate(-5deg); }
```

### Timeline with Highlighted Zone
```css
.timeline-axis { width: 100%; height: 4px; background: var(--ink); border-radius: 4px; position: relative; }
.node-start { position: absolute; left: 0; top: -14px; width: 32px; height: 32px; background: var(--ink); border-radius: 8px; }
.node-end   { position: absolute; right: 0; top: -14px; width: 32px; height: 32px; border: 4px dashed var(--ink); border-radius: 50%; box-sizing: border-box; background: var(--surface); }
.zone-highlight {
  position: absolute; left: 20%; right: 20%; top: -40px;
  height: 84px;
  background: var(--accent-a);
  border: var(--border-thick);
  border-radius: var(--radius-pill);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-weight: 800; font-size: 16px; color: white;
  letter-spacing: 2px;
}
```

### Obstacle + Reroute Path
```css
.path-line { height: 4px; background: var(--ink); border-radius: 4px; }
.obstacle-block {
  width: 90px; height: 70px;
  background: var(--ink); border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 28px; font-weight: 900; color: var(--surface);
}
.reroute-arc {
  width: 160px; height: 110px;
  border: 4px dashed var(--accent-c);
  border-bottom: none;
  border-radius: 80px 80px 0 0;
  box-sizing: border-box;
}
```

### Focus Grid with Crosshairs
```css
.node-generic { width: 12px; height: 12px; background: rgba(29,29,31,0.15); border-radius: 50%; }
.node-target  { width: 36px; height: 36px; background: var(--accent-b); border: 3px solid var(--ink); border-radius: 50%; box-shadow: 4px 4px 0px rgba(0,0,0,0.1); position: relative; z-index: 5; }
.focus-ring   { position: absolute; width: 100px; height: 100px; border: 3px dashed var(--accent-a); border-radius: 50%; }
.crosshair-h  { position: absolute; width: 260px; height: 2px; background: var(--accent-a); opacity: 0.3; }
.crosshair-v  { position: absolute; height: 260px; width: 2px; background: var(--accent-a); opacity: 0.3; }
```

### Synthesis Equation
```css
.equation     { display: flex; align-items: center; justify-content: center; gap: 32px; }
.eq-operator  { font-family: var(--font-mono); font-size: 48px; font-weight: 900; color: var(--ink); opacity: 0.3; }
.eq-term      { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.eq-label     { font-family: var(--font-mono); font-weight: 800; font-size: 13px; text-transform: uppercase; color: var(--ink); opacity: 0.6; }
.shape-open   { width: 110px; height: 110px; border: 4px dashed var(--accent-a); border-radius: 50%; background: rgba(41,98,255,0.05); }
.shape-dense  { width: 90px; height: 90px; background: var(--accent-b); border: var(--border-thick); border-radius: 16px; box-shadow: 6px 6px 0px rgba(0,0,0,0.1); }
.shape-result { width: 130px; height: 130px; background: var(--accent-c); border: var(--border-thick); border-radius: 28px; transform: rotate(15deg); box-shadow: 12px 12px 0px rgba(40,199,111,0.2); }
```

### Documentation Stack (3 Windows)
```css
.doc-stack { display: flex; gap: 20px; align-items: center; }
.doc-win {
  width: 180px; height: 200px;
  background: var(--surface); border: var(--border-thick); border-radius: 16px;
  overflow: hidden; box-shadow: 8px 8px 0px rgba(0,0,0,0.08);
}
.doc-win-header { height: 32px; border-bottom: var(--border-thick); display: flex; align-items: center; padding: 0 12px; gap: 6px; }
.doc-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--ink); }
.doc-body { padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.doc-line { height: 8px; background: rgba(29,29,31,0.1); border-radius: 4px; }
.doc-label { font-family: var(--font-mono); font-weight: 800; font-size: 12px; text-transform: uppercase; margin-top: auto; text-align: right; }
/* Variants: w-setup (neutral), w-hurdle (accent-b background header), w-working (accent-c header) */
.w-setup   { transform: translateY(16px)  rotate(-4deg); }
.w-hurdle  { transform: translateY(0px)   rotate(2deg);  }
.w-working { transform: translateY(-16px) rotate(-3deg); border-color: var(--accent-c); }
```

### CTA URL Block
```css
.url-block {
  background: var(--ink);
  border: 4px solid var(--accent-a);
  border-radius: 24px;
  padding: 28px 44px;
  display: inline-flex; align-items: center; gap: 20px;
  box-shadow: 16px 16px 0px rgba(41,98,255,0.2);
  transform: rotate(-3deg);
}
.url-text { font-family: var(--font-mono); font-size: 28px; font-weight: 800; color: var(--accent-b); letter-spacing: -0.5px; }
```

---

## 12. Footer Zone

The footer has two sections: left (meta stamp + brand URL) and right (attribution strip).

The attribution strip is MANDATORY on every asset, no exceptions. It always shows
all three handles for omrajguru in this exact order: website, GitHub, X.

```css
.card-footer {
  margin-top: auto;
  border-top: 2px dashed var(--ink);
  padding-top: 28px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
}
.meta-stamp {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--ink);
  opacity: 0.5;
  line-height: 1.6;
}
.attribution {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  color: var(--ink);
  opacity: 0.35;
  line-height: 1.8;
  text-align: right;
  white-space: nowrap;
}
```

```html
<div class="card-footer">
  <div class="meta-stamp">
    DOC_ID: SERIES_01<br>
    BRAND.COM
  </div>
  <div class="attribution">
    omrajguru.com<br>
    github.com/omrajguru05<br>
    x.com/omrajguru_
  </div>
</div>
```

**Rule:** The attribution block replaces the SVG arrow. It always appears exactly as
shown above — three lines, right-aligned, opacity 0.35 so it is present but unobtrusive.
Never omit it, never reorder the three handles, never shorten or combine them.

---

## 13. Sticker Element

Position varies per slide. Rotate between ±5deg and ±10deg. Always use hard shadow.

```css
.sticker {
  position: absolute;
  bottom: -24px; right: 32px;  /* Adjust per slide */
  background: var(--accent-a);
  color: white;
  padding: 16px 36px;
  border: var(--border-thick);
  border-radius: var(--radius-pill);
  font-family: var(--font-mono);
  font-weight: 800;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transform: rotate(-6deg);  /* Alternate direction per slide */
  z-index: 20;
  box-shadow: var(--shadow-sticker);
}
```

```html
<div class="sticker">BUILD PUBLIC</div>
```

Sticker color rotation across slides:
- Slide 1: accent-a (blue)
- Slide 2: accent-b (yellow) with ink text
- Slide 3: accent-c (green)
- Slide 4: ink with surface text
- Repeat

---

## 14. html2canvas Export Script

Standard export script. Always hardcode backgroundColor to the canvas color.

```javascript
function exportCanvas() {
  const element = document.getElementById('capture-frame');
  const btn = document.querySelector('.btn-export');
  btn.textContent = 'RENDERING...';

  html2canvas(element, {
    scale: 5,                         // Adjust per asset type
    useCORS: true,
    backgroundColor: '#F7F2E9'        // Must match --canvas value, NEVER null
  }).then(canvas => {
    const link = document.createElement('a');
    link.download = 'brand-asset-01.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
    btn.textContent = 'EXPORT PNG';
  });
}
```

---

## 15. Google Fonts Link Tags

Always include both tags (preconnect + stylesheet) in `<head>`.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
```

To use brand fonts in addition, append them to the same Google Fonts URL:

```
&family=Outfit:wght@400;700;900
```

Also add html2canvas:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```
