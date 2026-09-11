#!/usr/bin/env python3
"""One-time migration script: injects SEO/meta/JSON-LD, nav/footer links,
and anti-spam fields into the existing static pages. Not part of the
runtime site — safe to delete after review. Run from the repo root:
    python3 scripts/apply_seo.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://example.com/rrfb-redesign"  # TODO: replace with the real deployed domain

PAGES = {
    "index.html": {
        "title": "Roadrunner Food Bank of New Mexico — Redesign Concept",
        "desc": "A pitch concept redesign of rrfb.org: ending hunger in New Mexico, together.",
        "path": "index.html",
    },
    "about.html": {
        "title": "Our Story — Roadrunner Food Bank Redesign Concept",
        "desc": "45+ years fighting hunger in New Mexico: mission, history, and statewide impact.",
        "path": "about.html",
    },
    "get-help.html": {
        "title": "Get Help — Roadrunner Food Bank Redesign Concept",
        "desc": "Find food assistance near you: pantries, mobile distributions, senior programs, and FAQs.",
        "path": "get-help.html",
    },
    "ways-to-give.html": {
        "title": "Ways to Give — Roadrunner Food Bank Redesign Concept",
        "desc": "Give funds, food, or time — and see your impact in meals.",
        "path": "ways-to-give.html",
    },
    "get-involved.html": {
        "title": "Get Involved — Roadrunner Food Bank Redesign Concept",
        "desc": "Volunteer shifts, advocacy, and events — ways to get hands-on in the fight against hunger.",
        "path": "get-involved.html",
    },
    "contact.html": {
        "title": "Contact Us — Roadrunner Food Bank Redesign Concept",
        "desc": "Reach the Albuquerque or Las Cruces offices, or send feedback.",
        "path": "contact.html",
    },
}

def jsonld_block():
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "NGO",
  "name": "Roadrunner Food Bank of New Mexico",
  "url": "{BASE_URL}/index.html",
  "logo": "{BASE_URL}/assets/apple-touch-icon.png",
  "description": "Roadrunner Food Bank of New Mexico is a Feeding America member food bank sourcing, warehousing, and distributing food statewide since 1979.",
  "address": [
    {{
      "@type": "PostalAddress",
      "streetAddress": "5840 Office Blvd NE",
      "addressLocality": "Albuquerque",
      "addressRegion": "NM",
      "postalCode": "87109",
      "addressCountry": "US"
    }},
    {{
      "@type": "PostalAddress",
      "streetAddress": "2100 N. Main, Suite 2",
      "addressLocality": "Las Cruces",
      "addressRegion": "NM",
      "postalCode": "88001",
      "addressCountry": "US"
    }}
  ],
  "telephone": "+1-505-247-2052",
  "email": "info@rrfb.org",
  "sameAs": [
    "https://www.facebook.com/roadrunner.food.bank/",
    "https://www.instagram.com/roadrunnerfoodbank/",
    "https://twitter.com/RoadrunnerFdBnk",
    "https://www.linkedin.com/company/roadrunner-food-bank-of-new-mexico/",
    "https://www.youtube.com/user/roadrunnerfoodbank"
  ]
}}
</script>
"""

def head_block(meta):
    url = f"{BASE_URL}/{meta['path']}"
    return f"""<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#6E1B26">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Roadrunner Food Bank of New Mexico">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['desc']}">
<meta property="og:image" content="{BASE_URL}/assets/og-image.jpg">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{meta['title']}">
<meta name="twitter:description" content="{meta['desc']}">
<meta name="twitter:image" content="{BASE_URL}/assets/og-image.jpg">
"""

HONEYPOT = """<div style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;" aria-hidden="true">
            <label for="{id}_website">Leave this field empty</label>
            <input type="text" id="{id}_website" name="website" tabindex="-1" autocomplete="off">
          </div>
          <input type="hidden" name="form_rendered_at" class="form-rendered-at" value="">
"""

def process(fname, meta):
    p = ROOT / fname
    html = p.read_text()
    orig = html

    # 1. Insert SEO head block right after the description meta tag
    desc_line = f'<meta name="description" content="{meta["desc"]}">'
    assert desc_line in html, f"description line not found in {fname}"
    html = html.replace(desc_line, desc_line + "\n" + head_block(meta).rstrip("\n"), 1)

    # 2. Insert JSON-LD right before </head>
    assert "</head>" in html
    html = html.replace("</head>", jsonld_block() + "</head>", 1)

    # 3. Add "News" to primary nav, right before the Contact link
    nav_contact_variants = [
        '      <a href="contact.html" aria-current="page">Contact</a>',
        '      <a href="contact.html">Contact</a>',
    ]
    inserted_nav = False
    for variant in nav_contact_variants:
        if variant in html:
            html = html.replace(variant, '      <a href="news.html">News</a>\n' + variant, 1)
            inserted_nav = True
            break
    assert inserted_nav, f"nav Contact link not found in {fname}"

    # 4. Add legal links to the footer Resources column (whitespace-tolerant)
    resources_re = re.compile(
        r'(<li><a href="contact\.html">Feedback Form</a></li>)(\s*)(</ul>)'
    )
    assert resources_re.search(html), f"footer resources anchor not found in {fname}"
    html = resources_re.sub(
        r'\1\2<li><a href="news.html">News &amp; Updates</a></li>\2\3', html, count=1
    )

    # 5. Add legal row to footer bottom
    footer_bottom_anchor = '<div class="footer-badges"><span class="badge">Feeding America Member</span><span class="badge">EIN available on request</span></div>'
    assert footer_bottom_anchor in html, f"footer bottom anchor not found in {fname}"
    legal_row = (
        '<div class="footer-badges">'
        '<a href="privacy.html" style="color:rgba(255,255,255,.6);">Privacy</a>'
        '<span aria-hidden="true"> · </span>'
        '<a href="terms.html" style="color:rgba(255,255,255,.6);">Terms</a>'
        '<span aria-hidden="true"> · </span>'
        '<a href="accessibility.html" style="color:rgba(255,255,255,.6);">Accessibility</a>'
        '</div>'
    )
    html = html.replace(footer_bottom_anchor, footer_bottom_anchor + "\n      " + legal_row, 1)

    # 6. Honeypot + timestamp fields on every data-demo-form (unique id per form on the page)
    counter = {"n": 0}
    base_id = fname.replace(".html", "")

    def add_honeypot(match):
        counter["n"] += 1
        fid = f"{base_id}-{counter['n']}"
        return match.group(0) + "\n          " + HONEYPOT.format(id=fid)

    html = re.sub(r'<form data-demo-form[^>]*>', add_honeypot, html)

    if html != orig:
        p.write_text(html)
        print(f"updated {fname}")
    else:
        print(f"NO CHANGE {fname}")

for fname, meta in PAGES.items():
    process(fname, meta)

print("done")
