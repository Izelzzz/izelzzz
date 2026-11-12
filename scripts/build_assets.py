#!/usr/bin/env python3
"""Generate the animated SVG artwork used by the profile README.

Run from the repository root:  python3 scripts/build_assets.py

Every asset is self-contained (no external fonts, images or scripts) because
GitHub serves README images through a sanitising proxy. Animation is SMIL/CSS
only. Each asset is emitted in four variants: {desktop, mobile} x {dark, light}.
"""
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = Path(__file__).resolve().parent / "icons"

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": dict(
        card="#0E1126", card2="#151838", stroke="#2A2E55", ink="#F3ECDE",
        mute="#9B9CBB", gold="#F6C177", coral="#F28B6C", rose="#E58BA5",
        violet="#9C9AE6",
        sky=[(0, "#060817"), (0.5, "#0F1233"), (0.78, "#2A1D49"),
             (0.92, "#7A3F58"), (1, "#D9785A")],
        hill="#070919", hill_op=(0.55, 0.75, 0.95),
        sun=("#FFE9BD", "#F6A96A"), star="#FFFFFF",
    ),
    "light": dict(
        card="#FFFCF7", card2="#FDF1E3", stroke="#EBD9C2", ink="#1F2140",
        mute="#6F6C84", gold="#C17F22", coral="#D8603F", rose="#C7597A",
        violet="#5A57A8",
        sky=[(0, "#FFFCF6"), (0.5, "#FEF1E0"), (0.8, "#FBD9BC"),
             (0.93, "#F6B796"), (1, "#EE9577")],
        hill="#E98A6A", hill_op=(0.22, 0.34, 0.5),
        sun=("#FFFFFF", "#FFC978"), star="#D8603F",
    ),
}


def icon_path(name):
    return re.search(r'<path d="([^"]+)"', (ICONS / f"{name}.svg").read_text()).group(1)


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{label}">'
        f"<title>{label}</title>{body}</svg>\n"
    )


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def text(x, y, s, size, fill, font=SANS, weight=400, anchor="start", extra=""):
    s = re.sub(r"&(?!#)", "&amp;", s)
    return (
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'
    )


def card_bg(t, w, h, uid):
    return (
        f'<defs><linearGradient id="cb{uid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["card"]}"/>'
        f'<stop offset="1" stop-color="{t["card2"]}"/></linearGradient></defs>'
        f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" '
        f'fill="url(#cb{uid})" stroke="{t["stroke"]}"/>'
    )


def wave_path(w, h, y, amp, period):
    pts = []
    x = 0
    while x <= w + period + 10:
        pts.append(f"{x},{y + amp * math.sin(2 * math.pi * x / period):.1f}")
        x += 10
    return f'M{" L".join(pts)} L{w + period + 10},{h} L0,{h} Z'


def waves(t, w, h, ys, amps, periods, durs):
    out = ""
    for y, amp, period, dur, op in zip(ys, amps, periods, durs, t["hill_op"]):
        out += (
            f'<path d="{wave_path(w, h, y, amp, period)}" fill="{t["hill"]}" '
            f'fill-opacity="{op}"><animateTransform attributeName="transform" '
            f'type="translate" from="0 0" to="-{period} 0" dur="{dur}s" '
            f'repeatCount="indefinite"/></path>'
        )
    return out


# --------------------------------------------------------------------- banner
def banner(theme, mobile):
    t = THEMES[theme]
    w, h = (600, 340) if mobile else (1200, 340)
    hy = h - 52
    sx = w * 0.8
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in t["sky"])
    d = (
        f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{t["sun"][1]}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{t["sun"][1]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="disc" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["sun"][0]}"/><stop offset="1" stop-color="{t["sun"][1]}"/></linearGradient>'
        f'<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["gold"]}"/><stop offset="1" stop-color="{t["coral"]}"/></linearGradient>'
        f'<clipPath id="clip"><rect width="{w}" height="{h}" rx="18"/></clipPath>'
        "<style>.fi{opacity:0;animation:fi 1.4s ease-out forwards}"
        ".d1{animation-delay:.2s}.d2{animation-delay:.6s}.d3{animation-delay:1.1s}.d4{animation-delay:1.6s}"
        "@keyframes fi{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
        ".rule{stroke-dasharray:72;stroke-dashoffset:72;animation:dr 1.2s 1.3s ease-out forwards}"
        "@keyframes dr{to{stroke-dashoffset:0}}"
        "@media (prefers-reduced-motion:reduce){.fi,.rule{animation:none;opacity:1;stroke-dashoffset:0}}"
        "</style></defs>"
    )
    b = f'<g clip-path="url(#clip)"><rect width="{w}" height="{h}" fill="url(#sky)"/>'

    rnd = random.Random(7)
    if theme == "dark":
        for _ in range(26 if mobile else 54):
            x, y = rnd.uniform(0, w), rnd.uniform(8, hy - 70)
            r, dur = rnd.uniform(0.5, 1.5), rnd.uniform(2.5, 6)
            b += (
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{t["star"]}" opacity=".7">'
                f'<animate attributeName="opacity" values=".15;.9;.15" dur="{dur:.1f}s" '
                f'begin="-{rnd.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>'
            )
    else:
        for _ in range(8 if mobile else 14):
            x, y = rnd.uniform(w * 0.3, w), rnd.uniform(30, hy - 60)
            ln, dur = rnd.uniform(30, 90), rnd.uniform(14, 26)
            b += (
                f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + ln:.0f}" y2="{y:.0f}" stroke="{t["star"]}" '
                f'stroke-opacity=".16" stroke-linecap="round"><animateTransform attributeName="transform" '
                f'type="translate" values="0 0;24 0;0 0" dur="{dur:.0f}s" repeatCount="indefinite"/></line>'
            )

    # sun: glow, expanding ripples, rising disc
    b += (
        f'<circle cx="{sx}" cy="{hy - 6}" r="170" fill="url(#glow)">'
        f'<animate attributeName="r" values="150;185;150" dur="7s" repeatCount="indefinite"/></circle>'
    )
    for i in range(3):
        b += (
            f'<circle cx="{sx}" cy="{hy - 6}" r="50" fill="none" stroke="{t["gold"]}" stroke-width="1">'
            f'<animate attributeName="r" values="48;250" dur="9s" begin="-{i * 3}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".45;0" dur="9s" begin="-{i * 3}s" repeatCount="indefinite"/></circle>'
        )
    b += (
        f'<circle cx="{sx}" cy="{hy - 6}" r="46" fill="url(#disc)">'
        f'<animate attributeName="cy" values="{hy + 56};{hy - 6}" dur="4.5s" calcMode="spline" '
        f'keyTimes="0;1" keySplines=".2 .8 .2 1" fill="freeze"/></circle>'
    )
    b += waves(t, w, h, (hy + 4, hy + 16, hy + 30), (7, 9, 6), (300, 400, 240), (38, 26, 18))

    x = 40 if mobile else 76
    name_size = 82 if mobile else 96
    b += f'<g class="fi d1">{text(x + 2, 92, "HELLO, I&#8217;M", 13, t["gold"], MONO, 500, extra='letter-spacing="4"')}</g>'
    b += f'<g class="fi d2">{text(x - 4, 178, "Izel", name_size, t["ink"], SERIF, 600, extra='letter-spacing="1"')}</g>'
    b += f'<line class="rule" x1="{x}" y1="198" x2="{x + 72}" y2="198" stroke="url(#rule)" stroke-width="2.5" stroke-linecap="round"/>'
    b += (
        f'<g class="fi d3"><text x="{x}" y="236" font-family="{SERIF}" font-size="{23 if mobile else 27}" '
        f'font-style="italic" fill="{t["ink"]}">Build with AI. '
        f'<tspan fill="{t["gold"]}">Think beyond AI.</tspan></text></g>'
    )
    ls = 'letter-spacing="2.4"'
    if mobile:
        b += f'<g class="fi d4">{text(x, 262, "PRODUCT-MINDED BUILDER", 10.5, t["mute"], MONO, extra=ls)}</g>'
    else:
        b += f'<g class="fi d4">{text(x, 264, "PRODUCT-MINDED BUILDER  &#183;  AI &#215; SOFTWARE &#215; HUMAN CREATIVITY", 12, t["mute"], MONO, extra=ls)}</g>'
    b += "</g>"
    return svg(w, h, d + b, "Izel. Build with AI. Think beyond AI.")


# -------------------------------------------------------------- how I work
STAGES = [
    ("Question", "worth building?", "why"),
    ("Spec", "criteria before code", "criteria"),
    ("Build", "agents + artifacts", "agents"),
    ("Verify", "independent, evidenced", "evidence"),
    ("Ship", "a human decides", "human"),
]


def pause_gate(t, x, y, s):
    return (
        f'<rect x="{x - s / 2}" y="{y - s / 2}" width="{s}" height="{s}" rx="4" fill="{t["card"]}" stroke="{t["gold"]}"/>'
        f'<rect x="{x - s * .2}" y="{y - s * .22}" width="{s * .12:.1f}" height="{s * .44:.1f}" fill="{t["gold"]}"/>'
        f'<rect x="{x + s * .08:.1f}" y="{y - s * .22}" width="{s * .12:.1f}" height="{s * .44:.1f}" fill="{t["gold"]}"/>'
    )


def how(theme, mobile):
    t = THEMES[theme]
    w, h = (440, 212) if mobile else (880, 226)
    m = 46 if mobile else 92
    gap = (w - 2 * m) / 4
    xs = [m + gap * i for i in range(5)]
    y = 98
    span = xs[-1] - xs[0]
    b = card_bg(t, w, h, "h")
    b += (
        f'<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["gold"]}"/><stop offset="1" stop-color="{t["coral"]}"/></linearGradient></defs>'
    )
    b += f'<line x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{t["stroke"]}" stroke-width="2"/>'
    b += (
        f'<path d="M{xs[0]},{y} H{xs[-1]}" stroke="url(#pg)" stroke-width="2" fill="none" '
        f'stroke-dasharray="{span}" stroke-dashoffset="{span}">'
        f'<animate attributeName="stroke-dashoffset" values="{span};0;0;{span}" keyTimes="0;.6;.94;1" '
        f'dur="10s" repeatCount="indefinite"/></path>'
    )
    # rework loop: Verify -> Build
    ax, bx, top = xs[3], xs[2], (34 if mobile else 30)
    b += (
        f'<path d="M{ax},{y - 20} C{ax - 14},{top} {bx + 14},{top} {bx},{y - 22}" fill="none" stroke="{t["rose"]}" '
        f'stroke-width="1.3" stroke-dasharray="4 5" stroke-linecap="round">'
        f'<animate attributeName="stroke-dashoffset" values="18;0" dur="1.6s" repeatCount="indefinite"/></path>'
        f'<path d="M{bx - 4},{y - 28} L{bx},{y - 20} L{bx + 6},{y - 27}" fill="none" stroke="{t["rose"]}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    b += text((ax + bx) / 2, top - 4 if mobile else top + 2, "rework" if mobile else "rework, with the evidence attached",
              9 if mobile else 10.5, t["rose"], MONO, anchor="middle")
    for i, (name, cap, short) in enumerate(STAGES):
        x = xs[i]
        ti = max(0.01, 0.6 * i / 4)
        kt = f"0;{ti:.3f};{ti + 0.04:.3f};.94;1"
        b += (
            f'<circle cx="{x}" cy="{y}" r="15" fill="{t["card"]}" stroke="{t["stroke"]}" stroke-width="1.5">'
            f'<animate attributeName="stroke" values="{t["stroke"]};{t["stroke"]};{t["gold"]};{t["gold"]};{t["stroke"]}" '
            f'keyTimes="{kt}" dur="10s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x}" cy="{y}" r="5" fill="{t["gold"]}" opacity=".25">'
            f'<animate attributeName="opacity" values=".25;.25;1;1;.25" keyTimes="{kt}" dur="10s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="5;5;7;5;5" keyTimes="{kt}" dur="10s" repeatCount="indefinite"/></circle>'
        )
        b += text(x, y + 46, name, 16 if mobile else 20, t["ink"], SERIF, 600, "middle")
        b += text(x, y + 64, short if mobile else cap, 9 if mobile else 10.5, t["mute"], MONO, anchor="middle")
    for i in (1, 3):
        b += pause_gate(t, (xs[i] + xs[i + 1]) / 2, y, 14 if mobile else 18)
    ly = h - 22
    lab = "human approval gate" if mobile else "human approval before anything irreversible"
    lw = len(lab) * (5.5 if mobile else 6.4)
    b += pause_gate(t, w / 2 - lw / 2 - 12, ly - 4, 12)
    b += text(w / 2 + 4, ly, lab, 9 if mobile else 10.5, t["mute"], MONO, anchor="middle")
    return svg(w, h, b, "How I work with AI: question, spec, build, verify, ship, with human approval gates and an evidence-driven rework loop.")


# ------------------------------------------------------------ project cards
def motif_morgan(t, ox, oy):
    g = f'<g transform="translate({ox},{oy})">'
    cols = [t["gold"], t["coral"], t["rose"], t["violet"]]
    for i, c in enumerate(cols):
        y = 12 + i * 32
        p = f"M22,{y} C70,{y} 70,60 104,60"
        g += f'<path d="{p}" fill="none" stroke="{t["stroke"]}" stroke-width="1.4"/>'
        g += f'<circle cx="16" cy="{y}" r="6" fill="{c}" fill-opacity=".9"/>'
        g += (
            f'<circle r="2.6" fill="{c}"><animateMotion path="{p}" dur="2.8s" begin="-{i * 0.7}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="2.8s" begin="-{i * 0.7}s" repeatCount="indefinite"/></circle>'
        )
    g += (
        f'<circle cx="118" cy="60" r="14" fill="{t["card"]}" stroke="{t["gold"]}" stroke-width="1.6"/>'
        f'<circle cx="118" cy="60" r="14" fill="none" stroke="{t["gold"]}">'
        f'<animate attributeName="r" values="14;24" dur="2.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".6;0" dur="2.8s" repeatCount="indefinite"/></circle>'
        f'<path d="M112,60 l4.5,4.5 l8,-9" fill="none" stroke="{t["gold"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="132" y1="60" x2="158" y2="60" stroke="{t["stroke"]}" stroke-width="1.4"/>'
        f'<rect x="158" y="38" width="34" height="44" rx="5" fill="{t["card"]}" stroke="{t["stroke"]}" stroke-width="1.4"/>'
    )
    for j, c in enumerate([t["coral"], t["gold"], t["violet"]]):
        g += (
            f'<line x1="165" y1="{50 + j * 10}" x2="185" y2="{50 + j * 10}" stroke="{c}" stroke-width="2.4" stroke-linecap="round" '
            f'stroke-dasharray="20" stroke-dashoffset="20"><animate attributeName="stroke-dashoffset" values="20;20;0;0" '
            f'keyTimes="0;{0.3 + j * 0.15:.2f};{0.45 + j * 0.15:.2f};1" dur="4.2s" repeatCount="indefinite"/></line>'
        )
    return g + "</g>"


def motif_eos(t, ox, oy):
    g = f'<g transform="translate({ox},{oy})">'
    cx, cy, r = 100, 104, 84
    g += (
        f'<defs><clipPath id="hz"><rect x="0" y="0" width="200" height="{cy}"/></clipPath>'
        f'<radialGradient id="eg"><stop offset="0" stop-color="{t["gold"]}" stop-opacity=".5"/>'
        f'<stop offset="1" stop-color="{t["gold"]}" stop-opacity="0"/></radialGradient></defs>'
        f'<g clip-path="url(#hz)"><circle cx="{cx}" cy="{cy}" r="52" fill="url(#eg)">'
        f'<animate attributeName="r" values="44;58;44" dur="6s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="22" fill="{t["gold"]}"/>'
        f'<path d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}" fill="none" stroke="{t["stroke"]}" stroke-width="1.4" stroke-dasharray="2 6" stroke-linecap="round"/></g>'
        f'<line x1="4" y1="{cy}" x2="196" y2="{cy}" stroke="{t["stroke"]}" stroke-width="1.4"/>'
    )
    n = 6
    for i in range(n):
        a = math.pi - math.pi * (i + 0.5) / n
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        t0 = 0.02 + 0.11 * i
        kt = f"0;{t0:.2f};{t0 + 0.05:.2f};.9;1"
        col = t["coral"] if i in (0, 3, 4) else t["gold"]
        g += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="{t["card"]}" stroke="{t["stroke"]}" stroke-width="1.4"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{col}" opacity=".18">'
            f'<animate attributeName="opacity" values=".18;.18;1;1;.18" keyTimes="{kt}" dur="7s" repeatCount="indefinite"/></circle>'
        )
    return g + "</g>"


def motif_skill(t, ox, oy):
    g = f'<g transform="translate({ox},{oy})">'
    cols = [t["gold"], t["coral"], t["rose"], t["violet"]]
    for i, c in enumerate(cols):
        y = 12 + i * 32
        p = f"M40,60 C92,60 92,{y} 146,{y}"
        kt = f"0;{i * 0.25:.2f};{i * 0.25 + 0.05:.2f};{i * 0.25 + 0.22:.2f};{min(1, i * 0.25 + 0.25):.2f}"
        if i == 0:
            kt = "0;.001;.05;.22;.25"
        tail = "" if i == 3 else ";1"
        vals_tail = "" if i == 3 else f';{t["stroke"]}'
        g += (
            f'<path d="{p}" fill="none" stroke="{t["stroke"]}" stroke-width="1.6" stroke-linecap="round">'
            f'<animate attributeName="stroke" values="{t["stroke"]};{t["stroke"]};{c};{c};{t["stroke"]}{vals_tail}" '
            f'keyTimes="{kt}{tail}" dur="6s" repeatCount="indefinite"/></path>'
            f'<rect x="148" y="{y - 9}" width="44" height="18" rx="9" fill="{t["card"]}" stroke="{c}" stroke-width="1.3"/>'
            f'<line x1="158" y1="{y}" x2="{174 + (i % 2) * 8}" y2="{y}" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/>'
        )
    g += (
        f'<g transform="translate(24,60)"><rect x="-13" y="-13" width="26" height="26" rx="5" fill="{t["card"]}" '
        f'stroke="{t["gold"]}" stroke-width="1.6" transform="rotate(45)"/>'
        f'<circle r="4" fill="{t["gold"]}"><animate attributeName="r" values="3;5;3" dur="1.5s" repeatCount="indefinite"/></circle></g>'
    )
    return g + "</g>"


PROJECTS = [
    ("morgan-review", "01  &#8212;  MULTI-AGENT PR REVIEW", "Morgan-review",
     "A self-hosted review service. Dimension reviewers hunt in parallel, a verifier "
     "re-checks every finding, and code confirms each citation before a comment is posted.",
     "PYTHON  &#183;  DOCKER  &#183;  GITHUB ACTIONS", motif_morgan),
    ("eos-workbench", "02  &#8212;  AI DEV WORKBENCH", "Eos-workbench",
     "A Claude Code mod named after the goddess of dawn. /eos wakes a value-stream "
     "pipeline, spec to deploy, with human approval gates and flow metrics for every stage.",
     "CLAUDE CODE MOD  &#183;  SUBAGENTS  &#183;  HOOKS", motif_eos),
    ("izel-skill", "03  &#8212;  PRODUCT SKILLS FOR AGENTS", "izel-skill",
     "Executable product-management skills. Decide whether an idea is worth building "
     "first, then refine, research, and write the product spec and the tech spec.",
     "AGENT SKILLS  &#183;  SPEC-DRIVEN", motif_skill),
]


def project(theme, mobile, p):
    t = THEMES[theme]
    slug, kicker, name, desc, tags, motif = p
    ls = 'letter-spacing="1.8"'
    if mobile:
        lines = wrap(desc, 54)
        w, h = 440, 264 + 20 * len(lines)
        b = card_bg(t, w, h, "p") + motif(t, 120, 22)
        tx, ty = 26, 172
    else:
        lines = wrap(desc, 78)
        w, h = 880, 196
        b = card_bg(t, w, h, "p") + motif(t, 34, 38)
        b += f'<line x1="262" y1="28" x2="262" y2="{h - 28}" stroke="{t["stroke"]}"/>'
        tx, ty = 292, 46
    b += text(tx, ty, kicker, 10.5, t["gold"], MONO, 500, extra=ls)
    b += text(tx, ty + 34, name, 27, t["ink"], SERIF, 600)
    for i, ln in enumerate(lines):
        b += text(tx, ty + 60 + i * 20, ln, 14, t["mute"], SANS)
    b += text(tx, h - 24, tags, 10, t["mute"], MONO, extra=ls + ' opacity=".8"')
    b += (
        f'<path d="M{w - 40},38 l10,-10 M{w - 38},28 h8 v8" fill="none" stroke="{t["gold"]}" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round"><animateTransform attributeName="transform" type="translate" '
        f'values="0 0;2 -2;0 0" dur="2.4s" repeatCount="indefinite"/></path>'
    )
    return svg(w, h, b, f"{name}: {desc}")


# ------------------------------------------------------------- tech stack
STACK = [
    ("python", "Python"), ("typescript", "TypeScript"), ("git", "Git"),
    ("githubactions", "GitHub Actions"), ("docker", "Docker"), ("cloudflare", "Cloudflare"),
    ("claude", "Claude Code"), ("openai", "Codex"), ("cursor", "Cursor"), ("figma", "Figma"),
]


def stack(theme, mobile):
    t = THEMES[theme]
    cols = 5 if mobile else 10
    w = 500 if mobile else 1000
    rows = math.ceil(len(STACK) / cols)
    h = 34 + rows * 96
    gap = (w - 60) / cols
    b = card_bg(t, w, h, "s")
    for i, (ic, label) in enumerate(STACK):
        cx = 30 + gap * (i % cols) + gap / 2
        cy = 26 + (i // cols) * 96
        d = i * 0.35
        b += (
            f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="4s" '
            f'begin="-{d:.2f}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".4 0 .6 1;.4 0 .6 1"/>'
            f'<circle cx="{cx:.1f}" cy="{cy + 28}" r="27" fill="{t["card"]}" stroke="{t["stroke"]}"/>'
            f'<path d="{icon_path(ic)}" transform="translate({cx - 13:.1f},{cy + 15}) scale(1.0833)" fill="{t["ink"]}">'
            f'<animate attributeName="fill" values="{t["ink"]};{t["ink"]};{t["gold"]};{t["ink"]};{t["ink"]}" '
            f'keyTimes="0;{i * 0.08:.2f};{i * 0.08 + 0.06:.2f};{i * 0.08 + 0.14:.2f};1" dur="9s" repeatCount="indefinite"/></path></g>'
        )
        b += text(f"{cx:.1f}", cy + 78, label, 11.5, t["mute"], SANS, 500, "middle")
    return svg(w, h, b, "Stack and working environment: " + ", ".join(l for _, l in STACK))


# ---------------------------------------------------------------- beyond
def ill_squash(t):
    p = "M36,52 L150,22 L104,84 L36,52"
    return (
        f'<path d="M152,6 V86 H12" fill="none" stroke="{t["stroke"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="152" y1="46" x2="140" y2="46" stroke="{t["coral"]}" stroke-width="1.5"/>'
        f'<path d="{p}" fill="none" stroke="{t["gold"]}" stroke-opacity=".28" stroke-dasharray="2 5" stroke-linecap="round"/>'
        f'<g transform="translate(26,58)"><g><animateTransform attributeName="transform" type="rotate" values="-30;12;-30" '
        f'keyTimes="0;.12;1" dur="2.6s" repeatCount="indefinite"/>'
        f'<ellipse cx="0" cy="-22" rx="9" ry="13" fill="none" stroke="{t["ink"]}" stroke-width="1.8"/>'
        f'<line x1="0" y1="-9" x2="0" y2="12" stroke="{t["ink"]}" stroke-width="2.2" stroke-linecap="round"/></g></g>'
        f'<circle r="4" fill="{t["gold"]}"><animateMotion path="{p}" dur="2.6s" repeatCount="indefinite" '
        f'keyPoints="0;.42;.7;1" keyTimes="0;.36;.64;1" calcMode="linear"/></circle>'
    )


def ill_music(t):
    rnd = random.Random(3)
    out = (
        f'<defs><linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{t["coral"]}"/>'
        f'<stop offset="1" stop-color="{t["gold"]}"/></linearGradient></defs>'
    )
    for i in range(13):
        hs = [rnd.randint(10, 70) for _ in range(4)]
        hs.append(hs[0])
        x = 14 + i * 11
        dur = rnd.uniform(1.1, 2.0)
        out += (
            f'<rect x="{x}" width="5" rx="2.5" fill="url(#eq)" y="{86 - hs[0]}" height="{hs[0]}">'
            f'<animate attributeName="height" values="{";".join(map(str, hs))}" dur="{dur:.2f}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;.25;.5;.75;1" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/>'
            f'<animate attributeName="y" values="{";".join(str(86 - v) for v in hs)}" dur="{dur:.2f}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;.25;.5;.75;1" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/></rect>'
        )
    return out + f'<line x1="10" y1="88" x2="158" y2="88" stroke="{t["stroke"]}" stroke-width="1.5" stroke-linecap="round"/>'


def ill_games(t):
    rows = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    s = 9
    px = ""
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "X":
                col = t["rose"] if (r + c) % 3 else t["coral"]
                px += f'<rect x="{(c - 3.5) * s:.1f}" y="{(r - 3) * s:.1f}" width="{s - 1}" height="{s - 1}" rx="1.5" fill="{col}"/>'
    out = (
        f'<g transform="translate(84,48)"><g>{px}<animateTransform attributeName="transform" type="scale" '
        f'values="1;1.14;1;1.08;1;1" keyTimes="0;.12;.26;.38;.52;1" dur="1.8s" repeatCount="indefinite"/></g></g>'
    )
    for x, y, d in ((30, 22, 0), (142, 30, 0.8), (36, 76, 1.5), (134, 78, 2.1)):
        out += (
            f'<path d="M{x - 4},{y} h8 M{x},{y - 4} v8" stroke="{t["gold"]}" stroke-width="1.6" stroke-linecap="round">'
            f'<animate attributeName="opacity" values="0;1;0" dur="2.8s" begin="-{d}s" repeatCount="indefinite"/></path>'
        )
    return out


def ill_reflect(t):
    out = f'<g transform="translate(84,46)">'
    out += (
        f'<circle r="20" fill="{t["gold"]}" opacity=".14"><animate attributeName="r" values="14;24;14" dur="5s" repeatCount="indefinite"/></circle>'
        f'<circle r="5" fill="{t["gold"]}"/>'
    )
    for r, dur, col, pr in ((20, 9, t["coral"], 3), (32, 15, t["violet"], 3.5), (44, 24, t["rose"], 2.6)):
        out += (
            f'<ellipse rx="{r * 1.6:.0f}" ry="{r * .78:.0f}" fill="none" stroke="{t["stroke"]}" stroke-width="1.2"/>'
            f'<circle r="{pr}" fill="{col}"><animateMotion dur="{dur}s" repeatCount="indefinite" '
            f'path="M{r * 1.6:.0f},0 A{r * 1.6:.0f},{r * .78:.0f} 0 1 1 -{r * 1.6:.0f},0 A{r * 1.6:.0f},{r * .78:.0f} 0 1 1 {r * 1.6:.0f},0"/></circle>'
        )
    return out + "</g>"


BEYOND = [
    ("Squash", "discipline &#183; adaptability", ill_squash),
    ("Music", "jazz &#183; r&b &#183; funk", ill_music),
    ("Video Games", "stories filled with love", ill_games),
    ("Reflection", "consciousness &#183; meaning", ill_reflect),
]


def beyond(theme, mobile):
    t = THEMES[theme]
    cols = 2 if mobile else 4
    w = 440 if mobile else 880
    gap = 16
    tw = (w - gap * (cols - 1)) / cols
    th = 178
    rows = len(BEYOND) // cols
    h = rows * th + (rows - 1) * gap
    b = (
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["card"]}"/>'
        f'<stop offset="1" stop-color="{t["card2"]}"/></linearGradient></defs>'
    )
    for i, (title, cap, ill) in enumerate(BEYOND):
        x = (i % cols) * (tw + gap)
        y = (i // cols) * (th + gap)
        b += (
            f'<g transform="translate({x:.1f},{y})"><rect x="1" y="1" width="{tw - 2:.1f}" height="{th - 2}" rx="16" '
            f'fill="url(#bg)" stroke="{t["stroke"]}"/><g transform="translate({(tw - 168) / 2:.1f},14)">{ill(t)}</g>'
            + text(f"{tw / 2:.1f}", 136, title, 18, t["ink"], SERIF, 600, "middle")
            + text(f"{tw / 2:.1f}", 156, cap, 10, t["mute"], MONO, anchor="middle", extra='letter-spacing=".6"')
            + "</g>"
        )
    return svg(w, h, b, "Beyond the terminal: squash, music, video games, reflection and discovery.")


# ------------------------------------------------------- pills / dividers
def pill(theme, kind, label):
    t = THEMES[theme]
    w = round(52 + len(label) * 7.6)
    h = 32
    if kind == "web":
        ic = (
            f'<g fill="none" stroke="{t["gold"]}" stroke-width="1.4"><circle cx="22" cy="16" r="7"/>'
            f'<ellipse cx="22" cy="16" rx="3" ry="7"/><line x1="15" y1="16" x2="29" y2="16"/></g>'
        )
    elif kind == "x":
        ic = f'<path d="{icon_path("x")}" transform="translate(15.5,9.5) scale(.54)" fill="{t["gold"]}"/>'
    else:
        ic = (
            f'<g fill="none" stroke="{t["gold"]}" stroke-width="1.4" stroke-linejoin="round">'
            f'<rect x="15" y="10.5" width="14" height="11" rx="2"/><path d="M15.5,11.5 l6.5,5.5 l6.5,-5.5"/></g>'
        )
    b = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="{t["card"]}" stroke="{t["stroke"]}">'
        f'<animate attributeName="stroke" values="{t["stroke"]};{t["gold"]};{t["stroke"]}" dur="6s" repeatCount="indefinite"/></rect>'
        + ic + text(38, 20.5, label, 12.5, t["ink"], MONO, 500)
    )
    return svg(w, h, b, label)


def divider(theme):
    t = THEMES[theme]
    w, h = 880, 14
    b = (
        f'<defs><linearGradient id="dv" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["gold"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["gold"]}"/><stop offset="1" stop-color="{t["coral"]}" stop-opacity="0"/></linearGradient></defs>'
        f'<line x1="0" y1="7" x2="{w}" y2="7" stroke="{t["stroke"]}"/>'
        f'<rect x="0" y="6.25" width="220" height="1.5" fill="url(#dv)">'
        f'<animate attributeName="x" values="-220;{w}" dur="7s" repeatCount="indefinite"/></rect>'
        f'<circle cx="{w / 2}" cy="7" r="3" fill="{t["gold"]}"><animate attributeName="opacity" values=".4;1;.4" dur="3.5s" repeatCount="indefinite"/></circle>'
    )
    return svg(w, h, b, "divider")


def footer(theme):
    t = THEMES[theme]
    w, h = 880, 90
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in t["sky"])
    b = (
        f'<defs><linearGradient id="fs" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
        f'<clipPath id="fc"><rect width="{w}" height="{h}" rx="16"/></clipPath></defs>'
        f'<g clip-path="url(#fc)"><rect width="{w}" height="{h}" fill="url(#fs)"/>'
        + waves(t, w, h, (54, 64, 74), (5, 7, 4), (220, 300, 180), (30, 22, 15))
        + f'<text x="{w / 2}" y="36" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="17" '
        f'fill="{t["ink"]}">Build with AI. <tspan fill="{t["gold"]}">Think beyond AI.</tspan></text></g>'
    )
    return svg(w, h, b, "Build with AI. Think beyond AI.")


def main():
    OUT.mkdir(exist_ok=True)
    files = {}
    for theme in THEMES:
        for mobile in (False, True):
            sfx = f'{"-mobile" if mobile else ""}-{theme}.svg'
            files[f"banner{sfx}"] = banner(theme, mobile)
            files[f"how-i-work{sfx}"] = how(theme, mobile)
            files[f"stack{sfx}"] = stack(theme, mobile)
            files[f"beyond{sfx}"] = beyond(theme, mobile)
            for p in PROJECTS:
                files[f"project-{p[0]}{sfx}"] = project(theme, mobile, p)
        files[f"divider-{theme}.svg"] = divider(theme)
        files[f"footer-{theme}.svg"] = footer(theme)
        files[f"link-web-{theme}.svg"] = pill(theme, "web", "izelzzz.com")
        files[f"link-x-{theme}.svg"] = pill(theme, "x", "@izelzzz")
        files[f"link-mail-{theme}.svg"] = pill(theme, "mail", "965670101@qq.com")
    for name, content in files.items():
        (OUT / name).write_text(content)
    print(f"wrote {len(files)} files to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
