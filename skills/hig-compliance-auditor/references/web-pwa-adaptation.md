# Web and PWA Adaptation

> Source: Apple's Human Interface Guidelines. Knowledge base by Omraj Kumar.

## Table of Contents

1. [PWA Configuration for Native Feel](#pwa-configuration)
2. [Liquid Glass CSS Implementation](#liquid-glass-css)
3. [Typography on the Web](#web-typography)
4. [Icon Licensing Constraints](#icon-licensing)
5. [Interaction Fidelity](#interaction-fidelity)

---

## PWA Configuration

To make a web app feel native on Apple platforms, shed the browser wrapper.

### manifest.json Requirements

```json
{
  "display": "standalone"
}
```

`display: standalone` removes the Safari URL bar and bottom controls when the user adds the PWA to their Home Screen. The web app occupies the full screen like a native app.

### Theme Integration

Set the theme-color meta tag to match your app's top header background:

```html
<meta name="theme-color" content="#ffffff">
```

This blends the iOS status bar (battery, time, signal) seamlessly with the app UI.

### Apple Touch Icons

Provide properly dimensioned touch icons:

```html
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
```

The OS applies corner rounding automatically. The icon must look authentic alongside native apps on the Home Screen.

### Common PWA Audit Violations

- Missing `display: standalone` in manifest
- No `theme-color` meta tag (status bar looks disconnected)
- Missing or improperly sized apple-touch-icon
- App looks like a website in a wrapper rather than a native experience

---

## Liquid Glass CSS Implementation

Replicate Apple's Liquid Glass material on the web using standard CSS. This is a four-layer technique.

### The Four Layers

```css
.liquid-glass-nav {
  /* Layer 1: Translucent base */
  background: rgba(255, 255, 255, 0.15);
  /* Use rgba(30, 30, 30, 0.15) for dark mode */

  /* Layer 2: Backdrop blur (refraction) */
  -webkit-backdrop-filter: blur(12px);  /* Safari compatibility - REQUIRED */
  backdrop-filter: blur(12px);

  /* Layer 3: Edge highlight (border definition) */
  border: 1px solid rgba(255, 255, 255, 0.2);

  /* Layer 4: Elevation shadow */
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}
```

### Layer Breakdown

| Layer | CSS Property | Purpose |
|-------|-------------|---------|
| 1. Translucent base | `background: rgba(...)` | Allows underlying content to peek through |
| 2. Backdrop blur | `backdrop-filter: blur(12px)` | Diffuses content beneath, simulating frosted glass refraction |
| 3. Edge highlight | `border: 1px solid rgba(255, 255, 255, 0.2)` | Defines the glass panel shape against complex backgrounds |
| 4. Elevation shadow | `box-shadow: 0 8px 32px ...` | Establishes Z-axis elevation, separating control from content layer |

### Critical Implementation Notes

1. **Always include `-webkit-backdrop-filter`** - Safari requires the prefix. Without it, the effect breaks on all Apple devices in Safari.

2. **Manage z-index carefully** - Glass elements must float above the main scrolling content container.

3. **Performance warning** - Heavy backdrop filters are computationally expensive on older mobile devices. Test scrolling performance on target devices. Consider reducing blur radius or disabling on low-power devices.

4. **Apply only to control-layer elements** - Navigation bars, sidebars, tab bars. Never to content cards or text containers. This matches the native HIG rule.

### Dark Mode Variant

```css
@media (prefers-color-scheme: dark) {
  .liquid-glass-nav {
    background: rgba(30, 30, 30, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  }
}
```

### Common CSS Audit Violations

- Missing `-webkit-backdrop-filter` prefix (broken on Safari)
- Liquid Glass applied to content-layer elements
- No dark mode variant
- Excessive blur radius causing performance issues on mobile
- Missing z-index management (glass elements behind content)

---

## Web Typography

### The System Font Stack

Use the system font stack to render the native font on each platform without loading custom fonts:

```css
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont,
               "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
```

This renders:
- **SF Pro** on Apple devices
- **Roboto** on Android
- **Segoe UI** on Windows

### Tracking Adjustments for Web

When targeting Apple devices specifically, apply tracking adjustments to match native rendering:

```css
/* Body text (17px equivalent) */
.body-text {
  font-size: 1.0625rem; /* 17px */
  letter-spacing: -0.43px;
  line-height: 1.3; /* 130% */
}

/* Header text (28px equivalent) */
.header-text {
  font-size: 1.75rem; /* 28px */
  letter-spacing: -0.8px;
  line-height: 1.15; /* 115% */
}
```

### Dynamic Type on the Web

Native Dynamic Type doesn't exist on the web, but you can approximate it:

- Use `rem` units (not `px`) for all font sizes
- Respect the user's browser font-size preferences
- Test at 200% browser zoom without layout breaks
- Use CSS `clamp()` for responsive sizing if needed

### Common Web Typography Violations

- Hardcoded `px` font sizes instead of `rem`
- Missing tracking adjustments
- Layout breaks at 200% zoom
- Loading custom fonts when system font stack would suffice
- Body text smaller than 11pt equivalent

---

## Icon Licensing Constraints

### SF Symbols Are NOT Licensed for Web

Per Apple's licensing agreements:

> SF Symbols may only be used to create user interfaces for software products running natively on Apple's operating systems via Xcode. They cannot be extracted, hosted as web fonts, or embedded as SVGs on public-facing web applications.

### Compliant Alternatives

Use open-source icon libraries that match SF Symbols' visual characteristics:

| Library | Match Quality | Notes |
|---------|--------------|-------|
| **Phosphor Icons** | Excellent | Similar line weights, extensive set |
| **Lucide** | Very good | Clean, consistent stroke widths |
| **Heroicons** | Good | By Tailwind team, well maintained |

These libraries provide the same minimalist, outlined aesthetic while staying legally compliant.

### Common Icon Audit Violations

- SF Symbols font files extracted and hosted on web servers
- SF Symbols SVGs embedded directly in web pages
- Icons with inconsistent stroke weights (mixing libraries)
- No filled variants for active/selected states

---

## Interaction Fidelity

### Eliminating the 300ms Tap Delay

Native apps respond instantly. Web apps historically had a 300ms delay on mobile. Modern browsers have largely eliminated this, but ensure:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

This viewport meta tag is critical - without it, Safari may still impose the delay.

### Disabling Text Selection on UI Controls

Native buttons don't highlight with text selection when tapped:

```css
.ui-button {
  -webkit-user-select: none;
  user-select: none;
  -webkit-touch-callout: none; /* Prevents long-press context menu on iOS */
}
```

Apply only to interactive controls, never to actual content text.

### Gesture Conflict Prevention

- **Swipe-to-go-back** in Safari must not conflict with internal horizontal carousels or swipe gestures
- Test edge swipes carefully - if your app has horizontal scrolling near screen edges, ensure the browser's back gesture still works

### Safe Area Handling in PWAs

```css
body {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```

This ensures content doesn't get obscured by the Dynamic Island, home indicator, or rounded corners on iPhones.

### Common Interaction Violations

- Missing viewport meta tag (causes tap delay)
- Text selection highlighting on buttons
- Horizontal carousels conflicting with Safari swipe-back
- Content behind Dynamic Island or home indicator (missing safe-area-inset)
