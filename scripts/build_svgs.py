#!/usr/bin/env python3
"""Generate the hand-written animated SVGs in /assets (dark + light).

Run: python3 scripts/build_svgs.py   (no dependencies). Edit TERM_LINES / PAL to change text or colours."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

PAL = {
    "dark": dict(bg1="#0b1020", bg2="#111a2e", grid="#1e2a44", text="#e6edf3", sub="#9fb0c8",
                 muted="#6b7a94", cyan="#22d3ee", violet="#a78bfa", green="#34d399", amber="#fbbf24",
                 node="#0f172a", nodestroke="#2b3a5a", edge="#334766", chrome="#0d1424", border="#22304d"),
    "light": dict(bg1="#f8fafc", bg2="#eef2ff", grid="#dfe6f3", text="#0f172a", sub="#334155",
                  muted="#64748b", cyan="#0e7490", violet="#6d28d9", green="#047857", amber="#b45309",
                  node="#ffffff", nodestroke="#c7d2e6", edge="#b6c3dc", chrome="#ffffff", border="#d5ddeb"),
}


def hero(t):
    p = PAL[t]
    # agent graph geometry (right side)
    nodes = {
        "query":   (700, 170, "query"),
        "planner": (826, 170, "planner"),
        "rag":     (968, 92, "rag · faiss"),
        "mcp":     (968, 170, "tools · mcp"),
        "mem":     (968, 248, "memory"),
        "eval":    (1108, 170, "evals"),
    }
    edges = [
        ("e1", "M748 170 L778 170"),
        ("e2", "M874 170 C896 170 896 92 908 92"),
        ("e3", "M874 170 L908 170"),
        ("e4", "M874 170 C896 170 896 248 920 248"),
        ("e5", "M1028 92 C1044 92 1044 170 1060 170"),
        ("e6", "M1028 170 L1060 170"),
        ("e7", "M1016 248 C1044 248 1044 170 1060 170"),
    ]
    begins = {"e1": 0, "e2": 0.6, "e3": 0.8, "e4": 1.0, "e5": 1.6, "e6": 1.8, "e7": 2.0}
    colors = {"e1": p["cyan"], "e2": p["violet"], "e3": p["cyan"], "e4": p["green"],
              "e5": p["violet"], "e6": p["cyan"], "e7": p["green"]}
    e_svg = []
    for eid, d in edges:
        e_svg.append(f'<path id="{eid}" d="{d}" class="edge"/>')
    for eid, d in edges:
        b = begins[eid]
        e_svg.append(
            f'<circle r="3.6" fill="{colors[eid]}" opacity="0"><animateMotion dur="3.2s" begin="{b}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.28;1" calcMode="linear"><mpath xlink:href="#{eid}"/></animateMotion>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.02;0.26;0.3;1" dur="3.2s" begin="{b}s" repeatCount="indefinite"/></circle>')
    n_svg = []
    for i, (k, (x, y, label)) in enumerate(nodes.items()):
        w = 120 if len(label) > 7 else 96
        accent = p["green"] if k == "eval" else (p["cyan"] if k in ("query", "planner") else p["violet"])
        n_svg.append(
            f'<g class="node" style="animation-delay:{0.15*i:.2f}s"><rect x="{x-w/2}" y="{y-17}" width="{w}" height="34" rx="10" fill="{p["node"]}" stroke="{p["nodestroke"]}"/>'
            f'<circle cx="{x-w/2+13}" cy="{y}" r="3.5" fill="{accent}"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" begin="{0.3*i:.1f}s" repeatCount="indefinite"/></circle>'
            f'<text x="{x+6}" y="{y+4.5}" text-anchor="middle" class="nl">{label}</text></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="340" viewBox="0 0 1200 340" role="img" aria-labelledby="t d">
<title id="t">Selvin PaulRaj K, AI Engineer</title>
<desc id="d">Animated banner: Selvin PaulRaj K, AI Engineer building agentic AI and LLM apps, Chennai, India. An agent graph shows a query flowing through a planner to RAG, MCP tools and memory, then to evals.</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>
<linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["cyan"]}"/><stop offset=".55" stop-color="{p["violet"]}"/><stop offset="1" stop-color="{p["green"]}"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{p["grid"]}"/></pattern>
<linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/><stop offset=".5" stop-color="{p["cyan"]}" stop-opacity=".10"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity="0"/></linearGradient>
<clipPath id="card"><rect x="1" y="1" width="1198" height="338" rx="18"/></clipPath>
</defs>
<style>
.f{{font-family:{SANS}}} .m{{font-family:{MONO}}}
.name{{font:700 50px {SANS};fill:{p["text"]};letter-spacing:-.5px}}
.role{{font:600 22px {SANS};fill:{p["sub"]}}}
.meta{{font:400 15px {MONO};fill:{p["muted"]}}}
.tag{{font:500 13px {MONO};fill:{p["green"]}}}
.nl{{font:500 13px {MONO};fill:{p["text"]}}}
.edge{{fill:none;stroke:{p["edge"]};stroke-width:1.6;stroke-dasharray:4 5;animation:flow 1.6s linear infinite}}
.in{{opacity:0;animation:up .7s ease-out forwards}}
.node{{opacity:0;animation:pop .5s ease-out forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes flow{{to{{stroke-dashoffset:-18}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.in,.node{{animation:none;opacity:1}}.edge{{animation:none}}}}
</style>
<g clip-path="url(#card)">
<rect width="1200" height="340" fill="url(#bg)"/>
<rect width="1200" height="340" fill="url(#grid)"/>
<rect x="-300" y="0" width="300" height="340" fill="url(#scan)"><animate attributeName="x" values="-300;1200" dur="7s" repeatCount="indefinite"/></rect>
</g>
<rect x="1" y="1" width="1198" height="338" rx="18" fill="none" stroke="{p["border"]}"/>
<rect x="60" y="300" width="560" height="3" rx="1.5" fill="url(#acc)" class="in" style="animation-delay:.5s"/>
<g class="in" style="animation-delay:.05s"><circle cx="66" cy="84" r="5" fill="{p["green"]}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="80" y="89" class="tag">agent online · ~/selvin-paul-raj</text></g>
<text x="58" y="160" class="name in" style="animation-delay:.15s">Selvin PaulRaj K</text>
<text x="60" y="204" class="role in" style="animation-delay:.3s">AI Engineer · Agentic AI &amp; LLM apps</text>
<text x="60" y="246" class="meta in" style="animation-delay:.45s">Chennai, India · open to AI / LLM / agent roles</text>
<rect x="600" y="70" width="1" height="200" fill="{p["border"]}"/>
{"".join(e_svg)}
{"".join(n_svg)}
<text x="904" y="316" text-anchor="middle" class="meta" style="font-size:12px">plan → retrieve → act → evaluate</text>
</svg>
'''


TERM_LINES = [
    ("cmd", "whoami"),
    ("out", "AI Engineer · ~1 yr 2 mo shipping agentic AI and LLM apps"),
    ("cmd", "cat now.txt"),
    ("out", "Associate Data Analyst, AI Automation @ Zinnov (Draup)"),
    ("out", "Learning in public: #AIEngineerIn150Days on AI with SPR"),
    ("cmd", "ls stack/"),
    ("out", "langgraph  google-adk  mcp  fastapi  faiss+bm25  deepeval"),
    ("cmd", "echo $STATUS"),
    ("ok",  "open to AI / LLM / agentic engineer roles"),
]


def terminal(t):
    p = PAL[t]
    W, H = 900, 312
    x0, y0, lh = 34, 82, 26
    cw = 8.6  # approx mono char width at 14px; reveal is a mask so small mismatch is harmless
    parts, clips = [], []
    tcur = 0.4
    for i, (kind, txt) in enumerate(TERM_LINES):
        y = y0 + i * lh
        if kind == "cmd":
            full = (len(txt) + 2) * cw + 6
            dur = max(0.45, len(txt) * 0.06)
            n = len(txt) + 2
            vals = ";".join(f"{(k)*cw + (cw*2 if k else 0):.1f}" for k in range(n))
            clips.append(f'<clipPath id="c{i}"><rect x="{x0}" y="{y-18}" height="26" width="0"><animate attributeName="width" values="0;{full:.0f}" begin="{tcur:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
            parts.append(f'<g clip-path="url(#c{i})"><text x="{x0}" y="{y}" class="t"><tspan class="pr">❯</tspan> <tspan class="cm">{txt}</tspan></text></g>')
            tcur += dur + 0.25
        else:
            cls = "ok" if kind == "ok" else "o"
            parts.append(f'<text x="{x0+18}" y="{y}" class="t {cls}" opacity="0"><set attributeName="opacity" to="1" begin="{tcur:.2f}s" fill="freeze"/>{txt.replace("&", "&amp;")}</text>')
            tcur += 0.18
    last_y = y0 + (len(TERM_LINES) - 1) * lh
    cur_x = x0 + 18 + len(TERM_LINES[-1][1]) * cw + 6
    cursor = (f'<rect x="{cur_x:.0f}" y="{last_y-14}" width="9" height="18" fill="{p["cyan"]}" opacity="0">'
              f'<set attributeName="opacity" to="1" begin="{tcur:.2f}s" fill="freeze"/>'
              f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" begin="{tcur:.2f}s" repeatCount="indefinite"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Terminal intro</title>
<desc id="d">A terminal types out: whoami, AI Engineer with about 1 year 2 months shipping agentic AI and LLM apps. Now: Associate Data Analyst, AI Automation at Zinnov (Draup), learning in public with #AIEngineerIn150Days. Stack: LangGraph, Google ADK, MCP, FastAPI, FAISS plus BM25, DeepEval. Status: open to AI, LLM and agentic engineer roles.</desc>
<defs>{"".join(clips)}</defs>
<style>
.t{{font:400 14px {MONO};fill:{p["sub"]};white-space:pre}}
.pr{{fill:{p["green"]};font-weight:700}} .cm{{fill:{p["text"]};font-weight:600}}
.o{{fill:{p["sub"]}}} .ok{{fill:{p["cyan"]};font-weight:600}}
.ttl{{font:500 12px {MONO};fill:{p["muted"]}}}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{p["chrome"]}" stroke="{p["border"]}"/>
<path d="M1 15 a14 14 0 0 1 14 -14 H{W-15} a14 14 0 0 1 14 14 V44 H1 Z" fill="{p["bg2"]}"/>
<line x1="1" y1="44" x2="{W-1}" y2="44" stroke="{p["border"]}"/>
<circle cx="26" cy="23" r="6" fill="#ff5f57"/><circle cx="46" cy="23" r="6" fill="#febc2e"/><circle cx="66" cy="23" r="6" fill="#28c840"/>
<text x="{W/2}" y="27" text-anchor="middle" class="ttl">selvin@ai-engineer: ~</text>
{"".join(parts)}
{cursor}
</svg>
'''


def divider(t):
    p = PAL[t]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="28" viewBox="0 0 1200 28" role="img" aria-label="Section divider">
<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="40" y1="14" x2="1160" y2="14"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/><stop offset=".2" stop-color="{p["cyan"]}" stop-opacity=".55"/><stop offset=".5" stop-color="{p["violet"]}" stop-opacity=".7"/><stop offset=".8" stop-color="{p["green"]}" stop-opacity=".55"/><stop offset="1" stop-color="{p["green"]}" stop-opacity="0"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{p["cyan"]}" stop-opacity=".9"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity="0"/></radialGradient></defs>
<path id="ln" d="M40 14 H1160" stroke="url(#g)" stroke-width="1.5" fill="none"/>
<g fill="{p["node"]}" stroke="{p["violet"]}" stroke-width="1.5"><circle cx="300" cy="14" r="4"/><circle cx="600" cy="14" r="5"/><circle cx="900" cy="14" r="4"/></g>
<circle r="14" fill="url(#glow)"><animateMotion dur="6s" repeatCount="indefinite" path="M40 14 H1160"/></circle>
<circle r="3" fill="{p["cyan"]}"><animateMotion dur="6s" repeatCount="indefinite" path="M40 14 H1160"/></circle>
</svg>
'''


for t in ("dark", "light"):
    for name, fn in (("hero", hero), ("terminal", terminal), ("divider", divider)):
        with open(f"{OUT}/{name}-{t}.svg", "w") as f:
            f.write(fn(t))
print("ok")
