#!/usr/bin/env python3
"""Spanish-toggle tooling for the static pages (no dependencies).

    python3 scripts/i18n.py scan       # list translatable text not yet tagged
    python3 scripts/i18n.py annotate   # tag it with data-i18n / data-i18n-html
    python3 scripts/i18n.py check      # fail if anything is untagged/untranslated

`check` is the one to run after editing copy: it reports every piece of
visible text (and every placeholder / aria-label / title / alt) that isn't
tagged, every tagged key missing a Spanish string in js/i18n-data.js, and
every key whose English in the page no longer matches the dictionary (i.e.
the copy changed and the Spanish is now stale).

Tagging rules (see the header of js/i18n.js for the runtime side):
  - An element whose only content is text gets data-i18n="key".
  - An element mixing text with inline tags (<a>, <strong>, <br>, ...) gets
    data-i18n-html="key"; its dictionary entry holds the full inner HTML.
  - Attributes get data-i18n-attr="placeholder:key;aria-label:key".
  - data-i18n-skip on an element excludes it and its subtree (proper nouns,
    addresses, phone numbers, the internal style guide).
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "js" / "i18n-data.js"
# style-guide.html is an internal design reference (noindex, not in the nav),
# so it's deliberately left English-only.
PAGES = [
    "index.html", "about.html", "get-help.html", "ways-to-give.html",
    "get-involved.html", "news.html", "news-article.html", "contact.html",
    "privacy.html", "terms.html", "accessibility.html", "404.html",
]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
INLINE = {"a", "strong", "em", "b", "i", "span", "br", "small", "abbr", "code",
          "time", "mark", "sup", "sub", "u", "q", "cite"}
OPAQUE = {"script", "style", "svg", "template", "noscript"}
ATTRS = ["placeholder", "aria-label", "title", "alt"]
HAS_WORD = re.compile(r"[A-Za-z]{2,}")


class Node:
    def __init__(self, tag, attrs, start, raw, parent):
        self.tag, self.attrs, self.start, self.raw, self.parent = tag, dict(attrs), start, raw, parent
        self.children = []  # Node or str
        self.inner_start = start + len(raw)
        self.inner_end = None


class TreeBuilder(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_offsets = [0]
        for line in src.splitlines(keepends=True):
            self.line_offsets.append(self.line_offsets[-1] + len(line))
        self.root = Node("#root", [], 0, "", None)
        self.cur = self.root

    def abs_pos(self):
        line, col = self.getpos()
        return self.line_offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.abs_pos(), self.get_starttag_text(), self.cur)
        self.cur.children.append(node)
        if tag in VOID:
            node.inner_end = node.inner_start
        else:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, attrs, self.abs_pos(), self.get_starttag_text(), self.cur)
        node.inner_end = node.inner_start
        self.cur.children.append(node)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            return
        # close any unclosed descendants too
        end = self.abs_pos()
        c = self.cur
        while c is not n:
            c.inner_end = end
            c = c.parent
        n.inner_end = end
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)

    def handle_entityref(self, name):
        self.cur.children.append("&%s;" % name)

    def handle_charref(self, name):
        self.cur.children.append("&#%s;" % name)


def parse(src):
    b = TreeBuilder(src)
    b.feed(src)
    b.close()
    return b.root


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def text_of(node):
    out = []
    for c in node.children:
        out.append(c if isinstance(c, str) else ("" if c.tag in OPAQUE else text_of(c)))
    return "".join(out)


def has_words(s):
    return bool(HAS_WORD.search(html.unescape(s)))


def direct_text(node):
    return "".join(c for c in node.children if isinstance(c, str))


def phrasing_only(node):
    for c in node.children:
        if isinstance(c, Node):
            if c.tag not in INLINE or not phrasing_only(c):
                return False
    return True


def tagged(node):
    return any(k in node.attrs for k in ("data-i18n", "data-i18n-html"))


def skipped(node):
    return "data-i18n-skip" in node.attrs or node.tag in OPAQUE


def find_units(node, units, orphans):
    """Collect the elements that should carry a translation key."""
    for c in node.children:
        if not isinstance(c, Node) or skipped(c):
            continue
        if tagged(c):
            units.append(c)
            continue
        if not has_words(text_of(c)):
            continue
        has_direct = has_words(direct_text(c))
        if has_direct and phrasing_only(c):
            units.append(c)
        elif has_direct:
            orphans.append(c)
            find_units(c, units, orphans)
        else:
            find_units(c, units, orphans)


def attr_units(node, out):
    for c in node.children:
        if not isinstance(c, Node) or "data-i18n-skip" in c.attrs:
            continue
        done = dict(p.split(":", 1) for p in c.attrs.get("data-i18n-attr", "").split(";") if ":" in p)
        for a in ATTRS:
            v = c.attrs.get(a)
            if v and has_words(v) and a not in done:
                out.append((c, a, v))
        if c.tag not in OPAQUE:
            attr_units(c, out)


def unit_mode(node):
    return "text" if all(isinstance(c, str) for c in node.children) else "html"


def unit_en(src, node):
    inner = src[node.inner_start:node.inner_end]
    return norm(inner) if unit_mode(node) == "html" else norm(html.unescape(inner))


def slug(s, words=5):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).split()
    return "-".join(s[:words]) or "text"


def load_dict():
    if not DATA_FILE.exists():
        return {}
    raw = DATA_FILE.read_text()
    body = raw[raw.index("{"): raw.rindex("}") + 1]
    return json.loads(body)


def write_dict(d):
    header = (
        "// Spanish dictionary for the EN/ES toggle. Generated and checked by\n"
        "// scripts/i18n.py — each key's \"en\" must match the page copy it came\n"
        "// from (run `python3 scripts/i18n.py check` after editing copy).\n"
        "// Keys under \"common.\" are shared by every page (header, footer, etc.).\n"
    )
    DATA_FILE.write_text(header + "window.I18N_DATA = " + json.dumps(d, ensure_ascii=False, indent=2) + ";\n")


def page_prefix(page):
    return "p404" if page == "404.html" else page[:-5]


def collect():
    """Return {page: (src, root, units, orphans, attr_units)}."""
    res = {}
    for page in PAGES:
        src = (ROOT / page).read_text()
        root = parse(src)
        units, orphans, attrs = [], [], []
        find_units(root, units, orphans)
        attr_units(root, attrs)
        res[page] = (src, root, units, orphans, attrs)
    return res


def cmd_scan():
    for page, (src, root, units, orphans, attrs) in collect().items():
        todo = [u for u in units if not tagged(u)]
        print("== %s: %d untagged units, %d attrs, %d orphans" % (page, len(todo), len(attrs), len(orphans)))
        for u in todo:
            print("  [%s %s] %s" % (u.tag, unit_mode(u), unit_en(src, u)[:110]))
        for n, a, v in attrs:
            print("  [@%s on %s] %s" % (a, n.tag, v))
        for o in orphans:
            print("  [ORPHAN %s] %s" % (o.tag, norm(direct_text(o))[:80]))


def cmd_annotate():
    data = collect()
    d = load_dict()
    # English strings used on 2+ pages share one "common." key.
    seen = {}
    for page, (src, _, units, _, attrs) in data.items():
        for u in units:
            if not tagged(u):
                seen.setdefault((unit_mode(u), unit_en(src, u)), set()).add(page)
        for n, a, v in attrs:
            seen.setdefault(("attr", norm(v)), set()).add(page)
    by_en = {}  # (mode, en) -> key, reusing existing keys
    for k, v in d.items():
        by_en.setdefault((v.get("mode", "text"), v["en"]), k)

    def key_for(page, mode, en):
        if (mode, en) in by_en:
            return by_en[(mode, en)]
        prefix = "common" if len(seen.get((mode, en), ())) > 1 else page_prefix(page)
        base = "%s.%s" % (prefix, slug(en))
        k, i = base, 2
        while k in d:
            k, i = "%s-%d" % (base, i), i + 1
        d[k] = {"en": en, "es": ""}
        if mode != "text":
            d[k]["mode"] = mode
        by_en[(mode, en)] = k
        return k

    def rewrite(page, src, edits):
        """edits: {start offset: (raw start tag, new start tag)}"""
        out, pos = [], 0
        for start in sorted(edits):
            raw, new = edits[start]
            assert src.startswith(raw, start), (page, raw)
            out += [src[pos:start], new]
            pos = start + len(raw)
        out.append(src[pos:])
        (ROOT / page).write_text("".join(out))

    def add_attr(raw, attr):
        close = "/>" if raw.endswith("/>") else ">"
        return raw[: -len(close)].rstrip() + " " + attr + close

    # Pass 1: attributes (done first so pass 2 records final inner HTML).
    for page, (src, _, _, _, attrs) in data.items():
        specs = {}
        for n, a, v in attrs:
            specs.setdefault(n.start, [n, n.attrs.get("data-i18n-attr", "")])
            spec = specs[n.start][1]
            specs[n.start][1] = (spec + ";" if spec else "") + "%s:%s" % (a, key_for(page, "attr", norm(v)))
        edits = {}
        for start, (n, spec) in specs.items():
            if "data-i18n-attr=" in n.raw:
                new = re.sub(r'data-i18n-attr="[^"]*"', 'data-i18n-attr="%s"' % spec, n.raw)
            else:
                new = add_attr(n.raw, 'data-i18n-attr="%s"' % spec)
            edits[start] = (n.raw, new)
        rewrite(page, src, edits)

    # Pass 2: text / inner-HTML units.
    for page, (src, _, units, _, _) in collect().items():
        edits = {}
        for u in units:
            if tagged(u):
                continue
            mode = unit_mode(u)
            k = key_for(page, mode, unit_en(src, u))
            attr = "data-i18n" if mode == "text" else "data-i18n-html"
            edits[u.start] = (u.raw, add_attr(u.raw, '%s="%s"' % (attr, k)))
        rewrite(page, src, edits)
    write_dict(d)
    print("annotated; dictionary now has %d keys (%d missing Spanish)" % (
        len(d), sum(1 for v in d.values() if not v.get("es"))))


def cmd_check():
    d = load_dict()
    problems = []
    used = set()
    for page, (src, root, units, orphans, attrs) in collect().items():
        for u in units:
            if not tagged(u):
                problems.append("%s: untagged <%s>: %s" % (page, u.tag, unit_en(src, u)[:90]))
                continue
            k = u.attrs.get("data-i18n") or u.attrs.get("data-i18n-html")
            used.add(k)
            entry = d.get(k)
            if not entry:
                problems.append("%s: key %r not in dictionary" % (page, k))
            elif not entry.get("es"):
                problems.append("%s: key %r has no Spanish" % (page, k))
            elif entry["en"] != unit_en(src, u):
                problems.append("%s: key %r English changed (Spanish may be stale)\n    page: %s\n    dict: %s" % (
                    page, k, unit_en(src, u)[:90], entry["en"][:90]))
        for n, a, v in attrs:
            problems.append("%s: untagged %s=%r on <%s>" % (page, a, v, n.tag))
        stack = [root]
        while stack:
            n = stack.pop()
            for c in n.children:
                if isinstance(c, Node):
                    spec = c.attrs.get("data-i18n-attr", "")
                    for part in filter(None, spec.split(";")):
                        a, k = part.split(":", 1)
                        used.add(k)
                        if not d.get(k, {}).get("es"):
                            problems.append("%s: attr key %r has no Spanish" % (page, k))
                        elif d[k]["en"] != norm(c.attrs.get(a, "")):
                            problems.append("%s: attr key %r English changed" % (page, k))
                    stack.append(c)
        for o in orphans:
            problems.append("%s: loose text in <%s> next to block elements: %s" % (page, o.tag, norm(direct_text(o))[:80]))
    js_keys = set(re.findall(r"""\btr?\(\s*["']([\w.-]+)["']""", (ROOT / "js" / "main.js").read_text()))
    for k in js_keys:
        used.add(k)
        if not d.get(k, {}).get("es"):
            problems.append("js/main.js: key %r has no Spanish" % k)
    # Translated HTML must keep the same tags/links as the English.
    tags = lambda h: re.findall(r"<[^>]+>", h)
    for k, v in d.items():
        if v.get("mode") == "html" and v.get("es") and tags(v["es"]) != tags(v["en"]):
            problems.append("key %r: Spanish HTML tags differ from English" % k)
    unused = sorted(set(d) - used)
    for p in problems:
        print("✗", p)
    if unused:
        print("(unused dictionary keys: %s)" % ", ".join(unused))
    print("%d problem(s); %d keys in dictionary" % (len(problems), len(d)))
    return 1 if problems else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit({"scan": cmd_scan, "annotate": cmd_annotate, "check": cmd_check}[cmd]() or 0)
