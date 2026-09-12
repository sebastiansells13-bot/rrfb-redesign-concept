# Roadrunner Food Bank — Website Redesign Concept

A pitch-ready redesign concept for **[rrfb.org](https://www.rrfb.org)** (Roadrunner Food Bank of New Mexico). This is a static, dependency-free prototype meant to demonstrate direction — visual design, information architecture, and interactive touches — not a drop-in CMS replacement.

> **Not affiliated with Roadrunner Food Bank of New Mexico.** All copy is original and written for this concept; facts about the organization (founding year, service area, contact info) are public information used for illustration.

## Why a redesign

The current site (built on an older WordPress/Divi-style template) has real strengths — a clear mission and strong stats — but the experience works against them:

| Area | Current site | This concept |
|---|---|---|
| Hero contrast | Body copy sits in a dark-red-on-dark-red hero, hard to read at a glance | Warm maroon hero with white/gold text tuned for WCAG AA contrast |
| Navigation | Deep multi-level dropdowns (Give → Give Funds → Financial Securities → …) | Seven flat top-level sections; deep content lives one click down on its own page |
| Calls to action | Every section ends in a generic "LEARN MORE" | Specific, verb-led CTAs tied to the actual next step ("Find Food Near You", "Donate this amount") |
| Donation impact | Stated once in body copy ($1 → 5 meals) | An interactive calculator lets a visitor drag a slider and see meals in real time |
| Food finder | Buried under Find Help → Find Food | Surfaced on the homepage and given its own prominent section on Get Help |
| Mobile experience | Cramped nav, small tap targets | Full responsive rebuild — slide-in mobile nav, fluid type scale, tested at 375px width |
| Visual system | Stock template styling, inconsistent spacing | A defined design system: color tokens, type scale, consistent card/section rhythm (see `style-guide.html`) |
| Brand mark | The real roadrunner-with-a-corn-cob logo only appears as a static image | An original illustration inspired by the real mark — a small gold silhouette version in the nav/footer/favicon, and a full-color version as the homepage hero illustration and social-preview image |
| Accessibility | Low-contrast text, no skip link | Skip-to-content link, semantic landmarks, visible focus rings, reduced-motion support, WCAG AA target |
| Content/blog | News buried in a generic "Newsroom" | Dedicated News listing + article template, linked from nav and footer |
| SEO | No structured data or social preview cards seen | Open Graph/Twitter cards, JSON-LD Organization schema, sitemap, robots.txt on every page |
| Spam handling | Unknown | Honeypot field + render-timestamp check on every form, ready to wire to a real backend |

## What's included

- **13 pages**: Home, Our Story (About), Get Help, Ways to Give, Get Involved, News, a sample News article, Contact, Privacy Policy, Terms of Use, Accessibility Statement, a custom 404, and an internal Style Guide
- **Interactive prototypes** (front-end only, no backend):
  - Donation impact calculator (slider + presets → live meal count)
  - ZIP-code food finder demo
  - FAQ accordion
  - Mobile slide-in navigation
  - Animated stat counters on scroll
  - Contact/newsletter forms with demo confirmation states, protected by a honeypot field + timing check
- **Fully responsive**, mobile-first layout (tested at 375px, 768px, 1024px+)
- **SEO scaffolding**: per-page meta descriptions, Open Graph/Twitter cards, canonical links, JSON-LD Organization schema, `sitemap.xml`, `robots.txt`
- **Redirect map** (`_redirects` for Netlify, `.htaccess` for Apache) mapping the current rrfb.org URL structure to this one, so nothing 404s if this ever replaces the live site
- **Accessibility pass**: visible focus rings on every interactive element, `prefers-reduced-motion` support, semantic landmarks, ARIA on the accordion/mobile nav, and a dedicated Accessibility Statement page
- **No build step** — plain HTML/CSS/JS, opens directly in a browser or deploys as-is to GitHub Pages, Netlify, or any static host
- **No external dependencies** beyond Google Fonts (Fraunces + Work Sans)

## Structure

```
rrfb-redesign/
├── index.html            Home
├── about.html             Our Story — mission, history, Feeding America affiliation
├── get-help.html          Food-finder + assistance programs + FAQ
├── ways-to-give.html      Give funds/time/food + interactive impact calculator
├── get-involved.html      Volunteer shifts, advocacy, events
├── news.html              News & Updates listing
├── news-article.html      Sample article template
├── contact.html           Contact form + both office locations
├── privacy.html           Privacy Policy (template — needs legal review)
├── terms.html             Terms of Use (template — needs legal review)
├── accessibility.html     Accessibility Statement
├── 404.html               Custom not-found page
├── style-guide.html       Internal design-system reference (noindex, not in main nav)
├── sitemap.xml / robots.txt
├── _redirects / .htaccess Old-URL → new-URL redirect map (see file headers)
├── css/style.css          Design system + all page styles
├── js/main.js             Nav, counters, accordion, calculator, form demos, spam guard
├── assets/                favicon.svg, apple-touch-icon.png, og-image.jpg (roadrunner+corn mark)
├── scripts/apply_seo.py   One-time migration scripts that added SEO/meta and the new
└── scripts/apply_logo.py  brand mark to every page consistently — safe to delete,
                           kept for transparency
```

## Viewing it

Open `index.html` directly in a browser, or serve the folder locally:

```bash
python3 -m http.server 4173
```

Then visit `http://localhost:4173`.

## Before this goes anywhere real

A few placeholders are intentionally left for whoever deploys this for real:

- **Domain**: `BASE_URL`/canonical links/`sitemap.xml`/`robots.txt` all point to `https://example.com/rrfb-redesign` — swap in the real domain before launch.
- **Legal pages**: `privacy.html` and `terms.html` are solid starting templates, not finished legal documents — have an attorney confirm they match actual data practices.
- **Forms**: the contact and newsletter forms are demo-only (no backend). The honeypot + timing spam guard in `js/main.js` is written to run *before* a real submit — wire in Formspree, Netlify Forms, or a custom endpoint there.

## What this is / isn't

This is a **visual and UX pitch**, not a technical replacement for the live site. It doesn't include the real donation processor, partner-agency database, CMS, or a lawyer's sign-off on the legal pages — those would carry over from (or be re-integrated with) RRFB's existing systems. The goal here is to show what the same content could feel like with a modern, focused, accessible front end — and to get as much of the groundwork (SEO, accessibility, redirects, spam-resistant forms) actually done as can be, without needing access to RRFB's own accounts or data.
