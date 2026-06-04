"""
Genera un carosello LinkedIn con design elegante e minimalista.

Struttura (6 slide):
  0 — Cover:   titolo + tema
  1-4 — Punti: headline + body
  5 — CTA:     invito a seguire
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

W, H = 1080, 1080

# ── Palette raffinata ─────────────────────────────────────────────────────────
NAVY        = (7, 18, 36)
NAVY_MID    = (14, 32, 60)
GOLD        = (210, 172, 90)
GOLD_LIGHT  = (230, 200, 130)
WHITE       = (255, 255, 255)
CREAM       = (240, 235, 220)
SLATE       = (155, 165, 175)
DARK_SLATE  = (80, 95, 110)


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap_text(text: str, font, max_width: int, draw: ImageDraw) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def draw_base(draw: ImageDraw) -> None:
    """Sfondo navy uniforme."""
    draw.rectangle([0, 0, W, H], fill=NAVY)


def draw_corner_accent(draw: ImageDraw) -> None:
    """Angolo dorato in alto a sinistra — linea sottile verticale."""
    draw.rectangle([0, 0, 5, H], fill=GOLD)


def draw_progress_dots(draw: ImageDraw, current: int, total: int) -> None:
    """Pallini di progresso in basso al centro."""
    dot_r = 5
    spacing = 22
    n = total
    start_x = W // 2 - (n - 1) * spacing // 2
    y = H - 38
    for i in range(n):
        x = start_x + i * spacing
        if i == current:
            draw.ellipse([x - dot_r, y - dot_r, x + dot_r, y + dot_r], fill=GOLD)
        else:
            draw.ellipse([x - dot_r + 1, y - dot_r + 1, x + dot_r - 1, y + dot_r - 1],
                         outline=DARK_SLATE, width=2)


def draw_branding(draw: ImageDraw) -> None:
    """Branding minimalista in basso a destra."""
    font = get_font(20, bold=True)
    draw.text((W - 56, H - 48), "FB", font=font, fill=(*GOLD, 140))


def draw_thin_line(draw: ImageDraw, x1: int, y: int, x2: int, color=GOLD) -> None:
    draw.rectangle([x1, y, x2, y + 1], fill=color)


def slide_cover(title: str, topic: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_base(draw)
    draw_corner_accent(draw)
    draw_branding(draw)

    # Decorazioni geometriche eleganti: linee angolari in basso a destra
    for i, offset in enumerate([0, 18, 36]):
        alpha = 60 - i * 18
        draw.line([W - 80 - offset, H - 80, W - 80, H - 80 - offset],
                  fill=(*GOLD, alpha), width=1)

    # Topic tag — pillola dorata in alto
    font_tag = get_font(26)
    tag = topic.upper()
    tag_bbox = draw.textbbox((0, 0), tag, font=font_tag)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_x, tag_y = 72, 90
    draw.rectangle([tag_x - 14, tag_y - 8, tag_x + tag_w + 14, tag_y + 36],
                   outline=GOLD, width=1)
    draw.text((tag_x, tag_y), tag, font=font_tag, fill=GOLD)

    # Titolo principale
    font_title = get_font(76, bold=True)
    margin = 72
    lines = wrap_text(title, font_title, W - margin * 2, draw)
    y = 200
    for line in lines[:4]:
        draw.text((margin, y), line, font=font_title, fill=WHITE)
        y += 90

    # Linea sottile sotto il titolo
    draw_thin_line(draw, margin, y + 20, margin + 120)

    # Cerchi decorativi in basso a destra
    for radius, alpha in [(180, 18), (130, 30), (80, 45)]:
        draw.ellipse([W - radius * 2 + 60, H - radius * 2 + 60,
                      W + 60, H + 60],
                     outline=(*GOLD, alpha), width=1)

    # Swipe hint in basso a sinistra
    font_hint = get_font(28)
    draw.text((margin, H - 90), "scorri →", font=font_hint, fill=SLATE)

    return img


def slide_point(number: int, headline: str, body: str,
                slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_base(draw)
    draw_corner_accent(draw)
    draw_branding(draw)
    draw_progress_dots(draw, slide_idx, total)

    margin = 80

    # Numero decorativo grande (watermark, molto sottile)
    font_num_bg = get_font(320, bold=True)
    num_str = str(number)
    nb_bbox = draw.textbbox((0, 0), num_str, font=font_num_bg)
    nb_w = nb_bbox[2] - nb_bbox[0]
    draw.text((W - nb_w - 20, H // 2 - 200), num_str,
              font=font_num_bg, fill=(*NAVY_MID, 255))

    # Badge numero — cerchio dorato piccolo
    cx, cy, r = margin + 32, 100, 32
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=2)
    font_num = get_font(34, bold=True)
    n_bbox = draw.textbbox((0, 0), num_str, font=font_num)
    draw.text((cx - (n_bbox[2] - n_bbox[0]) // 2,
               cy - (n_bbox[3] - n_bbox[1]) // 2 - 2),
              num_str, font=font_num, fill=GOLD)

    # Headline
    font_h = get_font(64, bold=True)
    y = 185
    lines = wrap_text(headline, font_h, W - margin * 2, draw)
    for line in lines[:3]:
        draw.text((margin, y), line, font=font_h, fill=WHITE)
        y += 78

    # Separatore elegante: linea + punto
    sep_y = y + 28
    draw.rectangle([margin, sep_y, margin + 60, sep_y + 2], fill=GOLD)
    draw.ellipse([margin + 68, sep_y - 3, margin + 76, sep_y + 5], fill=GOLD)

    # Body
    font_b = get_font(38)
    y = sep_y + 44
    body_lines = wrap_text(body, font_b, W - margin * 2 - 20, draw)
    for line in body_lines[:6]:
        draw.text((margin, y), line, font=font_b, fill=CREAM)
        y += 54

    return img


def slide_cta(author_name: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_base(draw)
    draw_corner_accent(draw)
    draw_branding(draw)

    # Cerchio monogramma
    cx, cy, r = W // 2, 310, 100
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=2)
    # Cerchio interno sottile
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
                 outline=(*GOLD, 60), width=1)
    # Iniziali
    initials = "".join(w[0] for w in author_name.split()[:2]).upper()
    font_init = get_font(64, bold=True)
    ib = draw.textbbox((0, 0), initials, font=font_init)
    draw.text((cx - (ib[2] - ib[0]) // 2, cy - (ib[3] - ib[1]) // 2 - 2),
              initials, font=font_init, fill=GOLD)

    # Nome
    font_name = get_font(46, bold=True)
    nb = draw.textbbox((0, 0), author_name, font=font_name)
    draw.text(((W - (nb[2] - nb[0])) // 2, 448), author_name,
              font=font_name, fill=WHITE)

    # Ruolo
    font_role = get_font(30)
    role = "Consulente Finanziario Indipendente"
    rb = draw.textbbox((0, 0), role, font=font_role)
    draw.text(((W - (rb[2] - rb[0])) // 2, 512), role,
              font=font_role, fill=GOLD)

    # Linea decorativa centrata
    draw_thin_line(draw, W // 2 - 50, 578, W // 2 + 50)

    # CTA
    font_cta = get_font(42, bold=True)
    cta = "Ti è stato utile?"
    cb = draw.textbbox((0, 0), cta, font=font_cta)
    draw.text(((W - (cb[2] - cb[0])) // 2, 614), cta, font=font_cta, fill=WHITE)

    # Azioni — bullet dorato + testo (no emoji, non supportate da DejaVu)
    font_act = get_font(32)
    actions = [
        "Commenta la tua esperienza",
        "Condividi con chi ne ha bisogno",
        "Seguimi per altri contenuti",
    ]
    y = 692
    bullet_r = 5
    for action in actions:
        lb = draw.textbbox((0, 0), action, font=font_act)
        text_w = lb[2] - lb[0]
        total_w = bullet_r * 2 + 16 + text_w
        x = (W - total_w) // 2
        # Pallino dorato
        draw.ellipse([x, y + 12, x + bullet_r * 2, y + 12 + bullet_r * 2], fill=GOLD)
        # Testo
        draw.text((x + bullet_r * 2 + 16, y), action, font=font_act, fill=SLATE)
        y += 52

    return img


def build_slides(content: dict) -> list[Image.Image]:
    slides: list[Image.Image] = []
    slides.append(slide_cover(content["title"], content["topic"]))
    points = content["points"]
    total_content = len(points)
    for i, point in enumerate(points):
        slides.append(slide_point(
            number=i + 1,
            headline=point["headline"],
            body=point["body"],
            slide_idx=i,
            total=total_content,
        ))
    slides.append(slide_cta(content.get("author", "Federico Borrasso")))
    return slides


def build_carousel(content: dict, output_path: str = "automation/carousel.pdf") -> str:
    slides = build_slides(content)
    pdf = FPDF(unit="pt", format=[W, H])
    tmp_dir = Path("automation/tmp_slides")
    tmp_dir.mkdir(exist_ok=True)

    for idx, img in enumerate(slides):
        tmp_path = str(tmp_dir / f"slide_{idx:02d}.jpg")
        img.save(tmp_path, "JPEG", quality=95)
        pdf.add_page()
        pdf.image(tmp_path, 0, 0, W, H)

    pdf.output(output_path)
    for f in tmp_dir.glob("*.jpg"):
        f.unlink()
    tmp_dir.rmdir()
    return output_path


def save_slide_jpegs(content: dict, out_dir: str = "automation/preview_slides",
                     size: int = 1080) -> list[str]:
    """Salva le slide come JPEG. size=1080 per LinkedIn, 800 per Telegram preview."""
    slides = build_slides(content)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    paths = []
    for idx, img in enumerate(slides):
        if size != W:
            img = img.resize((size, size), Image.LANCZOS)
        p = str(out / f"slide_{idx:02d}.jpg")
        img.save(p, "JPEG", quality=92)
        paths.append(p)
    return paths


if __name__ == "__main__":
    test_content = {
        "title": "PAC: investi ogni mese, costruisci il futuro",
        "topic": "Piani di Accumulo del Capitale",
        "author": "Federico Borrasso",
        "points": [
            {"headline": "Cos'è un PAC", "body": "Investi una cifra fissa ogni mese, indipendentemente dal mercato. Semplice, automatico, efficace."},
            {"headline": "Dollar Cost Averaging", "body": "Compri più quote quando i prezzi scendono e meno quando salgono. Il tempo lavora per te."},
            {"headline": "Quanto serve per iniziare", "body": "Anche 50€ al mese sono sufficienti. L'abitudine conta più dell'importo iniziale."},
            {"headline": "Errori da evitare", "body": "Interrompere nei momenti di crisi è l'errore più costoso. Il PAC funziona proprio nelle fasi difficili."},
        ]
    }
    path = build_carousel(test_content)
    print(f"Carosello generato: {path}")
