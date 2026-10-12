#!/usr/bin/env python3
"""Self-generated, animated data cards for the profile README (dark + light).

Writes to assets/generated/:
  stats-*.svg      system telemetry: contributions, streaks, stars, repos, PRs, followers
  langs-*.svg      language mix (by number of own public repos)
  pulse-*.svg      neon contribution heatmap for the last year
  building-*.svg   "currently building": #AIEngineerIn150Days day counter, latest post / video / push
  project-<slug>-*.svg   one animated card per featured project (live stars, forks, last push)
  data.json        the numbers behind the cards (last good values are reused if a source is down)

Sources (all public): GitHub REST API, the public contributions calendar page,
the AI with SPR blog RSS and the @aiwithspr YouTube RSS. Uses $GITHUB_TOKEN when set (Actions).
Run: python3 scripts/build_stats.py   (standard library only)
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import PAL, THEMES, MONO, SANS, BASE_CSS, ROOT, esc, tw, glow_filter, svg_open, hud_corners, wrap  # noqa: E402

USER = os.environ.get("PROFILE_USER", "selvin-paul-raj")
BLOG_RSS = "https://ai-with-spr.vercel.app/rss.xml"
YT_RSS = "https://www.youtube.com/feeds/videos.xml?channel_id=UCf-gEIFJsn1M7Kn4A-WfRDw"
OUT = os.path.join(ROOT, "assets", "generated")
DATA = os.path.join(OUT, "data.json")

PROJECTS = [  # repo, title, one-liner, stack
    ("Finn-Advisor", "Finn Advisor", "Personal AI financial advisor: agent orchestration, tool calling, memory, a multi-provider LLM router and safety evals.", ["Google ADK", "LangGraph", "MCP", "DeepEval"]),
    ("chunklab", "ChunkLab", "Open-source lab to compare RAG chunking, embeddings, retrieval and reranking side by side, with Recall@K and MRR.", ["FAISS", "Sentence-Transformers", "Streamlit"]),
    ("Linkedin-Alpic-Mcp", "LinkedIn MCP for ChatGPT & Claude", "Production MCP server for posting, messaging, analytics and profiles, with OAuth automation and Alpic deployment.", ["MCP", "Composio", "OAuth 2.0"]),
    ("Instagram-Alpic-mcp", "Instagram MCP for ChatGPT & Claude", "Production MCP server on the Instagram Graph API: messaging, insights, health monitoring and Alpic deployment.", ["MCP", "Composio", "Graph API"]),
    ("outlook-cli", "outlook-cli", "CLI and MCP server for Outlook mail, calendar and contacts through Microsoft Graph. Published on npm.", ["Node.js", "MCP", "Microsoft Graph"]),
    ("Linkedin-MCP-Server", "LinkedIn MCP Server", "Lightweight MCP server for profile, company, job and post workflows that plugs into agent pipelines.", ["MCP", "Browser automation"]),
    ("ChatDex-AI", "ChatDex AI", "Chrome extension that indexes your ChatGPT and Gemini chats: search prompts, export Markdown/JSON, sync to Notion.", ["Chrome Extension", "JavaScript"]),
    ("daily-ai-digest", "Daily AI Digest", "Archive of my daily AI and tech news digest: the trending updates, the post that went out, and the sources.", ["Python", "Automation"]),
]
ACCENTS = ["cyan", "violet", "green", "pink"]


# ----------------------------------------------------------------------------- fetch
def get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-bot", "Accept": accept})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def gh(path):
    return json.loads(get(f"https://api.github.com{path}"))


def fetch_contrib():
    html = get(f"https://github.com/users/{USER}/contributions", accept="text/html")
    dates = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-[\d-]+)"', html))
    dates = {v: k for k, v in dates.items()}  # id -> date
    if not dates:
        for d, i in re.findall(r'id="(contribution-day-component-[\d-]+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html):
            dates[d] = i
    counts = {}
    for tid, txt in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*([\d,]+) contribution", txt)
        if tid in dates:
            counts[dates[tid]] = int(m.group(1).replace(",", "")) if m else 0
    levels = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        d = re.search(r'data-date="([\d-]+)"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        if d and lv:
            levels[d.group(1)] = int(lv.group(1))
    if len(counts) < 300:
        raise RuntimeError(f"contribution calendar parse failed ({len(counts)} days)")
    return {d: [counts.get(d, 0), levels.get(d, 0)] for d in sorted(counts)}


def fetch_feed(url, n=5):
    root = ET.fromstring(get(url, accept="application/xml"))
    items = []
    for it in root.iter("item"):  # RSS
        items.append({"title": (it.findtext("title") or "").strip(), "date": (it.findtext("pubDate") or "").strip()})
    if not items:  # Atom (YouTube)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for e in root.findall("a:entry", ns):
            items.append({"title": (e.findtext("a:title", namespaces=ns) or "").strip(), "date": (e.findtext("a:published", namespaces=ns) or "")[:10]})
    return items[:n] if n else items


def collect():
    old = {}
    if os.path.exists(DATA):
        with open(DATA) as f:
            old = json.load(f)
    data = dict(old)
    errors = []

    def attempt(key, fn):
        try:
            data[key] = fn()
        except Exception as e:  # keep the last good value
            errors.append(f"{key}: {e}")

    def repos():
        out, page = [], 1
        while True:
            batch = gh(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
            out += [{"name": r["name"], "stars": r["stargazers_count"], "forks": r["forks_count"], "lang": r["language"],
                     "fork": r["fork"], "pushed": r["pushed_at"], "archived": r.get("archived", False)} for r in batch]
            if len(batch) < 100:
                return out
            page += 1

    attempt("user", lambda: {k: v for k, v in gh(f"/users/{USER}").items() if k in ("followers", "public_repos", "created_at", "name")})
    attempt("repos", repos)
    attempt("prs", lambda: gh(f"/search/issues?q=author:{USER}+type:pr&per_page=1")["total_count"])
    attempt("contrib", fetch_contrib)
    attempt("blog", lambda: fetch_feed(BLOG_RSS, 0))
    attempt("youtube", lambda: fetch_feed(YT_RSS, 5))
    data["generated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    data["errors"] = errors
    return data


def derive(data):
    c = data.get("contrib", {})
    days = sorted(c)
    total = sum(c[d][0] for d in days)
    longest = cur = run = 0
    for d in days:
        run = run + 1 if c[d][0] > 0 else 0
        longest = max(longest, run)
    i = len(days) - 1
    if i >= 0 and c[days[i]][0] == 0:
        i -= 1  # today not counted yet
    while i >= 0 and c[days[i]][0] > 0:
        cur += 1
        i -= 1
    own = [r for r in data.get("repos", []) if not r["fork"]]
    stars = sum(r["stars"] for r in own)
    langs = Counter(r["lang"] for r in own if r["lang"])
    day_n = 0
    for it in data.get("blog", []):
        m = re.match(r"\s*Day\s+(\d+)", it["title"], re.I)
        if m:
            day_n = max(day_n, int(m.group(1)))
    pushed = sorted((r for r in own if r["name"].lower() != USER.lower() and not r["archived"]), key=lambda r: r["pushed"], reverse=True)
    return dict(total=total, longest=longest, current=cur, stars=stars, repos=len(own), prs=data.get("prs", 0),
                followers=data.get("user", {}).get("followers", 0), langs=langs.most_common(6), day=day_n,
                latest_push=pushed[0] if pushed else None)


def fmt_date(s):
    for f in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s.strip(), f).strftime("%b %-d, %Y")
        except ValueError:
            pass
    return s[:16]


def trunc(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def countup(x, y, value, cls, fill, begin, anchor="start"):
    """Fake count-up: five frames swap quickly, the last one stays."""
    steps = [round(value * k / 5) for k in range(1, 6)] if isinstance(value, int) else [value] * 5
    out = []
    for k, v in enumerate(steps):
        b = begin + k * 0.12
        last = k == 4
        label = f"{v:,}" if isinstance(v, int) else v
        anim = (f'<set attributeName="opacity" to="1" begin="{b:.2f}s"/>' +
                ("" if last else f'<set attributeName="opacity" to="0" begin="{b + 0.12:.2f}s"/>'))
        out.append(f'<text x="{x}" y="{y}" class="{cls}" fill="{fill}" text-anchor="{anchor}" opacity="0">{anim}{esc(label)}</text>')
    return "".join(out)


# ----------------------------------------------------------------------------- cards
def frame(p, W, H, title, right):
    return (f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#bg)" stroke="{p["line"]}"/>'
            f'{hud_corners(10, 10, W - 20, H - 20, p["cyan"], 14, 1.6)}'
            f'<circle cx="30" cy="34" r="4.5" fill="{p["green"]}" class="pl"/>'
            f'<text x="44" y="39" class="hd">{esc(title)}</text><text x="{W - 28}" y="39" text-anchor="end" class="hs">{esc(right)}</text>'
            f'<line x1="24" y1="54" x2="{W - 24}" y2="54" stroke="{p["line"]}"/>'
            f'<rect x="24" y="53" width="70" height="2" fill="url(#acc)"><animate attributeName="x" values="24;{W - 94};24" dur="6s" repeatCount="indefinite"/></rect>')


def defs(p, extra=""):
    return (f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>'
            f'<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".5" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["pink"]}"/></linearGradient>'
            f'{glow_filter(p)}{extra}</defs>')


def css(p, extra=""):
    return (f'<style>{BASE_CSS}.hd{{font:800 13px {MONO};fill:{p["text"]};letter-spacing:1.5px}} .hs{{font:500 11px {MONO};fill:{p["muted"]}}}'
            f'.v{{font:800 30px {MONO}}} .lb{{font:600 11px {MONO};fill:{p["sub"]};letter-spacing:1px}} .tx{{font:500 13px {MONO};fill:{p["text"]}}}{extra}</style>')


def stats_card(t, s, gen):
    p = PAL[t]
    W, H = 600, 270
    tiles = [("CONTRIBUTIONS · 1Y", s["total"], "cyan"), ("CURRENT STREAK", f'{s["current"]}d', "green"), ("LONGEST STREAK", f'{s["longest"]}d', "violet"),
             ("STARS EARNED", s["stars"], "amber"), ("PUBLIC REPOS", s["repos"], "cyan"), ("PULL REQUESTS", s["prs"], "pink")]
    body = []
    for i, (lab, val, col) in enumerate(tiles):
        x = 24 + (i % 3) * 188
        y = 72 + (i // 3) * 92
        c = p[col]
        b = 0.3 + i * 0.12
        body.append(f'<g class="in" style="animation-delay:{b:.2f}s"><rect x="{x}" y="{y}" width="176" height="80" rx="12" fill="{p["panel"]}" stroke="{c}" stroke-opacity=".45"/>'
                    f'<rect x="{x}" y="{y + 12}" width="3" height="56" rx="1.5" fill="{c}" filter="url(#glow)"/>'
                    f'<text x="{x + 16}" y="{y + 24}" class="lb">{lab}</text></g>')
        if isinstance(val, int):
            body.append(countup(x + 16, y + 60, val, "v", c, b + 0.2))
        else:
            body.append(f'<text x="{x + 16}" y="{y + 60}" class="v in" fill="{c}" style="animation-delay:{b + 0.3:.2f}s">{esc(val)}</text>')
        body.append(f'<rect x="{x + 120}" y="{y + 44}" width="40" height="20" rx="4" fill="none"/>'
                    + "".join(f'<rect x="{x + 124 + k * 8}" y="{y + 64 - h}" width="5" height="{h}" rx="1" fill="{c}" opacity=".55">'
                              f'<animate attributeName="height" values="{h};{max(3, 18 - h)};{h}" dur="{1.6 + k * 0.2:.1f}s" repeatCount="indefinite"/>'
                              f'<animate attributeName="y" values="{y + 64 - h};{y + 64 - max(3, 18 - h)};{y + 64 - h}" dur="{1.6 + k * 0.2:.1f}s" repeatCount="indefinite"/></rect>'
                              for k, h in enumerate((6, 12, 9, 16, 11))))
    return svg_open(W, H, "System telemetry",
                    f"Selvin's GitHub telemetry, generated {gen}: {s['total']:,} contributions in the last year, current streak {s['current']} days, longest streak {s['longest']} days, "
                    f"{s['stars']} stars earned, {s['repos']} public repos, {s['prs']} pull requests.") + defs(p) + css(p) + frame(p, W, H, "SYSTEM TELEMETRY", f"@{USER} · {gen}") + "".join(body) + "</svg>\n"


def langs_card(t, s, gen):
    p = PAL[t]
    W, H = 600, 270
    total = sum(n for _, n in s["langs"]) or 1
    cols = ["cyan", "violet", "green", "amber", "pink", "red"]
    body = []
    for i, (lang, n) in enumerate(s["langs"]):
        y = 82 + i * 30
        pct = n / total
        w = 330 * pct / (s["langs"][0][1] / total)
        c = p[cols[i % len(cols)]]
        b = 0.3 + i * 0.12
        body.append(f'<text x="28" y="{y + 12}" class="tx in" style="animation-delay:{b:.2f}s">{esc(lang)}</text>'
                    f'<rect x="170" y="{y}" width="330" height="14" rx="7" fill="{p["panel2"]}"/>'
                    f'<rect x="170" y="{y}" width="0" height="14" rx="7" fill="{c}" filter="url(#glow)"><animate attributeName="width" values="0;{w:.1f}" keyTimes="0;1" keySplines=".2 .8 .2 1" calcMode="spline" dur="1.1s" begin="{b:.2f}s" fill="freeze"/></rect>'
                    f'<rect x="170" y="{y + 3}" width="24" height="8" rx="4" fill="#fff" opacity="0"><animate attributeName="x" values="170;{170 + w - 24:.1f}" dur="2.4s" begin="{b + 1.2:.2f}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;.35;0" dur="2.4s" begin="{b + 1.2:.2f}s" repeatCount="indefinite"/></rect>'
                    f'<text x="572" y="{y + 12}" text-anchor="end" class="tx in" fill="{c}" style="fill:{c};animation-delay:{b + 0.6:.2f}s">{pct * 100:.0f}%</text>')
    desc = ", ".join(f"{l} {n / total * 100:.0f}%" for l, n in s["langs"])
    return svg_open(W, H, "Language mix", f"Languages across Selvin's own public repos (share of repos by main language): {desc}.") + defs(p) + css(p) + frame(p, W, H, "LANGUAGE MIX", "by repo · auto-updated") + "".join(body) + "</svg>\n"


def pulse_card(t, data, s, gen):
    p = PAL[t]
    c = data.get("contrib", {})
    days = sorted(c)
    if not days:
        return None
    first = dt.date.fromisoformat(days[0])
    offset = (first.weekday() + 1) % 7  # Sunday = row 0
    W, H = 1200, 220
    cs, gap, x0, y0 = 15, 3, 40, 70
    ramp = {"dark": ["#111c35", "#0e4a5c", "#0f8aa6", "#22c7e6", "#a5f3fc"],
            "light": ["#e6ecf5", "#bfe8f1", "#6fcde0", "#1f9fbf", "#0e5f75"]}[t]
    cols = {}
    for i, d in enumerate(days):
        k = i + offset
        cols.setdefault(k // 7, []).append((k % 7, c[d][1]))
    g = []
    for col, cells in sorted(cols.items()):
        x = x0 + col * (cs + gap)
        rects = "".join(f'<rect x="{x}" y="{y0 + r * (cs + gap)}" width="{cs}" height="{cs}" rx="3" class="l{lv}"/>' for r, lv in cells)
        g.append(f'<g class="cl" style="animation-delay:{col * 0.025:.3f}s">{rects}</g>')
    ncol = max(cols) + 1
    gx1 = x0 + ncol * (cs + gap)
    best = max(days, key=lambda d: c[d][0])
    extra_css = "".join(f".l{i}{{fill:{ramp[i]}}}" for i in range(5)) + "@keyframes lit{0%{opacity:.15}40%{opacity:1}100%{opacity:1}}.cl{opacity:.15;animation:lit 1.2s ease-out forwards}"
    side = gx1 + 26
    return svg_open(W, H, "Contribution pulse",
                    f"Neon heatmap of Selvin's GitHub contributions over the last year: {s['total']:,} contributions; best day {fmt_date(best)} with {c[best][0]}. A scanning beam sweeps across it.") + defs(
        p, f'<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity=".35"/></linearGradient>') + css(
        p, extra_css) + frame(p, W, H, "CONTRIBUTION PULSE · LAST 12 MONTHS", f"generated {gen}") + "".join(g) + (
        f'<rect x="{x0 - 40}" y="{y0 - 6}" width="40" height="{7 * (cs + gap) + 8}" fill="url(#beam)"><animate attributeName="x" values="{x0 - 40};{gx1}" dur="5s" begin="1.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="5s" begin="1.4s" repeatCount="indefinite"/></rect>'
        f'<line x1="{side - 12}" y1="70" x2="{side - 12}" y2="192" stroke="{p["line"]}"/>'
        + countup(side, 104, s["total"], "v", p["cyan"], 0.6) +
        f'<text x="{side}" y="122" class="lb">CONTRIBUTIONS</text>'
        f'<text x="{side}" y="160" class="v" fill="{p["green"]}" style="font-size:22px">{s["current"]}d / {s["longest"]}d</text>'
        f'<text x="{side}" y="178" class="lb">STREAK NOW / BEST</text>'
        f'<g transform="translate({x0} 204)"><text class="hs" y="0">less</text>'
        + "".join(f'<rect x="{34 + i * 16}" y="-10" width="12" height="12" rx="2" class="l{i}"/>' for i in range(5)) +
        '<text class="hs" x="118" y="0">more</text></g></svg>\n')


def building_card(t, data, s, gen):
    p = PAL[t]
    W, H = 1200, 250
    day = s["day"]
    blog = data.get("blog", [])
    yt = data.get("youtube", [])
    lp = s["latest_push"]
    rows = [("RUNNING", "green", "#AIEngineerIn150Days", "daily LinkedIn post · blog deep-dive · YouTube Short")]
    if blog:
        rows.append(("LATEST", "cyan", "blog", f'{trunc(blog[0]["title"], 62)} · {fmt_date(blog[0]["date"])}'))
    if yt:
        rows.append(("ON AIR", "pink", "youtube", f'{trunc(yt[0]["title"], 62)} · {fmt_date(yt[0]["date"])}'))
    if lp:
        rows.append(("SHIPPED", "violet", "github", f'pushed to {lp["name"]} · {fmt_date(lp["pushed"])}'))
    r, cx, cy = 66, 130, 146
    circ = 2 * 3.14159 * r
    frac = min(day, 150) / 150
    body = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["panel2"]}" stroke-width="12"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#acc)" stroke-width="12" stroke-linecap="round" transform="rotate(-90 {cx} {cy})" '
            f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" filter="url(#glow)"><animate attributeName="stroke-dashoffset" values="{circ:.1f};{circ * (1 - max(frac, 0.012)):.1f}" keyTimes="0;1" keySplines=".2 .8 .2 1" calcMode="spline" dur="1.6s" begin=".3s" fill="freeze"/></circle>',
            f'<circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="none" stroke="{p["cyan"]}" stroke-opacity=".3" stroke-dasharray="2 8"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></circle>',
            f'<text x="{cx}" y="{cy - 14}" text-anchor="middle" class="lb">DAY</text>',
            countup(cx, cy + 18, day, "v", p["text"], 0.4, "middle"),
            f'<text x="{cx}" y="{cy + 38}" text-anchor="middle" class="hs">of 150</text>']
    for i, (st, col, src, txt) in enumerate(rows):
        y = 84 + i * 40
        c = p[col]
        b = 0.4 + i * 0.15
        body.append(f'<g class="in" style="animation-delay:{b:.2f}s"><rect x="260" y="{y - 16}" width="912" height="32" rx="9" fill="{p["panel"]}" stroke="{p["line"]}"/>'
                    f'<rect x="270" y="{y - 10}" width="84" height="20" rx="6" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-opacity=".6"/>'
                    f'<text x="312" y="{y + 4}" text-anchor="middle" class="st" fill="{c}" style="fill:{c}">{st}</text>'
                    f'<text x="368" y="{y + 5}" class="src" fill="{c}" style="fill:{c}">{esc(src)}</text>'
                    f'<text x="{368 + tw(src, 12) + 14:.0f}" y="{y + 5}" class="tx">{esc(txt)}</text>'
                    f'<circle cx="1152" cy="{y}" r="4" fill="{c}" class="pl" style="animation-delay:{i * 0.4:.1f}s"/></g>')
    # indeterminate progress under the RUNNING row
    body.append(f'<rect x="270" y="{84 + 13}" width="892" height="2" fill="{p["panel2"]}"/><rect x="270" y="{84 + 13}" width="120" height="2" fill="{p["green"]}" filter="url(#glow)">'
                f'<animate attributeName="x" values="270;1042;270" dur="3.6s" repeatCount="indefinite"/></rect>')
    desc = f"Currently building: #AIEngineerIn150Days, day {day} of 150. " + " ".join(f"{st}: {src}, {txt}." for st, _, src, txt in rows[1:])
    return svg_open(W, H, "Currently building", desc) + defs(p) + css(p, f".st{{font:800 10.5px {MONO};letter-spacing:1px}} .src{{font:700 12px {MONO}}}") + frame(
        p, W, H, "CURRENTLY BUILDING · LIVE PROCESSES", f"auto-updated {gen}") + "".join(body) + "</svg>\n"


def project_card(t, i, proj, repo, gen):
    p = PAL[t]
    name, title, blurb, stack = proj
    W, H = 600, 210
    c = p[ACCENTS[i % 4]]
    per = 2 * (W - 4) + 2 * (H - 4)
    lines = wrap(blurb, 74)[:2]
    chips, x = [], 24
    for sname in stack:
        w = tw(sname, 11) + 18
        chips.append(f'<rect x="{x:.0f}" y="138" width="{w:.0f}" height="22" rx="11" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".5"/>'
                     f'<text x="{x + 9:.0f}" y="153" class="ch" fill="{c}" style="fill:{c}">{esc(sname)}</text>')
        x += w + 8
    meta = ""
    if repo:
        meta = f'★ {repo["stars"]}   ⑂ {repo["forks"]}   ● {repo["lang"] or "—"}   · updated {fmt_date(repo["pushed"])}'
    initials = "".join(w[0] for w in re.split(r"[\s-]+", title) if w[:1].isalnum())[:2].upper()
    return svg_open(W, H, title, f"Project card: {title}. {blurb} Stack: {', '.join(stack)}. {meta}") + defs(p) + css(
        p, f".ti{{font:800 18px {SANS};fill:{p['text']}}} .bd{{font:400 13px {SANS};fill:{p['sub']}}} .ch{{font:600 11px {MONO}}} .mt{{font:500 11.5px {MONO};fill:{p['muted']}}} .ic{{font:800 13px {MONO}}}") + (
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#bg)" stroke="{p["line"]}"/>'
        f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="15" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="140 {per - 140}" filter="url(#glow)">'
        f'<animate attributeName="stroke-dashoffset" values="0;-{per}" dur="{6 + i % 3}s" repeatCount="indefinite"/></rect>'
        f'<path d="M48 18 l20 11.5 v23 l-20 11.5 l-20 -11.5 v-23 z" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-width="1.5"/>'
        f'<text x="48" y="46" text-anchor="middle" class="ic" fill="{c}" style="fill:{c}">{esc(initials)}</text>'
        f'<text x="84" y="40" class="ti">{esc(title)}</text>'
        f'<text x="84" y="60" class="mt">github.com/{USER}/{esc(name)}</text>'
        f'<g class="pl"><text x="{W - 26}" y="42" text-anchor="end" class="ic" fill="{c}" style="fill:{c}">↗</text></g>'
        + "".join(f'<text x="24" y="{96 + k * 20}" class="bd">{esc(l)}</text>' for k, l in enumerate(lines))
        + "".join(chips) +
        f'<line x1="24" y1="176" x2="{W - 24}" y2="176" stroke="{p["line"]}"/>'
        f'<text x="24" y="196" class="mt">{esc(meta)}</text>'
        f'<circle cx="{W - 30}" cy="192" r="4" fill="{c}" class="pl"/></svg>\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    data = collect()
    s = derive(data)
    gen = data["generated"]
    repos = {r["name"].lower(): r for r in data.get("repos", [])}
    for th in THEMES:
        files = {"stats": stats_card(th, s, gen), "langs": langs_card(th, s, gen), "pulse": pulse_card(th, data, s, gen), "building": building_card(th, data, s, gen)}
        for i, proj in enumerate(PROJECTS):
            files[f"project-{proj[0].lower()}"] = project_card(th, i, proj, repos.get(proj[0].lower()), gen)
        for k, v in files.items():
            if v:
                with open(os.path.join(OUT, f"{k}-{th}.svg"), "w", encoding="utf-8") as f:
                    f.write(v)
    keep = {k: data[k] for k in ("generated", "errors", "user", "prs", "contrib", "youtube") if k in data}
    keep["blog"] = data.get("blog", [])[:20]
    keep["repos"] = data.get("repos", [])
    with open(DATA, "w") as f:
        json.dump(keep, f, separators=(",", ":"))
    print(json.dumps({k: v for k, v in s.items() if k != "latest_push"}), "errors:", data["errors"])


if __name__ == "__main__":
    main()
