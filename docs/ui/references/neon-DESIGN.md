---
version: alpha
name: Neon
description: "A serverless Postgres platform with a striking dark canvas (#0E0E0E / #111111) and Neon's signature bright green (#00E599) — the same green as a terminal cursor blinking in a dark room — used on the logo, primary CTAs, branch indicators, and compute status. The interface reads as developer-native and technically opinionated: branch-based workflows, instant database provisioning, and scale-to-zero compute visualized in a clean dark dashboard. Typography uses Inter at functional sizes. The system aesthetic is minimal-dark-technical with a single electric green accent that communicates instant-on energy and serverless simplicity."

colors:
  primary: "#00E599"
  on-primary: "#0E0E0E"
  primary-hover: "#00CC88"
  ink: "#EDEDED"
  ink-muted: "#777777"
  canvas: "#0E0E0E"
  surface-1: "#171717"
  surface-2: "#1F1F1F"
  border: "#2A2A2A"
  branch-active: "#00E599"
  branch-inactive: "#555555"
  compute-running: "#00E599"
  compute-idle: "#555555"
  success: "#00E599"
  danger: "#EF4444"

typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.025em
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  code:
    fontFamily: "JetBrains Mono, Fira Code, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5

spacing:
  base: 8px
  scale: [4, 8, 12, 16, 24, 32, 48, 64, 96]

radius:
  sm: 4px
  md: 6px
  lg: 12px
  pill: 9999px

shadows:
  card: "0 1px 4px rgba(0,0,0,0.5)"
  elevated: "0 4px 20px rgba(0,0,0,0.6)"
  glow: "0 0 24px rgba(0,229,153,0.15)"

motion:
  duration-fast: 100ms
  duration-base: 200ms
  easing: cubic-bezier(0.16, 1, 0.3, 1)
---

## Rationale

**Terminal green on near-black as developer nativity** — #00E599 on #0E0E0E is a direct visual callback to the CRT terminal — the environment where Postgres was born and where its users still feel most at home. It's a cultural alignment that says "we understand your context" without requiring any explanatory text.

**Near-black instead of pure black** — Starting at #0E0E0E rather than #000000 allows three distinct dark surface levels (#171717 / #1F1F1F) to be legible without needing color. On a pure black base, subtle gray differentiation becomes invisible on glossy monitors; the slight elevation gives the surface system room to breathe.

**Single-color semantic system** — Using the same neon green (#00E599) for success states, running compute, active branches, and primary CTAs creates a coherent vocabulary: green means "alive and working." This consolidation reduces the number of color meanings users need to learn in an already technically dense product.

**Git-branching metaphor as the core interaction model** — Structuring database operations around branches (inspired by Git) is a product philosophy that the visual design must reinforce. The branch tree visualization with green active nodes makes the metaphor tangible — users who understand Git immediately understand Neon's branching model from the diagram alone.

**JetBrains Mono for code surfaces** — Using JetBrains Mono rather than the more common Fira Code or Consolas is a developer cultural signal: JetBrains Mono was designed specifically for long coding sessions with ligature support optimized for database query syntax. It communicates that Neon understands the SQL workflow, not just the connection string.

## 1. Visual Theme & Atmosphere
Neon built serverless Postgres for the edge computing era, and the design reflects that technical identity. The near-black canvas is a deliberate nod to terminal tradition — developers recognize this as their native environment. The green (#00E599) is electric and precise: it's the color of "online," "connected," and "ready." Branch-based database workflows (inspired by Git branching) are the product's core differentiator, visualized as a simple tree diagram with green active nodes. The platform is minimal because Postgres doesn't need decoration.

## 2. Color System
- **Canvas**: #0E0E0E — as close to true black as you can get while allowing surface layering
- **Neon green**: #00E599 — the single chromatic point; compute running, branch active, primary CTA, logo
- **Surfaces**: #171717 / #1F1F1F — subtle dark layering for panels and cards
- **Ink**: #EDEDED — near-white, warm enough to not cause contrast fatigue
- **Muted**: #777777 — neutral gray for secondary metadata
- **Glow**: Green box-shadow on active elements — subtle but distinctive

## 3. Typography
Inter throughout — the technical world has standardized here, and Neon follows suit. 14px body for density in connection strings and configuration. Code and SQL use JetBrains Mono. Connection string display is always monospaced and selectable. Display headings use 700/48px with -0.025em tracking.

## 4. Components & Patterns
- **Branch tree**: Visual hierarchy of database branches — main + feature branches, with green active indicators
- **Compute indicator**: "Running" (green dot) / "Idle" (gray dot) — the core serverless status
- **Connection string**: Prominent display, one-click copy, syntax-highlighted
- **SQL editor**: Dark Monaco editor, Postgres syntax highlighting, query results table below
- **Storage/Compute metrics**: Simple charts, green accent line
- **Project card**: Branch count, compute status, region, created date

## 5. Spacing & Layout
Dashboard: 220px sidebar, content max 1100px. SQL editor: split pane (editor top, results bottom), resizable. Branch tree: compact tree layout with 8px spacing between nodes. Clean, minimal spacing throughout.

## 6. Motion & Interaction
Compute "waking up" has a subtle green pulse animation. Branch creation slides into the tree. SQL queries show a progress bar then snap to results. Connection string copy shows a brief checkmark. Compute scale-to-zero shows an idle fade.

## Accessibility

### Contrast Ratios
- **Primary on background** (#00E599 on #0E0E0E): 11.6:1 — passes AA, passes AAA
- **Text on background** (#EDEDED on #0E0E0E): 16.5:1 — passes AA, passes AAA
- **Muted on background** (#777777 on #0E0E0E): 4.3:1 — fails AA

### Minimum Requirements
- **Touch target**: 44×44px minimum for all interactive elements
- **Focus indicator**: #00E599 outline, 2px, 2px offset
- **Focus contrast**: 11.6:1 against #0E0E0E background

### Motion
- Respects `prefers-reduced-motion`: yes — all transitions and animations should be suppressed
- All transitions use `@media (prefers-reduced-motion: reduce)` guard

### Notes
- The neon green #00E599 achieves an outstanding 11.6:1 on near-black, easily clearing AAA — it is safe for all text sizes and weights on the dark canvas.
- Muted text #777777 at 4.3:1 falls just below the 4.5:1 AA threshold for normal text on the dark canvas — it must not be used for informational body copy; lighten to at least #7E7E7E (≈4.5:1) or restrict to decorative and large-text contexts.
- The compute "waking up" green pulse animation and branch-creation slide animation should be suppressed under `prefers-reduced-motion`; show a static green status indicator instead.
- High-luminance neon green on near-black creates significant halation for some users with low vision or astigmatism; provide sufficient spacing around green text elements and avoid tight green text on black at small sizes.
