// pages/api/post-linkedin.js
// Posts text content to LinkedIn using the UGC Posts API

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { text } = req.body;

  if (!text || text.trim().length === 0) {
    return res.status(400).json({ error: 'Il testo del post non può essere vuoto' });
  }

  const accessToken = process.env.LINKEDIN_ACCESS_TOKEN;
  const personId = process.env.LINKEDIN_PERSON_ID;

  if (!accessToken || !personId) {
    return res.status(500).json({
      error: 'LinkedIn non configurato',
      setup: 'Vai su /auth/setup per configurare le credenziali LinkedIn'
    });
  }

  try {
    const response = await fetch('https://api.linkedin.com/v2/ugcPosts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202304'
      },
      body: JSON.stringify({
        author: `urn:li:person:${personId}`,
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: {
              text: text
            },
            shareMediaCategory: 'NONE'
          }
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
      })
    });

    const data = await response.json();

    if (!response.ok) {
      // Token scaduto → restituiamo link per refresh
      if (response.status === 401) {
        return res.status(401).json({
          error: 'Token LinkedIn scaduto',
          setup: 'Vai su /auth/setup per rinnovare il token'
        });
      }
      return res.status(response.status).json({
        error: data.message || 'Errore LinkedIn API',
        details: data
      });
    }

    return res.status(200).json({
      success: true,
      postId: data.id,
      message: 'Post pubblicato su LinkedIn con successo! 🎉'
    });

  } catch (err) {
    console.error('LinkedIn post error:', err);
    return res.status(500).json({ error: 'Errore di connessione a LinkedIn' });
  }
}
