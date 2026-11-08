# Platform-Specific Paradigms

> Source: Apple's Human Interface Guidelines. Knowledge base by Omraj Kumar.

## Table of Contents

1. [iOS and iPadOS](#ios-and-ipados)
2. [macOS](#macos)
3. [watchOS](#watchos)
4. [tvOS](#tvos)
5. [visionOS](#visionos)
6. [Cross-Platform Comparison](#comparison)

---

## iOS and iPadOS

**Context**: Physical proximity (1-2 feet), direct multi-touch interaction.

### Thumb-Driven Ergonomics (iPhone)

- iPhones are predominantly single-hand operated
- **Critical navigation and frequent controls**: anchor to bottom (Thumb Zone)
- **Destructive actions and filters**: place at top (harder to reach accidentally)
- Tab bars live at the bottom for persistent access

### Dynamic Island

- Evolved from hardware cutout to core interaction paradigm
- Apps should leverage it for real-time contextual updates:
  - Live ride-share ETAs
  - Ongoing timers
  - Media playback indicators
- Updates must not disrupt primary screen content below

### iPadOS Distinctions

- iPads share iOS foundation but demand distinct layouts for larger canvas
- **Use sidebars instead of bottom tab bars** for primary navigation
- Layouts must reflow for multi-window split-screen multitasking
- Support Slide Over and Stage Manager window sizes

### Tab Bars (iOS)

- Anchor bottom of screen
- **Never create a "More" overflow tab** - if you need one, re-evaluate information architecture
- Tab icons must never be hidden or disabled (even if content is unavailable)
- Spatial layout must remain stable to support muscle memory
- Support persistent accessory views above the tab bar (e.g., Now Playing bar)

### Sheets

- **Modal sheets**: Self-contained tasks, prevent parent interaction until dismissed via Cancel/Done
- **Non-modal sheets** (iPadOS): Allow simultaneous interaction with sheet and parent view

### Lists and Tables

- Optimized for rapid vertical scanning of text-heavy data
- For image-heavy content, prefer Collection Views (grids)
- Support swipe-to-delete and drag-to-reorder in edit mode

**Common iOS audit violations:**
- Primary actions placed at top of screen instead of thumb zone
- No Dynamic Island integration for live activities
- Bottom tab bar on iPad (should use sidebar)
- "More" tab present
- Modal sheets missing Cancel/Done buttons

---

## macOS

**Context**: Precision input (mouse/trackpad), keyboard-driven, multi-window workflows. Viewing distance 2-3 feet.

### Multi-Window and Toolbars

- Users manage multiple overlapping windows simultaneously
- Top-anchored toolbars provide immediate access to complex actions
- Primary actions often use prominent text formatting rather than iOS-style blue tint
- Support window resizing, full-screen, and Stage Manager

### The Menu Bar

- Unique to macOS - houses exhaustive app commands
- Many commands hidden behind keyboard shortcuts with modifier keys
- Navigation must be comprehensive - provide redundant paths to every function
- Power users prefer keyboard navigation over mouse clicks
- Every significant action should have a keyboard shortcut

### Liquid Glass on macOS

- Uses **Hard** scroll-edge transitions (stronger, definitive boundaries)
- Sidebar navigation is the primary pattern
- Support for density variations (regular, compact)

**Common macOS audit violations:**
- No keyboard shortcuts for primary actions
- Missing menu bar integration
- Using mobile-style bottom tab bars
- No support for window resizing or multi-window
- Missing right-click context menus

---

## watchOS

**Context**: Wrist-worn, extreme brevity. Viewing sessions last seconds. Sub-1-foot viewing distance, user often in motion.

### Design Constraints

- Strip away ALL non-essential data and decorative chrome
- Text must be large, high-contrast, instantly readable while user is in motion
- **Pure black background** - blends with OLED bezel, content appears to float on wrist
- Maximum glanceability - user should get information in under 3 seconds

### Ergonomic Input

- Precise finger tapping is difficult on a tiny, moving display
- **Touch targets should span full screen width** wherever possible
- Vertical scrolling primarily handled via **Digital Crown** (prevents finger from occluding content)
- Dynamic Type must accommodate scaling to **140%**

### Navigation

- Vertical pagination rather than complex hierarchies
- Minimize depth - flatten information architecture
- Keep interactions brief - 3-5 seconds per session

**Common watchOS audit violations:**
- Too much information density
- Small touch targets (not spanning screen width)
- Complex multi-level navigation hierarchies
- Non-black backgrounds (breaks bezel blending)
- Text not readable at arm's length while in motion

---

## tvOS

**Context**: "10-foot UI" - massive screen, remote control input, 8-12 foot viewing distance.

### The Focus Engine

This is the core interaction model:

- Users **cannot** arbitrarily tap - they navigate a highlight sequentially via directional swipes on Siri Remote
- When an element receives focus:
  - It **physically scales up**
  - It responds to micro-movements on the remote's trackpad via **parallax animations**
  - This spatial feedback communicates which item is active from across the room

### Design Requirements

- All interactive elements must have clear, visible focus states
- Scale and parallax on focus are **mandatory** for discoverability
- Navigation is via **top tab bars** (not bottom)
- Use TV-safe title areas (content within 90% of screen edges)
- Large, bold typography - must be readable from 8-12 feet

**Common tvOS audit violations:**
- Missing focus states on interactive elements
- No parallax effect on focused items
- Bottom tab bars (should be top)
- Small text unreadable from viewing distance
- Content outside TV-safe areas

---

## visionOS

**Context**: Spatial computing, limitless 3D canvas. Eye-tracking for targeting, hand gestures (pinch) for selection.

### Spatial Containers

| Type | Purpose |
|------|---------|
| **Windows** | Standard 2D glass panels floating in physical space |
| **Volumes** | 3D objects that can be walked around and inspected |
| **Full Spaces** | Replace the physical room entirely with virtual environment |

### Critical Ergonomic Rules

- **Never head-lock UI** - content rigidly following head movement causes severe motion sickness
- Windows must remain stationary in physical space - user turns head to look at different elements
- Content centered within natural field of view
- Avoid placing required UI where users must crane their necks

### Ornaments (Not Tab Bars)

- Traditional tab bars cause eye strain with eye-tracking input
- **Ornaments** sit outside the main window boundaries, floating slightly forward off the bottom edge
- Provide quick toolbar/navigation access without encroaching on content

### Gaze and Pinch Interaction

- Selection: look at element + pinch two fingers
- Human eye is less precise than mouse pointer, so:
  - Interactive targets need **massive padding and generous spacing**
  - Elements must react to gaze with **subtle brightening hover effect**
  - Hover effect confirms system recognizes user intent before the pinch

**Common visionOS audit violations:**
- Head-locked UI elements
- Traditional tab bars instead of Ornaments
- Insufficient spacing between interactive targets for eye-tracking
- No gaze hover effects on interactive elements
- Required UI outside comfortable field of view

---

## Cross-Platform Comparison

| Feature | iOS/iPadOS | macOS | watchOS | tvOS | visionOS |
|---------|-----------|-------|---------|------|----------|
| Primary Input | Multi-touch | Mouse, Trackpad, Keyboard | Touch, Digital Crown | Siri Remote | Eye Tracking, Hand Gestures |
| Viewing Distance | 1-2 feet | 2-3 feet | < 1 foot (in motion) | 8-12 feet | Immersive (infinite) |
| Primary Navigation | Bottom Tab Bars, Sidebars | Top Toolbars, Menu Bar | Vertical Pagination | Top Tab Bar | Floating Ornaments |
| Interaction Feedback | Haptics, Visual Highlights | Cursor changes, Hover states | Prominent Haptics | Scale and Parallax (Focus) | Gaze Hover, Audio |
| Layout Constraint | Safe Areas, Ergonomics | Flexible Windows | Edge-to-Edge Bezels | TV Title Safe Areas | Field of View, Neck Comfort |
| Background | Semantic system colors | Semantic system colors | Pure black (OLED blend) | Rich imagery | Transparent glass panels |
| Min Touch Target | 44x44pt | N/A (pointer precision) | Full width preferred | N/A (focus-based) | Extra-large with padding |
