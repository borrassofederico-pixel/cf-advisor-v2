"""
Test end-to-end della pubblicazione sulla PAGINA LinkedIn (organization).
Eseguito da .github/workflows/test_page.yml (trigger su push).

Genera un carosello su un tema fisso e lo pubblica sulla pagina usando
LINKEDIN_ORG_ACCESS_TOKEN + LINKEDIN_ORG_ID. Nessuna interazione Telegram.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from generate_post import generate_content
from generate_carousel import save_slide_jpegs
from telegram_bot import _upload_and_publish

TOPIC = os.environ.get("TEST_TOPIC", "deducibilità delle somme versate nel fondo pensione")


def main():
    org_token = os.environ.get("LINKEDIN_ORG_ACCESS_TOKEN", "").strip()
    org_id = os.environ.get("LINKEDIN_ORG_ID", "").strip()

    if not org_token:
        print("::error::LINKEDIN_ORG_ACCESS_TOKEN mancante — aggiungi il secret su GitHub")
        sys.exit(1)
    if not org_id:
        print("::error::LINKEDIN_ORG_ID mancante")
        sys.exit(1)

    org_urn = f"urn:li:organization:{org_id}"
    print(f"[test_page] Pagina target: {org_urn}")
    print(f"[test_page] Tema: {TOPIC}")

    content = generate_content(TOPIC)
    content["topic"] = TOPIC
    content["author"] = "Federico Borrasso"
    print(f"[test_page] Contenuto generato: {content['title']}")

    slide_paths = save_slide_jpegs(content, out_dir="automation/publish_slides", size=1080)
    print(f"[test_page] {len(slide_paths)} slide generate")

    try:
        post_id = _upload_and_publish(slide_paths, content["caption"], org_token, org_urn)
        print(f"::notice::Post pubblicato sulla PAGINA! ID: {post_id}")
    except Exception as e:
        print(f"::error::Pubblicazione pagina fallita: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
