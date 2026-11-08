# HIG Foundations

> Source: Apple's Human Interface Guidelines. Knowledge base by Omraj Kumar.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Typography and Dynamic Type](#typography)
3. [Semantic Color System](#color)
4. [Materials and Liquid Glass](#materials)
5. [Layout, Safe Areas, Spatial Organization](#layout)
6. [Iconography and SF Symbols](#iconography)

---

## Core Principles

Six foundational principles govern all Apple interface design. These are UX mandates, not suggestions.

### Clarity - Eliminating Cognitive Friction

- Interfaces must be legible, precise, and immediately comprehensible
- Every interactive element must have a singular, explicit purpose
- If an app requires a tutorial to be understood, it fails the clarity test
- **UI**: High-contrast text, sharp icons, generous negative space
- **UX**: Group related items into distinct visual blocks separated by subtle spacing

**Audit check**: Can a new user complete the primary task without instructions?

### Deference - Elevating Content

- The UI exists to support content, not compete with it
- Minimize interruptions - use notifications, alerts, and modals sparingly
- **UI**: Minimize heavy chrome, thick borders, saturated interface elements. Use translucent materials so content permeates the visual field
- **UX**: Content is the hero. The interface recedes

**Audit check**: Does any UI element draw more attention than the content?

### Depth - Communicating Spatial Relationships

- Use depth to convey relationships, state, and interactive priority
- Users instinctively understand physical space - translate this digitally
- **UI**: Visual layers, calculated drop shadows, translucent materials, physics-based motion
- **UX**: When navigating deeper, the previous screen should feel like it still exists behind the current one

**Audit check**: Do layered elements (sheets, popovers, modals) communicate their Z-position clearly?

### Hierarchy - Guiding the Eye

- Users should instinctively know where to look first, second, third
- Without hierarchy, the interface is a wall of data causing cognitive overload
- **UI**: Variations in scale, semantic color weight, spatial grouping. Primary CTAs use bold tint colors or prominent placement
- **UX**: Most critical functions are easiest to reach with fewest taps

**Audit check**: Can you identify the primary action within 2 seconds of seeing a screen?

### Harmony - Software-Hardware Symbiosis

- Software UI must mirror the physical geometry of the hardware
- Corner radii of app windows/buttons are mathematically calculated to match device bezels (continuous squircles)
- Third-party apps should feel like organic extensions of the OS

**Audit check**: Do corner radii match the platform's physical hardware geometry?

### Consistency - Predictable Outcomes

- Use established patterns, controls, and interaction models
- Swipe-from-left-edge = back in Safari = back everywhere
- Use standard iconography, uniform typographic scales, predictable motion curves
- Brands can inject personality but must never break fundamental interaction conventions

**Audit check**: Does the app use platform-standard gestures and navigation patterns?

---

## Typography

### SF Font Family Rules

Apple's type system uses the San Francisco (SF) font family, engineered for legibility across all resolutions.

**Optical sizing threshold at 20 points:**

| Condition | Font | Characteristics |
|-----------|------|----------------|
| Text < 20pt | SF Pro Text | Loose tracking, optimized for dense body copy |
| Text >= 20pt | SF Pro Display | Tight tracking, elegant for headers |

### Required Tracking Adjustments

When developing outside native environments (Figma, web), manual tracking adjustments are required:

| Size | Tracking |
|------|----------|
| 17pt body | -0.43px |
| 28pt header | -0.8px |

**Line height (leading):**
- Body text: 120-130%
- Display text: 110-120%

### Dynamic Type (Critical for Compliance)

- **Never hardcode absolute font sizes**
- Use semantic text styles: `Title1`, `Title2`, `Title3`, `Headline`, `Body`, `Callout`, `Subheadline`, `Footnote`, `Caption1`, `Caption2`
- The OS scales text based on user accessibility preferences
- **Apps must accommodate text scaled to 200%** (140% for watchOS) without truncation, clipping, or overlapping
- Minimum base text size: **11 points**

**Audit violation examples:**
- Hardcoded `fontSize: 16` instead of semantic `.body`
- Text truncated at large Dynamic Type sizes
- Layout breaks when text scales to 200%

---

## Semantic Color System

### Why Semantic Colors Matter

Never use absolute hex values for system UI elements. Use semantic colors that automatically adapt to:
- Light/Dark Mode
- Increased Contrast accessibility setting
- Device display profiles (True Tone)

### Text Color Hierarchy

| Level | Semantic Name | Purpose |
|-------|--------------|---------|
| Primary | `primaryLabel` / `label` | Crucial text, titles |
| Secondary | `secondaryLabel` | Subtitles |
| Tertiary | `tertiaryLabel` | Placeholders |
| Quaternary | `quaternaryLabel` | Disabled text |

These adapt automatically - primary label is black in Light Mode, white in Dark Mode.

### Dark Mode Architecture

Dark Mode is **not** a simple color inversion. It uses a dual-tier background system:

| Layer | Background | When Used |
|-------|-----------|-----------|
| Base | `systemBackground` (pure black) | Root app layer |
| Elevated | `secondarySystemBackground` (slightly lighter grey) | Modal sheets, popovers, iPad multitasking floating views |

This dynamic shift maintains depth perception in dark interfaces.

### Contrast Requirements

- Hyperlinks vs body text: minimum **3:1 contrast ratio**
- Must pass under "Increase Contrast" accessibility mode
- Meaning must **never** be conveyed by color alone - add secondary indicators (underlines, icons, bolding)

**Audit violation examples:**
- Hardcoded `color: #000000` instead of semantic `label`
- Same background color for base and elevated surfaces in Dark Mode
- Links indistinguishable from body text (contrast < 3:1)

---

## Materials and Liquid Glass

### What is Liquid Glass?

Introduced at WWDC 2025, Liquid Glass is a dynamic translucent material that simulates physical glass with real-time blur, light refraction, and shadow casting. It unifies the visual language across macOS, iOS, iPadOS, and visionOS.

### Strict Application Rules

**Where to use Liquid Glass (control layer ONLY):**
- Bottom tab bars
- Top navigation bars / headers
- Sidebars
- Persistent toolbars

**Where NEVER to use Liquid Glass (content layer):**
- Standard scrolling content cards
- Generic text boxes
- Content backgrounds
- List item backgrounds

**Exception**: Transient interactive controls (sliders, toggles) may briefly adopt glass appearance while being actively manipulated.

### Scroll Edge Transitions

Navigation bars react to content scrolling beneath them:

| Style | Platform | Behavior |
|-------|----------|----------|
| Soft transition | iOS, iPadOS | Subtle, fluid blending |
| Hard transition | macOS | Stronger, definitive boundaries |

Before scrolling, the glass is transparent. When content scrolls underneath, the bar adopts a frosted blur that refracts content, keeping controls legible.

**Audit violation examples:**
- Liquid Glass material applied to content cards (hierarchy collapse)
- No scroll-edge transition on navigation bars
- Glass material making text illegible against complex backgrounds

---

## Layout, Safe Areas, Spatial Organization

### Edge-to-Edge with Safe Areas

- Content stretches edge-to-edge for immersion
- **Critical interactive elements and text must stay within safe areas**
- Safe areas protect against: Dynamic Island, camera housings, rounded display corners, home indicator

### Touch Targets

| Requirement | Size |
|-------------|------|
| Absolute minimum | **44x44 points** |
| Recommended for dense UIs | **64x64 points** (effective, with invisible padding) |
| Destructive actions | Must have substantial spatial separation from primary actions |

### Dynamic Adaptability

Layouts must gracefully handle:
- Device rotation (portrait to landscape)
- iPad multitasking split views
- External display resolutions
- Content that doesn't span the full window (use background extension views)

**Audit violation examples:**
- Touch target smaller than 44x44pt
- Delete button adjacent to Save button without spacing
- Content clipped by Dynamic Island or home indicator
- Layout broken in landscape or split-screen mode

---

## Iconography and SF Symbols

### SF Symbols Rules

| Context | Recommended Style | Why |
|---------|-------------------|-----|
| Top toolbars, inline with text | **Outlined** | Matches text visual weight |
| Bottom tab bar (active state) | **Filled** | High contrast, heavy visual weight for active indication |

### Rendering Modes

| Mode | Behavior |
|------|----------|
| Monochrome | Single tint color applied uniformly |
| Hierarchical | Varying opacities of a single tint to imply depth |
| Multicolor | Intrinsic system-defined colors (e.g., yellow sun, grey cloud) |

### Custom Glyphs

Custom symbols must match:
- Stroke weight of SF font family
- Baseline alignment
- Optical centering

Export an existing SF Symbol as SVG template and modify while preserving the structural hierarchy and naming conventions.

**Audit violation examples:**
- Filled icons in toolbar (should be outlined)
- Outlined icons in active tab bar state (should be filled)
- Custom icons with mismatched stroke weight
- Icons that don't scale with Dynamic Type
