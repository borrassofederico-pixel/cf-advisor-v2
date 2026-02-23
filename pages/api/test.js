export default async function handler(req, res) {
  const apiKey = process.env.GEMINI_API_KEY;
  
  if (!apiKey) {
    return res.status(200).json({ status: 'ERRORE', message: 'GEMINI_API_KEY mancante su Vercel' });
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: 'Rispondi solo: AI Gemini funziona!' }] }]
        })
      }
    );
    const data = await response.json();
    if (response.ok) {
      return res.status(200).json({ 
        status: 'OK ✅', 
        risposta: data.candidates?.[0]?.content?.parts?.[0]?.text || '',
        keyPrefix: apiKey.substring(0, 8) + '...'
      });
    } else {
      return res.status(200).json({ status: 'ERRORE API', dettaglio: data.error?.message, codice: response.status });
    }
  } catch (err) {
    return res.status(200).json({ status: 'ERRORE RETE', dettaglio: err.message });
  }
}
