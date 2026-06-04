# Setup — LinkedIn Automation

## Come funziona

```
08:30 → GitHub Actions si avvia
         ↓
      Claude genera il post del giorno
         ↓
      Telegram ti manda il post con 3 bottoni
         ↓
   [✅ Pubblica] → pubblica su LinkedIn
   [🔄 Rigenera] → genera un nuovo post (richiede altra approvazione)
   [❌ Salta oggi] → nessuna pubblicazione
         ↓
      Se non rispondi in 30 minuti → post saltato (ricevi notifica)
```

---

## Step 1 — Crea il Bot Telegram

1. Apri Telegram → cerca **@BotFather**
2. Invia `/newbot`
3. Scegli un nome (es. `LinkedIn Post Manager`) e uno username (es. `mio_linkedin_bot`)
4. BotFather ti manda il **token**: `123456:ABCdef...` → **salvalo**

### Trova il tuo Chat ID
1. Cerca il tuo bot su Telegram e clicca **Start**
2. Vai su: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Invia un messaggio al bot, poi ricarica quella URL
4. Trovi `"chat":{"id":123456789}` → il numero è il tuo **Chat ID**

---

## Step 2 — Crea l'app LinkedIn

1. Vai su [developer.linkedin.com](https://developer.linkedin.com) → **Create App**
2. Nome app, associa a una LinkedIn Company Page (puoi crearne una fittizia)
3. Tab **Products** → aggiungi:
   - ✅ **Share on LinkedIn**
   - ✅ **Sign In with LinkedIn using OpenID Connect**
4. Tab **Auth** → aggiungi Redirect URL: `https://tua-app.vercel.app/api/auth/linkedin-callback`
5. Nota **Client ID** e **Client Secret**

### Ottieni il token di accesso
La tua app su Vercel ha già l'OAuth flow su `/auth/setup`:
1. Deploya l'app con `NEXT_PUBLIC_LINKEDIN_CLIENT_ID` e `LINKEDIN_CLIENT_SECRET`
2. Vai su `/auth/setup` → clicca "Connetti LinkedIn"
3. Autorizza → l'app salva il token

In alternativa, per test rapido usa [LinkedIn OAuth 2.0 Playground](https://www.linkedin.com/developers/tools/oauth/token-generator).

Il **LINKEDIN_PERSON_ID** lo trovi nell'URL del tuo profilo LinkedIn oppure chiamando:
```
GET https://api.linkedin.com/v2/userinfo
Authorization: Bearer <ACCESS_TOKEN>
```
Il campo `sub` è il tuo Person ID.

---

## Step 3 — Configura i GitHub Secrets

Vai su GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Valore |
|--------|--------|
| `ANTHROPIC_API_KEY` | Da [console.anthropic.com](https://console.anthropic.com) |
| `TELEGRAM_BOT_TOKEN` | Token del bot (Step 1) |
| `TELEGRAM_CHAT_ID` | Il tuo Chat ID (Step 1) |
| `LINKEDIN_ACCESS_TOKEN` | Token OAuth LinkedIn (Step 2) |
| `LINKEDIN_PERSON_ID` | Il tuo Person ID LinkedIn (Step 2) |

---

## Step 4 — Primo test

1. Vai su **Actions** → **LinkedIn Daily Post** → **Run workflow**
2. Controlla Telegram: ricevi il post in ~30 secondi
3. Premi ✅ **Pubblica** → il post appare su LinkedIn

---

## Personalizzazione

### Cambiare i temi dei post
Modifica l'array `TOPICS` in `automation/generate_post.py`.

### Cambiare orario
Modifica il cron in `.github/workflows/linkedin_daily_post.yml`:
```yaml
- cron: "30 7 * * 1-5"   # 07:30 UTC = 08:30 ora italiana (estate)
```
Per ora solare (inverno) usa `"30 8 * * 1-5"`.

### Pubblicare anche nel weekend
```yaml
- cron: "30 7 * * *"   # tutti i giorni
```

### Cambiare il tono del post
Modifica `SYSTEM_PROMPT` in `automation/generate_post.py`.

---

## Rinnovo token LinkedIn

Il token LinkedIn scade ogni **60 giorni**. Quando scade:
1. Vai su `/auth/setup` della tua app Vercel
2. Rifai il flow OAuth
3. Aggiorna il secret `LINKEDIN_ACCESS_TOKEN` su GitHub
