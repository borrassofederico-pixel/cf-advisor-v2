"""
Genera contenuto per un carosello LinkedIn (consulente finanziario)
usando Claude API, poi invia anteprima su Telegram per approvazione.
"""

import os
import json
import anthropic
import requests
from datetime import datetime

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

    # Anteprima testuale per Telegram
    points_preview = "\n".join(
        f"  {i+1}. *{p['headline']}*\n      _{p['body']}_"
        for i, p in enumerate(content["points"])
    )

    preview = (
        f"🎠 *Carosello LinkedIn di oggi*\n"
        f"🏷️ Tema: _{topic}_\n\n"
        f"📌 *{content['title']}*\n\n"
        f"{points_preview}\n\n"
        f"{'─' * 28}\n"
        f"📝 *Caption post:*\n{content['caption']}\n"
        f"{'─' * 28}\n\n"
        f"Approvi la pubblicazione?"
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
            "text": preview,
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
