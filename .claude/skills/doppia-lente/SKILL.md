---
name: doppia-lente
description: >-
  Genera i post LinkedIn di Federico Borrasso, consulente finanziario e patrimoniale,
  nello stile editoriale "La doppia lente" (un consulente che legge il patrimonio anche
  con gli occhi del fisco). Usa questa skill ogni volta che l'utente chiede di scrivere
  un post LinkedIn, un contenuto per il profilo o la pagina, "il post del lunedì" o
  "del giovedì", un carosello finanziario, o un contenuto su successione, previdenza,
  fisco del patrimonio o gestione della liquidità — anche se non nomina esplicitamente
  "La doppia lente". Attivala anche per rivedere o riscrivere un post già fatto in questo
  stile, o per preparare la versione carosello di un testo.
---

# La doppia lente — post LinkedIn di Federico Borrasso

Questa skill serve a scrivere post LinkedIn che suonino autenticamente come Federico:
alti di tono, emotivamente risonanti, mai didascalici. Si parla di ciò che una persona
ha costruito e di cosa rischia di perdere — non di tecnicismi. Il lettore deve sentirsi
capito prima di essere corretto.

## Chi è Federico (e come rappresentarlo)

La professione è **una sola: consulenza finanziaria e patrimoniale**. Federico è anche
dottore commercialista, ma la competenza fiscale non è un secondo mestiere da esibire:
è ciò che rende *diversa* la sua consulenza. Il messaggio non è mai «commercialista e
consulente», è **«un consulente che legge il patrimonio anche con gli occhi del fisco»**.
Questa è "la doppia lente". Non nominare mai la banca mandante.

## A chi parla

Imprenditori e titolari di PMI, professionisti e dirigenti, famiglie in passaggio
generazionale, chi ha ricevuto un'eredità o ha liquidità ferma. Soglia di riferimento:
patrimonio investibile dai 50.000 € in su. Scrivi *a una persona*, non a una platea.

## I 4 pilastri (ruotano)

1. Passaggio generazionale e successione
2. Previdenza, TFR e reddito futuro
3. Fisco del patrimonio
4. Comportamento dell'investitore: liquidità ferma, decisioni prese sull'onda delle notizie

Non ripetere il pilastro usato nel post precedente: la rotazione tiene il profilo vario.
Se l'utente non indica un pilastro, scegline uno coerente col tema richiesto e dillo.

## I formati

Il post del **lunedì** è sempre la serie **«La doppia lente»**: il taglio fisco+patrimonio
su un tema, con la firma finale «La doppia lente · fisco e patrimonio».

Il post del **giovedì** ruota in base alla settimana del mese:

| Settimana | Formato | Cosa fa |
| --- | --- | --- |
| 1ª | Il numero che conta | Un solo dato verificato e perché cambia qualcosa per chi legge |
| 2ª | Si dice / In realtà | Un luogo comune, l'evidenza che lo smonta, la conseguenza pratica |
| 3ª | La lista | «5 errori che vedo in…», punti brevi, chiusura che porta al check-up |
| 4ª | Dalla scrivania | Un caso anonimo: il timore, la scelta, la lezione |
| 5ª | Libero | Il formato che si adatta meglio al tema |

Se l'utente chiede un post senza specificare giorno/formato, scegli il formato più adatto
al tema e dichiaralo in una riga prima del post.

## Anatomia del post

1. **Apertura**: il timore in forma di domanda, massimo 12 parole.
2. **Riconoscimento**: una frase che dà ragione a chi legge, *prima* di contraddirlo.
3. **Evidenza**: la norma o il numero, verificato (vedi regole).
4. **Significato**: cosa cambia concretamente per quella persona.
5. **Chiusura**: una domanda da farsi. Sul lunedì aggiungi «La doppia lente · fisco e patrimonio».
6. **Ultima riga, sempre**: «Contenuto informativo, non costituisce consulenza personalizzata.»

## Registro

Frasi brevi. Righe separate da spazi bianchi (si legge su mobile). Niente emoji, niente
hashtag, niente aperture da listicle tipo «Ecco 5 consigli per…». Lunghezza del post fra
**900 e 1.500 caratteri**. L'eleganza sta nella sottrazione: se una frase non aggiunge
tensione o chiarezza, togliela.

Leggi `references/esempi.md` prima di scrivere: sono tre post approvati e sono il metro del
tono. Non copiarli — assorbine il ritmo e il livello di concretezza.

## Regole non negoziabili (perché proteggono Federico)

Queste non sono burocrazia: un consulente che sbaglia un dato o sembra promettere rendimenti
perde credibilità e si espone a problemi di compliance. Quindi:

- **Nessuna previsione sui mercati, nessuna indicazione su quando comprare o vendere.**
- **Nessun prodotto, rendimento o performance**, né passata né attesa.
- **Casi reali solo anonimi e irriconoscibili** — cambia dettagli finché nessuno possa riconoscersi.
- **Ogni cifra, aliquota, franchigia, soglia o scadenza va verificata con una ricerca web
  prima di usarla**, perché le norme cambiano spesso (es. i tetti di deducibilità). Se hai
  lo strumento di ricerca web, usalo e riporta le fonti separatamente. Se non puoi verificare
  un dato, **scrivi il post senza quel dato** invece di rischiare un numero sbagliato.
- La riga di disclaimer chiude **sempre** il post.

## Output

Per un post semplice, restituisci il **testo pronto da pubblicare** (disclaimer incluso),
preceduto da una riga che dichiara formato e pilastro scelti, e — se hai citato dati — da
un breve elenco delle **fonti** (fuori dal testo del post, servono solo al controllo).

Se l'utente vuole anche la **versione carosello** (slide), oltre al testo produci:
- `title`: l'apertura-domanda, max 12 parole (copertina)
- `kicker`: la frase di riconoscimento sintetizzata (max ~90 caratteri)
- `topic`: etichetta breve del pilastro per l'occhiello (2-3 parole)
- `points`: 3-4 passaggi, ognuno `headline` (max 5 parole) + `body` (max 30 parole, concreto),
  che seguono i beat del post (evidenza → significato → conseguenza)

Se l'utente lavora col sistema automatizzato (job settimanale), usa il formato JSON descritto
in `references/formato-json.md`.
