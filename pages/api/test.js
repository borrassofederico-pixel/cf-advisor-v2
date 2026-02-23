// pages/api/test.js
// Pagina diagnostica — visita /api/test per vedere lo stato

export default async function handler(req, res) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  
  const result = {
    timestamp: new Date().toISOString(),
    apiKeyPresent: !!apiKey,
    apiKeyPrefix: apiKey ? apiKey.substring(0, 12) + '...' : 'MANCANTE',
    tests: {}
  };

  if (!apiKey) {
    return res.status(200).json({
      ...result,
      status: 'ERRORE',
      message: 'ANTHROPIC_API_KEY non trovata nelle variabili ambiente'
    });
  }

  // Test chiamata reale ad Anthropic
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
        max_tokens: 50,
        messages: [{ role: 'user', content: 'Rispondi solo: "AI funziona!"' }],
      }),
    });

    const data = await response.json();
    
    if (response.ok) {
      result.tests.anthropic = 'OK ✅';
      result.tests.risposta = data.content?.[0]?.text || '';
      result.status = 'TUTTO OK';
    } else {
      result.tests.anthropic = `ERRORE ${response.status}`;
      result.tests.dettaglio = data.error?.message || JSON.stringify(data);
      result.status = 'ERRORE API';
    }
  } catch (err) {
    result.tests.anthropic = 'ERRORE CONNESSIONE';
    result.tests.dettaglio = err.message;
    result.status = 'ERRORE RETE';
  }

  return res.status(200).json(result);
}
