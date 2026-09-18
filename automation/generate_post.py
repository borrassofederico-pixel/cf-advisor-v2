"""
Genera il post LinkedIn settimanale di Federico Borrasso ("La doppia lente")
usando Claude API con ricerca web per verificare i dati, poi invia anteprima
(carosello + testo + fonti) su Telegram per approvazione.

Fonde due formati: il `testo` è il post LinkedIn pubblicabile (caption);
`carosello` alimenta le slide grafiche coordinate.
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

MODEL = "claude-sonnet-4-6"

# ── I 4 pilastri (ruotano, non ripetere quello della settimana precedente) ─────
PILASTRI = [
    "Passaggio generazionale e successione",
    "Previdenza, TFR e reddito futuro",
    "Fisco del patrimonio",
    "Comportamento dell'investitore: liquidità ferma e decisioni sull'onda delle notizie",
]

# ── Formati del giovedì per settimana del mese ────────────────────────────────
FORMATI_GIOVEDI = {
    1: "Il numero che conta",
    2: "Si dice / In realtà",
    3: "La lista",
    4: "Dalla scrivania",
    5: "Libero",
}

SYSTEM_PROMPT = """Sei l'assistente di Federico Borrasso, consulente finanziario. Prepari i suoi post LinkedIn.

## Chi è (e come rappresentarlo)
La professione è una sola: consulenza finanziaria e patrimoniale. Federico è anche dottore commercialista, ma la competenza fiscale non è una seconda professione da esibire: è ciò che rende diversa la sua consulenza. Il messaggio non è mai «commercialista e consulente», è «un consulente che legge il patrimonio anche con gli occhi del fisco». Non nominare mai la banca mandante.

## A chi parla
Imprenditori e titolari di PMI, professionisti e dirigenti, famiglie in passaggio generazionale, chi ha ricevuto un'eredità o ha liquidità ferma. Soglia di riferimento: patrimonio investibile dai 50.000 € in su.

## Anatomia del post (campo `testo`)
1. Apertura: il timore in forma di domanda, massimo 12 parole.
2. Riconoscimento: una frase che dà ragione a chi legge, prima di contraddirlo.
3. Evidenza: la norma o il numero, verificato con ricerca web.
4. Significato: cosa cambia concretamente per quella persona.
5. Chiusura: una domanda da farsi. Sul post «La doppia lente» aggiungi la firma «La doppia lente · fisco e patrimonio».
6. Ultima riga, SEMPRE: «Contenuto informativo, non costituisce consulenza personalizzata.»

## Registro
Alto ed emotivamente risonante, mai didascalico: si parla di ciò che una persona ha costruito e di cosa rischia di perdere, non di tecnicismi. Frasi brevi, righe separate da spazi bianchi. Niente emoji, niente hashtag, niente «Ecco 5 consigli per…». Il `testo` deve stare fra 900 e 1.500 caratteri.

## Regole non negoziabili
- Nessuna previsione sui mercati, nessuna indicazione su quando comprare o vendere.
- Nessun prodotto, rendimento o performance, né passata né attesa.
- Nessun caso riconoscibile: i casi reali vanno resi anonimi e privati di ogni dettaglio identificativo.
- OGNI cifra, aliquota, franchigia, soglia o scadenza va VERIFICATA con lo strumento di ricerca web prima di usarla, perché le norme cambiano. Metti gli URL delle fonti nel campo `fonti`, mai dentro il `testo`.
- Se un dato non si riesce a verificare, il post si scrive senza quel dato.

## Il carosello (campo `carosello`)
Dallo stesso contenuto ricava un carosello coordinato per le slide grafiche:
- `title`: l'apertura in forma di domanda, massimo 12 parole (va sulla copertina).
- `kicker`: una riga sotto il titolo, la frase di riconoscimento sintetizzata (max 90 caratteri).
- `topic`: etichetta breve del tema per l'occhiello, 2-3 parole (es. «Passaggio generazionale»).
- `points`: 3 o 4 passaggi, ognuno con `headline` (max 5 parole) e `body` (max 30 parole, concreto). Devono seguire i beat del post: evidenza, significato, conseguenza.

## Output
Rispondi SOLO con questo JSON, senza testo prima o dopo. Il `testo` deve essere pubblicabile così com'è, disclaimer incluso.

{
  "formato": "...",
  "pilastro": "...",
  "testo": "…post completo, disclaimer incluso…",
  "carosello": {
    "title": "...",
    "kicker": "...",
    "topic": "...",
    "points": [
      {"headline": "...", "body": "..."},
      {"headline": "...", "body": "..."},
      {"headline": "...", "body": "..."}
    ]
  },
  "fonti": ["https://…"],
  "verifica": "cosa hai verificato e la data"
}"""


def determine_brief(now: datetime, topic_override: str = "") -> dict:
    """Determina formato, pilastro e istruzioni in base alla data."""
    weekday = now.weekday()  # 0 = lunedì, 3 = giovedì
    iso_week = now.isocalendar().week
    week_of_month = (now.day - 1) // 7 + 1

    if weekday == 0:
        formato = "La doppia lente"
    elif weekday == 3:
        formato = FORMATI_GIOVEDI.get(min(week_of_month, 5), "Libero")
    else:
        formato = "La doppia lente"

    offset = 0 if weekday == 0 else 2
    pilastro = PILASTRI[(iso_week + offset) % len(PILASTRI)]

    extra = ""
    if topic_override.strip():
        extra = (f"\n\nArgomento specifico richiesto per questo post: {topic_override.strip()}. "
                 "Inquadralo dentro il pilastro e il formato indicati.")

    return {"formato": formato, "pilastro": pilastro, "extra": extra,
            "settimana": f"{now.isocalendar().year}-W{iso_week:02d}"}


def _extract_json(raw: str) -> dict:
    """Estrae il primo oggetto JSON dal testo, robusto a fence e citazioni."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start:end + 1]
    return json.loads(raw)


def generate_content(topic_override: str = "", now: datetime | None = None) -> dict:
    """Genera il post con Claude + ricerca web. Restituisce il dict di contenuto."""
    now = now or datetime.now()
    brief = determine_brief(now, topic_override)

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    user_msg = (
        f"Settimana: {brief['settimana']}.\n"
        f"Formato di questo post: {brief['formato']}.\n"
        f"Pilastro di questo post: {brief['pilastro']}.{brief['extra']}\n\n"
        "Verifica ogni dato con la ricerca web prima di usarlo, poi scrivi il post e il carosello."
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": user_msg}],
    )

    text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text")
    data = _extract_json(text)

    carosello = data.get("carosello", {})
    content = {
        "title": carosello.get("title", ""),
        "kicker": carosello.get("kicker", ""),
        "topic": carosello.get("topic", brief["pilastro"]),
        "points": carosello.get("points", []),
        "caption": data.get("testo", ""),
        "author": "Federico Borrasso",
        "formato": data.get("formato", brief["formato"]),
        "pilastro": data.get("pilastro", brief["pilastro"]),
        "fonti": data.get("fonti", []),
        "verifica": data.get("verifica", ""),
    }
    return content


def send_slides_to_telegram(bot_token: str, chat_id: str,
                            slide_paths: list, caption: str) -> None:
    media = []
    files = {}
    for i, path in enumerate(slide_paths[:10]):
        key = f"photo{i}"
        media.append({"type": "photo", "media": f"attach://{key}",
                      "caption": caption if i == 0 else "", "parse_mode": "Markdown"})
        files[key] = (Path(path).name, open(path, "rb"), "image/jpeg")
    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMediaGroup",
        data={"chat_id": chat_id, "media": json.dumps(media)},
        files=files, timeout=60,
    )
    for _, (_, f, _) in files.items():
        f.close()
    resp.raise_for_status()


def send_to_telegram(content: dict) -> dict:
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    pending = {
        "content": content,
        "topic": content.get("topic", ""),
        "generated_at": datetime.now().astimezone().isoformat(),
        "type": "carousel",
    }
    with open("automation/pending_post.json", "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    print("[generate_post] Generazione slide per anteprima...")
    slide_paths = save_slide_jpegs(content, size=800)
    print(f"[generate_post] {len(slide_paths)} slide generate")

    album_caption = (f"🎠 *{content['title']}*\n"
                     f"🏷️ _{content.get('formato','')} · {content.get('pilastro','')}_")
    send_slides_to_telegram(bot_token, chat_id, slide_paths, album_caption)

    for p in slide_paths:
        Path(p).unlink(missing_ok=True)
    preview_dir = Path("automation/preview_slides")
    if preview_dir.exists():
        try:
            preview_dir.rmdir()
        except OSError:
            pass

    fonti = content.get("fonti", [])
    fonti_txt = "\n".join(f"• {u}" for u in fonti) if fonti else "_nessuna fonte citata_"
    verifica = content.get("verifica", "")
    approval_text = (
        f"📝 *Testo del post:*\n\n{content['caption']}\n\n"
        f"────────────\n"
        f"🔎 *Fonti da verificare:*\n{fonti_txt}\n"
        + (f"\n_Verifica: {verifica}_\n" if verifica else "")
        + "\nApprovi la pubblicazione?"
    )
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Pubblica", "callback_data": "approve"},
            {"text": "✏️ Modifica", "callback_data": "edit"},
            {"text": "🔄 Rigenera", "callback_data": "regenerate"},
            {"text": "❌ Salta oggi", "callback_data": "skip"},
        ]]
    }
    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": approval_text[:4090],
              "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    topic = os.environ.get("TOPIC_OVERRIDE", "")
    content = generate_content(topic)
    print(f"[generate_post] Formato: {content['formato']} · Pilastro: {content['pilastro']}")
    print(f"[generate_post] Titolo: {content['title']}")
    print(f"[generate_post] Caratteri testo: {len(content['caption'])}")
    result = send_to_telegram(content)
    print(f"[generate_post] Inviato su Telegram. Message ID: {result['result']['message_id']}")


if __name__ == "__main__":
    main()
