"""Shared theme + helpers for the AGENT_OS profile art (dark + light).

Pure standard library. Everything renders on github.com: SVG + CSS/SMIL animation, no JS.
"""
import os
from xml.sax.saxutils import escape as _esc

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ASSETS = os.path.join(ROOT, "assets")

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
CHAR = 0.602  # monospace advance as a fraction of font-size (Menlo / DejaVu Sans Mono / Consolas ~0.55-0.60)

PAL = {
    "dark": dict(
        bg0="#050814", bg1="#0a1024", panel="#0b1328", panel2="#0e1833", grid="#16233f", line="#22335a",
        text="#e6f1ff", sub="#a9bbd6", muted="#6a7fa3", cyan="#22d3ee", violet="#a78bfa", pink="#f472b6",
        green="#34d399", amber="#fbbf24", red="#fb7185", glow="1", chrome="#081022"),
    "light": dict(
        bg0="#f8fafc", bg1="#eef3fb", panel="#ffffff", panel2="#f3f6fc", grid="#dbe3f0", line="#c8d4e8",
        text="#0b1220", sub="#334155", muted="#5b6b85", cyan="#0e7490", violet="#6d28d9", pink="#be185d",
        green="#047857", amber="#b45309", red="#be123c", glow="0", chrome="#ffffff"),
}
THEMES = ("dark", "light")


def esc(s):
    return _esc(str(s), {'"': "&quot;"})


def tw(text, size):
    """Approximate width of monospace text."""
    return len(text) * size * CHAR


def glow_filter(p, fid="glow", std=3.2):
    if p["glow"] == "1":
        return (f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
                f'<feGaussianBlur stdDeviation="{std}" result="b"/><feMerge><feMergeNode in="b"/>'
                f'<feMergeNode in="SourceGraphic"/></feMerge></filter>')
    # light theme: no bloom, keep a crisp shape (filter is a no-op so references stay valid)
    return f'<filter id="{fid}"><feOffset dx="0" dy="0"/></filter>'


def svg_open(w, h, title, desc, extra_ns=False):
    ns = ' xmlns:xlink="http://www.w3.org/1999/xlink"' if extra_ns else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{ns} width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>')


BASE_CSS = """
.m{{font-family:{mono}}} .s{{font-family:{sans}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes dash{{to{{stroke-dashoffset:-40}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.in{{opacity:0;animation:fadeUp .6s ease-out forwards}}
.fd{{opacity:0;animation:fade .6s ease-out forwards}}
.bl{{animation:blink 1s steps(1) infinite}}
.pl{{animation:pulse 1.8s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.in,.fd{{opacity:1}}}}
""".format(mono=MONO, sans=SANS)


def hud_corners(x, y, w, h, color, L=16, sw=2):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">'
            f'<path d="M{x} {y+L} V{y} H{x+L}"/><path d="M{x+w-L} {y} H{x+w} V{y+L}"/>'
            f'<path d="M{x} {y+h-L} V{y+h} H{x+L}"/><path d="M{x+w-L} {y+h} H{x+w} V{y+h-L}"/></g>')


def wrap(text, width_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def write(name, theme, svg):
    os.makedirs(ASSETS, exist_ok=True)
    path = os.path.join(ASSETS, f"{name}-{theme}.svg" if theme else f"{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path
