export default async function handler(req, res) {
  const apiKey = process.env.GEMINI_API_KEY;
  
  if (!apiKey) {
    return res.status(200).json({ status: 'ERRORE', message: 'GEMINI_API_KEY mancante' });
  }

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: 'Rispondi solo: AI funziona!' }] }]
        })
      }
    );
    const data = await response.json();
    if (response.ok) {
      return res.status(200).json({ 
        status: 'OK ✅', 
        risposta: data.candidates?.[0]?.content?.parts?.[0]?.text || ''
      });
    } else {
      return res.status(200).json({ status: 'ERRORE', dettaglio: data.error?.message });
    }
  } catch (err) {
    return res.status(200).json({ status: 'ERRORE RETE', dettaglio: err.message });
  }
}
