// pages/api/auth/linkedin-callback.js
// Gestisce il callback OAuth LinkedIn per ottenere l'access token

export default async function handler(req, res) {
  const { code, error, error_description } = req.query;

  if (error) {
    return res.redirect(`/auth/setup?error=${encodeURIComponent(error_description || error)}`);
  }

  if (!code) {
    return res.status(400).json({ error: 'Codice autorizzazione mancante' });
  }

  const clientId = process.env.LINKEDIN_CLIENT_ID;
  const clientSecret = process.env.LINKEDIN_CLIENT_SECRET;
  const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/linkedin-callback`;

  try {
    // Scambia il codice per l'access token
    const tokenRes = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: redirectUri,
        client_id: clientId,
        client_secret: clientSecret
      })
    });

    const tokenData = await tokenRes.json();

    if (tokenData.error || !tokenData.access_token) {
      return res.redirect(`/auth/setup?error=${encodeURIComponent(tokenData.error_description || 'Errore ottenimento token')}`);
    }

    // Ottieni il profile ID dell'utente
    const profileRes = await fetch('https://api.linkedin.com/v2/userinfo', {
      headers: { 'Authorization': `Bearer ${tokenData.access_token}` }
    });
    const profileData = await profileRes.json();

    // Mostra i valori da copiare in Vercel
    const accessToken = tokenData.access_token;
    const personId = profileData.sub; // LinkedIn person ID
    const expiresIn = tokenData.expires_in; // secondi (di solito 5184000 = 60 giorni)

    return res.redirect(
      `/auth/setup?` +
      `li_token=${encodeURIComponent(accessToken)}&` +
      `li_person=${encodeURIComponent(personId)}&` +
      `li_expires=${expiresIn}&` +
      `li_name=${encodeURIComponent(profileData.name || '')}&` +
      `step=li_done`
    );

  } catch (err) {
    console.error('LinkedIn OAuth error:', err);
    return res.redirect(`/auth/setup?error=${encodeURIComponent('Errore di connessione')}`);
  }
}
