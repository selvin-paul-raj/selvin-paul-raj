#!/usr/bin/env python3
"""AGENT_OS profile art: the hand-written animated SVGs in /assets (dark + light).

Run: python3 scripts/build_svgs.py   (no dependencies)
Data-driven cards (stats, languages, heatmap, now-building, project cards) are in build_stats.py.
"""
from svgkit import PAL, THEMES, MONO, SANS, BASE_CSS, esc, tw, glow_filter, svg_open, hud_corners, write


# ----------------------------------------------------------------------------- helpers
def disc_type(n, char_w, start, per_char, hide, cycle, base=0.0):
    """keyTimes/values for a discrete typewriter clip (width grows one char at a time, then resets)."""
    kt, vals = [0.0], [0.0 if start > 0 else base]
    for k in range(0 if start > 0 else 1, n + 1):
        t = (start + k * per_char) / cycle
        if t <= kt[-1]:
            continue
        kt.append(t)
        vals.append(base + k * char_w + (2 if k == n else 0))
    if hide < cycle:
        kt.append(hide / cycle)
        vals.append(0.0)
    if kt[-1] < 1:
        kt.append(1.0)
        vals.append(vals[-1])
    return ";".join(f"{v:.4f}" for v in kt), ";".join(f"{v:.1f}" for v in vals)


def window(start, end, cycle, fade=0.15):
    """opacity keyTimes/values: hidden, visible between start and end (seconds), hidden again."""
    pts = [(0, 0)]
    if start > 0:
        pts += [(start, 0), (min(start + fade, end), 1)]
    else:
        pts = [(0, 1)]
    pts += [(end, 1), (min(end + fade, cycle), 0)]
    if pts[-1][0] < cycle:
        pts.append((cycle, 0))
    kt, vals, last = [], [], -1
    for t, v in pts:
        t = t / cycle
        if t <= last:
            t = last + 0.0001
        kt.append(min(t, 1))
        vals.append(v)
        last = t
    kt[-1] = 1
    return ";".join(f"{k:.4f}" for k in kt), ";".join(str(v) for v in vals)


# ----------------------------------------------------------------------------- hero
def hero(t):
    p = PAL[t]
    W, H = 1200, 420
    hub = (905, 228)
    nodes = [  # key, x, y, label, sub, colour
        ("query", 722, 120, "USER QUERY", "plain English", p["cyan"]),
        ("rag", 905, 72, "RAG", "faiss + bm25", p["violet"]),
        ("tools", 1095, 120, "TOOLS", "mcp servers", p["violet"]),
        ("mem", 722, 338, "MEMORY", "state + context", p["green"]),
        ("router", 905, 386, "LLM ROUTER", "multi-provider", p["cyan"]),
        ("evals", 1095, 338, "EVALS", "deepeval + hitl", p["green"]),
    ]
    edges, pulses, ndraw = [], [], []
    for i, (k, x, y, lab, sub, col) in enumerate(nodes):
        cx, cy = (hub[0] + x) / 2, (hub[1] + y) / 2
        bend = 26 if i % 2 else -26
        d = f"M{hub[0]} {hub[1]} Q{cx + bend:.0f} {cy - bend * 0.4:.0f} {x} {y}"
        edges.append(f'<path id="e{i}" d="{d}" class="edge"/>')
        inbound = k in ("query", "router")
        for j, b in enumerate((0.25 * i, 0.25 * i + 1.6)):
            kp = "1;0" if inbound else "0;1"
            pulses.append(
                f'<circle r="{4 if j == 0 else 2.6}" fill="{col}" filter="url(#glow)">'
                f'<animateMotion dur="3.2s" begin="{b:.2f}s" repeatCount="indefinite" keyPoints="{kp}" keyTimes="0;1" calcMode="linear">'
                f'<mpath xlink:href="#e{i}"/></animateMotion>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3.2s" begin="{b:.2f}s" repeatCount="indefinite"/></circle>')
        w = max(118, int(max(tw(lab, 13) + len(lab), tw(sub, 11)) + 40))
        ndraw.append(
            f'<g class="in" style="animation-delay:{0.35 + 0.12 * i:.2f}s">'
            f'<rect x="{x - w / 2:.0f}" y="{y - 22}" width="{w}" height="44" rx="12" fill="{p["panel"]}" stroke="{col}" stroke-opacity=".75"/>'
            f'<rect x="{x - w / 2 - 4:.0f}" y="{y - 26}" width="{w + 8}" height="52" rx="15" fill="none" stroke="{col}" stroke-width="1.2" opacity="0">'
            f'<animate attributeName="opacity" values="0;.7;0" dur="3.2s" begin="{0.25 * i + (0 if k in ("query", "router") else 3.0):.2f}s" repeatCount="indefinite"/></rect>'
            f'<circle cx="{x - w / 2 + 14:.0f}" cy="{y - 5}" r="3.5" fill="{col}" filter="url(#glow)" class="pl" style="animation-delay:{0.3 * i:.1f}s"/>'
            f'<text x="{x - w / 2 + 24:.0f}" y="{y - 1}" class="nl">{lab}</text>'
            f'<text x="{x - w / 2 + 24:.0f}" y="{y + 14}" class="ns">{sub}</text></g>')

    # tagline: three lines typed in a 12 s loop after the name reveal
    tag_lines = [
        ("I build agents that plan, retrieve, act and get evaluated.", p["text"]),
        ("LangGraph · Google ADK · MCP · RAG · evals", p["cyan"]),
        ("Learning in public → #AIEngineerIn150Days", p["green"]),
    ]
    cyc, fs, cw = 12.0, 15, 15 * 0.602
    tag_svg, tag_clips = [], []
    for i, (txt, col) in enumerate(tag_lines):
        s = i * 4.0
        kt, vals = disc_type(len(txt), cw, s + 0.05, 0.035, s + 3.75, cyc)
        tag_clips.append(f'<clipPath id="tg{i}"><rect x="78" y="262" height="24" width="0">'
                         f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" calcMode="discrete" dur="{cyc}s" begin="1.4s" repeatCount="indefinite"/></rect></clipPath>')
        tag_svg.append(f'<text x="80" y="279" clip-path="url(#tg{i})" class="tg" fill="{col}">{esc(txt)}</text>')
        ckt, cv = disc_type(len(txt), cw, s + 0.05, 0.035, s + 3.75, cyc, base=82)
        okt, ov = window(s, s + 3.75, cyc, 0.01)
        tag_svg.append(f'<rect y="265" width="9" height="18" fill="{p["cyan"]}" x="82" opacity="0">'
                       f'<animate attributeName="x" values="{cv}" keyTimes="{ckt}" calcMode="discrete" dur="{cyc}s" begin="1.4s" repeatCount="indefinite"/>'
                       f'<animate attributeName="opacity" values="{ov}" keyTimes="{okt}" calcMode="discrete" dur="{cyc}s" begin="1.4s" repeatCount="indefinite"/></rect>')
    caret = ""

    name = "Selvin PaulRaj K"
    chips = [("● OPEN TO AI / LLM / AGENTIC ROLES", p["green"]), ("CHENNAI, IN", p["cyan"]), ("1+ YR SHIPPING AGENTS", p["violet"])]
    cx, chip_svg = 60, []
    for i, (c, col) in enumerate(chips):
        w = tw(c, 11) + len(c) * 0.5 + 22
        chip_svg.append(f'<g class="in" style="animation-delay:{1.0 + 0.12 * i:.2f}s"><rect x="{cx:.0f}" y="314" width="{w:.0f}" height="26" rx="13" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-opacity=".55"/>'
                        f'<text x="{cx + 11:.0f}" y="331" class="chip" fill="{col}">{c}</text></g>')
        cx += w + 10

    return svg_open(W, H, "Selvin PaulRaj K, AI Engineer",
                    "Animated AGENT_OS banner: Selvin PaulRaj K, AI Engineer building agentic AI and LLM apps in Chennai, India, open to AI, LLM and agentic engineer roles. "
                    "On the right a glowing agent network: a planner hub sends pulses to RAG, MCP tools, memory, an LLM router and evals.", True) + f'''
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".5" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["pink"]}"/></linearGradient>
<radialGradient id="hubg"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity=".45"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity=".12"/></linearGradient>
<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20"/></clipPath>
<clipPath id="nm"><rect x="56" y="150" height="80" width="0"><animate attributeName="width" values="0;560" keyTimes="0;1" keySplines=".6 0 .2 1" calcMode="spline" dur="1s" begin=".25s" fill="freeze"/></rect></clipPath>
{"".join(tag_clips)}
{glow_filter(p)}{glow_filter(p, "glow2", 7)}
</defs>
<style>{BASE_CSS}
.name{{font:800 58px {SANS};letter-spacing:-1px}}
.role{{font:600 22px {SANS};fill:{p["sub"]}}}
.bar{{font:600 12px {MONO};fill:{p["muted"]};letter-spacing:1.5px}}
.boot{{font:500 13px {MONO};fill:{p["green"]}}}
.tg{{font:500 15px {MONO};white-space:pre}}
.chip{{font:700 11px {MONO};letter-spacing:.5px}}
.nl{{font:700 13px {MONO};fill:{p["text"]};letter-spacing:1px}}
.ns{{font:400 11px {MONO};fill:{p["muted"]}}}
.edge{{fill:none;stroke:{p["line"]};stroke-width:1.6;stroke-dasharray:3 7;animation:dash 2.4s linear infinite}}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#grid)" opacity=".55"/>
<rect x="0" y="-120" width="{W}" height="120" fill="url(#scan)"><animate attributeName="y" values="-120;{H}" dur="6s" repeatCount="indefinite"/></rect>
<circle cx="{hub[0]}" cy="{hub[1]}" r="190" fill="url(#hubg)" opacity=".5"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="{p["line"]}"/>
{hud_corners(14, 14, W - 28, H - 28, p["cyan"], 22, 2)}
<g>
<text x="40" y="46" class="bar">AGENT_OS v3.0</text>
<text x="190" y="46" class="bar">SESSION: selvin-paul-raj</text>
<text x="420" y="46" class="bar">STATUS:</text><text x="490" y="46" class="bar" fill="{p["green"]}" style="fill:{p["green"]}">ONLINE</text>
<circle cx="560" cy="42" r="4" fill="{p["green"]}" filter="url(#glow)" class="pl"/>
<line x1="40" y1="60" x2="610" y2="60" stroke="{p["line"]}"/>
<rect x="40" y="59" width="90" height="2" fill="url(#acc)"><animate attributeName="x" values="40;520;40" dur="5s" repeatCount="indefinite"/></rect>
</g>
<text x="60" y="110" class="boot fd" style="animation-delay:.05s">&gt; boot agent --id selvin_paulraj_k ... ok</text>
<g clip-path="url(#nm)">
<text x="58" y="208" class="name" fill="{p["cyan"]}" opacity="0">{name}<animate attributeName="opacity" values="0;.85;0;.6;0;0" keyTimes="0;.015;.03;.045;.06;1" dur="6s" begin="1.3s" repeatCount="indefinite"/>
<animateTransform attributeName="transform" type="translate" values="0 0;-4 0;3 0;-2 0;0 0;0 0" keyTimes="0;.015;.03;.045;.06;1" dur="6s" begin="1.3s" repeatCount="indefinite"/></text>
<text x="58" y="208" class="name" fill="{p["pink"]}" opacity="0">{name}<animate attributeName="opacity" values="0;.75;0;.5;0;0" keyTimes="0;.015;.03;.045;.06;1" dur="6s" begin="1.3s" repeatCount="indefinite"/>
<animateTransform attributeName="transform" type="translate" values="0 0;4 1;-3 0;2 0;0 0;0 0" keyTimes="0;.015;.03;.045;.06;1" dur="6s" begin="1.3s" repeatCount="indefinite"/></text>
<text x="58" y="208" class="name" fill="{p["text"]}">{name}</text>
</g>
<rect x="56" y="158" width="4" height="60" fill="{p["cyan"]}" filter="url(#glow)" opacity="0"><animate attributeName="x" values="56;616" keyTimes="0;1" keySplines=".6 0 .2 1" calcMode="spline" dur="1s" begin=".25s" fill="freeze"/>
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.05;.9;1" dur="1.1s" begin=".25s" fill="freeze"/></rect>
<text x="60" y="244" class="role in" style="animation-delay:.8s">AI Engineer · Agentic AI &amp; LLM apps</text>
<text x="60" y="279" class="tg" fill="{p["green"]}">❯</text>
<g transform="translate(20 0)">{"".join(tag_svg)}</g>
{caret}
{"".join(chip_svg)}
<rect x="60" y="364" width="540" height="3" rx="1.5" fill="url(#acc)" class="in" style="animation-delay:1.3s"/>
<text x="60" y="390" class="bar fd" style="animation-delay:1.5s">PLAN → RETRIEVE → ACT → EVALUATE</text>
{"".join(edges)}
<g class="fd" style="animation-delay:.2s">
<circle cx="{hub[0]}" cy="{hub[1]}" r="58" fill="none" stroke="{p["cyan"]}" stroke-opacity=".5" stroke-dasharray="6 8"><animateTransform attributeName="transform" type="rotate" from="0 {hub[0]} {hub[1]}" to="360 {hub[0]} {hub[1]}" dur="14s" repeatCount="indefinite"/></circle>
<circle cx="{hub[0]}" cy="{hub[1]}" r="70" fill="none" stroke="{p["violet"]}" stroke-opacity=".35" stroke-dasharray="2 10"><animateTransform attributeName="transform" type="rotate" from="360 {hub[0]} {hub[1]}" to="0 {hub[0]} {hub[1]}" dur="20s" repeatCount="indefinite"/></circle>
<circle cx="{hub[0]}" cy="{hub[1]}" r="44" fill="none" stroke="{p["cyan"]}" stroke-width="2" opacity=".6"><animate attributeName="r" values="44;92" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".6;0" dur="2.4s" repeatCount="indefinite"/></circle>
<circle cx="{hub[0]}" cy="{hub[1]}" r="44" fill="{p["panel"]}" stroke="{p["cyan"]}" stroke-width="2" filter="url(#glow)"/>
<text x="{hub[0]}" y="{hub[1] - 2}" text-anchor="middle" class="nl" style="font-size:14px">PLANNER</text>
<text x="{hub[0]}" y="{hub[1] + 15}" text-anchor="middle" class="ns">langgraph</text>
</g>
{"".join(ndraw)}
{"".join(pulses)}
</svg>
'''


# ----------------------------------------------------------------------------- terminal
TERM = [
    ("cmd", "whoami"),
    ("out", "AI Engineer · 1+ yr shipping agentic AI & LLM apps"),
    ("cmd", "cat now.txt"),
    ("out", "Associate Data Analyst, AI Automation @ Zinnov (Draup)"),
    ("out", "M.E. CSE (AI) @ Kings Engineering College"),
    ("cmd", "ls ~/stack"),
    ("out", "langgraph  google-adk  mcp  rag  fastapi  faiss+bm25  deepeval"),
    ("cmd", "./learn --in-public"),
    ("out", "#AIEngineerIn150Days → blog · LinkedIn · YouTube Shorts"),
    ("cmd", "echo $STATUS"),
    ("ok", "✔ open to AI / LLM / agentic engineer roles · Chennai, India"),
]


def terminal(t):
    p = PAL[t]
    W, lh, x0, y0, fs = 900, 26, 30, 84, 14
    H = y0 + len(TERM) * lh + 12
    cw = fs * 0.602
    cyc = 16.0
    hide = 15.3
    tcur = 0.0
    clips, body = [], []
    for i, (kind, txt) in enumerate(TERM):
        y = y0 + i * lh
        always = i <= 1  # first command + answer are visible at frame 0 (never blank)
        if kind == "cmd":
            n = len(txt)
            base = 2 * cw
            if always:
                clips.append(f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 18}" height="26" width="{base + n * cw + 4:.0f}"/></clipPath>')
            else:
                kt, vals = disc_type(n, cw, tcur, 0.06, hide, cyc, base=base)
                clips.append(f'<clipPath id="c{i}"><rect x="{x0}" y="{y - 18}" height="26" width="0">'
                             f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/></rect></clipPath>')
                # type-head cursor
                ckt, cvals = disc_type(n, cw, tcur, 0.06, hide, cyc, base=x0 + base)
                okt, ov = window(tcur, tcur + n * 0.06 + 0.25, cyc, 0.01)
                body.append(f'<rect y="{y - 13}" width="8" height="16" fill="{p["cyan"]}" x="{x0 + base:.0f}" opacity="0">'
                            f'<animate attributeName="x" values="{cvals}" keyTimes="{ckt}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/>'
                            f'<animate attributeName="opacity" values="{ov}" keyTimes="{okt}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/></rect>')
                tcur += n * 0.06 + 0.3
            body.append(f'<g clip-path="url(#c{i})"><text x="{x0}" y="{y}" class="t"><tspan class="pr">❯</tspan> <tspan class="cm">{esc(txt)}</tspan></text></g>')
        else:
            cls = "ok" if kind == "ok" else "o"
            if always:
                body.append(f'<text x="{x0 + 18}" y="{y}" class="t {cls}">{esc(txt)}</text>')
            else:
                okt, ov = window(tcur, hide, cyc, 0.12)
                body.append(f'<text x="{x0 + 18}" y="{y}" class="t {cls}" opacity="0"><animate attributeName="opacity" values="{ov}" keyTimes="{okt}" dur="{cyc}s" repeatCount="indefinite"/>{esc(txt)}</text>')
                tcur += 0.22
    # idle cursor after the last line
    last_y = y0 + (len(TERM) - 1) * lh
    cx = x0 + 18 + len(TERM[-1][1]) * cw + 8
    okt, ov = window(tcur, hide, cyc, 0.01)
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="{ov}" keyTimes="{okt}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/>'
                f'<rect x="{cx:.0f}" y="{last_y - 13}" width="8" height="16" fill="{p["cyan"]}" class="bl"/></g>')
    return svg_open(W, H, "Terminal: whoami",
                    "A terminal types: whoami, AI Engineer with 1+ year shipping agentic AI and LLM apps. Now: Associate Data Analyst, AI Automation at Zinnov (Draup); "
                    "M.E. CSE (AI) at Kings Engineering College. Stack: LangGraph, Google ADK, MCP, RAG, FastAPI, FAISS plus BM25, DeepEval. "
                    "Learning in public with #AIEngineerIn150Days. Status: open to AI, LLM and agentic engineer roles, Chennai, India.") + f'''
<defs>{"".join(clips)}
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".5" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["pink"]}"/></linearGradient>
<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{p["text"]}" opacity=".035"/></pattern></defs>
<style>{BASE_CSS}
.t{{font:400 {fs}px {MONO};fill:{p["sub"]};white-space:pre}}
.pr{{fill:{p["green"]};font-weight:700}} .cm{{fill:{p["text"]};font-weight:700}}
.o{{fill:{p["sub"]}}} .ok{{fill:{p["green"]};font-weight:700}}
.ttl{{font:600 12px {MONO};fill:{p["muted"]};letter-spacing:1px}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{p["chrome"]}" stroke="{p["line"]}"/>
<path d="M1 15 a14 14 0 0 1 14 -14 H{W - 15} a14 14 0 0 1 14 14 V46 H1 Z" fill="{p["panel2"]}"/>
<rect x="1" y="45" width="{W - 2}" height="2" fill="url(#acc)" opacity=".8"/>
<circle cx="26" cy="23" r="6" fill="#ff5f57"/><circle cx="46" cy="23" r="6" fill="#febc2e"/><circle cx="66" cy="23" r="6" fill="#28c840"/>
<text x="{W / 2}" y="28" text-anchor="middle" class="ttl">selvin@agent-os: ~ — zsh</text>
<text x="{W - 24}" y="28" text-anchor="end" class="ttl" style="fill:{p["green"]}">● live</text>
<rect x="1" y="47" width="{W - 2}" height="{H - 48}" fill="url(#sl)"/>
{"".join(body)}
</svg>
'''


# ----------------------------------------------------------------------------- section headers
SECTIONS = [
    ("whoami", "01", "WHOAMI", "who is running this agent"),
    ("building", "02", "CURRENTLY BUILDING", "live processes"),
    ("work", "03", "WHAT I BUILD", "agents in production"),
    ("projects", "04", "FEATURED PROJECTS", "click a card to open the repo"),
    ("stack", "05", "TECH STACK", "orbiting the agent core"),
    ("telemetry", "06", "TELEMETRY", "self-generated daily by GitHub Actions"),
    ("arcade", "07", "CONTRIBUTION ARCADE", "snake · pac-man · 3D city"),
    ("feeds", "08", "LATEST TRANSMISSIONS", "blog + YouTube, auto-updated"),
    ("connect", "09", "ASK MY AGENT", "let's build something"),
]


def header(t, idx, title, sub):
    p = PAL[t]
    W, H = 1200, 64
    tx = 92
    tw_ = tw(title, 22) + len(title) * 1.6 + 8
    lx = tx + tw_ + 22
    sub_w = tw("// " + sub, 12)
    return svg_open(W, H, f"{idx} {title}", f"Section header: {title.title()}, {sub}.") + f'''
<defs><linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{lx:.0f}" x2="{W - 30 - sub_w - 16:.0f}" y1="0" y2="0"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".6" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["violet"]}" stop-opacity="0"/></linearGradient>
<clipPath id="tc"><rect x="{tx}" y="10" height="40" width="0"><animate attributeName="width" values="0;{tw_ + 4:.0f}" dur=".7s" begin=".1s" fill="freeze"/></rect></clipPath>
{glow_filter(p)}</defs>
<style>{BASE_CSS}
.ix{{font:800 14px {MONO};fill:{p["cyan"]}}} .tt{{font:800 22px {MONO};fill:{p["text"]};letter-spacing:1px}}
.sb{{font:500 12px {MONO};fill:{p["muted"]}}}
</style>
<rect x="20" y="16" width="56" height="30" rx="8" fill="{p["cyan"]}" fill-opacity=".1" stroke="{p["cyan"]}" stroke-opacity=".6"/>
<text x="48" y="36" text-anchor="middle" class="ix">{idx}</text>
<rect x="18" y="14" width="60" height="34" rx="10" fill="none" stroke="{p["cyan"]}" opacity="0"><animate attributeName="opacity" values="0;.8;0" dur="2.4s" repeatCount="indefinite"/></rect>
<text x="{tx}" y="39" class="tt" clip-path="url(#tc)">{esc(title)}</text>
<rect x="{tx + tw_ + 4:.0f}" y="20" width="10" height="22" fill="{p["cyan"]}" class="bl"/>
<line x1="{lx:.0f}" y1="31" x2="{W - 30 - sub_w - 16:.0f}" y2="31" stroke="url(#ln)" stroke-width="2" stroke-dasharray="{W:.0f}" stroke-dashoffset="{W:.0f}"><animate attributeName="stroke-dashoffset" values="{W:.0f};0" dur="1.2s" begin=".4s" fill="freeze"/></line>
<circle r="3.5" cy="31" fill="{p["cyan"]}" filter="url(#glow)"><animate attributeName="cx" values="{lx:.0f};{W - 30 - sub_w - 16:.0f}" dur="3.5s" begin="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="3.5s" begin="1.6s" repeatCount="indefinite"/></circle>
<text x="{W - 30}" y="36" text-anchor="end" class="sb fd" style="animation-delay:.9s">// {esc(sub)}</text>
<line x1="20" y1="62" x2="{W - 20}" y2="62" stroke="{p["line"]}" opacity=".6"/>
</svg>
'''


# ----------------------------------------------------------------------------- divider
def divider(t):
    p = PAL[t]
    W, H = 1200, 34
    hexes = "".join(f'<path d="M{x} 9 l7 4 v8 l-7 4 l-7 -4 v-8 z" fill="{p["panel"]}" stroke="{c}" stroke-width="1.4"/>'
                    for x, c in ((300, p["cyan"]), (600, p["violet"]), (900, p["green"])))
    pk = "".join(f'<rect y="16" width="{w}" height="2" rx="1" fill="{c}" filter="url(#glow)"><animate attributeName="x" values="20;1180" dur="{d}s" begin="{b}s" repeatCount="indefinite"/></rect>'
                 for w, c, d, b in ((40, p["cyan"], 4.5, 0), (18, p["violet"], 6, 1.2), (26, p["green"], 5.2, 2.6)))
    return svg_open(W, H, "Divider", "Section divider: a data line with packets travelling between three hexagon nodes.") + f'''
<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="20" x2="1180"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/><stop offset=".25" stop-color="{p["cyan"]}" stop-opacity=".6"/><stop offset=".5" stop-color="{p["violet"]}" stop-opacity=".7"/><stop offset=".75" stop-color="{p["green"]}" stop-opacity=".6"/><stop offset="1" stop-color="{p["green"]}" stop-opacity="0"/></linearGradient>{glow_filter(p, "glow", 2.5)}</defs>
<path d="M20 17 H1180" stroke="url(#g)" stroke-width="1.2" stroke-dasharray="2 4"/>
{pk}{hexes}
</svg>
'''


# ----------------------------------------------------------------------------- tech orbit
RINGS = [
    (230, 78, 26, "cyan", ["LangGraph", "Google ADK", "MCP", "RAG", "DeepEval", "LangChain"]),
    (380, 128, 40, "violet", ["Claude", "Gemini", "Hugging Face", "FAISS + BM25", "Pydantic", "Playwright", "FastAPI", "Sentence-Transformers"]),
    (520, 178, 56, "green", ["Python", "TypeScript", "Docker", "PostgreSQL", "AWS", "Next.js", "React", "Git", "Linux", "Vercel", "Node.js", "GitHub Actions"]),
]


def orbit(t):
    p = PAL[t]
    W, H = 1200, 470
    cx, cy = 600, 232
    rings, items = [], []
    for ri, (rx, ry, dur, col, labels) in enumerate(RINGS):
        c = p[col]
        d = f"M{cx} {cy + ry} A{rx} {ry} 0 1 1 {cx} {cy - ry} A{rx} {ry} 0 1 1 {cx} {cy + ry}"
        rings.append(f'<path id="r{ri}" d="{d}" fill="none" stroke="{c}" stroke-opacity=".35" stroke-dasharray="3 9" style="animation:dash {4 + ri * 2}s linear infinite"/>')
        n = len(labels)
        for i, lab in enumerate(labels):
            b = -dur * i / n
            w = tw(lab, 12.5) + 26
            items.append(
                f'<g><animateMotion dur="{dur}s" begin="{b:.2f}s" repeatCount="indefinite"><mpath xlink:href="#r{ri}"/></animateMotion>'
                f'<animate attributeName="opacity" values="1;.4;1" keyTimes="0;.5;1" dur="{dur}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
                f'<rect x="{-w / 2:.1f}" y="-13" width="{w:.1f}" height="26" rx="13" fill="{p["panel"]}" stroke="{c}" stroke-opacity=".8"/>'
                f'<circle cx="{-w / 2 + 11:.1f}" cy="0" r="3" fill="{c}"/>'
                f'<text x="{-w / 2 + 19:.1f}" y="4.3" class="lb">{esc(lab)}</text></g>')
    return svg_open(W, H, "Tech stack orbit",
                    "Animated orbit of Selvin's stack around an agent core. Inner ring, agent frameworks: LangGraph, Google ADK, MCP, RAG, DeepEval, LangChain. "
                    "Middle ring, models and tooling: Claude, Gemini, Hugging Face, FAISS plus BM25, Pydantic, Playwright, FastAPI, Sentence-Transformers. "
                    "Outer ring, engineering: Python, TypeScript, Docker, PostgreSQL, AWS, Next.js, React, Git, Linux, Vercel, Node.js, GitHub Actions.", True) + f'''
<defs><radialGradient id="core"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity=".55"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{p["grid"]}"/></pattern>{glow_filter(p)}</defs>
<style>{BASE_CSS}
.lb{{font:600 12.5px {MONO};fill:{p["text"]}}} .ct{{font:800 15px {MONO};fill:{p["text"]};letter-spacing:2px}} .cs{{font:500 11px {MONO};fill:{p["muted"]}}}
.lg{{font:600 11px {MONO};letter-spacing:1px}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#bg)" stroke="{p["line"]}"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#dots)" opacity=".7"/>
{hud_corners(12, 12, W - 24, H - 24, p["violet"], 18, 1.6)}
<circle cx="{cx}" cy="{cy}" r="150" fill="url(#core)" opacity=".55"/>
{"".join(rings)}
<g>
<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{p["cyan"]}" stroke-width="2"><animate attributeName="r" values="40;120" dur="3s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="3s" repeatCount="indefinite"/></circle>
<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{p["violet"]}" stroke-width="2"><animate attributeName="r" values="40;120" dur="3s" begin="1.5s" repeatCount="indefinite"/><animate attributeName="opacity" values=".7;0" dur="3s" begin="1.5s" repeatCount="indefinite"/></circle>
<path d="M{cx} {cy - 50} l43 25 v50 l-43 25 l-43 -25 v-50 z" fill="{p["panel"]}" stroke="{p["cyan"]}" stroke-width="2" filter="url(#glow)"/>
<text x="{cx}" y="{cy - 2}" text-anchor="middle" class="ct">AGENT</text>
<text x="{cx}" y="{cy + 16}" text-anchor="middle" class="cs">core</text>
</g>
{"".join(items)}
<g transform="translate(36 {H - 26})"><circle r="4" fill="{p["cyan"]}"/><text x="10" y="4" class="lg" fill="{p["cyan"]}">AGENTS &amp; RAG</text>
<circle cx="150" r="4" fill="{p["violet"]}"/><text x="160" y="4" class="lg" fill="{p["violet"]}">MODELS &amp; TOOLING</text>
<circle cx="330" r="4" fill="{p["green"]}"/><text x="340" y="4" class="lg" fill="{p["green"]}">ENGINEERING</text></g>
</svg>
'''


# ----------------------------------------------------------------------------- ask my agent
def ask_agent(t):
    p = PAL[t]
    W, H = 1000, 330
    cyc = 15.0
    q = "Hey! Can Selvin build AI agents for my team?"
    a1 = "Yes. He ships LangGraph + MCP agents with RAG, tools, memory"
    a2 = "and evals, and he's open to AI / LLM / agentic engineer roles."
    fs, cw = 14, 14 * 0.602
    qw = tw(q, fs) + 36
    ukt, uv = window(0.5, 14.2, cyc, 0.25)
    dkt, dv = window(1.3, 2.9, cyc, 0.1)
    k1, v1 = disc_type(len(a1), cw, 3.0, 0.028, 14.2, cyc)
    k2, v2 = disc_type(len(a2), cw, 3.0 + len(a1) * 0.028 + 0.1, 0.028, 14.2, cyc)
    akt, av = window(2.9, 14.2, cyc, 0.1)
    bkt, bv = window(7.4, 14.2, cyc, 0.3)
    dots = "".join(f'<circle cx="{76 + i * 16}" cy="171" r="4" fill="{p["muted"]}"><animate attributeName="cy" values="171;164;171" dur=".9s" begin="{i * 0.15}s" repeatCount="indefinite"/></circle>' for i in range(3))
    bw = max(tw(a1, fs), tw(a2, fs)) + 40
    return svg_open(W, H, "Ask my agent",
                    "Animated chat. A visitor asks: Can Selvin build AI agents for my team? The agent replies: Yes. He ships LangGraph and MCP agents with RAG, tools, memory and evals, "
                    "and he's open to AI, LLM and agentic engineer roles. Then a button: open portfolio, selvinpaulraj.vercel.app.") + f'''
<defs><clipPath id="a1"><rect x="56" y="162" height="26" width="0"><animate attributeName="width" values="{v1}" keyTimes="{k1}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/></rect></clipPath>
<clipPath id="a2"><rect x="56" y="190" height="26" width="0"><animate attributeName="width" values="{v2}" keyTimes="{k2}" calcMode="discrete" dur="{cyc}s" repeatCount="indefinite"/></rect></clipPath>
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".5" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["pink"]}"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>{glow_filter(p)}</defs>
<style>{BASE_CSS}
.c{{font:500 {fs}px {MONO};white-space:pre}} .h{{font:700 13px {MONO};fill:{p["text"]};letter-spacing:1px}} .hs{{font:500 12px {MONO};fill:{p["muted"]}}}
.btn{{font:800 13px {MONO};letter-spacing:1px}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{p["line"]}"/>
<rect x="1" y="1" width="{W - 2}" height="50" rx="18" fill="{p["panel2"]}"/><rect x="1" y="34" width="{W - 2}" height="17" fill="{p["panel2"]}"/>
<rect x="1" y="50" width="{W - 2}" height="2" fill="url(#acc)"/>
<circle cx="34" cy="26" r="12" fill="none" stroke="{p["cyan"]}" stroke-width="2" filter="url(#glow)"/><circle cx="34" cy="26" r="4" fill="{p["cyan"]}" class="pl"/>
<text x="56" y="31" class="h">agent://selvin-paul-raj</text>
<circle cx="268" cy="27" r="4" fill="{p["green"]}" class="pl"/><text x="278" y="31" class="hs">online · replies in plain English</text>
<g opacity="0"><animate attributeName="opacity" values="{uv}" keyTimes="{ukt}" dur="{cyc}s" repeatCount="indefinite"/>
<rect x="{W - 40 - qw:.0f}" y="76" width="{qw:.0f}" height="40" rx="14" fill="{p["cyan"]}" fill-opacity=".14" stroke="{p["cyan"]}" stroke-opacity=".6"/>
<text x="{W - 40 - qw + 18:.0f}" y="101" class="c" fill="{p["text"]}">{esc(q)}</text>
<text x="{W - 44}" y="132" text-anchor="end" class="hs">visitor</text></g>
<g opacity="0"><animate attributeName="opacity" values="{dv}" keyTimes="{dkt}" dur="{cyc}s" repeatCount="indefinite"/>
<rect x="40" y="150" width="88" height="40" rx="14" fill="{p["panel"]}" stroke="{p["line"]}"/>{dots}</g>
<g opacity="0"><animate attributeName="opacity" values="{av}" keyTimes="{akt}" dur="{cyc}s" repeatCount="indefinite"/>
<rect x="40" y="150" width="{bw:.0f}" height="84" rx="14" fill="{p["panel"]}" stroke="{p["violet"]}" stroke-opacity=".7"/>
<text x="58" y="146" class="hs">selvin's agent</text></g>
<text x="58" y="180" class="c" fill="{p["text"]}" clip-path="url(#a1)">{esc(a1)}</text>
<text x="58" y="208" class="c" fill="{p["text"]}" clip-path="url(#a2)">{esc(a2.replace("'", "’"))}</text>
<g opacity="0"><animate attributeName="opacity" values="{bv}" keyTimes="{bkt}" dur="{cyc}s" repeatCount="indefinite"/>
<rect x="40" y="252" width="410" height="44" rx="22" fill="url(#acc)" opacity=".95"/>
<rect x="36" y="248" width="418" height="52" rx="26" fill="none" stroke="{p["cyan"]}" stroke-width="1.5"><animate attributeName="opacity" values=".9;0" dur="1.6s" repeatCount="indefinite"/></rect>
<text x="245" y="279" text-anchor="middle" class="btn" fill="#ffffff">↗ OPEN PORTFOLIO · selvinpaulraj.vercel.app</text></g>
<rect x="{W - 300}" y="256" width="260" height="36" rx="18" fill="{p["panel"]}" stroke="{p["line"]}"/>
<text x="{W - 282}" y="279" class="hs">Ask my agent…</text>
<rect x="{W - 172}" y="265" width="2" height="18" fill="{p["cyan"]}" class="bl"/>
</svg>
'''


# ----------------------------------------------------------------------------- footer wave
def footer(t):
    p = PAL[t]
    W, H = 1200, 190

    def wave(y, amp, ph):
        pts = []
        for k in range(7):
            x = k * 200
            pts.append((x, y + (amp if (k + ph) % 2 else -amp)))
        d = f"M0 {pts[0][1]}"
        for k in range(1, 7):
            x0, y0 = pts[k - 1]
            x1, y1 = pts[k]
            d += f" C{x0 + 100} {y0} {x1 - 100} {y1} {x1} {y1}"
        return d + f" V{H} H0 Z"

    layers = []
    for i, (y, amp, col, op, dur) in enumerate(((122, 14, p["violet"], .25, 7), (136, 12, p["cyan"], .30, 5.5), (152, 10, p["pink"], .22 if t == "dark" else .12, 9))):
        a, b = wave(y, amp, 0), wave(y, amp, 1)
        layers.append(f'<path d="{a}" fill="{col}" fill-opacity="{op if t == "dark" else op * 0.55:.2f}"><animate attributeName="d" values="{a};{b};{a}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path>')
    return svg_open(W, H, "Footer", "Animated footer: neon waves under the words Plan, retrieve, act, evaluate. Thanks for visiting.") + f'''
<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["bg0"]}" stop-opacity="0"/><stop offset="1" stop-color="{p["bg0"]}" stop-opacity="0"/></linearGradient>
<clipPath id="cl"><rect width="{W}" height="{H}" rx="18"/></clipPath>{glow_filter(p)}</defs>
<style>{BASE_CSS}
.ft{{font:800 22px {MONO};fill:{p["text"]};letter-spacing:3px}} .fs{{font:500 12px {MONO};fill:{p["muted"]};letter-spacing:1.5px}}
.w1{{fill:{p["cyan"]}}} .w2{{fill:{p["violet"]}}} .w3{{fill:{p["green"]}}} .w4{{fill:{p["pink"]}}}
</style>
<g clip-path="url(#cl)">{"".join(layers)}</g>
<text x="600" y="54" text-anchor="middle" class="ft"><tspan class="w1">PLAN</tspan> → <tspan class="w2">RETRIEVE</tspan> → <tspan class="w3">ACT</tspan> → <tspan class="w4">EVALUATE</tspan></text>
<text x="600" y="84" text-anchor="middle" class="fs">thanks for visiting · AGENT_OS v3 · selvin-paul-raj · chennai, india</text>
<rect x="520" y="96" width="160" height="2" rx="1" fill="{p["cyan"]}" filter="url(#glow)"><animate attributeName="width" values="20;160;20" dur="4s" repeatCount="indefinite"/><animate attributeName="x" values="590;520;590" dur="4s" repeatCount="indefinite"/></rect>
</svg>
'''


# ----------------------------------------------------------------------------- badges (one file each, readable on dark and light pages)
BADGES = [  # file, label, glyph, colour
    ("portfolio", "PORTFOLIO", "◆", "#22d3ee"),
    ("linkedin", "LINKEDIN", "in", "#4c9aff"),
    ("x", "X / TWITTER", "𝕏", "#e6f1ff"),
    ("youtube", "YOUTUBE", "▶", "#ff4d4d"),
    ("blog", "BLOG", "✎", "#a78bfa"),
    ("resume", "RÉSUMÉ", "⇩", "#34d399"),
]


def badge(label, glyph, col):
    w = int(tw(label, 12) + 64)
    H = 38
    return svg_open(w, H, label, f"{label.title()} link badge") + f'''
<defs><linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect x="1" y="1" width="{w - 2}" height="{H - 2}" rx="10"/></clipPath></defs>
<style>.l{{font:800 12px {MONO};fill:#e6f1ff;letter-spacing:1.5px}} .g{{font:800 13px {SANS};fill:{col}}}</style>
<rect x="1" y="1" width="{w - 2}" height="{H - 2}" rx="10" fill="#0b1328" stroke="{col}" stroke-opacity=".9"/>
<g clip-path="url(#c)"><rect x="-60" y="0" width="50" height="{H}" fill="url(#sh)" transform="skewX(-20)"><animate attributeName="x" values="-60;{w + 40};{w + 40}" keyTimes="0;.4;1" dur="3.2s" repeatCount="indefinite"/></rect></g>
<circle cx="20" cy="{H / 2}" r="11" fill="{col}" fill-opacity=".16"><animate attributeName="r" values="9;12;9" dur="2s" repeatCount="indefinite"/></circle>
<text x="20" y="{H / 2 + 4.5}" text-anchor="middle" class="g">{esc(glyph)}</text>
<text x="38" y="{H / 2 + 4.3}" class="l">{esc(label)}</text>
</svg>
'''


if __name__ == "__main__":
    for th in THEMES:
        write("hero", th, hero(th))
        write("terminal", th, terminal(th))
        write("divider", th, divider(th))
        write("orbit", th, orbit(th))
        write("ask-agent", th, ask_agent(th))
        write("footer", th, footer(th))
        for slug, idx, title, sub in SECTIONS:
            write(f"h-{slug}", th, header(th, idx, title, sub))
    for slug, label, glyph, col in BADGES:
        write(f"badge-{slug}", None, badge(label, glyph, col))
    print("ok")
