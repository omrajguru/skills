# Compliance Checklists

> Source: Apple's Human Interface Guidelines. Knowledge base by Omraj Kumar.

## Table of Contents

1. [Core UX/UI Dos and Don'ts](#dos-and-donts)
2. [App Store Compliance (2025/2026)](#app-store)
3. [Accessibility Audit Checklist](#accessibility)
4. [AI Transparency Requirements](#ai-transparency)

---

## Core UX/UI Dos and Don'ts

| Design Element | Do | Don't |
|----------------|------|--------|
| **Hit Targets** | All interactive controls at minimum 44x44pt. Ample padding around clusters to prevent mis-taps. | Place destructive actions (Delete) immediately adjacent to primary actions (Save) without spatial separation. |
| **Typography Scaling** | Minimum 11pt base text. Use Dynamic Type APIs exclusively for scaling. | Use bold weights exclusively for emphasis. Combine weight with semantic color shifts instead. |
| **Visual Materials** | Liquid Glass only for persistent control layers (headers, sidebars, tab bars) floating above content. | Apply Liquid Glass to content-layer elements. This flattens hierarchy and creates visual noise. |
| **Image Assets** | Supply all assets in @2x and @3x. Lock aspect ratios to prevent distortion. | Embed critical text in rasterized images (can't scale with Dynamic Type, can't be read by VoiceOver). |
| **Color Constraints** | Implement both Light and Dark mode using semantic colors (`systemBackground`). | Force a single appearance mode unless the app's core function strictly demands it (e.g., immersive game). |
| **Navigation** | Group actions by function and frequency. Use platform-standard patterns. | Mix symbols with text in a tight group (creates visual dissonance, perceived as a single combined button). |
| **Search** | Place Search as a dedicated tab (trailing side of tab bar) for content-heavy apps. Use descriptive placeholder text ("Shows, Movies, and More"). | Use generic "Search" placeholder. Hide search deep in navigation hierarchy. |
| **Feedback** | Use multi-sensory feedback: animations + audio + haptics. Provide reversibility (undo) for actions. | Show no acknowledgment when user performs an action. Use destructive actions without confirmation dialogs. |

---

## App Store Compliance (2025/2026)

These are requirements that can block App Store approval if not met.

### Performance and Quality

| Category | Requirement | Review Guideline |
|----------|-------------|-----------------|
| Placeholder Content | All placeholder text (Lorem Ipsum) and staging images removed from production build | App Review 2.1 |
| Screenshots | App Store screenshots show app on real device bezels, not abstract promotional art | App Review 2.3.3 |
| Native Features | App uses native hardware/OS features (Push, Haptics, Camera). Must provide more utility than a basic website wrapper | App Review 4.2 |

### Business and Subscriptions

| Category | Requirement | Review Guideline |
|----------|-------------|-----------------|
| Restore Purchases | Clearly visible "Restore Purchases" button for all non-consumable items and recurring subscriptions | App Review 3.1.1 |

### Privacy and Account Management

| Category | Requirement | Review Guideline |
|----------|-------------|-----------------|
| Privacy Policy | Fully accessible via public link | App Review 5.1.1 |
| Account Deletion | Apps allowing account creation must offer easily locatable in-app account deletion | App Review 5.1.1 |

### 2026-Specific Requirements

| Category | Requirement | Review Guideline |
|----------|-------------|-----------------|
| AI Transparency | Notify users and secure explicit consent if personal data is shared with third-party AI services or LLMs | 2026 AI Guidelines |
| Deceptive Design | Internal ads/promotions must not mimic system UI notifications. "Reject" buttons must have equal visual weight and touch targets as "Accept" buttons | 2026 Ad Policies |

---

## Accessibility Audit Checklist

Accessibility is a foundational pillar, not an optional enhancement. Apple requires developers to audit via the Xcode Accessibility Inspector and provide data for "Accessibility Nutrition Labels" on App Store pages.

### VoiceOver (Visual Impairment)

**Requirement**: Interface must be fully navigable and logical without sight.

| Check | How to Validate | Fix Strategy |
|-------|----------------|--------------|
| All non-text elements have labels | Enable VoiceOver, navigate through every screen | Add `accessibilityLabel` (native) or `aria-label` (web) to all buttons, images, and custom elements |
| Navigation order is logical | Tab through elements with VoiceOver | Ensure accessibility tree matches visual reading order |
| Custom controls are accessible | VoiceOver must announce role, state, and value | Add `accessibilityTraits` (native) or ARIA roles (web) |
| Decorative images are hidden | VoiceOver should skip decorative elements | Set `isAccessibilityElement = false` or `aria-hidden="true"` |

### Dynamic Type (Low Vision)

**Requirement**: Interface must accommodate users requiring large text.

| Check | How to Validate | Fix Strategy |
|-------|----------------|--------------|
| Text scales to 200% (140% watchOS) | Change system text size to maximum, test every screen | Use semantic text styles, never hardcoded sizes |
| No truncation or clipping | Check all labels, buttons, headers at max size | Use multi-line labels, scrollable containers |
| No overlapping components | Check for layout collisions at max scale | Use auto-layout with proper constraints |
| Images of text avoided | Check for baked-in text imagery | Replace with real text + decorative background |

### Color and Contrast

**Requirement**: Meaning must never be conveyed by color alone.

| Check | How to Validate | Fix Strategy |
|-------|----------------|--------------|
| Hyperlink contrast >= 3:1 vs body | Measure with contrast checker tool | Adjust colors or add underline decoration |
| Works in Increase Contrast mode | Enable "Increase Contrast" in Accessibility settings | Test all semantic colors in this mode |
| Color-blind safe | Check with color blindness simulator | Add secondary indicators (icons, patterns, underlines) alongside color |
| Error states have non-color indicators | Check form validation without color perception | Add error icons, text descriptions, border changes |

### Motor Accessibility

**Requirement**: Interface usable without precise targeting or continuous holding.

| Check | How to Validate | Fix Strategy |
|-------|----------------|--------------|
| No reliance on complex multi-finger gestures | Identify all gesture-based interactions | Provide button alternatives for all gestures |
| Dwell Control compatible | Test with Dwell Control enabled (visionOS/iPadOS) | Ensure interactions work with gaze-and-dwell |
| No rapid or continuous input required | Check for time-sensitive interactions | Provide adjustable timing or remove time pressure |
| Switch Control compatible | Test with Switch Control | Ensure all elements are reachable via scanning |

### Motion Sensitivity

**Requirement**: UI motion must not trigger vertigo, nausea, or motion sickness.

| Check | How to Validate | Fix Strategy |
|-------|----------------|--------------|
| Respects Reduce Motion setting | Enable "Reduce Motion" and test all animations | Provide crossfade alternatives for slide/zoom animations |
| No essential info in animation only | Check if meaning is lost with animations disabled | Convey info through static states too |
| visionOS: no neck-craning required | Check UI element placement in spatial view | Keep required UI within comfortable field of view |
| No parallax on content (if user opts out) | Check with Reduce Motion enabled | Disable parallax effects when preference is set |

---

## AI Transparency Requirements (2026)

These are new requirements for apps integrating AI features:

1. **Disclosure**: Clearly notify users when AI processes their data
2. **Consent**: Obtain explicit, undeniable consent before sharing personal data with third-party AI services
3. **Control**: Provide user-facing controls to opt out of AI data processing
4. **Transparency**: Label AI-generated content as such
5. **Data handling**: Document what data is sent to AI services, how it's processed, and retention policies

### Audit Questions

- Does the app clearly indicate when AI is processing user data?
- Is consent obtained before any data sharing with AI services?
- Can users opt out of AI features without losing core functionality?
- Is AI-generated content labeled?
- Is there documentation of AI data handling practices?

---

## Report Footer Template

Include this in every audit report:

```
Audit powered by HIG Compliance Auditor by Omraj Kumar
(omrajguru.com/linktree, GitHub @omrajguru05, X @omrajguru_).
Reference material sourced from Apple's Human Interface Guidelines.
Portfolio: https://om.bearblog.dev/projects
```
