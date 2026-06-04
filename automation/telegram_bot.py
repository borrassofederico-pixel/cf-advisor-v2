"""
Webhook Telegram: riceve i callback dei bottoni (approva/rigenera/salta)
e triggera la pubblicazione su LinkedIn o la rigenerazione del post.

Questo script gira come GitHub Actions workflow separato in risposta
all'approvazione dell'utente, oppure come server standalone.

Modalità: polling (semplice, senza server pubblico esposto).
Il workflow GitHub Actions lo fa girare per N minuti dopo la generazione.
"""

import os
import json
import time
import requests
import subprocess
from datetime import datetime, timezone

POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_MINUTES", "30")) * 60  # default 30 min


def get_updates(bot_token: str, offset: int = 0) -> list:
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    resp = requests.get(url, params={"offset": offset, "timeout": 20}, timeout=30)
    resp.raise_for_status()
    return resp.json().get("result", [])


def answer_callback(bot_token: str, callback_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_id, "text": text}, timeout=10)


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)


def publish_to_linkedin(post_text: str) -> bool:
    app_url = os.environ.get("APP_URL", "").rstrip("/")
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    person_id = os.environ.get("LINKEDIN_PERSON_ID", "")

    if not all([access_token, person_id]):
        print("[telegram_bot] Credenziali LinkedIn mancanti nelle env vars")
        return False

    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202304",
        },
        json={
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        },
        timeout=15,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"[telegram_bot] Post pubblicato! ID: {data.get('id')}")
        return True
    else:
        print(f"[telegram_bot] Errore LinkedIn {resp.status_code}: {resp.text}")
        return False


def load_pending_post() -> dict | None:
    path = "automation/pending_post.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def main():
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    print(f"[telegram_bot] In ascolto per {POLL_TIMEOUT // 60} minuti...")

    offset = 0
    start_time = time.time()
    handled = False

    while not handled and (time.time() - start_time) < POLL_TIMEOUT:
        try:
            updates = get_updates(bot_token, offset)
        except Exception as e:
            print(f"[telegram_bot] Errore polling: {e}")
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1

            cb = update.get("callback_query")
            if not cb:
                continue

            data = cb.get("data")
            user = cb["from"].get("username") or cb["from"].get("first_name")
            print(f"[telegram_bot] Callback da {user}: {data}")

            if data == "approve":
                answer_callback(bot_token, cb["id"], "⏳ Pubblicazione in corso...")
                pending = load_pending_post()
                if pending and publish_to_linkedin(pending["post"]):
                    send_message(
                        bot_token, chat_id,
                        f"✅ *Post pubblicato su LinkedIn!*\n\n_{pending['topic']}_"
                    )
                else:
                    send_message(bot_token, chat_id, "❌ Errore durante la pubblicazione. Controlla i log.")
                handled = True

            elif data == "regenerate":
                answer_callback(bot_token, cb["id"], "🔄 Rigenerazione in corso...")
                send_message(bot_token, chat_id, "🔄 Sto rigenerando il post, attendi...")
                subprocess.run(["python", "automation/generate_post.py"], check=False)
                # Ricomincia il loop di polling per intercettare la nuova risposta
                start_time = time.time()

            elif data == "skip":
                answer_callback(bot_token, cb["id"], "⏭️ Post saltato per oggi.")
                send_message(bot_token, chat_id, "⏭️ *Post saltato.* A domani!")
                handled = True

    if not handled:
        send_message(
            bot_token, chat_id,
            "⏰ Nessuna risposta ricevuta entro i tempi. Il post non è stato pubblicato.\n"
            "Puoi pubblicarlo manualmente dalla dashboard."
        )
        print("[telegram_bot] Timeout scaduto senza risposta.")


if __name__ == "__main__":
    main()
