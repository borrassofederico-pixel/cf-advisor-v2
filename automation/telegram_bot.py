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
LI_REST_VERSION = "202308"
LI_REST_HEADERS = {
    "Content-Type": "application/json",
    "LinkedIn-Version": LI_REST_VERSION,
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


def get_active_li_version(access_token: str) -> str:
    """Trova la versione LinkedIn REST API più recente attiva."""
    candidates = ["20250101", "20241201", "20241101", "20241001", "20240901",
                  "20240801", "20240701", "20240601", "20240501", "20240401"]
    for version in candidates:
        resp = requests.get(
            "https://api.linkedin.com/rest/posts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "LinkedIn-Version": version,
                "X-Restli-Protocol-Version": "2.0.0",
            },
            params={"author": "urn:li:person:test", "count": 0},
            timeout=5,
        )
        # 426 = versione non valida, altri errori = versione OK ma parametri sbagliati
        if resp.status_code != 426:
            print(f"[telegram_bot] Versione LinkedIn attiva: {version} (status {resp.status_code})")
            return version
    raise RuntimeError("Nessuna versione LinkedIn REST API attiva trovata")


def get_person_urn(access_token: str) -> str:
    """Recupera urn:li:person:SUB dal token via /v2/userinfo (scope openid+profile)."""
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.ok:
        sub = resp.json().get("sub", "")
        if sub:
            print(f"[telegram_bot] Person sub: {sub}")
            return f"urn:li:person:{sub}"
    raise RuntimeError(f"Impossibile ottenere person sub da userinfo: {resp.status_code} {resp.text}")


def init_image_upload(access_token: str, person_urn: str, version: str) -> tuple[str, str]:
    """REST API: inizializza upload immagine. Restituisce (upload_url, image_urn)."""
    headers = {
        "Content-Type": "application/json",
        "LinkedIn-Version": version,
        "X-Restli-Protocol-Version": "2.0.0",
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": person_urn}},
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn initializeUpload error {resp.status_code}: {resp.text}")
    data = resp.json()["value"]
    return data["uploadUrl"], data["image"]


def upload_image(upload_url: str, image_path: str, access_token: str) -> None:
    """Carica i byte dell'immagine sull'URL fornito da LinkedIn."""
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    resp = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/jpeg",
        },
        data=img_bytes,
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn image upload error {resp.status_code}: {resp.text}")


def publish_post(caption: str, image_urns: list[str],
                 access_token: str, person_urn: str, version: str) -> str:
    """REST API: pubblica un post LinkedIn multi-immagine."""
    headers = {
        "Content-Type": "application/json",
        "LinkedIn-Version": version,
        "X-Restli-Protocol-Version": "2.0.0",
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json={
            "author": person_urn,
            "commentary": caption,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "multiImage": {
                    "images": [{"id": urn, "altText": ""} for urn in image_urns]
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        },
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn posts error {resp.status_code}: {resp.text}")
    return resp.headers.get("x-restli-id", resp.json().get("id", "unknown"))


def publish_to_linkedin(pending: dict) -> str | None:
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")

    if not access_token:
        print("[telegram_bot] LINKEDIN_ACCESS_TOKEN mancante")
        return None

    content = pending["content"]
    content["topic"] = pending.get("topic", "Finanza personale")

    try:
        li_version = get_active_li_version(access_token)
        person_urn = get_person_urn(access_token)
        print("[telegram_bot] Generazione slide immagini...")
        slide_paths = save_slide_jpegs(content, out_dir="automation/publish_slides", size=1080)
        print(f"[telegram_bot] {len(slide_paths)} slide generate")

        image_urns = []
        for i, path in enumerate(slide_paths):
            print(f"[telegram_bot] Upload slide {i+1}/{len(slide_paths)}...")
            upload_url, image_urn = init_image_upload(access_token, person_urn, li_version)
            upload_image(upload_url, path, access_token)
            image_urns.append(image_urn)

        for p in slide_paths:
            Path(p).unlink(missing_ok=True)
        publish_dir = Path("automation/publish_slides")
        if publish_dir.exists():
            try:
                publish_dir.rmdir()
            except OSError:
                pass

        print(f"[telegram_bot] Pubblicazione post con {len(image_urns)} immagini...")
        post_id = publish_post(
            caption=content["caption"],
            image_urns=image_urns,
            access_token=access_token,
            person_urn=person_urn,
            version=li_version,
        )
        print(f"[telegram_bot] Post pubblicato! ID: {post_id}")
        return post_id

    except Exception as e:
        print(f"[telegram_bot] Errore pubblicazione: {e}")
        return None


def load_pending() -> dict | None:
    path = "automation/pending_post.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _save_to_history(pending: dict, post_id: str = "", error: str = "", status: str = "published") -> None:
    from datetime import datetime, timezone
    history_path = Path("automation/post_history.json")
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    content = pending.get("content", {})
    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "status": status,
        "topic": pending.get("topic", ""),
        "title": content.get("title", ""),
        "caption": content.get("caption", ""),
        "linkedin_post_id": post_id,
        "error": error,
    }
    history.append(entry)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2))


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
                post_id = publish_to_linkedin(pending) if pending else None
                if post_id:
                    send_message(bot_token, chat_id,
                        f"✅ *Post pubblicato su LinkedIn!*\n\n_{pending['topic']}_")
                    _save_to_history(pending, post_id=post_id, status="published")
                else:
                    send_message(bot_token, chat_id,
                        "❌ Errore pubblicazione. Controlla i log su GitHub Actions.")
                    if pending:
                        _save_to_history(pending, error="publish_failed", status="error")
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
                pending = load_pending()
                if pending:
                    _save_to_history(pending, status="skipped")
                handled = True

    if not handled:
        send_message(bot_token, chat_id,
            "⏰ Nessuna risposta in 30 minuti. Post non pubblicato.")
        print("[telegram_bot] Timeout.")
        pending = load_pending()
        if pending:
            _save_to_history(pending, status="timeout")


if __name__ == "__main__":
    main()
