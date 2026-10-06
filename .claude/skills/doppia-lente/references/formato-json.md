# Formato JSON per il sistema automatizzato

Quando il post serve al job settimanale (generazione automatica → approvazione Telegram →
pubblicazione via API), rispondi SOLO con questo JSON, senza testo prima o dopo. Il campo
`testo` dev'essere pubblicabile così com'è, disclaimer incluso. `fonti` e `verifica` non si
pubblicano: servono al controllo prima dell'approvazione.

```json
{
  "settimana": "2026-W40",
  "post": [
    {
      "id": "lunedi",
      "pubblicare_il": "2026-10-05T08:00:00+02:00",
      "formato": "La doppia lente",
      "pilastro": "Passaggio generazionale",
      "testo": "…post completo, disclaimer incluso…",
      "carosello": {
        "title": "apertura-domanda, max 12 parole",
        "kicker": "frase di riconoscimento sintetizzata",
        "topic": "Passaggio generazionale",
        "points": [
          {"headline": "max 5 parole", "body": "max 30 parole, concreto"}
        ]
      },
      "caratteri": 1180,
      "fonti": ["https://…"],
      "verifica": "franchigia e aliquota controllate il 05/10/2026"
    }
  ]
}
```

Un solo post alla volta è perfettamente valido: basta un elemento nell'array `post`.
