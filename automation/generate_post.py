"""
Genera un post LinkedIn per consulenti finanziari usando Claude API,
poi lo invia su Telegram per approvazione.
"""

import os
import json
import random
import anthropic
import requests
from datetime import datetime

# ── Temi a rotazione ────────────────────────────────────────────────────────
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

SYSTEM_PROMPT = """Sei un consulente finanziario italiano esperto e autorevole.
Scrivi post LinkedIn professionali, coinvolgenti e utili per il tuo pubblico.

Regole:
- Tono professionale ma accessibile, non accademico
- Lunghezza: 150-250 parole
- Struttura: hook forte nella prima riga, corpo con valore concreto, CTA finale
- Usa emoji con moderazione (2-4 max)
- Niente hashtag generici come #finanza — solo hashtag specifici e rilevanti (3-5 max)
- NON fare mai promesse di rendimento o consulenze specifiche
- Il post deve essere in italiano
- Non includere titoli o intestazioni, solo testo fluente"""


def pick_topic() -> str:
    # Rotazione semi-casuale basata sul giorno dell'anno per evitare ripetizioni ravvicinate
    day_of_year = datetime.now().timetuple().tm_yday
    return TOPICS[day_of_year % len(TOPICS)]


def generate_post(topic: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Scrivi un post LinkedIn sul tema: {topic}",
            }
        ],
    )
    return message.content[0].text.strip()


def send_to_telegram(post_text: str, topic: str) -> dict:
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    # Salva il post in un file temporaneo per il passaggio al workflow di pubblicazione
    pending = {"post": post_text, "topic": topic, "generated_at": datetime.utcnow().isoformat()}
    with open("automation/pending_post.json", "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    # Messaggio di anteprima
    preview = (
        f"📝 *Post LinkedIn di oggi*\n"
        f"🏷️ Tema: _{topic}_\n\n"
        f"{'─' * 30}\n\n"
        f"{post_text}\n\n"
        f"{'─' * 30}\n\n"
        f"Approvi la pubblicazione?"
    )

    # Keyboard con bottoni inline
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Pubblica", "callback_data": "approve"},
                {"text": "🔄 Rigenera", "callback_data": "regenerate"},
                {"text": "❌ Salta oggi", "callback_data": "skip"},
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": preview,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard),
    }

    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():
    topic = pick_topic()
    print(f"[generate_post] Generando post su: {topic}")

    post = generate_post(topic)
    print(f"[generate_post] Post generato ({len(post)} caratteri)")

    result = send_to_telegram(post, topic)
    print(f"[generate_post] Inviato su Telegram. Message ID: {result['result']['message_id']}")


if __name__ == "__main__":
    main()
