"""Test della generazione contenuti (prompt + web search), senza Telegram né pubblicazione.
Stampa il post generato e le fonti, così si verifica la pipeline in CI."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from generate_post import generate_content

topic = os.environ.get("TOPIC_OVERRIDE", "")
content = generate_content(topic)
print("═" * 50)
print("FORMATO:", content["formato"])
print("PILASTRO:", content["pilastro"])
print("TITLE:", content["title"])
print("KICKER:", content["kicker"])
print("TOPIC(occhiello):", content["topic"])
print("CARATTERI TESTO:", len(content["caption"]))
print("PUNTI:", len(content["points"]))
for p in content["points"]:
    print("  -", p.get("headline"), "→", p.get("body")[:60])
print("FONTI:", content["fonti"])
print("VERIFICA:", content["verifica"])
print("═" * 50)
print("\n--- TESTO COMPLETO ---\n")
print(content["caption"])
