// pages/api/ai.js
// Proxy per chiamate Anthropic Claude — tiene la API key sicura nel backend

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const { system, prompt } = req.body;
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY non configurata' });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        system: system || 'Sei un assistente per consulenti finanziari italiani.',
        messages: [{ role: 'user', content: prompt }],
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({ error: data.error?.message || 'Errore AI' });
    }

    return res.status(200).json({ text: data.content?.[0]?.text || '' });
  } catch (err) {
    return res.status(500).json({ error: 'Errore connessione AI' });
  }
}
