# Setup Firebase — Guida passo passo

## Cosa ti serve
- Un account Google (Gmail)
- 20 minuti

---

## PASSO 1 — Crea il progetto Firebase

1. Vai su **https://console.firebase.google.com**
2. Clicca **"Aggiungi progetto"**
3. Nome progetto: es. `presenze-azienda`
4. Disabilita Google Analytics (non serve)
5. Clicca **"Crea progetto"**

---

## PASSO 2 — Attiva Authentication

1. Nel menu laterale: **Build → Authentication**
2. Clicca **"Inizia"**
3. Scheda **"Sign-in method"** → abilita **Email/Password**

---

## PASSO 3 — Crea il database Firestore

1. Nel menu laterale: **Build → Firestore Database**
2. Clicca **"Crea database"**
3. Scegli **"Inizia in modalità produzione"**
4. Scegli la regione **europe-west1** (Belgio — la più vicina all'Italia)
5. Clicca **"Avanti"** poi **"Fine"**

### Regole Firestore (sicurezza)
Vai in **Firestore → Regole** e incolla questo:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Utenti: admin vede tutto, dipendente solo sé stesso
    match /users/{userId} {
      allow read, write: if request.auth != null &&
        (request.auth.uid == userId ||
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
    }

    // Richieste: admin vede tutto, dipendente solo le sue
    match /requests/{reqId} {
      allow read: if request.auth != null &&
        (resource.data.userId == request.auth.uid ||
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null &&
        (resource.data.userId == request.auth.uid ||
         get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
    }

    // Audit log: solo admin in scrittura, solo admin in lettura
    match /auditLog/{logId} {
      allow read: if request.auth != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      allow create: if request.auth != null;
    }
  }
}
```

Clicca **"Pubblica"**.

---

## PASSO 4 — Ottieni la configurazione Firebase

1. Clicca l'icona **⚙️ (Impostazioni progetto)** → **Impostazioni generali**
2. Scorri fino a **"Le tue app"**
3. Clicca l'icona **</>** (Web app)
4. Nome: `presenze-web`, clicca **"Registra app"**
5. Vedrai un blocco di codice con `firebaseConfig`

Copia i valori e aprì il file `index.html`.
Trova questa sezione in alto:

```js
const firebaseConfig = {
  apiKey: "SOSTITUISCI_CON_TUA_API_KEY",
  authDomain: "SOSTITUISCI.firebaseapp.com",
  projectId: "SOSTITUISCI_CON_TUO_PROJECT_ID",
  storageBucket: "SOSTITUISCI.appspot.com",
  messagingSenderId: "SOSTITUISCI",
  appId: "SOSTITUISCI"
};
```

Sostituisci ogni valore con quelli di Firebase.

---

## PASSO 5 — Crea l'account Admin

1. **Firebase → Authentication → Utenti → Aggiungi utente**
2. Email: la tua email da admin
3. Password: scegli una password sicura
4. Copia l'**UID** che compare nella lista (es. `abc123xyz...`)

Poi vai in **Firestore → Dati → Aggiungi documento**:
- Collezione: `users`
- ID documento: incolla l'UID copiato
- Campi:
  - `name` (string): `Admin`
  - `email` (string): la tua email
  - `role` (string): `admin`
  - `ferieGiorni` (number): `0`
  - `permessiOre` (number): `0`

---

## PASSO 6 — Pubblica online (hosting gratuito)

### Opzione A — Firebase Hosting (consigliata)
1. Installa Node.js da https://nodejs.org
2. Apri il terminale nella cartella del progetto
3. Esegui:
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Scegli il tuo progetto
# Public directory: . (punto)
# Single-page app: NO
firebase deploy
```
4. Il sito sarà online su `https://NOME-PROGETTO.web.app`

### Opzione B — Netlify Drop (ancora più semplice)
1. Vai su **https://app.netlify.com/drop**
2. Trascina la cartella `presenze-app` nella pagina
3. Il sito è online in 30 secondi con URL gratuito

---

## PASSO 7 — Aggiungi dipendenti

Per ogni dipendente:
1. **Firebase → Authentication → Aggiungi utente** (email + password)
2. Copia l'UID dalla lista
3. Accedi al pannello admin → scheda **Dipendenti** → inserisci il dipendente con quell'UID

---

## Importa dati storici (Excel/CSV)

1. Scarica il template CSV dal pannello admin
2. Aprilo con Excel
3. Compila le righe (rispetta il formato delle colonne)
4. Salva come CSV con separatore `;`
5. Caricalo dal pannello admin → sezione **Importa da file**

---

## Costi

Piano **Spark (gratuito)** di Firebase:
- Autenticazione: illimitata
- Firestore: 1GB storage, 50.000 letture/giorno, 20.000 scritture/giorno
- Hosting: 10GB/mese di banda

Per un'azienda fino a 50 dipendenti: **costo zero**.
