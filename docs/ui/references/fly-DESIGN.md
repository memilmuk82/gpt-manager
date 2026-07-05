---
version: alpha
name: Fly.io
description: "A developer deployment platform with a distinctive dark canvas (#1A1A2E deep navy-dark) and Fly's signature brand palette that moves through electric purple (#7C3AED), hot pink, and neon green — a bold, playful combination that positions Fly as the anti-corporate cloud. The marketing site uses expressive illustrations of servers and global networks with a graphic novel aesthetic. The dashboard is more functional — dark surfaces, CLI-first philosophy, and a global deployment map showing where your machines are running. Typography uses Inter at developer-comfortable sizes. The brand communicates: we're nerds who love Elixir and distributed systems, and so are you."

colors:
  primary: "#7C3AED"
  on-primary: "#ffffff"
  primary-hover: "#6D28D9"
  secondary: "#F0047F"
  accent-green: "#00FF85"
  ink: "#E4E4E7"
  ink-muted: "#71717A"
  canvas: "#1A1A2E"
  surface-1: "#212140"
  surface-2: "#292950"
  border: "#383860"
  machine-running: "#00FF85"
  machine-stopped: "#EF4444"
  machine-starting: "#F59E0B"
  region-active: "#7C3AED"

typography:
  display:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 48px
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: -0.03em
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
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
  card: "0 2px 8px rgba(0,0,0,0.4)"
  elevated: "0 4px 24px rgba(0,0,0,0.5)"

motion:
  duration-fast: 100ms
  duration-base: 200ms
  easing: cubic-bezier(0.16, 1, 0.3, 1)
---

## Rationale

**Purple/pink/neon anti-corporate palette** — The vibrant #7C3AED / #F0047F / #00FF85 combination is a deliberate rejection of the enterprise AWS color vocabulary (orange/white) and the generic Heroku purple. For a platform trying to win developers who are bored with their current cloud provider, looking like a new thing is strategically important.

**Deep navy canvas (#1A1A2E) instead of pure black** — The slight blue tint in the dark surface communicates "distributed systems in the ether" rather than just "dark mode." It's a subtle visual reference to nighttime, the sea, and distributed global infrastructure — the brand's conceptual territory.

**World map as the signature product visual** — Making global deployment geography the hero UI element is a product positioning statement: Fly is about running things close to users everywhere, not just in us-east-1. The map makes infrastructure feel spatial and exciting rather than abstract and bureaucratic.

**CLI-first philosophy expressed in empty states** — Prominently showing `fly launch` commands in empty states rather than onboarding wizards is a cultural signal: this product respects developer intelligence. It says "you're the kind of person who uses a terminal" and attracts the specific developer identity Fly is optimizing for.

**800-weight display with 14px body** — The dramatic contrast between ultra-bold marketing headlines and small functional product type reflects two different audiences: the marketing site converts skeptical developers who need to feel the energy, while the dashboard serves users who've already committed and need information density.

## 1. Visual Theme & Atmosphere
Fly.io is the platform for developers who've outgrown Heroku and don't want AWS complexity. The brand identity is unusual for infrastructure: playful, nerdy, opinionated. The purple/pink/green palette is vibrant in marketing contexts and used more subtly in the product dashboard. The world map showing your deployed machines is the signature product visual — green dots across global regions, each one a running machine. The philosophy is fly.toml and a CLI first, dashboard second.

## 2. Color System
**Dark marketing**:
- Canvas: #1A1A2E — deep navy, darker and warmer than pure black
- Purple: #7C3AED — primary brand, buttons, active states
- Hot pink: #F0047F — secondary accent, gradient partner, highlights
- Neon green: #00FF85 — machine running status, healthy indicators, success

**Dashboard**:
- Same dark canvas, surface layers shift navy-dark
- Machine status: green (running), red (stopped), amber (starting/stopping)
- Region dots: purple for your regions, gray for available regions

## 3. Typography
Inter at 800 for display marketing copy — aggressive weight matching the brand energy. Dashboard uses 400/14px for functional density. CLI output is always monospaced. Documentation favors code examples prominently.

## 4. Components & Patterns
- **World map**: SVG global projection, dots for available regions, colored for your deployments
- **Machine list**: Machine name, region flag, status dot, CPU/memory bar, age
- **App card**: App name, machine count, volume, last deployed
- **Logs panel**: Real-time streaming terminal output, dark with colored log levels
- **Deployment status**: Purple progress bar with stage labels (building / deploying / healthy)
- **flyctl commands**: Prominently shown on empty states — "fly launch" to start

## 5. Spacing & Layout
Dashboard: 220px sidebar, content max 1200px. World map: full-width panel at 300px height. Machine list: table layout with 8px row padding. Marketing: 1280px max, sections use generous 96px+ vertical padding.

## 6. Motion & Interaction
World map dots pulse on region with active deployment. Machine status changes animate the status dot color. Deployment log streams in real-time. The map can zoom to a specific region on click. Active machine count increments with a number animation.

## Accessibility

### Contrast Ratios
- **Primary on background** (#7C3AED on #1A1A2E): 3.0:1 — passes AA (large text/UI components), fails AAA
- **Text on background** (#E4E4E7 on #1A1A2E): 13.4:1 — passes AA, passes AAA
- **Muted on background** (#71717A on #1A1A2E): 3.5:1 — passes AA (large text/UI components), fails AAA

### Minimum Requirements
- **Touch target**: 44×44px minimum for all interactive elements
- **Focus indicator**: #7C3AED outline, 2px, 2px offset
- **Focus contrast**: 3.0:1 against #1A1A2E background

### Motion
- Respects `prefers-reduced-motion`: yes — all transitions and animations should be suppressed
- All transitions use `@media (prefers-reduced-motion: reduce)` guard

### Notes
- The electric purple #7C3AED at 3.0:1 on the dark navy canvas barely clears the 3:1 threshold for large text and UI components but fails for normal-weight body text (4.5:1 required); restrict it to interactive elements, large headings, and borders.
- Muted #71717A at 3.5:1 on the dark canvas fails AA for normal text too — avoid using it for informational text; reserve it for decorative dividers or secondary icons only.
- World map pulsing dots and machine-status color-transition animations should be suppressed under `prefers-reduced-motion`; use a static colored dot with a visible label instead.
- The neon green accent #00FF85 (if used as text) on the dark canvas should be verified — it provides very high contrast but can cause halation issues for users with certain visual sensitivities; pair with sufficient surrounding whitespace.
