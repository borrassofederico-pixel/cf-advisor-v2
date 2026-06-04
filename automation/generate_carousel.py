"""
Genera un carosello LinkedIn come PDF multi-pagina.
Ogni pagina = una slide visiva con design navy/oro.

Struttura del carosello (6 slide):
  0 — Cover:   titolo grande + tema
  1-4 — Punti: un concetto per slide con numero e testo
  5 — CTA:     invito a seguire / commentare
"""

import os
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# ── Dimensioni slide (LinkedIn consiglia 1080×1080 per i documenti) ──────────
W, H = 1080, 1080

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY      = (11, 25, 41)
NAVY_LIGHT= (18, 40, 65)
GOLD      = (196, 160, 80)
GOLD_DARK = (150, 118, 50)
WHITE     = (255, 255, 255)
GRAY      = (180, 180, 180)

# ── Font (usa i font di sistema disponibili su Ubuntu GitHub Actions) ─────────
def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_background(draw: ImageDraw, slide_idx: int, total: int) -> None:
    """Sfondo sfumato navy con decorazioni geometriche."""
    draw.rectangle([0, 0, W, H], fill=NAVY)

    # Rettangolo decorativo in alto a sinistra
    draw.rectangle([0, 0, 6, H], fill=GOLD)

    # Cerchio decorativo in basso a destra (parziale)
    cx, cy, r = W + 80, H + 80, 300
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=(*GOLD, 30), width=2)

    # Indicatore progresso slide in basso
    bar_y = H - 18
    bar_h = 4
    draw.rectangle([40, bar_y, W - 40, bar_y + bar_h], fill=NAVY_LIGHT)
    if total > 1:
        progress = int((W - 80) * (slide_idx / (total - 1)))
        draw.rectangle([40, bar_y, 40 + progress, bar_y + bar_h], fill=GOLD)

    # Branding "FB" in basso a destra
    font_brand = get_font(22, bold=True)
    draw.text((W - 58, H - 42), "FB", font=font_brand, fill=(*GOLD, 180))


def wrap_text(text: str, font, max_width: int, draw: ImageDraw) -> list[str]:
    """Spezza il testo per adattarlo alla larghezza."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def slide_cover(title: str, topic: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_background(draw, 0, 1)

    # Linea oro orizzontale decorativa
    draw.rectangle([60, 320, W - 60, 322], fill=GOLD)

    # Sovratitolo
    font_over = get_font(28)
    draw.text((60, 270), topic.upper(), font=font_over, fill=GOLD)

    # Titolo principale (grande, multi-riga)
    font_title = get_font(72, bold=True)
    margin = 60
    lines = wrap_text(title, font_title, W - margin * 2, draw)
    y = 345
    for line in lines[:4]:
        draw.text((margin, y), line, font=font_title, fill=WHITE)
        y += 84

    # Swipe CTA in basso
    font_cta = get_font(30)
    draw.text((60, H - 90), "→  Scorri per scoprire di più", font=font_cta, fill=GRAY)

    return img


def slide_point(number: int, headline: str, body: str,
                slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_background(draw, slide_idx, total)

    # Numero grande in background (decorativo)
    font_num_bg = get_font(280, bold=True)
    draw.text((W - 220, H // 2 - 180), str(number),
              font=font_num_bg, fill=(*NAVY_LIGHT, 255))

    # Numero piccolo evidenziato
    font_num = get_font(52, bold=True)
    draw.rectangle([60, 80, 114, 134], fill=GOLD)
    draw.text((72, 83), str(number), font=font_num, fill=NAVY)

    # Headline
    font_h = get_font(62, bold=True)
    margin = 60
    lines = wrap_text(headline, font_h, W - margin * 2, draw)
    y = 180
    for line in lines[:3]:
        draw.text((margin, y), line, font=font_h, fill=WHITE)
        y += 74

    # Separatore
    draw.rectangle([margin, y + 10, margin + 80, y + 14], fill=GOLD)
    y += 50

    # Body text
    font_b = get_font(38)
    body_lines = wrap_text(body, font_b, W - margin * 2, draw)
    for line in body_lines[:6]:
        draw.text((margin, y), line, font=font_b, fill=GRAY)
        y += 52

    return img


def slide_cta(author_name: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_background(draw, 1, 1)

    # Cerchio avatar placeholder
    cx, cy, r = W // 2, 300, 90
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    font_init = get_font(72, bold=True)
    # Iniziali nel cerchio
    initials = "".join(w[0] for w in author_name.split()[:2]).upper()
    bbox = draw.textbbox((0, 0), initials, font=font_init)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - 45), initials, font=font_init, fill=NAVY)

    # Nome
    font_name = get_font(48, bold=True)
    bbox = draw.textbbox((0, 0), author_name, font=font_name)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 420), author_name, font=font_name, fill=WHITE)

    # Ruolo
    font_role = get_font(32)
    role = "Consulente Finanziario"
    bbox = draw.textbbox((0, 0), role, font=font_role)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 490), role, font=font_role, fill=GOLD)

    # Separatore
    draw.rectangle([W // 2 - 60, 560, W // 2 + 60, 563], fill=GOLD)

    # CTA testo
    font_cta = get_font(44, bold=True)
    cta1 = "Ti è stato utile?"
    bbox = draw.textbbox((0, 0), cta1, font=font_cta)
    draw.text(((W - bbox[2]) // 2, 600), cta1, font=font_cta, fill=WHITE)

    font_cta2 = get_font(36)
    cta2 = "💬 Commenta  •  ♻️ Condividi  •  ➕ Seguimi"
    bbox = draw.textbbox((0, 0), cta2, font=font_cta2)
    draw.text(((W - bbox[2]) // 2, 680), cta2, font=font_cta2, fill=GRAY)

    return img


def build_carousel(content: dict, output_path: str = "automation/carousel.pdf") -> str:
    """
    content = {
      "title": "...",
      "topic": "...",
      "points": [{"headline": "...", "body": "..."}, ...],  # 3-5 punti
      "author": "Federico Borrasso"
    }
    """
    slides: list[Image.Image] = []

    # Slide 0: cover
    slides.append(slide_cover(content["title"], content["topic"]))

    # Slide 1-N: punti
    points = content["points"]
    total_slides = 1 + len(points) + 1  # cover + points + cta
    for i, point in enumerate(points):
        slides.append(slide_point(
            number=i + 1,
            headline=point["headline"],
            body=point["body"],
            slide_idx=i + 1,
            total=total_slides - 1
        ))

    # Ultima slide: CTA
    slides.append(slide_cta(content.get("author", "Federico Borrasso")))

    # ── Salva come PDF (A4 landscape per LinkedIn, 1:1 aspect ratio) ─────────
    pdf = FPDF(unit="pt", format=[W, H])
    tmp_dir = Path("automation/tmp_slides")
    tmp_dir.mkdir(exist_ok=True)

    for idx, img in enumerate(slides):
        tmp_path = str(tmp_dir / f"slide_{idx:02d}.jpg")
        img.save(tmp_path, "JPEG", quality=95)
        pdf.add_page()
        pdf.image(tmp_path, 0, 0, W, H)

    pdf.output(output_path)

    # Pulizia file temporanei
    for f in tmp_dir.glob("*.jpg"):
        f.unlink()
    tmp_dir.rmdir()

    return output_path


if __name__ == "__main__":
    # Test locale
    test_content = {
        "title": "5 errori che distruggono il tuo portafoglio",
        "topic": "Finanza comportamentale",
        "author": "Federico Borrasso",
        "points": [
            {
                "headline": "Vendere nel panico",
                "body": "Il mercato scende e vendi tutto. Realizzi la perdita e perdi il rimbalzo. È l'errore più costoso."
            },
            {
                "headline": "Ignorare l'inflazione",
                "body": "I soldi sul conto corrente perdono potere d'acquisto ogni anno. Il 2% annuo dimezza il valore in 35 anni."
            },
            {
                "headline": "Manca diversificazione",
                "body": "Concentrare tutto su un solo asset o mercato amplifica il rischio senza aumentare il rendimento atteso."
            },
            {
                "headline": "Orizzonte temporale sbagliato",
                "body": "Investire a breve termine capitali che servono tra 20 anni — o viceversa — porta a scelte irrazionali."
            },
        ]
    }
    path = build_carousel(test_content)
    print(f"Carosello generato: {path}")
