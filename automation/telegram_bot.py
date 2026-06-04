"""
Polling Telegram: riceve approvazione e pubblica il carosello su LinkedIn
come documento PDF (ogni pagina = una slide del carosello).
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

from generate_carousel import build_carousel

POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_MINUTES", "30")) * 60


def get_updates(bot_token: str, offset: int = 0) -> list:
    resp = requests.get(
        f"https://api.telegram.org/bot{bot_token}/getUpdates",
        params={"offset": offset, "timeout": 20},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("result", [])


def answer_callback(bot_token: str, callback_id: str, text: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery",
        json={"callback_query_id": callback_id, "text": text},
        timeout=10,
    )


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )


def initialize_linkedin_upload(access_token: str, person_id: str) -> tuple[str, str]:
    """Inizializza l'upload documento su LinkedIn. Restituisce (upload_url, asset_urn)."""
    resp = requests.post(
        "https://api.linkedin.com/rest/documents",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202304",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json={"initializeUploadRequest": {"owner": f"urn:li:person:{person_id}"}},
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn init upload error {resp.status_code}: {resp.text}")
    data = resp.json()
    upload_url = data["value"]["uploadUrl"]
    asset_urn = data["value"]["document"]
    return upload_url, asset_urn


def upload_pdf(upload_url: str, pdf_path: str, access_token: str) -> None:
    """Carica il PDF sull'URL di upload fornito da LinkedIn."""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    resp = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
        },
        data=pdf_bytes,
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn upload error {resp.status_code}: {resp.text}")


def publish_carousel(caption: str, asset_urn: str,
                     access_token: str, person_id: str) -> str:
    """Crea il post LinkedIn con il documento carosello."""
    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202304",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json={
            "author": f"urn:li:person:{person_id}",
            "commentary": caption,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "media": {
                    "title": caption[:100],
                    "id": asset_urn,
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        },
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn post error {resp.status_code}: {resp.text}")
    return resp.headers.get("x-restli-id", "unknown")


def publish_to_linkedin(pending: dict) -> bool:
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    person_id = os.environ.get("LINKEDIN_PERSON_ID", "")

    if not all([access_token, person_id]):
        print("[telegram_bot] Credenziali LinkedIn mancanti")
        return False

    content = pending["content"]

    try:
        # 1. Genera il PDF carosello
        print("[telegram_bot] Generazione carosello PDF...")
        pdf_path = build_carousel(content)
        print(f"[telegram_bot] PDF creato: {pdf_path}")

        # 2. Inizializza upload LinkedIn
        print("[telegram_bot] Inizializzazione upload LinkedIn...")
        upload_url, asset_urn = initialize_linkedin_upload(access_token, person_id)

        # 3. Carica il PDF
        print("[telegram_bot] Upload PDF...")
        upload_pdf(upload_url, pdf_path, access_token)

        # 4. Pubblica il post
        print("[telegram_bot] Pubblicazione post...")
        post_id = publish_carousel(
            caption=content["caption"],
            asset_urn=asset_urn,
            access_token=access_token,
            person_id=person_id,
        )
        print(f"[telegram_bot] Post pubblicato! ID: {post_id}")

        # Pulizia PDF
        Path(pdf_path).unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"[telegram_bot] Errore pubblicazione: {e}")
        return False


def load_pending() -> dict | None:
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
            user = cb["from"].get("first_name", "?")
            print(f"[telegram_bot] {user}: {data}")

            if data == "approve":
                answer_callback(bot_token, cb["id"], "⏳ Generazione carosello...")
                send_message(bot_token, chat_id, "🎨 Creo le slide e pubblico su LinkedIn...")
                pending = load_pending()
                if pending and publish_to_linkedin(pending):
                    send_message(bot_token, chat_id,
                        f"✅ *Carosello pubblicato su LinkedIn!*\n\n_{pending['topic']}_")
                else:
                    send_message(bot_token, chat_id,
                        "❌ Errore pubblicazione. Controlla i log su GitHub Actions.")
                handled = True

            elif data == "regenerate":
                answer_callback(bot_token, cb["id"], "🔄 Rigenero...")
                send_message(bot_token, chat_id, "🔄 Rigenerazione in corso, attendi...")
                subprocess.run(
                    [sys.executable, "automation/generate_post.py"],
                    check=False,
                    cwd=os.getcwd(),
                    env=os.environ.copy(),
                )
                start_time = time.time()

            elif data == "skip":
                answer_callback(bot_token, cb["id"], "⏭️ Saltato.")
                send_message(bot_token, chat_id, "⏭️ *Post saltato.* A domani!")
                handled = True

    if not handled:
        send_message(bot_token, chat_id,
            "⏰ Nessuna risposta in 30 minuti. Post non pubblicato.")
        print("[telegram_bot] Timeout.")


if __name__ == "__main__":
    main()
