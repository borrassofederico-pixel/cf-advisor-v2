// pages/auth/setup.jsx
// Pagina guidata per configurare i token LinkedIn e Meta/Instagram
// Accessibile su /auth/setup

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

const C = {
  bg: '#080b12', bgAlt: '#0f1420', card: '#131926', cardH: '#161d2e',
  border: '#1e2a3a', text: '#e8eaf2', textD: '#8a93a8', muted: '#4a5568',
  gold: '#b8973a', goldL: '#d4af5a', goldD: '#8a6f2a',
  green: '#4caf7d', greenD: '#0d2a1a', red: '#f44', redD: '#2a0808',
  blue: '#4a90d9', blueD: '#0a1828', blueL: '#6aadff',
  linkedin: '#0A66C2', linkedinD: 'rgba(10,102,194,.15)',
  meta: '#1877F2', metaD: 'rgba(24,119,242,.15)',
};

const Step = ({ num, title, done, active, children }) => (
  <div style={{
    background: C.card, border: `1px solid ${active ? C.gold : done ? C.green + '66' : C.border}`,
    borderRadius: 16, padding: 24, marginBottom: 16, transition: 'all .3s'
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: active ? 20 : 0 }}>
      <div style={{
        width: 36, height: 36, borderRadius: '50%',
        background: done ? C.green + '22' : active ? `linear-gradient(135deg,${C.gold},${C.goldL})` : C.bgAlt,
        border: `2px solid ${done ? C.green : active ? C.goldL : C.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontWeight: 800, fontSize: 14, color: done ? C.green : active ? '#000' : C.muted, flexShrink: 0
      }}>
        {done ? '✓' : num}
      </div>
      <div>
        <div style={{ fontWeight: 700, color: done ? C.green : active ? C.goldL : C.textD, fontSize: 15 }}>{title}</div>
        {done && <div style={{ fontSize: 11, color: C.green, marginTop: 1 }}>✓ Configurato</div>}
      </div>
    </div>
    {active && <div>{children}</div>}
  </div>
);

const Inp = ({ value, onChange, placeholder, readOnly, label }) => (
  <div style={{ marginBottom: 10 }}>
    {label && <div style={{ fontSize: 10, color: C.muted, marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>}
    <input
      value={value || ''} onChange={e => onChange && onChange(e.target.value)}
      readOnly={readOnly} placeholder={placeholder}
      style={{
        background: readOnly ? C.bgAlt : C.bgAlt, border: `1px solid ${readOnly ? C.border : C.gold + '66'}`,
        borderRadius: 10, padding: '11px 14px', color: readOnly ? C.textD : C.text,
        fontSize: 13, width: '100%', fontFamily: 'monospace', outline: 'none',
        cursor: readOnly ? 'text' : 'auto'
      }}
    />
  </div>
);

const CopyBox = ({ value, label }) => {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 10, color: C.muted, marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input readOnly value={value || ''} style={{
          flex: 1, background: C.bgAlt, border: `1px solid ${C.green}44`, borderRadius: 10,
          padding: '10px 14px', color: C.green, fontSize: 12, fontFamily: 'monospace'
        }} />
        <button onClick={copy} style={{
          background: copied ? C.greenD : C.bgAlt, border: `1px solid ${copied ? C.green : C.border}`,
          color: copied ? C.green : C.textD, borderRadius: 10, padding: '10px 16px',
          cursor: 'pointer', fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap'
        }}>
          {copied ? '✓ Copiato' : 'Copia'}
        </button>
      </div>
    </div>
  );
};

export default function SetupPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [liToken, setLiToken] = useState('');
  const [liPerson, setLiPerson] = useState('');
  const [liName, setLiName] = useState('');
  const [liExpires, setLiExpires] = useState('');
  const [igToken, setIgToken] = useState('');
  const [igAccountId, setIgAccountId] = useState('');
  const [error, setError] = useState('');
  const [liDone, setLiDone] = useState(false);
  const [igDone, setIgDone] = useState(false);

  useEffect(() => {
    const q = router.query;
    if (q.step === 'li_done' && q.li_token) {
      setLiToken(decodeURIComponent(q.li_token));
      setLiPerson(decodeURIComponent(q.li_person || ''));
      setLiName(decodeURIComponent(q.li_name || ''));
      setLiExpires(q.li_expires || '');
      setStep(2); setLiDone(false); // step 2 = mostra valori da copiare
    }
    if (q.error) setError(decodeURIComponent(q.error));
  }, [router.query]);

  const appUrl = typeof window !== 'undefined' ? window.location.origin : '';

  const liAuthUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
    `response_type=code&` +
    `client_id=${process.env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID || 'INSERISCI_CLIENT_ID'}&` +
    `redirect_uri=${encodeURIComponent(appUrl + '/api/auth/linkedin-callback')}&` +
    `scope=openid%20profile%20w_member_social`;

  const expiryDate = liExpires
    ? new Date(Date.now() + parseInt(liExpires) * 1000).toLocaleDateString('it-IT')
    : '';

  return (
    <div style={{
      minHeight: '100vh', background: C.bg, color: C.text,
      fontFamily: "'Outfit', sans-serif", padding: '40px 20px'
    }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Outfit:wght@400;600;700;800&display=swap'); * { box-sizing: border-box; }`}</style>

      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⚙️</div>
          <h1 style={{ fontFamily: "'Playfair Display',serif", fontSize: 34, fontWeight: 900, color: C.goldL, margin: 0 }}>
            Configurazione Social
          </h1>
          <p style={{ color: C.textD, marginTop: 10, fontSize: 15 }}>
            Collega LinkedIn e Instagram per il posting automatico
          </p>
          {error && (
            <div style={{ background: C.redD, border: `1px solid ${C.red}44`, borderRadius: 10, padding: 12, marginTop: 16, color: C.red, fontSize: 13 }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Avviso pre-requisiti */}
        <div style={{ background: C.blueD, border: `1px solid ${C.blueL}33`, borderRadius: 14, padding: 20, marginBottom: 28 }}>
          <div style={{ fontWeight: 700, color: C.blueL, marginBottom: 10, fontSize: 14 }}>📋 Cosa ti serve prima di iniziare</div>
          <div style={{ color: C.textD, fontSize: 13, lineHeight: 1.8 }}>
            <strong style={{ color: C.text }}>LinkedIn:</strong> Un'app su <a href="https://developer.linkedin.com/" target="_blank" style={{ color: C.blueL }}>developer.linkedin.com</a> con scope <code style={{ color: C.goldL }}>w_member_social</code><br />
            <strong style={{ color: C.text }}>Instagram:</strong> Account Business + Pagina Facebook collegata + App su <a href="https://developers.facebook.com/" target="_blank" style={{ color: C.meta }}>developers.facebook.com</a>
          </div>
        </div>

        {/* STEP 1: LinkedIn OAuth */}
        <Step num={1} title="Connetti LinkedIn" active={step === 1} done={liDone}>
          <div style={{ color: C.textD, fontSize: 13, lineHeight: 1.7, marginBottom: 20 }}>
            Clicca il bottone per autorizzare l'app. Verrai reindirizzato a LinkedIn e poi tornato qui con il token già pronto.
          </div>
          <div style={{
            background: C.bgAlt, border: `1px solid ${C.border}`, borderRadius: 12, padding: 16, marginBottom: 20, fontSize: 12, color: C.muted
          }}>
            <strong style={{ color: C.textD }}>Redirect URI da inserire nella tua LinkedIn App:</strong><br />
            <code style={{ color: C.goldL }}>{appUrl}/api/auth/linkedin-callback</code>
          </div>
          <a href={liAuthUrl} style={{
            display: 'inline-flex', alignItems: 'center', gap: 10,
            background: C.linkedin, color: '#fff', borderRadius: 12, padding: '14px 28px',
            fontWeight: 700, fontSize: 14, textDecoration: 'none', cursor: 'pointer'
          }}>
            <span style={{ fontSize: 18 }}>in</span> Autorizza su LinkedIn
          </a>
        </Step>

        {/* STEP 2: Copia token LinkedIn in Vercel */}
        {(step === 2 || liDone) && liToken && (
          <Step num={2} title="Salva token LinkedIn su Vercel" active={step === 2} done={liDone}>
            <div style={{
              background: C.greenD, border: `1px solid ${C.green}44`, borderRadius: 12, padding: 14, marginBottom: 20
            }}>
              <div style={{ color: C.green, fontWeight: 700, marginBottom: 4 }}>✅ Connesso come: {liName}</div>
              <div style={{ color: C.textD, fontSize: 12 }}>Token valido fino al: {expiryDate} (60 giorni) · Dopo dovrai ripetere questo step.</div>
            </div>
            <div style={{ color: C.textD, fontSize: 13, marginBottom: 16 }}>
              Vai su <strong style={{ color: C.text }}>Vercel → Il tuo progetto → Settings → Environment Variables</strong> e aggiungi:
            </div>
            <CopyBox label="LINKEDIN_ACCESS_TOKEN" value={liToken} />
            <CopyBox label="LINKEDIN_PERSON_ID" value={liPerson} />
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button onClick={() => { setLiDone(true); setStep(3); }} style={{
                background: `linear-gradient(135deg,${C.gold},${C.goldL})`, color: '#000',
                border: 'none', borderRadius: 10, padding: '12px 28px', fontWeight: 700, fontSize: 14, cursor: 'pointer'
              }}>
                ✓ Salvato su Vercel → Avanti
              </button>
            </div>
          </Step>
        )}

        {/* STEP 3: Meta / Instagram */}
        <Step num={3} title="Connetti Instagram (Meta)" active={step === 3} done={igDone}>
          <div style={{ color: C.textD, fontSize: 13, lineHeight: 1.7, marginBottom: 16 }}>
            Per Instagram non c'è un OAuth automatico in questa versione (Meta richiede review dell'app). Inserisci manualmente il <strong style={{ color: C.text }}>Page Access Token</strong> e l'<strong style={{ color: C.text }}>Instagram Account ID</strong> che trovi su Graph API Explorer.
          </div>

          <div style={{
            background: C.bgAlt, border: `1px solid ${C.border}`, borderRadius: 12, padding: 16, marginBottom: 20, fontSize: 12
          }}>
            <strong style={{ color: C.textD }}>Come ottenere il token:</strong>
            <ol style={{ color: C.muted, lineHeight: 2.1, paddingLeft: 16, marginTop: 8 }}>
              <li>Vai su <a href="https://developers.facebook.com/tools/explorer/" target="_blank" style={{ color: C.meta }}>Graph API Explorer</a></li>
              <li>Seleziona la tua App → genera un <em>Page Access Token</em></li>
              <li>Aggiungi permission: <code style={{ color: C.goldL }}>instagram_content_publish</code>, <code style={{ color: C.goldL }}>pages_read_engagement</code></li>
              <li>Chiama: <code style={{ color: C.goldL }}>GET /me/accounts</code> → trova la tua pagina</li>
              <li>Da lì ottieni anche l'<strong>instagram_business_account id</strong></li>
            </ol>
          </div>

          <Inp label="INSTAGRAM_ACCESS_TOKEN (Page Access Token)" value={igToken} onChange={setIgToken} placeholder="EAAxxxxxx..." />
          <Inp label="INSTAGRAM_ACCOUNT_ID" value={igAccountId} onChange={setIgAccountId} placeholder="17841xxxxxxxxxx" />

          {igToken && igAccountId && (
            <div style={{ marginTop: 16 }}>
              <div style={{ color: C.textD, fontSize: 13, marginBottom: 12 }}>Aggiungi queste variabili su Vercel:</div>
              <CopyBox label="INSTAGRAM_ACCESS_TOKEN" value={igToken} />
              <CopyBox label="INSTAGRAM_ACCOUNT_ID" value={igAccountId} />
            </div>
          )}

          <button onClick={() => { setIgDone(true); setStep(4); }} style={{
            background: igToken && igAccountId ? `linear-gradient(135deg,${C.gold},${C.goldL})` : C.bgAlt,
            color: igToken && igAccountId ? '#000' : C.muted,
            border: `1px solid ${igToken && igAccountId ? 'transparent' : C.border}`,
            borderRadius: 10, padding: '12px 28px', fontWeight: 700, fontSize: 14,
            cursor: igToken && igAccountId ? 'pointer' : 'default', marginTop: 16
          }}>
            {igToken && igAccountId ? '✓ Salvato su Vercel → Avanti' : 'Compila i campi per continuare'}
          </button>
        </Step>

        {/* STEP 4: Done! */}
        {step === 4 && (
          <div style={{
            background: C.greenD, border: `1px solid ${C.green}55`, borderRadius: 16, padding: 32, textAlign: 'center'
          }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>🎉</div>
            <h2 style={{ fontFamily: "'Playfair Display',serif", color: C.green, fontSize: 26, margin: '0 0 10px' }}>
              Setup completato!
            </h2>
            <p style={{ color: C.textD, marginBottom: 24 }}>
              Fai il redeploy su Vercel dopo aver aggiunto le variabili d'ambiente, poi torna all'app.
            </p>
            <a href="/" style={{
              display: 'inline-block', background: `linear-gradient(135deg,${C.gold},${C.goldL})`,
              color: '#000', borderRadius: 12, padding: '14px 32px', fontWeight: 800, textDecoration: 'none', fontSize: 15
            }}>
              → Vai all'App
            </a>
          </div>
        )}

        {/* Skip Instagram */}
        {step === 3 && (
          <div style={{ textAlign: 'center', marginTop: 12 }}>
            <button onClick={() => setStep(4)} style={{
              background: 'transparent', border: 'none', color: C.muted,
              fontSize: 12, cursor: 'pointer', textDecoration: 'underline'
            }}>
              Salta Instagram per ora
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
