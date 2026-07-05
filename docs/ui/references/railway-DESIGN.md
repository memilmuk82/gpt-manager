---
version: alpha
name: Railway
description: "A deployment platform with a dark, developer-native canvas (#0B0D0E near-black) and a distinctive brand palette that cycles through vivid pinks, purples, and the iconic Railway violet (#7C3AED / #A855F7) used on CTAs and deployment status indicators. The system reads as creative infrastructure — not as sterile DevOps but as deployment-as-craft. Typography uses a clean grotesque (Inter) with occasional expressive moments in heavier weights on marketing pages. The service graph visualization is Railway's signature UI: colorful service nodes connected by edges in a dark canvas, making infrastructure feel like a living system diagram."

colors:
  primary: "#A855F7"
  on-primary: "#ffffff"
  primary-hover: "#9333EA"
  secondary: "#EC4899"
  ink: "#E8E8E8"
  ink-muted: "#818181"
  canvas: "#0B0D0E"
  surface-1: "#131619"
  surface-2: "#1A1D21"
  border: "#272B2F"
  success: "#22C55E"
  danger: "#EF4444"
  warning: "#F59E0B"
  deploy-active: "#A855F7"
  service-pink: "#EC4899"
  service-blue: "#3B82F6"
  service-green: "#22C55E"

typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 52px
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: -0.03em
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: 0

spacing:
  base: 8px
  scale: [4, 8, 12, 16, 24, 32, 48, 64, 96]

radius:
  sm: 4px
  md: 8px
  lg: 12px
  pill: 9999px

shadows:
  card: "0 1px 4px rgba(0,0,0,0.4)"
  elevated: "0 4px 20px rgba(0,0,0,0.5)"
  glow: "0 0 20px rgba(168,85,247,0.2)"

motion:
  duration-fast: 100ms
  duration-base: 200ms
  easing: cubic-bezier(0.16, 1, 0.3, 1)
---

## Rationale

**Purple as deployment-as-craft identity** — #A855F7 positions Railway in the creative-developer space rather than the enterprise DevOps space. Purple communicates creativity and passion — appropriate for a platform targeting developers who care about their infrastructure as much as their code. It differentiates from AWS orange, GCP blue, and Azure blue while signaling "this is a product made by people who care about design."

**Service graph as emotional centerpiece** — The canvas-based node diagram with colored service nodes is Railway's most important design decision. It makes invisible infrastructure (containers, networks, databases) spatial and tangible. When developers can see their entire application as a living diagram, they develop attachment to the infrastructure they've built — which is Railway's most powerful retention mechanism.

**Multi-color service nodes as identity** — Assigning purple, pink, blue, and green to different service types isn't decoration — it's a navigation system. When a deployment graph has 20+ services, color is the fastest distinguishing signal. The palette also communicates energy and variety, reinforcing the "deployment is craft" brand message.

**Near-true-black (#0B0D0E) as the darkest developer canvas** — Railway goes darker than most dark-mode products, which creates stronger contrast for the colorful service nodes and deployment status indicators. It also communicates premium seriousness — this is a product that takes deployment as seriously as its users do.

**Purple glow on deploy button** — The `0 0 20px rgba(168,85,247,0.2)` box shadow on the active deploy button is a signature detail that makes deployment feel significant. The glow transforms a routine action (clicking "Deploy") into a moment with weight — reinforcing that shipping code is worth celebrating.

## 1. Visual Theme & Atmosphere
Railway is the deployment platform that made infrastructure feel fun. The dark canvas (#0B0D0E) grounds a playful palette of purples, pinks, and greens that appear on service nodes in the project graph. The signature visual is the canvas-based service graph: a spatial, node-and-edge diagram of your entire infrastructure that makes deployments feel tangible and alive. Marketing embraces a "we're different from AWS" energy — bold type, vivid gradients, dark surfaces.

## 2. Color System
- **Canvas**: #0B0D0E — near-true black, darker than most dark themes
- **Purple primary**: #A855F7 — Railway's brand purple, deploy button, active states
- **Pink secondary**: #EC4899 — secondary service nodes, gradient partner
- **Surfaces**: #131619 / #1A1D21 — subtle layering in the dark environment
- **Service node colors**: Purple, pink, blue, green assigned per-service to aid identification
- **Semantic**: Green #22C55E (deploy success), Red #EF4444 (failure), Amber #F59E0B (building)
- **Glow**: Purple glow shadow on active deploy button — a signature detail

## 3. Typography
Inter at 800 weight for display — very bold, very tight (-0.03em). The marketing hero headlines are some of the most aggressively tracked in developer tooling. Product UI uses 400/14px — small and dense for infrastructure dashboards. The contrast between heavy marketing type and light product type is intentional.

## 4. Components & Patterns
- **Service graph**: Canvas-based node diagram, drag-to-reposition, edge connections, deploy status as node border color
- **Deploy logs**: Real-time streaming terminal output, monospace, in dark panel
- **Environment variables**: Key-value pairs in dark panel, reveal/hide toggle
- **Metrics graphs**: Spark-line style CPU/memory charts in dark tiles
- **Deploy button**: Purple, full-width within service card, with glow on active
- **Status indicators**: Small colored dots — green/yellow/red — always visible on service nodes

## 5. Spacing & Layout
Project canvas: infinite canvas, no fixed grid. Sidebar: 240px fixed, service list. Settings: centered content area, max 800px. Dense UI — most panels use 12–16px padding.

## 6. Motion & Interaction
Service graph nodes drag with spring physics. Deploy log streams in real-time with smooth scroll-to-bottom. Build progress shows animated percentage. Node status transitions animate with color fade. The canvas pans and zooms smoothly.

## Accessibility

### Contrast Ratios
- **Primary on background** (#A855F7 on #0B0D0E): 4.9:1 — passes AA, fails AAA
- **Text on background** (#E8E8E8 on #0B0D0E): 15.9:1 — passes AA, passes AAA
- **Muted on background** (#818181 on #0B0D0E): 5.0:1 — passes AA, fails AAA

### Minimum Requirements
- **Touch target**: 44×44px minimum for all interactive elements
- **Focus indicator**: #A855F7 outline, 2px, 2px offset
- **Focus contrast**: 4.9:1 against #0B0D0E background

### Motion
- Respects `prefers-reduced-motion`: yes — all transitions and animations should be suppressed
- All transitions use `@media (prefers-reduced-motion: reduce)` guard

### Notes
- The purple primary (#A855F7) passes AA at 4.9:1 on the near-black canvas but does not reach AAA; restrict to interactive elements (buttons, links, deploy indicators) rather than dense informational text
- The service graph relies on color alone to distinguish service node types (purple, pink, blue, green); always pair node color with a visible text label or icon to satisfy WCAG 1.4.1 (use of color)
- Semantic status colors (success green #22C55E, danger red #EF4444, warning amber #F59E0B) must not convey deploy status through color alone — pair with a text label or icon in the node or log stream
- The spring-physics canvas pan/zoom and node-drag animations should be disabled or replaced with instant positioning under `prefers-reduced-motion: reduce`
