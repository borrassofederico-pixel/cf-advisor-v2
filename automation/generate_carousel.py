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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;900&family=Inter:wght@300;400;500;600&display=swap');
"""

# ── Stili base condivisi ──────────────────────────────────────────────────────
BASE_STYLES = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  width: 1080px; height: 1080px; overflow: hidden;
  background: #07121E;
  font-family: 'Inter', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
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
  <div class="gold-bar"></div>
  <div class="content">
    <div class="tag">{topic.upper()}</div>
    <h1 class="title">{title}</h1>
    <div class="divider"></div>
    <p class="hint">Scorri per scoprire &rarr;</p>
  </div>
  <div class="deco-circles">
    <div class="circle c1"></div>
    <div class="circle c2"></div>
    <div class="circle c3"></div>
  </div>
  <div class="brand">FB</div>
</div>
""", """
.slide {
  width: 1080px; height: 1080px;
  background: linear-gradient(145deg, #07121E 0%, #0D1F35 60%, #071220 100%);
  position: relative; overflow: hidden;
}
.gold-bar {
  position: absolute; left: 0; top: 0;
  width: 5px; height: 100%;
  background: linear-gradient(to bottom, #C9A84C, #E8C96A, #C9A84C);
}
.content {
  position: absolute;
  left: 80px; top: 0; right: 80px; bottom: 0;
  display: flex; flex-direction: column; justify-content: center;
  gap: 0;
}
.tag {
  display: inline-block;
  border: 1px solid #C9A84C;
  color: #C9A84C;
  font-family: 'Inter', sans-serif;
  font-size: 20px; font-weight: 500;
  letter-spacing: 2.5px;
  padding: 8px 20px;
  border-radius: 3px;
  margin-bottom: 44px;
  width: fit-content;
}
.title {
  font-family: 'Playfair Display', serif;
  font-size: 82px; font-weight: 900;
  line-height: 1.1;
  color: #FFFFFF;
  letter-spacing: -1px;
  margin-bottom: 40px;
}
.divider {
  width: 80px; height: 3px;
  background: linear-gradient(to right, #C9A84C, #E8C96A);
  border-radius: 2px;
  margin-bottom: 36px;
}
.hint {
  font-family: 'Inter', sans-serif;
  font-size: 22px; font-weight: 400;
  color: #7A8FA6;
  letter-spacing: 0.5px;
}
.deco-circles {
  position: absolute;
  right: -60px; bottom: -60px;
}
.circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(201, 168, 76, 0.18);
  transform: translate(-50%, -50%);
}
.c1 { width: 420px; height: 420px; }
.c2 { width: 290px; height: 290px; border-color: rgba(201, 168, 76, 0.28); }
.c3 { width: 160px; height: 160px; border-color: rgba(201, 168, 76, 0.40); }
.brand {
  position: absolute; right: 36px; bottom: 32px;
  font-family: 'Inter', sans-serif;
  font-size: 18px; font-weight: 600;
  letter-spacing: 2px;
  color: rgba(201, 168, 76, 0.55);
}
""")


def html_point(number: int, headline: str, body: str,
               slide_idx: int, total: int) -> str:
    dots_html = "".join(
        f'<div class="dot {"active" if i == slide_idx else ""}"></div>'
        for i in range(total)
    )
    return _html_page(f"""
<div class="slide">
  <div class="gold-bar"></div>
  <div class="num-bg">{number}</div>
  <div class="content">
    <div class="badge">{number}</div>
    <h2 class="headline">{headline}</h2>
    <div class="sep"><span class="sep-line"></span><span class="sep-dot"></span></div>
    <p class="body-text">{body}</p>
  </div>
  <div class="progress">{dots_html}</div>
  <div class="brand">FB</div>
</div>
""", """
.slide {
  width: 1080px; height: 1080px;
  background: linear-gradient(145deg, #07121E 0%, #0D1F35 60%, #071220 100%);
  position: relative; overflow: hidden;
}
.gold-bar {
  position: absolute; left: 0; top: 0;
  width: 5px; height: 100%;
  background: linear-gradient(to bottom, #C9A84C, #E8C96A, #C9A84C);
}
.num-bg {
  position: absolute;
  right: -20px; top: 50%; transform: translateY(-55%);
  font-family: 'Playfair Display', serif;
  font-size: 380px; font-weight: 900;
  color: rgba(255,255,255,0.035);
  line-height: 1; user-select: none;
  pointer-events: none;
}
.content {
  position: absolute;
  left: 90px; top: 0; right: 90px; bottom: 80px;
  display: flex; flex-direction: column; justify-content: center;
}
.badge {
  width: 68px; height: 68px;
  border: 2px solid #C9A84C;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif;
  font-size: 30px; font-weight: 700;
  color: #C9A84C;
  margin-bottom: 40px;
  flex-shrink: 0;
}
.headline {
  font-family: 'Playfair Display', serif;
  font-size: 68px; font-weight: 700;
  line-height: 1.15;
  color: #FFFFFF;
  letter-spacing: -0.5px;
  margin-bottom: 36px;
}
.sep {
  display: flex; align-items: center;
  gap: 10px; margin-bottom: 36px;
}
.sep-line {
  display: block; width: 64px; height: 2px;
  background: linear-gradient(to right, #C9A84C, #E8C96A);
  border-radius: 1px;
}
.sep-dot {
  display: block; width: 8px; height: 8px;
  border-radius: 50%; background: #C9A84C;
}
.body-text {
  font-family: 'Inter', sans-serif;
  font-size: 34px; font-weight: 400;
  line-height: 1.65;
  color: #C8D5E0;
  letter-spacing: 0.2px;
}
.progress {
  position: absolute; bottom: 36px; left: 50%;
  transform: translateX(-50%);
  display: flex; gap: 14px; align-items: center;
}
.dot {
  width: 8px; height: 8px; border-radius: 50%;
  border: 1.5px solid #3A5068;
  background: transparent;
  transition: all 0.3s;
}
.dot.active {
  background: #C9A84C; border-color: #C9A84C;
  width: 28px; border-radius: 4px;
}
.brand {
  position: absolute; right: 36px; bottom: 32px;
  font-family: 'Inter', sans-serif;
  font-size: 18px; font-weight: 600;
  letter-spacing: 2px;
  color: rgba(201, 168, 76, 0.55);
}
""")


def html_cta(author_name: str) -> str:
    initials = "".join(w[0] for w in author_name.split()[:2]).upper()
    return _html_page(f"""
<div class="slide">
  <div class="gold-bar"></div>
  <div class="content">
    <div class="avatar">
      <div class="avatar-inner">{initials}</div>
    </div>
    <div class="name">{author_name}</div>
    <div class="role">Consulente Finanziario Indipendente</div>
    <div class="divider"></div>
    <div class="cta-title">Ti è stato utile?</div>
    <div class="actions">
      <div class="action"><span class="bullet"></span>Commenta la tua esperienza</div>
      <div class="action"><span class="bullet"></span>Condividi con chi ne ha bisogno</div>
      <div class="action"><span class="bullet"></span>Seguimi per altri contenuti</div>
    </div>
  </div>
  <div class="brand">FB</div>
</div>
""", """
.slide {
  width: 1080px; height: 1080px;
  background: linear-gradient(145deg, #07121E 0%, #0D1F35 60%, #071220 100%);
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}
.gold-bar {
  position: absolute; left: 0; top: 0;
  width: 5px; height: 100%;
  background: linear-gradient(to bottom, #C9A84C, #E8C96A, #C9A84C);
}
.content {
  display: flex; flex-direction: column;
  align-items: center; gap: 0;
  text-align: center;
  padding: 0 80px;
}
.avatar {
  width: 130px; height: 130px; border-radius: 50%;
  border: 2px solid #C9A84C;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 32px;
  background: rgba(201, 168, 76, 0.06);
  box-shadow: 0 0 40px rgba(201, 168, 76, 0.12);
}
.avatar-inner {
  font-family: 'Playfair Display', serif;
  font-size: 48px; font-weight: 700;
  color: #C9A84C;
}
.name {
  font-family: 'Playfair Display', serif;
  font-size: 46px; font-weight: 700;
  color: #FFFFFF; margin-bottom: 12px;
}
.role {
  font-family: 'Inter', sans-serif;
  font-size: 24px; font-weight: 400;
  color: #C9A84C; letter-spacing: 0.3px;
  margin-bottom: 36px;
}
.divider {
  width: 60px; height: 2px;
  background: linear-gradient(to right, transparent, #C9A84C, transparent);
  margin-bottom: 36px;
}
.cta-title {
  font-family: 'Playfair Display', serif;
  font-size: 40px; font-weight: 700;
  color: #FFFFFF; margin-bottom: 32px;
}
.actions {
  display: flex; flex-direction: column; gap: 20px;
  align-items: flex-start;
}
.action {
  display: flex; align-items: center; gap: 16px;
  font-family: 'Inter', sans-serif;
  font-size: 28px; font-weight: 400;
  color: #7A8FA6;
}
.bullet {
  width: 8px; height: 8px; border-radius: 50%;
  background: #C9A84C; flex-shrink: 0;
}
.brand {
  position: absolute; right: 36px; bottom: 32px;
  font-family: 'Inter', sans-serif;
  font-size: 18px; font-weight: 600;
  letter-spacing: 2px;
  color: rgba(201, 168, 76, 0.55);
}
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
