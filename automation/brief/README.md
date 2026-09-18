# Come si usa questa cartella

## Il giro completo

1. Un job settimanale (domenica sera o lunedì presto) lancia Claude Code con il contenuto di `prompt-post-linkedin.md`.
2. Claude verifica con una ricerca web ogni numero che cita e restituisce **solo** il JSON con i due post.
3. Il tuo script manda i due `testo` su Telegram per l'approvazione.
4. Approvi (o chiedi il rifacimento) e lo script pubblica alle date indicate in `pubblicare_il`.

## Il formato che il tuo script riceve

```json
{
  "settimana": "2026-W39",
  "post": [
    { "id": "lunedi", "pubblicare_il": "2026-09-21T08:00:00+02:00",
      "formato": "La doppia lente", "pilastro": "Passaggio generazionale",
      "testo": "…pronto da pubblicare, disclaimer incluso…",
      "caratteri": 1180, "fonti": ["https://…"], "verifica": "…" }
  ]
}
```

Il campo `testo` è pubblicabile così com'è. `fonti` e `verifica` non vanno pubblicati: servono a te per il controllo.

## I tre controlli prima di approvare

Dieci secondi in tutto, su Telegram:

1. Il numero citato ha una fonte in `fonti` ed è dell'anno in corso.
2. Non c'è nulla che somigli a una previsione di mercato o alla promozione di un prodotto.
3. Il caso, se c'è, non è riconoscibile da nessuno.

Se uno dei tre non passa, rispondi «no» e chiedi il rifacimento: correggere prima costa molto meno che correggere dopo la pubblicazione.

## Cosa NON sta qui

Il check-up patrimoniale e la sua guida vivono sul tuo hosting, non in questa cartella. La strategia, il playbook completo e il business plan restano nel documento condiviso: qui c'è solo ciò che serve a produrre i post.

## Se cambia qualcosa

Se cambi posizionamento, pilastri o regole, modifica `CLAUDE.md` e `prompt-post-linkedin.md`: sono le due fonti di verità del job.
