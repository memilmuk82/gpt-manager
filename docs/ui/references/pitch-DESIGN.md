---
version: alpha
name: Pitch
description: "A presentation platform with a creative-professional canvas built around a near-black surface (#1A1A2E / #16213E) for the editor and clean white for slides and marketing. Pitch's brand uses a distinctive coral-salmon accent (#FF6B6B or brand-specific coral) with deep purples and a refined collaborative design aesthetic. The editor chrome is minimal dark, making the slide canvas the undisputed hero. Typography uses Inter or a geometric sans at clean weights, with generous whitespace and an art-director's eye for proportion. The system reads as 'presentation software for people who care about design.'"

colors:
  primary: "#5C33F6"
  on-primary: "#ffffff"
  primary-hover: "#4B29D4"
  secondary: "#FF6B6B"
  ink: "#1A1A2E"
  ink-muted: "#6E7191"
  canvas: "#ffffff"
  surface-1: "#F8F9FC"
  surface-2: "#EEF0F8"
  border: "#DDE2F0"
  editor-bg: "#16213E"
  editor-surface: "#1A2744"
  editor-border: "#283860"
  editor-ink: "#E8EAF6"

typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 52px
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: -0.03em
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: 0

spacing:
  base: 8px
  scale: [4, 8, 12, 16, 24, 32, 48, 64, 96]

radius:
  sm: 4px
  md: 8px
  lg: 16px
  pill: 9999px

shadows:
  card: "0 2px 8px rgba(26,26,46,0.08)"
  elevated: "0 8px 24px rgba(26,26,46,0.12)"
  editor-elevated: "0 4px 20px rgba(0,0,0,0.4)"

motion:
  duration-fast: 100ms
  duration-base: 200ms
  easing: cubic-bezier(0.4, 0, 0.2, 1)
---

## Rationale

**Deep navy editor (#16213E) as slide-forward design** — The dark editor chrome creates maximum contrast against the white slide canvas, making the slide the brightest and most attention-commanding element in the viewport. This isn't just aesthetics — it's a psychological priming that says "your slides are the star; the tool is the stage."

**Purple (#5C33F6) as creative-professional positioning** — Pitch competes with PowerPoint and Google Slides for design-conscious teams. The violet-blue primary communicates creative sophistication without the consumer associations of brighter hues. It sits in the same neighborhood as Linear, Notion, and other products that are winning design-literate B2B buyers.

**Live cursors as a product differentiator** — The decision to build simultaneous collaboration with per-collaborator cursor colors directly into the design system reflects Pitch's core bet: presentations are made collaboratively, not sequentially. The visual language of collaboration (cursor color palette, comment overlay system) is as important as the slide editing tools.

**Slide canvas as the only white surface** — Making the slide canvas white while surrounding it with dark or blue-gray chrome creates an "exhibit" framing — the slide is displayed like artwork in a gallery. This framing elevates what users are building from "a deck" to "a designed artifact," which is the positioning Pitch needs to command premium pricing.

**Template gallery as conversion surface** — Large, full-site previews in the template gallery function as persuasion: users see what their output can look like before they start working. This is a conversion optimization decision as much as a design choice — template browsing reduces time-to-first-beautiful-slide and increases trial conversion.

## 1. Visual Theme & Atmosphere
Pitch is the presentation tool for design-literate teams. The editor surfaces a dark, focused chrome that disappears behind the slide — a 1:1 reversal of PowerPoint's cluttered toolbar paradigm. The slide canvas is always the hero. Collaboration features (live cursors, comments, version history) are built in without disrupting the focus. The marketing site uses expressive, bold typography and rich template previews to demonstrate what's possible when presentation software gets out of your way.

## 2. Color System
**Editor (dark)**:
- Background: #16213E — deep navy-dark for long editing sessions
- Surface: #1A2744 — panel backgrounds within the editor
- Ink: #E8EAF6 — light lavender-white for text in dark context

**Marketing/Web (light)**:
- Canvas: white, surface layers in light blue-gray
- Primary: #5C33F6 — brand purple, primary CTAs
- Secondary: coral/salmon — template highlight accent

## 3. Typography
Inter at high contrast weights — display at 700 with very tight tracking (-0.03em). The presentation context demands type that works at 14px on a laptop and 100px projected on a conference room screen simultaneously. Pitch's built-in text styles accommodate this range.

## 4. Components & Patterns
- **Slide canvas**: Centered in editor, drop shadow against dark editor background, 16:9 ratio
- **Slide panel**: Left thumbnail strip showing all slides, drag to reorder
- **Template picker**: Gallery view, filterable by theme/industry, large previews
- **Collaboration bar**: Top-right live avatar cluster, cursor colors per collaborator
- **Comment overlay**: Pin comments directly on slide elements, thread conversations
- **Present mode**: Full-screen, presenter notes panel on secondary display

## 5. Spacing & Layout
Editor: slide panel left (200px) + canvas center (flex) + properties panel right (280px). All dark chrome. Marketing: 1200px max, feature sections alternating direction.

## 6. Motion & Interaction
Slide transitions (pitch uses smooth animated transitions). Live cursors move with CSS transitions. Template previews scale up on hover. Slide thumbnail drag uses spring physics. Present mode transitions configurable per-deck.

## Accessibility

### Contrast Ratios
- **Primary on background** (#5C33F6 on #ffffff): 6.4:1 — passes AA, fails AAA
- **Text on background** (#1A1A2E on #ffffff): 17.1:1 — passes AA, passes AAA
- **Muted on background** (#6E7191 on #ffffff): 4.7:1 — passes AA, fails AAA

### Minimum Requirements
- **Touch target**: 44×44px minimum for all interactive elements
- **Focus indicator**: #5C33F6 outline, 2px, 2px offset
- **Focus contrast**: 6.4:1 against #ffffff background

### Motion
- Respects `prefers-reduced-motion`: yes — all transitions and animations should be suppressed
- All transitions use `@media (prefers-reduced-motion: reduce)` guard

### Notes
- The purple primary (#5C33F6) is a strong 6.4:1 on white — comfortably passes AA and is safe for normal-weight interactive text; it still falls short of AAA (7:1), so prefer it for UI chrome rather than dense body reading text
- #6E7191 muted text sits at 4.7:1 on white — it clears AA but only just; avoid using it for text smaller than 14px bold or 18px regular
- In the dark editor (#16213E canvas), verify that editor-ink (#E8EAF6) and editor-primary usages are rechecked — the deep navy background differs significantly from the light marketing surface
- Secondary coral (#FF6B6B) is approximately 3.0:1 on white — decorative and large-text only; never use it for normal-weight label text without additional non-color differentiation
