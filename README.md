# CF Advisor Suite — Deploy su Vercel

App Next.js per consulenti finanziari con posting automatico su LinkedIn e Instagram.

## 🚀 Deploy in 5 passi

### 1. Carica su GitHub
```bash
git init
git add .
git commit -m "CF Advisor Suite v4"
git remote add origin https://github.com/TUO_USERNAME/cf-advisor-suite.git
git push -u origin main
```

### 2. Connetti a Vercel
- Vai su [vercel.com](https://vercel.com) → **Add New Project**
- Importa il repository GitHub appena creato
- Framework: **Next.js** (rilevato automaticamente)
- Clicca **Deploy**

### 3. Aggiungi le variabili d'ambiente su Vercel
Settings → Environment Variables → aggiungi:

| Variabile | Dove ottenerla |
|-----------|----------------|
| `NEXT_PUBLIC_APP_URL` | L'URL del tuo progetto Vercel (es. `https://cf-advisor.vercel.app`) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `NEXT_PUBLIC_LINKEDIN_CLIENT_ID` | LinkedIn Developer App |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn Developer App |

### 4. Rideploya
Dopo aver aggiunto le variabili → **Redeploy** (Deployments → ⋯ → Redeploy)

### 5. Configura i social
Vai su `https://tua-app.vercel.app/auth/setup` e segui la procedura guidata per:
- ✅ Connettere LinkedIn (OAuth automatico)
- ✅ Connettere Instagram (token manuale da Graph API Explorer)

---

## 📋 Credenziali necessarie

### LinkedIn
1. [developer.linkedin.com](https://developer.linkedin.com) → crea app
2. Aggiungi prodotti: **"Share on LinkedIn"** + **"Sign In with LinkedIn using OpenID Connect"**
3. Redirect URL: `https://tua-app.vercel.app/api/auth/linkedin-callback`
4. Scope: `openid profile w_member_social`

### Instagram
1. [developers.facebook.com](https://developers.facebook.com) → crea app **Business**
2. Aggiungi prodotto: **Instagram Graph API**
3. Vai su [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
4. Genera Page Access Token con permessi: `instagram_content_publish`, `pages_read_engagement`
5. Chiama `GET /me/accounts` → trova `instagram_business_account` → copia l'ID
6. Incolla token e ID su `/auth/setup`

---

## 🔄 Rinnovo token

- **LinkedIn**: il token scade ogni **60 giorni** → ripeti il setup OAuth su `/auth/setup`
- **Instagram**: il Page Access Token dura **60-90 giorni** (o può essere long-lived) → rigenera da Graph API Explorer

---

## 📁 Struttura

```
pages/
  index.jsx              # App principale (Dashboard, CRM, Social Hub, Lead Tracker, Prodotti)
  auth/
    setup.jsx            # Pagina guidata configurazione token
  api/
    ai.js                # Proxy Anthropic API (generazione contenuti)
    post-linkedin.js     # POST → pubblica su LinkedIn
    post-instagram.js    # POST → pubblica su Instagram
    auth/
      linkedin-callback.js  # Callback OAuth LinkedIn
```

---

## 💡 Note tecniche

- I dati CRM e Lead sono salvati in **localStorage** (solo browser locale)
- Per persistenza multi-device aggiungere un database (es. Vercel KV o Supabase)
- Instagram richiede obbligatoriamente un'immagine pubblica per ogni post
- Il token LinkedIn ha durata 60 giorni; dopo `/auth/setup` mostra la data di scadenza
