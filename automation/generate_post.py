"""
Genera contenuto per un carosello LinkedIn (consulente finanziario)
usando Claude API, poi invia anteprima su Telegram per approvazione.
"""

import os
import sys
import json
import anthropic
import requests
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from generate_carousel import save_slide_jpegs

# ── Temi a rotazione ─────────────────────────────────────────────────────────
TOPICS = [
    "pianificazione pensionistica e previdenza complementare",
    "gestione del rischio e diversificazione del portafoglio",
    "educazione finanziaria per le famiglie",
    "inflazione e protezione del potere d'acquisto",
    "investire in ETF vs fondi attivi",
    "l'importanza dell'orizzonte temporale negli investimenti",
    "errori comportamentali negli investimenti (finanza comportamentale)",
    "come costruire un fondo di emergenza",
    "fiscalità degli investimenti in Italia",
    "obiettivi finanziari: come definirli e raggiungerli",
]

SYSTEM_PROMPT = """Sei un consulente finanziario italiano esperto. Crei contenuti LinkedIn
sotto forma di carosello: ogni slide ha un titolo breve e un testo esplicativo.

Rispondi SOLO con un JSON valido (nessun testo prima o dopo), con questa struttura:
{
  "title": "Titolo della slide di copertina (max 8 parole, incisivo)",
  "caption": "Testo del post LinkedIn che accompagna il carosello (100-150 parole, hook forte, CTA finale, 3-4 hashtag pertinenti)",
  "points": [
    {"headline": "Titolo punto 1 (max 5 parole)", "body": "Spiegazione (max 30 parole, concreta e utile)"},
    {"headline": "Titolo punto 2 (max 5 parole)", "body": "Spiegazione (max 30 parole, concreta e utile)"},
    {"headline": "Titolo punto 3 (max 5 parole)", "body": "Spiegazione (max 30 parole, concreta e utile)"},
    {"headline": "Titolo punto 4 (max 5 parole)", "body": "Spiegazione (max 30 parole, concreta e utile)"}
  ]
}

Regole:
- Tono professionale ma accessibile
- NON promettere rendimenti specifici
- Italiano corretto, zero gergo inutile
- I titoli dei punti devono essere autonomi e leggibili anche senza il body"""


def pick_topic() -> str:
    override = os.environ.get("TOPIC_OVERRIDE", "").strip()
    if override:
        return override
    day_of_year = datetime.now().timetuple().tm_yday
    return TOPICS[day_of_year % len(TOPICS)]


def generate_content(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Tema del carosello: {topic}"}],
    )
    raw = message.content[0].text.strip()
    # Rimuovi eventuali backtick markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def send_slides_to_telegram(bot_token: str, chat_id: str,
                             slide_paths: list[str], caption: str) -> None:
    """Manda le slide come album foto su Telegram (max 10 immagini)."""
    media = []
    files = {}
    for i, path in enumerate(slide_paths[:10]):
        key = f"photo{i}"
        media.append({
            "type": "photo",
            "media": f"attach://{key}",
            "caption": caption if i == 0 else "",
            "parse_mode": "Markdown",
        })
        files[key] = (Path(path).name, open(path, "rb"), "image/jpeg")

    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMediaGroup",
        data={"chat_id": chat_id, "media": json.dumps(media)},
        files=files,
        timeout=60,
    )
    # Chiudi i file aperti
    for _, (_, f, _) in files.items():
        f.close()
    resp.raise_for_status()


def send_to_telegram(content: dict, topic: str) -> dict:
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    # Salva pending
    pending = {
        "content": content,
        "topic": topic,
        "generated_at": datetime.utcnow().isoformat(),
        "type": "carousel"
    }
    with open("automation/pending_post.json", "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    # 1. Genera slide immagini
    print("[generate_post] Generazione slide per anteprima...")
    content["topic"] = topic
    slide_paths = save_slide_jpegs(content)
    print(f"[generate_post] {len(slide_paths)} slide generate")

    # 2. Manda le immagini come album
    album_caption = f"🎠 *{content['title']}*\n🏷️ _{topic}_"
    send_slides_to_telegram(bot_token, chat_id, slide_paths, album_caption)

    # Pulizia immagini preview
    for p in slide_paths:
        Path(p).unlink(missing_ok=True)
    Path("automation/preview_slides").rmdir() if Path("automation/preview_slides").exists() else None

    # 3. Manda messaggio con bottoni di approvazione
    approval_text = (
        f"📝 *Caption del post:*\n{content['caption']}\n\n"
        f"Approvi la pubblicazione su LinkedIn?"
    )
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Pubblica", "callback_data": "approve"},
            {"text": "🔄 Rigenera", "callback_data": "regenerate"},
            {"text": "❌ Salta oggi", "callback_data": "skip"},
        ]]
    }
    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": approval_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard),
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    topic = pick_topic()
    print(f"[generate_post] Tema: {topic}")

    content = generate_content(topic)
    content["author"] = "Federico Borrasso"
    print(f"[generate_post] Contenuto generato: {content['title']}")

    result = send_to_telegram(content, topic)
    print(f"[generate_post] Inviato su Telegram. Message ID: {result['result']['message_id']}")


if __name__ == "__main__":
    main()
