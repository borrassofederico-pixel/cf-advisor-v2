// pages/api/post-instagram.js
// Posts to Instagram Business Account via Meta Graph API
// NOTA: Instagram richiede obbligatoriamente un'immagine.
// Questo endpoint accetta: { caption, imageUrl }
// Se non fornisci imageUrl, usa un'immagine default branded.

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { caption, imageUrl } = req.body;

  if (!caption || caption.trim().length === 0) {
    return res.status(400).json({ error: 'La caption non può essere vuota' });
  }

  const accessToken = process.env.INSTAGRAM_ACCESS_TOKEN;
  const igAccountId = process.env.INSTAGRAM_ACCOUNT_ID;

  if (!accessToken || !igAccountId) {
    return res.status(500).json({
      error: 'Instagram non configurato',
      setup: 'Vai su /auth/setup per configurare le credenziali Meta/Instagram'
    });
  }

  // Immagine default branded se non fornita
  // In produzione: genera dinamicamente con testo sovrapposto
  const finalImageUrl = imageUrl || process.env.INSTAGRAM_DEFAULT_IMAGE_URL;

  if (!finalImageUrl) {
    return res.status(400).json({
      error: 'Instagram richiede un\'immagine',
      message: 'Fornisci una imageUrl o imposta INSTAGRAM_DEFAULT_IMAGE_URL nelle env vars'
    });
  }

  try {
    const baseUrl = `https://graph.facebook.com/v18.0`;

    // STEP 1: Crea container media
    const containerRes = await fetch(
      `${baseUrl}/${igAccountId}/media`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_url: finalImageUrl,
          caption: caption,
          access_token: accessToken
        })
      }
    );

    const containerData = await containerRes.json();

    if (!containerRes.ok || containerData.error) {
      if (containerRes.status === 401 || containerData.error?.code === 190) {
        return res.status(401).json({
          error: 'Token Instagram scaduto',
          setup: 'Vai su /auth/setup per rinnovare il token'
        });
      }
      return res.status(containerRes.status).json({
        error: containerData.error?.message || 'Errore creazione media Instagram',
        details: containerData
      });
    }

    const containerId = containerData.id;

    // STEP 2: Pubblica container
    const publishRes = await fetch(
      `${baseUrl}/${igAccountId}/media_publish`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          creation_id: containerId,
          access_token: accessToken
        })
      }
    );

    const publishData = await publishRes.json();

    if (!publishRes.ok || publishData.error) {
      return res.status(publishRes.status).json({
        error: publishData.error?.message || 'Errore pubblicazione Instagram',
        details: publishData
      });
    }

    return res.status(200).json({
      success: true,
      postId: publishData.id,
      message: 'Post pubblicato su Instagram con successo! 🎉'
    });

  } catch (err) {
    console.error('Instagram post error:', err);
    return res.status(500).json({ error: 'Errore di connessione a Instagram/Meta' });
  }
}
