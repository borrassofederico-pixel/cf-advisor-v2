"""
Genera slide del carosello LinkedIn come immagini 1080x1080
usando HTML/CSS renderizzato via Playwright (headless Chromium).
"""

import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

W, H = 1080, 1080

# ── Font Google ───────────────────────────────────────────────────────────────
FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
"""

# Grana sottile (texture) come overlay SVG in data-uri: dà profondità "premium".
GRAIN = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' "
    "baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E"
    "%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E\")"
)

# ── Stili base condivisi ──────────────────────────────────────────────────────
BASE_STYLES = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  width: 1080px; height: 1080px; overflow: hidden;
  background: #060F1A;
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
/* Elementi comuni a tutte le slide */
.slide {{
  width: 1080px; height: 1080px;
  position: relative; overflow: hidden;
  background:
    radial-gradient(1200px 700px at 12% 8%, rgba(201,168,76,0.10), transparent 55%),
    radial-gradient(900px 900px at 92% 100%, rgba(28,58,94,0.55), transparent 60%),
    linear-gradient(150deg, #060F1A 0%, #0C1F35 58%, #060E19 100%);
}}
.grain {{
  position: absolute; inset: 0;
  background-image: {GRAIN};
  background-size: 300px 300px;
  opacity: 0.06; mix-blend-mode: overlay;
  pointer-events: none;
}}
.vignette {{
  position: absolute; inset: 0;
  box-shadow: inset 0 0 220px rgba(0,0,0,0.55);
  pointer-events: none;
}}
.edge {{
  position: absolute; left: 0; top: 0;
  width: 4px; height: 100%;
  background: linear-gradient(to bottom, #C9A84C, #EBD07A 45%, #C9A84C);
}}
.corner {{
  position: absolute; width: 54px; height: 54px;
  border-color: rgba(201,168,76,0.55); pointer-events: none;
}}
.corner.tr {{ right: 40px; top: 40px; border-top: 2px solid; border-right: 2px solid; }}
.corner.bl {{ left: 40px; bottom: 40px; border-bottom: 2px solid; border-left: 2px solid; }}
.brand {{
  position: absolute; right: 44px; bottom: 40px;
  font-family: 'Inter', sans-serif;
  font-size: 17px; font-weight: 700;
  letter-spacing: 3px;
  color: rgba(201,168,76,0.60);
}}
"""

def _html_page(body_html: str, extra_styles: str = "") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{FONT_IMPORT}
{BASE_STYLES}
{extra_styles}
</style>
</head>
<body>{body_html}</body>
</html>"""


def html_cover(title: str, topic: str) -> str:
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
    <div class="rule"></div>
  </div>
  <div class="read-hint">
    <span class="rh-text">SCORRI</span>
    <span class="rh-arrow">&rarr;</span>
  </div>
  <div class="brand">FB</div>
  <div class="grain"></div>
  <div class="vignette"></div>
</div>
""", """
.content {
  position: absolute;
  left: 96px; right: 96px; top: 0; bottom: 0;
  display: flex; flex-direction: column; justify-content: center;
}
.eyebrow { display: flex; align-items: center; gap: 18px; margin-bottom: 46px; }
.eyebrow-line {
  width: 46px; height: 2px;
  background: linear-gradient(to right, #C9A84C, #EBD07A);
}
.eyebrow-text {
  font-family: 'Inter', sans-serif;
  font-size: 21px; font-weight: 600;
  letter-spacing: 4px; color: #D9B85E;
}
.title {
  font-family: 'Playfair Display', serif;
  font-size: 88px; font-weight: 800;
  line-height: 1.08; color: #FFFFFF;
  letter-spacing: -1.5px;
  text-shadow: 0 2px 30px rgba(0,0,0,0.4);
}
.rule {
  margin-top: 46px;
  width: 96px; height: 4px; border-radius: 2px;
  background: linear-gradient(to right, #C9A84C, #EBD07A);
  box-shadow: 0 0 24px rgba(201,168,76,0.4);
}
.read-hint {
  position: absolute; left: 96px; bottom: 70px;
  display: flex; align-items: center; gap: 12px;
}
.rh-text {
  font-family: 'Inter', sans-serif;
  font-size: 19px; font-weight: 600;
  letter-spacing: 3px; color: #6F8AA6;
}
.rh-arrow { color: #C9A84C; font-size: 24px; }
""")


def html_point(number: int, headline: str, body: str,
               slide_idx: int, total: int) -> str:
    dots_html = "".join(
        f'<div class="dot {"active" if i == slide_idx else ""}"></div>'
        for i in range(total)
    )
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
""", """
.num-bg {
  position: absolute;
  right: -40px; top: 50%; transform: translateY(-52%);
  font-family: 'Playfair Display', serif;
  font-size: 460px; font-weight: 900;
  color: rgba(201,168,76,0.045);
  line-height: 1; user-select: none; pointer-events: none;
}
.content {
  position: absolute;
  left: 100px; right: 100px; top: 0; bottom: 96px;
  display: flex; flex-direction: column; justify-content: center;
}
.top-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 44px;
}
.badge {
  width: 74px; height: 74px;
  border: 2px solid #C9A84C; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-size: 30px; font-weight: 700; color: #EBD07A;
  box-shadow: 0 0 30px rgba(201,168,76,0.18);
  flex-shrink: 0;
}
.counter {
  font-family: 'Inter', sans-serif;
  font-size: 22px; font-weight: 600;
  letter-spacing: 2px; color: #6F8AA6;
}
.counter .c-sep { color: #C9A84C; margin: 0 4px; }
.headline {
  font-family: 'Playfair Display', serif;
  font-size: 70px; font-weight: 700;
  line-height: 1.13; color: #FFFFFF;
  letter-spacing: -0.5px;
}
.sep { display: flex; align-items: center; gap: 10px; margin: 34px 0; }
.sep-line {
  display: block; width: 68px; height: 2px;
  background: linear-gradient(to right, #C9A84C, #EBD07A);
}
.sep-dot { display: block; width: 8px; height: 8px; border-radius: 50%; background: #C9A84C; }
.body-text {
  font-family: 'Inter', sans-serif;
  font-size: 35px; font-weight: 400;
  line-height: 1.62; color: #CBD8E4;
  letter-spacing: 0.2px;
}
.progress {
  position: absolute; bottom: 44px; left: 50%;
  transform: translateX(-50%);
  display: flex; gap: 13px; align-items: center;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  border: 1.5px solid #3A5068; background: transparent;
}
.dot.active {
  background: #C9A84C; border-color: #C9A84C;
  width: 30px; border-radius: 4px;
  box-shadow: 0 0 14px rgba(201,168,76,0.5);
}
""")


def html_cta(author_name: str) -> str:
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
""", """
.cta { display: flex; align-items: center; justify-content: center; }
.content {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; padding: 0 90px;
}
.avatar {
  width: 138px; height: 138px; border-radius: 50%;
  border: 2px solid #C9A84C;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 34px;
  background: rgba(201,168,76,0.06);
  box-shadow: 0 0 50px rgba(201,168,76,0.16);
}
.avatar-inner {
  font-family: 'Playfair Display', serif;
  font-size: 52px; font-weight: 700; color: #EBD07A;
}
.name {
  font-family: 'Playfair Display', serif;
  font-size: 50px; font-weight: 700; color: #FFFFFF;
  margin-bottom: 12px;
}
.role {
  font-family: 'Inter', sans-serif;
  font-size: 21px; font-weight: 600;
  letter-spacing: 4px; color: #D9B85E;
  margin-bottom: 38px;
}
.divider {
  width: 70px; height: 2px; margin-bottom: 38px;
  background: linear-gradient(to right, transparent, #C9A84C, transparent);
}
.cta-title {
  font-family: 'Playfair Display', serif;
  font-size: 44px; font-weight: 700; color: #FFFFFF;
  margin-bottom: 36px;
}
.actions { display: flex; flex-direction: column; gap: 22px; align-items: flex-start; }
.action {
  display: flex; align-items: center; gap: 18px;
  font-family: 'Inter', sans-serif;
  font-size: 29px; font-weight: 400; color: #B9C7D6;
}
.ic { color: #C9A84C; font-size: 16px; flex-shrink: 0; }
""")


def render_html_to_jpeg(html: str, output_path: str) -> None:
    """Renderizza una stringa HTML in un JPEG 1080x1080 via Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.set_content(html, wait_until="networkidle")
        page.screenshot(path=output_path, type="jpeg", quality=95,
                        clip={"x": 0, "y": 0, "width": W, "height": H})
        browser.close()


def build_slides_html(content: dict) -> list[str]:
    """Restituisce la lista di HTML per ogni slide."""
    pages = [html_cover(content["title"], content["topic"])]
    points = content["points"]
    total = len(points)
    for i, point in enumerate(points):
        pages.append(html_point(i + 1, point["headline"], point["body"], i, total))
    pages.append(html_cta(content.get("author", "Federico Borrasso")))
    return pages


def build_carousel(content: dict, output_path: str = "automation/carousel.pdf") -> str:
    """Genera il PDF carosello (per compatibilità, usa le JPEG come prima)."""
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
    """Renderizza ogni slide HTML in JPEG e restituisce i path."""
    pages = build_slides_html(content)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for idx, html in enumerate(pages):
            page = browser.new_page(viewport={"width": W, "height": H})
            page.set_content(html, wait_until="networkidle")
            path = str(out / f"slide_{idx:02d}.jpg")
            page.screenshot(path=path, type="jpeg", quality=95,
                            clip={"x": 0, "y": 0, "width": W, "height": H})
            page.close()

            # Ridimensiona se richiesto (es. 800 per Telegram)
            if size != W:
                from PIL import Image
                img = Image.open(path)
                img = img.resize((size, size), Image.LANCZOS)
                img.save(path, "JPEG", quality=90)

        browser.close()
    return sorted(str(p) for p in out.glob("slide_*.jpg"))


if __name__ == "__main__":
    test_content = {
        "title": "PAC: investi ogni mese senza stress",
        "topic": "Piani di Accumulo del Capitale",
        "author": "Federico Borrasso",
        "points": [
            {"headline": "Cos'è un PAC", "body": "Investi una cifra fissa ogni mese, indipendentemente da cosa fa il mercato. Semplice, automatico, efficace."},
            {"headline": "Dollar Cost Averaging", "body": "Compri più quote quando i prezzi scendono e meno quando salgono. Il tempo abbassa il costo medio."},
            {"headline": "Quanto serve per iniziare", "body": "Anche 50€ al mese sono sufficienti. L'abitudine conta più dell'importo iniziale."},
            {"headline": "L'errore da non fare", "body": "Interrompere nei momenti di crisi è il più costoso. Il PAC funziona proprio nelle fasi difficili."},
        ]
    }
    paths = save_slide_jpegs(test_content, out_dir="/tmp/test_slides")
    print(f"Slide generate: {paths}")
