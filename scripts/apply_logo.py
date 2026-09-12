#!/usr/bin/env python3
"""One-time migration: swaps the abstract brand-mark SVG for a more literal
roadrunner-carrying-a-corn-cob silhouette (a nod to RRFB's real logo), in
both its header and footer sizing/positions, across every page.
Safe to delete after review. Run from the repo root: python3 scripts/apply_logo.py
"""
from pathlib import Path
import glob
import re

ROOT = Path(__file__).resolve().parent.parent

BIRD_INNER = """<g transform="translate(8,10) scale(0.315)">
{i2}<g stroke="#3F0F16" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none">
{i3}<path d="M42,60 L37,78 M37,78 L31,80 M37,78 L41,83"/>
{i3}<path d="M54,61 L58,79 M58,79 L64,80 M58,79 L54,84"/>
{i2}</g>
{i2}<path d="M66,36 C82,26 98,12 108,2 C100,18 88,32 74,42 Z" fill="#E29A2E"/>
{i2}<path d="M68,43 C86,36 102,28 111,22 C101,36 88,46 74,50 Z" fill="#E29A2E"/>
{i2}<path d="M67,49 C82,49 96,50 106,53 C93,59 79,60 68,55 Z" fill="#E29A2E"/>
{i2}<path d="M13,44 C9,31 20,20 36,19 C49,18 60,23 64,32 C69,31 74,33 76,38 C79,44 76,50 69,52 C58,57 46,59 35,58 C22,57 15,53 13,44 Z" fill="#E29A2E"/>
{i2}<path d="M16,40 C10,38 5,34 2,29 C8,30 14,32 19,36 Z" fill="#E29A2E"/>
{i2}<circle cx="15" cy="34" r="7.5" fill="#E29A2E"/>
{i2}<path d="M9,32 L-8,26 L11,40 Z" fill="#3F0F16"/>
{i1}</g>"""

NEW_HEADER = """      <svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="24" fill="#6E1B26"/>
        {bird}
      </svg>""".format(bird=BIRD_INNER.format(i1="        ", i2="          ", i3="            "))

NEW_FOOTER = """          <svg class="brand-mark" width="36" height="36" viewBox="0 0 48 48" aria-hidden="true">
            <circle cx="24" cy="24" r="24" fill="#8A2432"/>
            {bird}
          </svg>""".format(bird=BIRD_INNER.format(i1="            ", i2="              ", i3="                "))

# Whitespace-tolerant patterns (some pages have the old mark on one line,
# others spread across several) — each literal fragment is escaped, joined
# by \s* so formatting differences don't matter.
def ws_pattern(*fragments):
    return re.compile(r"\s*".join(re.escape(f) for f in fragments), re.DOTALL)

OLD_HEADER_RE = ws_pattern(
    '<svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true">',
    '<circle cx="24" cy="24" r="24" fill="#6E1B26"/>',
    '<path d="M9 31c4.5-1 7.6-4 8.8-8.4 1 3.2 3.1 5.4 6.4 6.4l9.8-10.6-3.2 9.6c3.2 0 6.4-1.1 8.6-3.2-2.1 5.3-6.4 8.5-11.7 8.5-2.2 3.1-5.3 5-8.7 5-3.1-4.1-6.3-5.3-10-6.3z" fill="#E29A2E"/>',
    '<circle cx="34" cy="16.5" r="2.1" fill="#3F0F16"/>',
    "</svg>",
)

OLD_FOOTER_RE = ws_pattern(
    '<svg class="brand-mark" width="36" height="36" viewBox="0 0 48 48" aria-hidden="true">',
    '<circle cx="24" cy="24" r="24" fill="#8A2432"/>',
    '<path d="M9 31c4.5-1 7.6-4 8.8-8.4 1 3.2 3.1 5.4 6.4 6.4l9.8-10.6-3.2 9.6c3.2 0 6.4-1.1 8.6-3.2-2.1 5.3-6.4 8.5-11.7 8.5-2.2 3.1-5.3 5-8.7 5-3.1-4.1-6.3-5.3-10-6.3z" fill="#E29A2E"/>',
    "</svg>",
)

changed = {"header": 0, "footer": 0}
for path in sorted(glob.glob(str(ROOT / "*.html"))):
    s = open(path).read()
    orig = s
    s, n = OLD_HEADER_RE.subn(NEW_HEADER.replace("\\", "\\\\"), s, count=1)
    changed["header"] += n
    s, n = OLD_FOOTER_RE.subn(NEW_FOOTER.replace("\\", "\\\\"), s, count=1)
    changed["footer"] += n
    if s != orig:
        open(path, "w").write(s)
        print(f"updated {Path(path).name}")

print(changed)
