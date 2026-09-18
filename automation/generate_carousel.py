"""
Genera slide del carosello LinkedIn come immagini 1080x1080
usando HTML/CSS renderizzato via Playwright (headless Chromium).

Design: impronta "private banking" con rotazione di palette (mood diverso a
ogni post, stesso linguaggio visivo) per non avere post sempre identici.
"""

import os
import json
import hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright

W, H = 1080, 1080

# ── Font Google ───────────────────────────────────────────────────────────────
FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,900&family=Inter:wght@300;400;500;600;700&display=swap');
"""

# ── Palette a rotazione ───────────────────────────────────────────────────────
# Ogni tema: sfondo (3 stop), accento, accento chiaro, glow. Impronta coerente,
# mood diverso. Il tema è scelto in modo deterministico dall'hash del topic.
THEMES = {
    "oro":     {"bg1": "#070F1A", "bg2": "#0C2036", "bg3": "#060D18",
                "accent": "#C9A24C", "accentLt": "#EBD07A", "glow": "rgba(201,162,76,0.12)"},
    "foresta": {"bg1": "#07130F", "bg2": "#0C2A20", "bg3": "#06120E",
                "accent": "#57B08A", "accentLt": "#A6E6C6", "glow": "rgba(87,176,138,0.14)"},
    "zaffiro": {"bg1": "#080C1C", "bg2": "#122246", "bg3": "#070A16",
                "accent": "#7C96E8", "accentLt": "#BFCEFB", "glow": "rgba(124,150,232,0.14)"},
    "porpora": {"bg1": "#140813", "bg2": "#2C1030", "bg3": "#110711",
                "accent": "#C58AD0", "accentLt": "#E9C4F0", "glow": "rgba(197,138,208,0.14)"},
    "rame":    {"bg1": "#160C08", "bg2": "#301A10", "bg3": "#120A06",
                "accent": "#D68C5C", "accentLt": "#F0BE9E", "glow": "rgba(214,140,92,0.14)"},
}

# Grana sottile (texture) come overlay SVG in data-uri.
GRAIN = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' "
    "baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E"
    "%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E\")"
)


def pick_theme(content: dict) -> dict:
    """Sceglie una palette in modo deterministico dal topic (stesso topic → stesso mood)."""
    override = content.get("theme")
    if override in THEMES:
        return THEMES[override]
    seed = (content.get("topic", "") + content.get("title", "")).encode("utf-8")
    idx = int(hashlib.md5(seed).hexdigest(), 16) % len(THEMES)
    return list(THEMES.values())[idx]


def _theme_css(t: dict) -> str:
    return f"""
:root {{
  --bg1: {t['bg1']}; --bg2: {t['bg2']}; --bg3: {t['bg3']};
  --accent: {t['accent']}; --accent-lt: {t['accentLt']}; --glow: {t['glow']};
  --ink: #FFFFFF; --body: #CBD8E4; --muted: #6F8AA6;
}}
"""

# ── Stili base condivisi ──────────────────────────────────────────────────────
BASE_STYLES = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  width: 1080px; height: 1080px; overflow: hidden;
  background: var(--bg1);
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
.slide {{
  width: 1080px; height: 1080px;
  position: relative; overflow: hidden;
  background:
    radial-gradient(1200px 720px at 12% 6%, var(--glow), transparent 55%),
    radial-gradient(900px 900px at 92% 102%, rgba(255,255,255,0.04), transparent 60%),
    linear-gradient(150deg, var(--bg1) 0%, var(--bg2) 58%, var(--bg3) 100%);
}}
.grain {{
  position: absolute; inset: 0;
  background-image: {GRAIN}; background-size: 300px 300px;
  opacity: 0.055; mix-blend-mode: overlay; pointer-events: none;
}}
.vignette {{
  position: absolute; inset: 0;
  box-shadow: inset 0 0 220px rgba(0,0,0,0.5); pointer-events: none;
}}
.edge {{
  position: absolute; left: 0; top: 0; width: 4px; height: 100%;
  background: linear-gradient(to bottom, var(--accent), var(--accent-lt) 45%, var(--accent));
}}
.corner {{
  position: absolute; width: 54px; height: 54px;
  border-color: color-mix(in srgb, var(--accent) 55%, transparent); pointer-events: none;
}}
.corner.tr {{ right: 40px; top: 40px; border-top: 2px solid; border-right: 2px solid; }}
.corner.bl {{ left: 40px; bottom: 40px; border-bottom: 2px solid; border-left: 2px solid; }}
.brand {{
  position: absolute; right: 44px; bottom: 40px;
  font-family: 'Inter', sans-serif; font-size: 17px; font-weight: 700;
  letter-spacing: 3px; color: color-mix(in srgb, var(--accent) 65%, transparent);
}}
"""

def _html_page(body_html: str, theme: dict, extra_styles: str = "") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{FONT_IMPORT}
{_theme_css(theme)}
{BASE_STYLES}
{extra_styles}
</style>
</head>
<body>{body_html}</body>
</html>"""


def html_cover(title: str, topic: str, theme: dict, kicker: str = "") -> str:
    kicker_html = f'<div class="kicker">{kicker}</div>' if kicker else ""
    return _html_page(f"""
<div class="slide">
  <div class="edge"></div>
  <span class="corner tr"></span>
  <div class="content">
    <div class="eyebrow">
      <span class="eyebrow-line"></span>
      <span class="eyebrow-text">{topic.upper()}</span>
    </div>
    <h1 class="title">{title}</h1>
    {kicker_html}
    <div class="rule"></div>
  </div>
  <div class="read-hint"><span class="rh-text">SCORRI</span><span class="rh-arrow">&rarr;</span></div>
  <div class="brand">FB</div>
  <div class="grain"></div>
  <div class="vignette"></div>
</div>
""", theme, """
.content { position: absolute; left: 96px; right: 96px; top: 0; bottom: 0;
  display: flex; flex-direction: column; justify-content: center; }
.eyebrow { display: flex; align-items: center; gap: 18px; margin-bottom: 44px; }
.eyebrow-line { width: 46px; height: 2px; background: linear-gradient(to right, var(--accent), var(--accent-lt)); }
.eyebrow-text { font-size: 21px; font-weight: 600; letter-spacing: 4px; color: var(--accent-lt); }
.title { font-family: 'Fraunces', serif; font-size: 90px; font-weight: 900; line-height: 1.05;
  color: var(--ink); letter-spacing: -1.5px; text-shadow: 0 2px 30px rgba(0,0,0,0.4); }
.kicker { margin-top: 30px; font-size: 30px; font-weight: 400; line-height: 1.4;
  color: var(--body); max-width: 760px; }
.rule { margin-top: 40px; width: 96px; height: 4px; border-radius: 2px;
  background: linear-gradient(to right, var(--accent), var(--accent-lt));
  box-shadow: 0 0 24px var(--glow); }
.read-hint { position: absolute; left: 96px; bottom: 70px; display: flex; align-items: center; gap: 12px; }
.rh-text { font-size: 19px; font-weight: 600; letter-spacing: 3px; color: var(--muted); }
.rh-arrow { color: var(--accent); font-size: 24px; }
""")


def html_point(number: int, headline: str, body: str, slide_idx: int, total: int, theme: dict) -> str:
    dots_html = "".join(
        f'<div class="dot {"active" if i == slide_idx else ""}"></div>' for i in range(total))
    counter = f"{number:02d}<span class='c-sep'>/</span>{total:02d}"
    return _html_page(f"""
<div class="slide">
  <div class="edge"></div>
  <div class="num-bg">{number:02d}</div>
  <div class="content">
    <div class="top-row">
      <div class="badge">{number:02d}</div>
      <div class="counter">{counter}</div>
    </div>
    <h2 class="headline">{headline}</h2>
    <div class="sep"><span class="sep-line"></span><span class="sep-dot"></span></div>
    <p class="body-text">{body}</p>
  </div>
  <div class="progress">{dots_html}</div>
  <div class="brand">FB</div>
  <div class="grain"></div>
  <div class="vignette"></div>
</div>
""", theme, """
.num-bg { position: absolute; right: -40px; top: 50%; transform: translateY(-52%);
  font-family: 'Fraunces', serif; font-size: 470px; font-weight: 900;
  color: color-mix(in srgb, var(--accent) 5%, transparent); line-height: 1; pointer-events: none; }
.content { position: absolute; left: 100px; right: 100px; top: 0; bottom: 96px;
  display: flex; flex-direction: column; justify-content: center; }
.top-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 42px; }
.badge { width: 74px; height: 74px; border: 2px solid var(--accent); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Fraunces', serif; font-size: 30px; font-weight: 700; color: var(--accent-lt);
  box-shadow: 0 0 30px var(--glow); flex-shrink: 0; }
.counter { font-size: 22px; font-weight: 600; letter-spacing: 2px; color: var(--muted); }
.counter .c-sep { color: var(--accent); margin: 0 4px; }
.headline { font-family: 'Fraunces', serif; font-size: 72px; font-weight: 700; line-height: 1.12;
  color: var(--ink); letter-spacing: -0.5px; }
.sep { display: flex; align-items: center; gap: 10px; margin: 32px 0; }
.sep-line { display: block; width: 68px; height: 2px; background: linear-gradient(to right, var(--accent), var(--accent-lt)); }
.sep-dot { display: block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
.body-text { font-size: 36px; font-weight: 400; line-height: 1.6; color: var(--body); letter-spacing: 0.2px; }
.progress { position: absolute; bottom: 44px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 13px; align-items: center; }
.dot { width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid color-mix(in srgb, var(--muted) 70%, transparent); background: transparent; }
.dot.active { background: var(--accent); border-color: var(--accent); width: 30px; border-radius: 4px; box-shadow: 0 0 14px var(--glow); }
""")


def html_cta(author_name: str, theme: dict) -> str:
    initials = "".join(w[0] for w in author_name.split()[:2]).upper()
    return _html_page(f"""
<div class="slide cta">
  <div class="edge"></div>
  <span class="corner tr"></span>
  <span class="corner bl"></span>
  <div class="content">
    <div class="avatar"><div class="avatar-inner">{initials}</div></div>
    <div class="name">{author_name}</div>
    <div class="role">CONSULENTE FINANZIARIO</div>
    <div class="divider"></div>
    <div class="cta-title">Ti &egrave; stato utile?</div>
    <div class="actions">
      <div class="action"><span class="ic">&#9670;</span>Salva il post per rileggerlo</div>
      <div class="action"><span class="ic">&#9670;</span>Condividi con chi ne ha bisogno</div>
      <div class="action"><span class="ic">&#9670;</span>Seguimi per altri contenuti</div>
    </div>
  </div>
  <div class="brand">FB</div>
  <div class="grain"></div>
  <div class="vignette"></div>
</div>
""", theme, """
.cta { display: flex; align-items: center; justify-content: center; }
.content { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 0 90px; }
.avatar { width: 138px; height: 138px; border-radius: 50%; border: 2px solid var(--accent);
  display: flex; align-items: center; justify-content: center; margin-bottom: 34px;
  background: color-mix(in srgb, var(--accent) 6%, transparent); box-shadow: 0 0 50px var(--glow); }
.avatar-inner { font-family: 'Fraunces', serif; font-size: 52px; font-weight: 700; color: var(--accent-lt); }
.name { font-family: 'Fraunces', serif; font-size: 52px; font-weight: 700; color: var(--ink); margin-bottom: 12px; }
.role { font-size: 21px; font-weight: 600; letter-spacing: 4px; color: var(--accent-lt); margin-bottom: 38px; }
.divider { width: 70px; height: 2px; margin-bottom: 38px; background: linear-gradient(to right, transparent, var(--accent), transparent); }
.cta-title { font-family: 'Fraunces', serif; font-size: 46px; font-weight: 700; color: var(--ink); margin-bottom: 36px; }
.actions { display: flex; flex-direction: column; gap: 22px; align-items: flex-start; }
.action { display: flex; align-items: center; gap: 18px; font-size: 29px; font-weight: 400; color: var(--body); }
.ic { color: var(--accent); font-size: 16px; flex-shrink: 0; }
""")


def html_single(eyebrow: str, headline: str, question: str, theme: dict,
                author_name: str = "Federico Borrasso") -> str:
    """Creatività a immagine singola stile annuncio (per post organico o LinkedIn Ads).
    headline = affermazione forte (con numero); question = la domanda sotto."""
    initials = "".join(w[0] for w in author_name.split()[:2]).upper()
    # Motivo classico (colonnato + arco + sole) in line-art, evoca l'aspirazionale
    motif = """
<svg class="motif" viewBox="0 0 1080 320" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="var(--accent-lt)"/><stop offset="1" stop-color="var(--accent)"/>
  </linearGradient></defs>
  <g fill="none" stroke="url(#g)" stroke-width="2.5" opacity="0.55">
    <circle cx="540" cy="150" r="70"/>
    <path d="M300 300 V150 a40 40 0 0 1 80 0 V300"/>
    <path d="M420 300 V130 a40 40 0 0 1 80 0 V300"/>
    <path d="M580 300 V130 a40 40 0 0 1 80 0 V300"/>
    <path d="M700 300 V150 a40 40 0 0 1 80 0 V300"/>
    <line x1="270" y1="300" x2="810" y2="300"/>
    <line x1="285" y1="286" x2="795" y2="286"/>
  </g>
</svg>
"""
    return _html_page(f"""
<div class="slide single">
  <div class="edge"></div>
  <span class="corner tr"></span>
  <div class="head">
    <div class="mono">{initials}</div>
    <div class="who">{author_name.upper()}<span class="who-sub">CONSULENTE FINANZIARIO</span></div>
  </div>
  <div class="content">
    <div class="eyebrow"><span class="eyebrow-line"></span><span class="eyebrow-text">{eyebrow.upper()}</span></div>
    <div class="headline">{headline}</div>
    <div class="question">{question}</div>
  </div>
  {motif}
  <div class="grain"></div>
  <div class="vignette"></div>
</div>
""", theme, """
.single .head { position: absolute; top: 70px; left: 96px; display: flex; align-items: center; gap: 20px; }
.mono { width: 66px; height: 66px; border-radius: 50%; border: 2px solid var(--accent);
  display: flex; align-items: center; justify-content: center; font-family: 'Fraunces', serif;
  font-size: 26px; font-weight: 700; color: var(--accent-lt); }
.who { display: flex; flex-direction: column; font-size: 22px; font-weight: 700; letter-spacing: 1.5px; color: var(--ink); }
.who-sub { font-size: 14px; font-weight: 600; letter-spacing: 3px; color: var(--accent-lt); margin-top: 4px; }
.single .content { position: absolute; left: 96px; right: 96px; top: 300px; }
.single .eyebrow { display: flex; align-items: center; gap: 16px; margin-bottom: 34px; }
.single .eyebrow-line { width: 44px; height: 2px; background: linear-gradient(to right, var(--accent), var(--accent-lt)); }
.single .eyebrow-text { font-size: 20px; font-weight: 600; letter-spacing: 4px; color: var(--accent-lt); }
.headline { font-family: 'Fraunces', serif; font-size: 104px; font-weight: 900; line-height: 1.0;
  color: var(--accent-lt); letter-spacing: -2px; text-shadow: 0 2px 30px rgba(0,0,0,0.45); }
.question { margin-top: 26px; font-family: 'Fraunces', serif; font-size: 52px; font-weight: 600;
  font-style: italic; line-height: 1.15; color: var(--ink); }
.motif { position: absolute; left: 0; right: 0; bottom: 46px; width: 1080px; height: 320px; }
""")


def save_single_image(headline: str, question: str, eyebrow: str,
                      out_path: str = "automation/single_ad.jpg",
                      theme_name: str = "oro",
                      author_name: str = "Federico Borrasso") -> str:
    """Renderizza una creatività a immagine singola in JPEG 1080x1080."""
    theme = THEMES.get(theme_name, THEMES["oro"])
    html = html_single(eyebrow, headline, question, theme, author_name)
    render_html_to_jpeg(html, out_path)
    return out_path


def render_html_to_jpeg(html: str, output_path: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=output_path, type="jpeg", quality=95,
                        clip={"x": 0, "y": 0, "width": W, "height": H})
        browser.close()


def build_slides_html(content: dict) -> list[str]:
    """Restituisce la lista di HTML per ogni slide."""
    theme = pick_theme(content)
    pages = [html_cover(content["title"], content["topic"], theme, content.get("kicker", ""))]
    points = content["points"]
    total = len(points)
    for i, point in enumerate(points):
        pages.append(html_point(i + 1, point["headline"], point["body"], i, total, theme))
    pages.append(html_cta(content.get("author", "Federico Borrasso"), theme))
    return pages


def build_carousel(content: dict, output_path: str = "automation/carousel.pdf") -> str:
    from fpdf import FPDF
    slide_paths = save_slide_jpegs(content, out_dir="automation/tmp_carousel", size=1080)
    pdf = FPDF(unit="pt", format=[W, H])
    for path in slide_paths:
        pdf.add_page()
        pdf.image(path, 0, 0, W, H)
    pdf.output(output_path)
    for p in slide_paths:
        Path(p).unlink(missing_ok=True)
    Path("automation/tmp_carousel").rmdir()
    return output_path


def save_slide_jpegs(content: dict, out_dir: str = "automation/preview_slides",
                     size: int = 1080) -> list[str]:
    pages = build_slides_html(content)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for idx, html in enumerate(pages):
            page = browser.new_page(viewport={"width": W, "height": H})
            page.set_content(html, wait_until="networkidle")
            path = str(out / f"slide_{idx:02d}.jpg")
            page.screenshot(path=path, type="jpeg", quality=95,
                            clip={"x": 0, "y": 0, "width": W, "height": H})
            page.close()
            if size != W:
                from PIL import Image
                img = Image.open(path)
                img = img.resize((size, size), Image.LANCZOS)
                img.save(path, "JPEG", quality=90)
        browser.close()
    return sorted(str(p) for p in out.glob("slide_*.jpg"))


if __name__ == "__main__":
    test_content = {
        "title": "Il TFR in azienda ti costa 30.000€",
        "topic": "TFR e fondo pensione",
        "kicker": "Lasciarlo fermo è una scelta. Quasi sempre, quella sbagliata.",
        "author": "Federico Borrasso",
        "points": [
            {"headline": "Il TFR perde valore", "body": "In azienda rende l'1,5% + 75% dell'inflazione. Spesso non basta nemmeno a coprire il carovita."},
            {"headline": "Il fondo lavora per te", "body": "Investito sui mercati, nel lungo periodo il rendimento medio supera nettamente la rivalutazione di legge."},
            {"headline": "Tassazione dimezzata", "body": "Alla liquidazione il fondo tassa dal 15% al 9%. Il TFR in azienda parte dal 23%."},
        ]
    }
    paths = save_slide_jpegs(test_content, out_dir="/tmp/test_slides")
    print(f"Slide generate: {paths}")
