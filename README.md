# Roadrunner Food Bank — Website Redesign Concept

A pitch-ready redesign concept for **[rrfb.org](https://www.rrfb.org)** (Roadrunner Food Bank of New Mexico). This is a static, dependency-free prototype meant to demonstrate direction — visual design, information architecture, and interactive touches — not a drop-in CMS replacement.

> **Not affiliated with Roadrunner Food Bank of New Mexico.** All copy is original and written for this concept; facts about the organization (founding year, service area, contact info) are public information used for illustration.

## Why a redesign

The current site (built on an older WordPress/Divi-style template) has real strengths — a clear mission and strong stats — but the experience works against them:

| Area | Current site | This concept |
|---|---|---|
| Hero contrast | Body copy sits in a dark-red-on-dark-red hero, hard to read at a glance | Warm maroon hero with white/gold text tuned for WCAG AA contrast |
| Navigation | Deep multi-level dropdowns (Give → Give Funds → Financial Securities → …) | Six flat top-level sections; deep content lives one click down on its own page |
| Calls to action | Every section ends in a generic "LEARN MORE" | Specific, verb-led CTAs tied to the actual next step ("Find Food Near You", "Donate this amount") |
| Donation impact | Stated once in body copy ($1 → 5 meals) | An interactive calculator lets a visitor drag a slider and see meals in real time |
| Food finder | Buried under Find Help → Find Food | Surfaced on the homepage and given its own prominent section on Get Help |
| Mobile experience | Cramped nav, small tap targets | Full responsive rebuild — slide-in mobile nav, fluid type scale, tested at 375px width |
| Visual system | Stock template styling, inconsistent spacing | A defined design system: color tokens, type scale, consistent card/section rhythm |
| Accessibility | Low-contrast text, no skip link | Skip-to-content link, semantic landmarks, focus states, accordion with proper ARIA |

## What's included

- **6 pages**: Home, Our Story (About), Get Help, Ways to Give, Get Involved, Contact
- **Interactive prototypes** (front-end only, no backend):
  - Donation impact calculator (slider + presets → live meal count)
  - ZIP-code food finder demo
  - FAQ accordion
  - Mobile slide-in navigation
  - Animated stat counters on scroll
  - Contact/newsletter forms with demo confirmation states
- **Fully responsive**, mobile-first layout (tested at 375px, 768px, 1024px+)
- **No build step** — plain HTML/CSS/JS, opens directly in a browser or deploys as-is to GitHub Pages, Netlify, or any static host
- **No external dependencies** beyond Google Fonts (Fraunces + Work Sans)

## Structure

```
rrfb-redesign/
├── index.html          Home
├── about.html           Our Story — mission, history, Feeding America affiliation
├── get-help.html        Food-finder + assistance programs + FAQ
├── ways-to-give.html    Give funds/time/food + interactive impact calculator
├── get-involved.html    Volunteer shifts, advocacy, events
├── contact.html         Contact form + both office locations
├── css/style.css        Design system + all page styles
└── js/main.js           Nav, counters, accordion, calculator, form demos
```

## Viewing it

Open `index.html` directly in a browser, or serve the folder locally:

```bash
python3 -m http.server 4173
```

Then visit `http://localhost:4173`.

## What this is / isn't

This is a **visual and UX pitch**, not a technical replacement for the live site. It doesn't include the real donation processor, partner-agency database, CMS, or accessibility/legal review a production relaunch would need — those would carry over from (or be re-integrated with) RRFB's existing systems. The goal here is to show what the same content could feel like with a modern, focused, accessible front end.
