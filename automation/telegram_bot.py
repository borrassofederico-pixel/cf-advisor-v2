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
import anthropic
from pathlib import Path

from generate_carousel import save_slide_jpegs

POLL_TIMEOUT = int(os.environ.get("TELEGRAM_POLL_MINUTES", "300")) * 60
LI_V2_HEADERS = {
    "Content-Type": "application/json",
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


def get_author_urn(access_token: str) -> str:
    """Prova a ottenere l'URN author per ugcPosts.
    Prima tenta /v2/me (numeric ID → urn:li:member:ID),
    poi fallback su /v2/userinfo (sub → urn:li:person:SUB)."""
    # Tentativo 1: /v2/me con numeric member ID (richiesto da ugcPosts)
    resp = requests.get(
        "https://api.linkedin.com/v2/me",
        headers={**LI_V2_HEADERS, "Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    print(f"[telegram_bot] /v2/me: status={resp.status_code} body={resp.text[:120]}")
    if resp.ok:
        numeric_id = resp.json().get("id", "")
        if numeric_id:
            print(f"[telegram_bot] Numeric member ID: {numeric_id}")
            return f"urn:li:member:{numeric_id}"

    # Tentativo 2: /v2/userinfo (sub alfanumerico OpenID)
    resp2 = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp2.ok:
        sub = resp2.json().get("sub", "")
        if sub:
            print(f"[telegram_bot] OpenID sub: {sub} → urn:li:person:{sub}")
            return f"urn:li:person:{sub}"

    raise RuntimeError("Impossibile ottenere author URN")


def register_image(access_token: str, author_urn: str) -> tuple[str, str]:
    """Registra asset immagine su LinkedIn v2. Restituisce (upload_url, asset_urn)."""
    # Estrae il member_id dall'URN per il campo owner
    owner = author_urn  # può essere urn:li:member:ID o urn:li:person:SUB
    resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers={**LI_V2_HEADERS, "Authorization": f"Bearer {access_token}"},
        json={
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": owner,
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }],
            }
        },
        timeout=15,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn registerUpload error {resp.status_code}: {resp.text}")
    data = resp.json()
    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn = data["value"]["asset"]
    return upload_url, asset_urn


def upload_image(upload_url: str, image_path: str, access_token: str) -> None:
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "image/jpeg"},
        data=img_bytes,
        timeout=60,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn image upload error {resp.status_code}: {resp.text}")


def publish_ugc_post(caption: str, asset_urns: list[str],
                     access_token: str, author_urn: str) -> str:
    """Pubblica ugcPost LinkedIn con una o più immagini."""
    media = [{"status": "READY", "description": {"text": ""}, "media": urn, "title": {"text": ""}}
             for urn in asset_urns]
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={**LI_V2_HEADERS, "Authorization": f"Bearer {access_token}"},
        json={
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": caption},
                    "shareMediaCategory": "IMAGE",
                    "media": media,
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        },
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(f"LinkedIn ugcPost error {resp.status_code}: {resp.text}")
    return resp.json().get("id", "unknown")


def _upload_and_publish(slide_paths: list, caption: str,
                        access_token: str, author_urn: str) -> str:
    """Registra+carica le slide per un dato author e pubblica il ugcPost.
    Gli asset LinkedIn sono legati all'owner: vanno ri-registrati per ogni author."""
    asset_urns = []
    for i, path in enumerate(slide_paths):
        print(f"[telegram_bot] Upload slide {i+1}/{len(slide_paths)} per {author_urn}...")
        upload_url, asset_urn = register_image(access_token, author_urn)
        upload_image(upload_url, path, access_token)
        asset_urns.append(asset_urn)
    print(f"[telegram_bot] Pubblicazione post come {author_urn}...")
    return publish_ugc_post(
        caption=caption,
        asset_urns=asset_urns,
        access_token=access_token,
        author_urn=author_urn,
    )


def publish_to_linkedin(pending: dict) -> str | None:
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
    org_id = os.environ.get("LINKEDIN_ORG_ID", "").strip()
    # Token dedicato alla pagina (app Community Management API).
    # Se non impostato, usa lo stesso token del profilo.
    org_token = os.environ.get("LINKEDIN_ORG_ACCESS_TOKEN", "").strip() or access_token

    if not access_token:
        print("[telegram_bot] LINKEDIN_ACCESS_TOKEN mancante")
        return None

    content = pending["content"]
    content["topic"] = pending.get("topic", "Finanza personale")

    try:
        author_urn = get_author_urn(access_token)
        print("[telegram_bot] Generazione slide immagini...")
        slide_paths = save_slide_jpegs(content, out_dir="automation/publish_slides", size=1080)
        print(f"[telegram_bot] {len(slide_paths)} slide generate")

        # 1) Pubblicazione sul profilo personale
        post_id = _upload_and_publish(slide_paths, content["caption"], access_token, author_urn)
        print(f"[telegram_bot] Post profilo pubblicato! ID: {post_id}")

        # 2) Pubblicazione sulla pagina LinkedIn collegata (se configurata)
        if org_id:
            org_urn = f"urn:li:organization:{org_id}"
            try:
                org_post_id = _upload_and_publish(
                    slide_paths, content["caption"], org_token, org_urn)
                print(f"[telegram_bot] Post pagina pubblicato! ID: {org_post_id}")
            except Exception as org_err:
                print(f"[telegram_bot] Errore pubblicazione pagina: {org_err}")

        for p in slide_paths:
            Path(p).unlink(missing_ok=True)
        publish_dir = Path("automation/publish_slides")
        if publish_dir.exists():
            try:
                publish_dir.rmdir()
            except OSError:
                pass

        return post_id

    except Exception as e:
        print(f"[telegram_bot] Errore pubblicazione: {e}")
        return None


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


def _generate_content(topic: str) -> dict:
    """Genera contenuto ex-novo per un dato tema."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Tema del carosello: {topic}"}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def refine_content(existing: dict, feedback: str) -> dict:
    """Chiama Claude per applicare le modifiche richieste al contenuto esistente."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_msg = (
        f"Contenuto attuale:\n{json.dumps(existing, ensure_ascii=False, indent=2)}\n\n"
        f"Modifica richiesta: {feedback}\n\n"
        "Restituisci il JSON completo aggiornato con le modifiche applicate."
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _send_slides_to_telegram(bot_token: str, chat_id: str, slide_paths: list, caption: str) -> None:
    import json as _json
    from pathlib import Path as _Path
    media = []
    files = {}
    for i, path in enumerate(slide_paths[:10]):
        key = f"photo{i}"
        media.append({"type": "photo", "media": f"attach://{key}",
                      "caption": caption if i == 0 else "", "parse_mode": "Markdown"})
        files[key] = (_Path(path).name, open(path, "rb"), "image/jpeg")
    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMediaGroup",
        data={"chat_id": chat_id, "media": _json.dumps(media)},
        files=files, timeout=60,
    )
    for _, (_, f, _) in files.items():
        f.close()
    resp.raise_for_status()


def send_preview_to_telegram(bot_token: str, chat_id: str, pending: dict) -> None:
    """Ri-invia l'anteprima slide + bottoni di approvazione su Telegram."""
    content = pending["content"]
    topic = pending.get("topic", "")

    slide_paths = save_slide_jpegs(content, size=800)
    album_caption = f"🎠 *{content['title']}*\n🏷️ _{topic}_"
    _send_slides_to_telegram(bot_token, chat_id, slide_paths, album_caption)
    for p in slide_paths:
        Path(p).unlink(missing_ok=True)
    preview_dir = Path("automation/preview_slides")
    if preview_dir.exists():
        try:
            preview_dir.rmdir()
        except OSError:
            pass

    approval_text = (
        f"📝 *Caption del post:*\n{content['caption']}\n\n"
        f"Approvi la pubblicazione su LinkedIn?"
    )
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Pubblica", "callback_data": "approve"},
            {"text": "✏️ Modifica", "callback_data": "edit"},
            {"text": "🔄 Rigenera", "callback_data": "regenerate"},
            {"text": "❌ Salta oggi", "callback_data": "skip"},
        ]]
    }
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": approval_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard),
        },
        timeout=10,
    )


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
    waiting_for_edit = None  # None | "text" | "tema"

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

            # Gestione messaggio di testo (modifica testo o cambio tema)
            if waiting_for_edit:
                msg = update.get("message", {})
                text = msg.get("text", "").strip()
                if text and not text.startswith("/"):
                    mode = waiting_for_edit
                    waiting_for_edit = False
                    pending = load_pending()
                    if pending:
                        try:
                            if mode == "text":
                                send_message(bot_token, chat_id, "✏️ Applico le modifiche, attendi...")
                                updated = refine_content(pending["content"], text)
                                updated["topic"] = pending.get("topic", "")
                                pending["content"] = updated
                            else:  # tema
                                send_message(bot_token, chat_id, f"🔀 Genero un nuovo post su: _{text}_...")
                                updated = _generate_content(text)
                                updated["topic"] = text
                                updated["author"] = "Federico Borrasso"
                                pending["content"] = updated
                                pending["topic"] = text
                            with open("automation/pending_post.json", "w") as f:
                                json.dump(pending, f, ensure_ascii=False, indent=2)
                            send_message(bot_token, chat_id, "✅ Modifiche applicate! Ecco il post aggiornato:")
                            send_preview_to_telegram(bot_token, chat_id, pending)
                        except Exception as e:
                            print(f"[telegram_bot] Errore modifica: {e}")
                            send_message(bot_token, chat_id, f"❌ Errore: {e}")
                    continue

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

            elif data == "edit":
                answer_callback(bot_token, cb["id"], "✏️ Cosa vuoi fare?")
                edit_keyboard = {
                    "inline_keyboard": [[
                        {"text": "✏️ Modifica testo", "callback_data": "edit_text"},
                        {"text": "🔀 Cambia tema", "callback_data": "edit_tema"},
                    ]]
                }
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "Cosa vuoi modificare?",
                        "reply_markup": json.dumps(edit_keyboard),
                    },
                    timeout=10,
                )

            elif data == "edit_text":
                answer_callback(bot_token, cb["id"], "✏️ Scrivi le modifiche...")
                send_message(bot_token, chat_id,
                    "✍️ Scrivi cosa vuoi cambiare nel post\n"
                    "_(es: \"rendi il tono più diretto\" o \"rimuovi il punto 3\")_")
                waiting_for_edit = "text"

            elif data == "edit_tema":
                answer_callback(bot_token, cb["id"], "🔀 Scrivi il nuovo tema...")
                send_message(bot_token, chat_id,
                    "🔀 Scrivi il tema che vuoi per il post\n"
                    "_(es: \"come investire in ETF\" o \"gestione del debito\")_")
                waiting_for_edit = "tema"

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
            "⏰ Nessuna risposta ricevuta. Post non pubblicato.")
        print("[telegram_bot] Timeout.")
        pending = load_pending()
        if pending:
            _save_to_history(pending, status="timeout")


if __name__ == "__main__":
    main()
