"""
Polling Telegram: riceve approvazione e pubblica il carosello su LinkedIn
come post multi-immagine (ogni slide = una foto).
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

from generate_carousel import save_slide_jpegs

POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_MINUTES", "30")) * 60
LI_VERSION = "202404"
LI_HEADERS_BASE = {
    "Content-Type": "application/json",
    "LinkedIn-Version": LI_VERSION,
    "X-Restli-Protocol-Version": "2.0.0",
}


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


def upload_image_to_linkedin(image_path: str, access_token: str, person_id: str) -> str:
    """Carica una singola immagine su LinkedIn e restituisce l'URN."""
    headers = {**LI_HEADERS_BASE, "Authorization": f"Bearer {access_token}"}

    resp = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": f"urn:li:person:{person_id}"}},
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn image init error {resp.status_code}: {resp.text}")
    data = resp.json()
    upload_url = data["value"]["uploadUrl"]
    image_urn = data["value"]["image"]

    with open(image_path, "rb") as f:
        img_bytes = f.read()
    resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {access_token}"},
        data=img_bytes,
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn image upload error {resp.status_code}: {resp.text}")

    return image_urn


def publish_image_post(caption: str, image_urns: list[str],
                       access_token: str, person_id: str) -> str:
    """Pubblica un post LinkedIn con una o più immagini."""
    headers = {**LI_HEADERS_BASE, "Authorization": f"Bearer {access_token}"}

    if len(image_urns) == 1:
        content = {"media": {"id": image_urns[0]}}
    else:
        content = {"multiImage": {"images": [{"id": urn} for urn in image_urns]}}

    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json={
            "author": f"urn:li:person:{person_id}",
            "commentary": caption,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": content,
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
    content["topic"] = pending.get("topic", "Finanza personale")

    try:
        print("[telegram_bot] Generazione slide immagini...")
        slide_paths = save_slide_jpegs(content, out_dir="automation/publish_slides", size=1080)
        print(f"[telegram_bot] {len(slide_paths)} slide generate")

        image_urns = []
        for i, path in enumerate(slide_paths):
            print(f"[telegram_bot] Upload slide {i+1}/{len(slide_paths)}...")
            urn = upload_image_to_linkedin(path, access_token, person_id)
            image_urns.append(urn)

        for p in slide_paths:
            Path(p).unlink(missing_ok=True)
        publish_dir = Path("automation/publish_slides")
        if publish_dir.exists():
            try:
                publish_dir.rmdir()
            except OSError:
                pass

        print(f"[telegram_bot] Pubblicazione post con {len(image_urns)} immagini...")
        post_id = publish_image_post(
            caption=content["caption"],
            image_urns=image_urns,
            access_token=access_token,
            person_id=person_id,
        )
        print(f"[telegram_bot] Post pubblicato! ID: {post_id}")
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
            wait = 15 if "409" in str(e) else 5
            time.sleep(wait)
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
                answer_callback(bot_token, cb["id"], "⏳ Carico le slide su LinkedIn...")
                send_message(bot_token, chat_id, "🎨 Carico le slide e pubblico su LinkedIn...")
                pending = load_pending()
                if pending and publish_to_linkedin(pending):
                    send_message(bot_token, chat_id,
                        f"✅ *Post pubblicato su LinkedIn!*\n\n_{pending['topic']}_")
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
