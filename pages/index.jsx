// pages/index.jsx — CF Advisor Suite v4 — Full Next.js App
// Social posting via API reali (LinkedIn + Instagram)

import { useState, useEffect } from 'react';

const C = {
  bg:'#080b12',bgAlt:'#0f1420',card:'#131926',cardH:'#161d2e',surface:'#1a2234',
  border:'#1e2a3a',text:'#e8eaf2',textD:'#8a93a8',muted:'#4a5568',
  gold:'#b8973a',goldL:'#d4af5a',goldD:'#8a6f2a',
  green:'#4caf7d',greenD:'#0d2a1a',red:'#f66',redD:'#2a0808',
  blue:'#4a90d9',blueD:'#0a1828',blueL:'#6aadff',
  amber:'#f59e0b',
  linkedin:'#0A66C2',linkedinD:'rgba(10,102,194,.18)',
  meta:'#1877F2',metaD:'rgba(24,119,242,.15)',
  instagram:'#E1306C',instagramD:'rgba(225,48,108,.12)',
  purple:'#9b59b6',purpleD:'rgba(155,89,182,.15)',
};

const fmt = n => Number(n).toLocaleString('it-IT');
const todayStr = () => new Date().toLocaleDateString('it-IT');

// ─── PRODUCTS ────────────────────────────────────────────────────────────────
const PRODUCTS = [
  {id:1,name:'PAC Azionario Globale',cat:'Investimento',risk:'Alto',fee:'1.2%',min:50,desc:'Piano accumulo su fondi azionari globali. Orizzonte 10+ anni.'},
  {id:2,name:'Portafoglio Bilanciato',cat:'Investimento',risk:'Medio',fee:'1.0%',min:30000,desc:'Mix 60/40 obbligazioni-azioni per profilo moderato.'},
  {id:3,name:'Polizza Vita Multiramo',cat:'Assicurazione',risk:'Basso',fee:'2.5%',min:10000,desc:'Protezione patrimonio + rendimento. Vantaggi fiscali.'},
  {id:4,name:'Conto Deposito Premium',cat:'Risparmio',risk:'Basso',fee:'0.3%',min:5000,desc:'Tasso 3.5% lordo annuo. Vincolo 12 mesi.'},
  {id:5,name:'ETF ESG Portfolio',cat:'Investimento',risk:'Medio-Alto',fee:'0.8%',min:10000,desc:'Portafoglio sostenibile con ETF a basso costo.'},
  {id:6,name:'Fondo Pensione Aperto',cat:'Previdenza',risk:'Variabile',fee:'1.8%',min:100,desc:'Deducibilità fiscale fino a €5.164/anno.'},
  {id:7,name:'100% Vitariv — Ramo I',cat:'Assicurazione',risk:'Basso',fee:'da 0,95%',min:5000,desc:'Polizza rivalutabile Allianz. Gestione separata VITARIV (obbligazioni+Titoli Stato). Garanzia capitale al 5°-10°-15° anno e in caso di decesso. Premio unico €5.000-500.000. Caricamento 2%. Orizzonte 10+ anni. Esenzione imposta successione. Riscatto dopo 1 anno: penale 3%, 2%, 1%, poi €50 fisso. Nessun costo riscatto al 5°/10°/15° anniversario. Età assicurabile 18-85 anni.'},
  {id:8,name:'Challenge PRO — Unit Linked',cat:'Assicurazione',risk:'Variabile',fee:'da 0,6%',min:10000,desc:'Polizza Unit Linked Allianz Darta Saving (Ramo III). CAPITAL (min €10k), PLAN (ricorrente €1.200/anno) o combinata. Premi aggiuntivi da €2.500. 50+ fondi interni: azionari, bilanciati, obbligazionari, monetari. Opzioni: Plan for You, Easy Switch, Easy Rebalancing, Profit Lock-in (consolida al 5-10%), Start & Go. Smart Protection automatica under 60. Primo switch gratuito/anno poi €25.'},
];

// ─── AI CALL ──────────────────────────────────────────────────────────────────
async function ai(system, prompt) {
  try {
    const r = await fetch('/api/ai', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({system,prompt}) });
    const d = await r.json();
    return d.text || 'Nessuna risposta AI.';
  } catch { return 'Errore AI. Riprova.'; }
}

// ─── PRIMITIVES ───────────────────────────────────────────────────────────────
function Btn({children,onClick,variant='primary',disabled,full,sm,style={}}) {
  const v={
    primary:{background:`linear-gradient(135deg,${C.gold},${C.goldL})`,color:'#07090f'},
    ghost:{background:'transparent',color:C.textD,border:`1px solid ${C.border}`},
    danger:{background:C.redD,color:C.red,border:`1px solid ${C.red}44`},
    accent:{background:C.blueD,color:C.blueL,border:`1px solid ${C.blueL}44`},
    linkedin:{background:C.linkedinD,color:C.linkedin,border:`1px solid rgba(10,102,194,.38)`},
    instagram:{background:C.instagramD,color:C.instagram,border:`1px solid rgba(225,48,108,.32)`},
    green:{background:C.greenD,color:C.green,border:`1px solid ${C.green}44`},
    success:{background:'rgba(76,175,125,.2)',color:C.green,border:`1px solid ${C.green}66`},
  };
  return <button onClick={onClick} disabled={disabled} style={{
    border:'none',cursor:disabled?'not-allowed':'pointer',borderRadius:10,
    fontFamily:"'Outfit',sans-serif",fontWeight:600,transition:'all .18s',
    opacity:disabled?.5:1,display:'inline-flex',alignItems:'center',gap:7,
    fontSize:sm?12:13,padding:sm?'7px 13px':'10px 18px',
    width:full?'100%':undefined,justifyContent:full?'center':undefined,
    whiteSpace:'nowrap',...v[variant],...style
  }}>{children}</button>;
}
function Card({children,style={},onClick,hover}) {
  const [h,setH]=useState(false);
  return <div onClick={onClick} onMouseEnter={()=>hover&&setH(true)} onMouseLeave={()=>hover&&setH(false)}
    style={{background:h?C.cardH:C.card,border:`1px solid ${C.border}`,borderRadius:16,padding:20,cursor:onClick?'pointer':'default',transition:'all .2s',...style}}>
    {children}
  </div>;
}
function Input({value,onChange,placeholder,type='text',multiline,rows=3,style={}}) {
  const base={background:C.bgAlt,border:`1px solid ${C.border}`,borderRadius:10,padding:'10px 14px',color:C.text,fontSize:13,width:'100%',resize:multiline?'vertical':'none',...style};
  return multiline
    ?<textarea value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder} rows={rows} style={base}/>
    :<input type={type} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder} style={base}/>;
}
function Sel({value,onChange,options,style={}}) {
  return <select value={value} onChange={e=>onChange(e.target.value)}
    style={{background:C.bgAlt,border:`1px solid ${C.border}`,borderRadius:10,padding:'10px 14px',color:C.text,fontSize:13,width:'100%',...style}}>
    {options.map(o=>typeof o==='string'?<option key={o}>{o}</option>:<option key={o.v} value={o.v}>{o.l}</option>)}
  </select>;
}
function Badge({label,color=C.gold,small}) {
  return <span style={{background:color+'22',color,border:`1px solid ${color}44`,borderRadius:6,padding:small?'2px 6px':'3px 9px',fontSize:small?10:11,fontWeight:600,letterSpacing:.4,whiteSpace:'nowrap'}}>{label}</span>;
}
function Loading() {
  return <div style={{display:'flex',alignItems:'center',gap:6,color:C.textD,fontSize:13}}>
    <span>●</span><span>●</span><span>●</span>
    <span style={{marginLeft:4}}>Generazione AI…</span>
  </div>;
}
function ST({children,sub}) {
  return <div style={{marginBottom:22}}>
    <h2 style={{fontFamily:"'Playfair Display',serif",fontSize:26,fontWeight:900,color:C.goldL,lineHeight:1.1}}>{children}</h2>
    {sub&&<div style={{fontSize:12,color:C.muted,marginTop:4}}>{sub}</div>}
  </div>;
}

// ─── SOCIAL HUB (con posting reale) ──────────────────────────────────────────
function SocialHub() {
  const [platform, setPlatform] = useState('linkedin');
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('Professionale');
  const [generated, setGenerated] = useState('');
  const [genLoading, setGenLoading] = useState(false);
  const [postLoading, setPostLoading] = useState(false);
  const [postResult, setPostResult] = useState(null); // {success, message, error}
  const [igImageUrl, setIgImageUrl] = useState('');
  const [showIgImageField, setShowIgImageField] = useState(false);

  const TOPICS = ['Perché pianificare la pensione a 30 anni','Inflazione e patrimonio: cosa fare','ETF vs fondi attivi','I 5 errori del risparmiatore','PAC: come iniziare con poco','Successione: pianifica in anticipo','Gestione separata Ramo I: cos\'è','Polizza vita: protezione o investimento?'];
  const TONES = ['Professionale','Autorevole','Educativo','Storytelling','Dati e numeri'];

  const generate = async () => {
    if (!topic.trim()) return;
    setGenLoading(true); setGenerated(''); setPostResult(null);
    const sysMap = {
      linkedin:'Sei un CF italiano esperto. Scrivi post LinkedIn professionali, max 1300 caratteri, con hook potente, valore concreto, CTA. Niente promesse di rendimento. Conforme MiFID II.',
      instagram:'Sei un CF italiano su Instagram. Scrivi caption coinvolgenti, max 400 caratteri, tono più personale, emoji pertinenti, hashtag rilevanti (10-15). Conforme MiFID II.'
    };
    const t = await ai(sysMap[platform], `Argomento: ${topic}. Tono: ${tone}. Scrivi il post completo pronto da pubblicare.`);
    setGenerated(t);
    setGenLoading(false);
  };

  const publishLinkedIn = async () => {
    if (!generated.trim()) return;
    setPostLoading(true); setPostResult(null);
    try {
      const res = await fetch('/api/post-linkedin', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ text: generated })
      });
      const data = await res.json();
      if (data.success) {
        setPostResult({ success: true, message: data.message });
      } else if (res.status === 401) {
        setPostResult({ success: false, error: data.error, setupLink: true });
      } else if (res.status === 500 && data.setup) {
        setPostResult({ success: false, error: data.error, setupLink: true });
      } else {
        setPostResult({ success: false, error: data.error || 'Errore sconosciuto' });
      }
    } catch { setPostResult({ success: false, error: 'Errore di rete' }); }
    setPostLoading(false);
  };

  const publishInstagram = async () => {
    if (!generated.trim()) return;
    if (!igImageUrl.trim()) { setShowIgImageField(true); return; }
    setPostLoading(true); setPostResult(null);
    try {
      const res = await fetch('/api/post-instagram', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ caption: generated, imageUrl: igImageUrl })
      });
      const data = await res.json();
      if (data.success) {
        setPostResult({ success: true, message: data.message });
      } else if (res.status === 401 || data.setup) {
        setPostResult({ success: false, error: data.error, setupLink: true });
      } else {
        setPostResult({ success: false, error: data.error || 'Errore sconosciuto' });
      }
    } catch { setPostResult({ success: false, error: 'Errore di rete' }); }
    setPostLoading(false);
  };

  const handlePublish = () => {
    if (platform === 'linkedin') publishLinkedIn();
    else publishInstagram();
  };

  return (
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:20}}>
      {/* Left: generazione */}
      <Card>
        <ST sub="Genera e pubblica direttamente">Social Hub</ST>

        {/* Platform */}
        <div style={{display:'flex',gap:8,marginBottom:20}}>
          {[['linkedin','in','LinkedIn',C.linkedin],['instagram','📷','Instagram',C.instagram]].map(([p,icon,label,col])=>(
            <button key={p} onClick={()=>{setPlatform(p);setGenerated('');setPostResult(null);setShowIgImageField(false);}} style={{
              flex:1,padding:'12px 16px',borderRadius:12,cursor:'pointer',transition:'all .2s',
              background:platform===p?`${col}22`:'transparent',
              border:`2px solid ${platform===p?col:C.border}`,
              color:platform===p?col:C.muted,fontWeight:700,fontSize:13,
              display:'flex',alignItems:'center',gap:6,justifyContent:'center'
            }}>
              <span style={{fontSize:platform===p?18:16}}>{icon}</span> {label}
              {platform===p&&<span style={{fontSize:9,background:col+'33',padding:'2px 6px',borderRadius:4,marginLeft:4}}>ATTIVO</span>}
            </button>
          ))}
        </div>

        {/* Topic */}
        <div style={{marginBottom:14}}>
          <div style={{fontSize:10,color:C.muted,marginBottom:5,textTransform:'uppercase',letterSpacing:1}}>Argomento</div>
          <Input value={topic} onChange={setTopic} placeholder="Es: Perché investire in ETF" multiline rows={2}/>
          <div style={{display:'flex',gap:6,flexWrap:'wrap',marginTop:8}}>
            {TOPICS.slice(0,4).map(t=>(
              <button key={t} onClick={()=>setTopic(t)} style={{
                background:C.bgAlt,border:`1px solid ${C.border}`,borderRadius:8,padding:'4px 10px',
                color:C.textD,fontSize:10,cursor:'pointer'
              }}>{t}</button>
            ))}
          </div>
        </div>

        {/* Tone */}
        <div style={{marginBottom:20}}>
          <div style={{fontSize:10,color:C.muted,marginBottom:5,textTransform:'uppercase',letterSpacing:1}}>Tono</div>
          <div style={{display:'flex',gap:6,flexWrap:'wrap'}}>
            {TONES.map(t=>(
              <button key={t} onClick={()=>setTone(t)} style={{
                background:tone===t?C.gold+'22':'transparent',border:`1px solid ${tone===t?C.gold:C.border}`,
                borderRadius:8,padding:'5px 12px',color:tone===t?C.goldL:C.muted,fontSize:11,cursor:'pointer',fontWeight:tone===t?700:400
              }}>{t}</button>
            ))}
          </div>
        </div>

        <Btn full onClick={generate} disabled={!topic.trim()||genLoading} variant="primary">
          {genLoading?'Generazione…':'◈ Genera Contenuto AI'}
        </Btn>
        {genLoading&&<div style={{marginTop:12}}><Loading/></div>}
      </Card>

      {/* Right: preview e pubblicazione */}
      <Card>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
          <div style={{fontWeight:700,color:C.goldL,fontSize:15}}>Preview & Pubblica</div>
          {generated&&(
            <button onClick={()=>navigator.clipboard.writeText(generated)} style={{
              background:'transparent',border:`1px solid ${C.border}`,borderRadius:8,
              padding:'4px 10px',color:C.muted,fontSize:11,cursor:'pointer'
            }}>📋 Copia</button>
          )}
        </div>

        {!generated&&!genLoading&&(
          <div style={{textAlign:'center',padding:'60px 20px',color:C.muted,fontSize:13}}>
            <div style={{fontSize:40,marginBottom:12}}>✍️</div>
            Scegli un argomento e genera il contenuto
          </div>
        )}

        {generated&&(
          <div style={{
            background:C.bgAlt,borderRadius:12,padding:16,fontSize:13,
            lineHeight:1.75,color:C.text,whiteSpace:'pre-wrap',
            minHeight:200,marginBottom:20,
            border:`1px solid ${platform==='linkedin'?C.linkedin+'44':C.instagram+'44'}`
          }}>
            {generated}
          </div>
        )}

        {/* Instagram image URL */}
        {generated && platform==='instagram' && showIgImageField && (
          <div style={{marginBottom:16}}>
            <div style={{fontSize:11,color:C.amber,marginBottom:8}}>
              ⚠️ Instagram richiede un'immagine. Inserisci l'URL di un'immagine pubblica (es. da Canva o Dropbox):
            </div>
            <Input value={igImageUrl} onChange={setIgImageUrl} placeholder="https://...jpg"/>
          </div>
        )}

        {/* Publish result */}
        {postResult&&(
          <div style={{
            background:postResult.success?C.greenD:C.redD,
            border:`1px solid ${postResult.success?C.green+'44':C.red+'44'}`,
            borderRadius:12,padding:14,marginBottom:16,
          }}>
            {postResult.success?(
              <div style={{color:C.green,fontWeight:700}}>{postResult.message}</div>
            ):(
              <div>
                <div style={{color:C.red,fontWeight:700,marginBottom:6}}>⚠️ {postResult.error}</div>
                {postResult.setupLink&&(
                  <a href="/auth/setup" style={{color:C.blueL,fontSize:12}}>
                    → Vai alla configurazione token
                  </a>
                )}
              </div>
            )}
          </div>
        )}

        {/* Publish button */}
        {generated&&(
          <Btn full
            onClick={handlePublish}
            disabled={postLoading}
            variant={platform==='linkedin'?'linkedin':'instagram'}
            style={{fontSize:14,padding:'14px',fontWeight:800}}
          >
            {postLoading?'Pubblicazione in corso…':`🚀 Pubblica su ${platform==='linkedin'?'LinkedIn':'Instagram'}`}
          </Btn>
        )}

        {/* Status indicators */}
        <div style={{display:'flex',gap:8,marginTop:16}}>
          <div style={{
            flex:1,background:C.bgAlt,borderRadius:10,padding:'10px 14px',
            border:`1px solid ${C.linkedin}33`,textAlign:'center'
          }}>
            <div style={{fontSize:10,color:C.muted,marginBottom:2}}>LinkedIn</div>
            <div style={{fontSize:12,color:C.linkedin,fontWeight:700}}>
              {process.env.NEXT_PUBLIC_LINKEDIN_CONFIGURED==='true'?'✅ Connesso':'⚙️ Da configurare'}
            </div>
          </div>
          <div style={{
            flex:1,background:C.bgAlt,borderRadius:10,padding:'10px 14px',
            border:`1px solid ${C.instagram}33`,textAlign:'center'
          }}>
            <div style={{fontSize:10,color:C.muted,marginBottom:2}}>Instagram</div>
            <div style={{fontSize:12,color:C.instagram,fontWeight:700}}>
              {process.env.NEXT_PUBLIC_INSTAGRAM_CONFIGURED==='true'?'✅ Connesso':'⚙️ Da configurare'}
            </div>
          </div>
          <a href="/auth/setup" style={{
            flex:1,background:C.bgAlt,borderRadius:10,padding:'10px 14px',
            border:`1px solid ${C.gold}33`,textAlign:'center',textDecoration:'none',
            display:'flex',alignItems:'center',justifyContent:'center'
          }}>
            <div>
              <div style={{fontSize:10,color:C.muted,marginBottom:2}}>Setup</div>
              <div style={{fontSize:12,color:C.goldL,fontWeight:700}}>⚙️ Configura</div>
            </div>
          </a>
        </div>
      </Card>
    </div>
  );
}

// ─── CRM ──────────────────────────────────────────────────────────────────────
function CRM({clients,setClients}) {
  const [sel,setSel]=useState(null);const [add,setAdd]=useState(false);
  const [form,setForm]=useState({});const [ai2,setAi2]=useState('');const [aiL,setAiL]=useState(false);
  const [filter,setFilter]=useState('Tutti');
  const open=(c)=>{setSel(c);setAdd(false);setForm({...c});setAi2('');};
  const save=()=>{
    if(add)setClients(prev=>[...prev,{id:Date.now(),lastContact:todayStr(),...form,aum:Number(form.aum)}]);
    else setClients(prev=>prev.map(c=>c.id===sel.id?{...c,...form,aum:Number(form.aum)}:c));
    setSel(null);setAdd(false);
  };
  const del=()=>{
    if(window.confirm(`Eliminare ${sel.name}?`)){
      setClients(prev=>prev.filter(c=>c.id!==sel.id));
      setSel(null);
    }
  };
  const filtered=clients.filter(c=>filter==='Tutti'||c.status===filter);
  const sC={Lead:C.blueL,Prospect:C.amber,Cliente:C.green,Inattivo:C.muted};
  return <div style={{display:'grid',gridTemplateColumns:sel||add?'1fr 320px':'1fr',gap:16}}>
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
        <ST sub={`${clients.length} contatti`}>CRM Clienti</ST>
        <Btn onClick={()=>{setSel(null);setAdd(true);setForm({name:'',phone:'',email:'',status:'Lead',aum:0,notes:''});}}>+ Nuovo</Btn>
      </div>
      <div style={{display:'flex',gap:6,marginBottom:12}}>
        {['Tutti','Lead','Prospect','Cliente','Inattivo'].map(f=><Btn key={f} variant={filter===f?'primary':'ghost'} sm onClick={()=>setFilter(f)}>{f}</Btn>)}
      </div>
      {filtered.map(c=><Card key={c.id} hover onClick={()=>open(c)} style={{display:'flex',alignItems:'center',gap:12,cursor:'pointer',marginBottom:7,border:`1px solid ${sel?.id===c.id?C.goldD:C.border}`}}>
        <div style={{width:38,height:38,borderRadius:'50%',background:`linear-gradient(135deg,${C.gold},${C.goldL})`,display:'flex',alignItems:'center',justifyContent:'center',fontWeight:800,fontSize:12,color:'#000',flexShrink:0}}>{c.name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()}</div>
        <div style={{flex:1,minWidth:0}}>
          <div style={{fontWeight:600,fontSize:13}}>{c.name}</div>
          <div style={{fontSize:10,color:C.muted,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.email} · {c.lastContact}</div>
        </div>
        <div style={{textAlign:'right',flexShrink:0}}>
          <Badge label={c.status} color={sC[c.status]||C.gold} small/>
          {c.aum>0&&<div style={{fontSize:11,color:C.gold,marginTop:2,fontWeight:600}}>€{fmt(c.aum)}</div>}
        </div>
      </Card>)}
    </div>
    {(sel||add)&&<Card style={{alignSelf:'start',position:'sticky',top:20,maxHeight:'calc(100vh - 80px)',overflowY:'auto'}}>
      <div style={{fontWeight:800,color:C.goldL,marginBottom:14,fontSize:14}}>{add?'Nuovo Cliente':sel.name}</div>
      {[['name','Nome'],['phone','Tel'],['email','Email']].map(([f,l])=><div key={f} style={{marginBottom:8}}>
        <div style={{fontSize:9,color:C.muted,marginBottom:3,textTransform:'uppercase'}}>{l}</div>
        <Input value={form[f]||''} onChange={v=>setForm(p=>({...p,[f]:v}))} placeholder={l}/>
      </div>)}
      <div style={{marginBottom:8}}>
        <div style={{fontSize:9,color:C.muted,marginBottom:3,textTransform:'uppercase'}}>Status</div>
        <Sel value={form.status||'Lead'} onChange={v=>setForm(p=>({...p,status:v}))} options={['Lead','Prospect','Cliente','Inattivo']}/>
      </div>
      <div style={{marginBottom:8}}>
        <div style={{fontSize:9,color:C.muted,marginBottom:3,textTransform:'uppercase'}}>AUM €</div>
        <Input type="number" value={form.aum||0} onChange={v=>setForm(p=>({...p,aum:v}))}/>
      </div>
      <div style={{marginBottom:12}}>
        <div style={{fontSize:9,color:C.muted,marginBottom:3,textTransform:'uppercase'}}>Note</div>
        <Input value={form.notes||''} onChange={v=>setForm(p=>({...p,notes:v}))} multiline rows={2}/>
      </div>
      <div style={{display:'flex',gap:6,marginBottom:8}}>
        <Btn full onClick={save}>Salva</Btn>
        <Btn variant="ghost" onClick={()=>{setSel(null);setAdd(false);}}>✕</Btn>
      </div>
      {!add&&sel&&<Btn variant="danger" full style={{marginBottom:12}} onClick={del}>🗑 Elimina</Btn>}
      {!add&&<div style={{borderTop:`1px solid ${C.border}`,paddingTop:12}}>
        <Btn variant="accent" full onClick={async()=>{setAiL(true);const t=await ai('Coach CF. Strategie brevi.',`Cliente: ${form.name}. Status: ${form.status}. AUM: €${fmt(form.aum)}. Note: ${form.notes}. 3 azioni concrete settimana prossima.`);setAi2(t);setAiL(false);}} disabled={aiL}>{aiL?'Analisi…':'◈ Strategia AI'}</Btn>
        {aiL&&<div style={{marginTop:8}}><Loading/></div>}
        {ai2&&<div style={{background:C.surface,borderRadius:8,padding:10,marginTop:10,fontSize:11.5,lineHeight:1.6,color:C.textD,whiteSpace:'pre-wrap'}}>{ai2}</div>}
      </div>}
    </Card>}
  </div>;
}

// ─── PRODUCTS ─────────────────────────────────────────────────────────────────
function Products() {
  const [cat,setCat]=useState('Tutti');const [sel,setSel]=useState(null);
  const [pitch,setPitch]=useState('');const [pL,setPL]=useState(false);
  const cats=['Tutti',...new Set(PRODUCTS.map(p=>p.cat))];
  const filtered=PRODUCTS.filter(p=>cat==='Tutti'||p.cat===cat);
  const rC={Alto:C.red,Medio:C.amber,'Medio-Alto':C.amber,Basso:C.green,Variabile:C.blueL};
  return <div>
    <ST sub="Schede prodotto con pitch AI">Prodotti</ST>
    <div style={{display:'flex',gap:6,marginBottom:14}}>{cats.map(c=><Btn key={c} variant={cat===c?'primary':'ghost'} sm onClick={()=>{setCat(c);setSel(null);setPitch('');}}>  {c}</Btn>)}</div>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))',gap:10,marginBottom:12}}>
      {filtered.map(p=><Card key={p.id} hover onClick={()=>{setSel(p);setPitch('');}} style={{cursor:'pointer',border:`1px solid ${sel?.id===p.id?C.goldD:C.border}`}}>
        <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}><Badge label={p.cat} color={C.blueL} small/><Badge label={p.risk} color={rC[p.risk]||C.gold} small/></div>
        <div style={{fontWeight:700,fontSize:13,marginBottom:5}}>{p.name}</div>
        <div style={{fontSize:11,color:C.textD,lineHeight:1.5,marginBottom:10}}>{p.desc.slice(0,120)}{p.desc.length>120?'…':''}</div>
        <div style={{display:'flex',justifyContent:'space-between',fontSize:10}}>
          <span style={{color:C.muted}}>Min: €{fmt(p.min)}</span>
          <span style={{color:C.gold,fontWeight:700}}>Fee {p.fee}</span>
        </div>
      </Card>)}
    </div>
    {sel&&<Card>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
        <div>
          <div style={{fontWeight:700,color:C.goldL,fontSize:15}}>{sel.name}</div>
          <div style={{fontSize:11,color:C.muted,marginTop:3}}>{sel.desc}</div>
        </div>
        <Btn variant="accent" onClick={async()=>{setPL(true);const t=await ai('Esperto vendita etica CF italiani. Pitch brevi trasparenti. No promesse rendimento.',`Prodotto: ${sel.name}. Fee: ${sel.fee}. Rischio: ${sel.risk}. Desc: ${sel.desc}. Pitch 5-6 frasi per appuntamento. CTA: fissare call.`);setPitch(t);setPL(false);}} disabled={pL}>{pL?'…':'◈ Genera Pitch'}</Btn>
      </div>
      {pL&&<Loading/>}
      {pitch&&<div style={{background:C.bgAlt,borderRadius:10,padding:16,fontSize:13,lineHeight:1.75,color:C.text,whiteSpace:'pre-wrap'}}>{pitch}</div>}
    </Card>}
  </div>;
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function Dashboard({clients,leads}) {
  const today = leads.filter(l=>l.date===todayStr()).length;
  const week = leads.filter(l=>{const d=new Date(l.date.split('/').reverse().join('-'));return(Date.now()-d.getTime())<7*86400000;}).length;
  const clienti = clients.filter(c=>c.status==='Cliente').length;
  const aum = clients.reduce((s,c)=>s+(c.aum||0),0);
  return <div>
    <ST sub={`Oggi ${new Date().toLocaleDateString('it-IT',{weekday:'long',day:'numeric',month:'long'})}`}>Dashboard</ST>
    <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:12,marginBottom:24}}>
      {[
        {l:'Lead oggi',v:today,g:1,c:today>=1?C.green:C.red,sub:today>=1?'✅ Obiettivo raggiunto':'🎯 Obiettivo: 1/giorno'},
        {l:'Lead settimana',v:week,c:C.blueL,sub:'Target: 7+'},
        {l:'Clienti attivi',v:clienti,c:C.gold,sub:`su ${clients.length} contatti`},
        {l:'AUM gestito',v:'€'+fmt(aum),c:C.purple,sub:'portafoglio totale'},
      ].map(k=><Card key={k.l}>
        <div style={{fontSize:11,color:C.muted,marginBottom:8,textTransform:'uppercase',letterSpacing:.8}}>{k.l}</div>
        <div style={{fontSize:30,fontWeight:900,color:k.c,lineHeight:1}}>{k.v}</div>
        <div style={{fontSize:10,color:C.muted,marginTop:6}}>{k.sub}</div>
      </Card>)}
    </div>
    <Card>
      <div style={{fontWeight:700,color:C.goldL,marginBottom:14}}>🎯 Azioni consigliate oggi</div>
      {[
        today<1&&{icon:'📣',text:'Pubblica un post Social — nessun lead ancora oggi',urgent:true},
        {icon:'📞',text:`Richiama ${clients.filter(c=>c.status==='Prospect')[0]?.name||'un prospect'} per avanzare la trattativa`},
        {icon:'📧',text:'Invia follow-up ai Lead degli ultimi 3 giorni'},
        {icon:'📊',text:'Aggiorna AUM portafoglio clienti attivi'},
      ].filter(Boolean).map((a,i)=><div key={i} style={{display:'flex',alignItems:'flex-start',gap:12,padding:'10px 0',borderBottom:`1px solid ${C.border}`}}>
        <span style={{fontSize:18}}>{a.icon}</span>
        <div style={{fontSize:13,color:a.urgent?C.amber:C.textD,lineHeight:1.5}}>{a.text}</div>
      </div>)}
    </Card>
  </div>;
}

// ─── LEAD TRACKER ─────────────────────────────────────────────────────────────
function Leads({leads,setLeads}) {
  const [form,setForm]=useState({name:'',source:'LinkedIn',status:'Nuovo',notes:'',date:todayStr()});
  const today=leads.filter(l=>l.date===todayStr()).length;
  const SOURCES=['LinkedIn','Instagram','Referral','Meta Ads','LinkedIn Ads','Evento','Altro'];
  const SC={Nuovo:C.blueL,Contattato:C.amber,Qualificato:C.green,Perso:C.red};
  return <div>
    <ST sub={`${today}/1 lead oggi`}>Lead Tracker</ST>
    <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16,marginBottom:20}}>
      <Card>
        <div style={{fontWeight:700,color:C.goldL,marginBottom:14}}>+ Aggiungi Lead</div>
        <Input value={form.name} onChange={v=>setForm(p=>({...p,name:v}))} placeholder="Nome lead" style={{marginBottom:8}}/>
        <Sel value={form.source} onChange={v=>setForm(p=>({...p,source:v}))} options={SOURCES} style={{marginBottom:8}}/>
        <Input value={form.notes} onChange={v=>setForm(p=>({...p,notes:v}))} placeholder="Note" multiline rows={2} style={{marginBottom:12}}/>
        <Btn full onClick={()=>{if(form.name.trim()){setLeads(p=>[{id:Date.now(),...form},...p]);setForm(f=>({...f,name:'',notes:''}));}}}>Aggiungi</Btn>
      </Card>
      <Card style={{background:`linear-gradient(135deg,${today>=1?C.greenD:C.redD},${C.card})`,border:`1px solid ${today>=1?C.green+'44':C.red+'44'}`}}>
        <div style={{textAlign:'center',padding:'20px 0'}}>
          <div style={{fontSize:60,fontWeight:900,color:today>=1?C.green:C.red}}>{today}</div>
          <div style={{color:C.textD,fontSize:14,marginTop:4}}>lead oggi</div>
          <div style={{fontSize:12,color:today>=1?C.green:C.red,marginTop:8,fontWeight:700}}>{today>=1?'✅ Obiettivo raggiunto!':'🎯 Obiettivo: 1 lead/giorno'}</div>
        </div>
      </Card>
    </div>
    <div style={{display:'flex',flexDirection:'column',gap:8}}>
      {leads.map(l=><Card key={l.id} style={{display:'flex',alignItems:'center',gap:12}}>
        <div style={{width:8,height:8,borderRadius:'50%',background:SC[l.status]||C.gold,flexShrink:0}}/>
        <div style={{flex:1}}>
          <div style={{fontWeight:600,fontSize:13}}>{l.name}</div>
          <div style={{fontSize:11,color:C.muted}}>{l.source} · {l.date}</div>
        </div>
        <Badge label={l.status} color={SC[l.status]||C.gold} small/>
        <Sel value={l.status} onChange={v=>setLeads(p=>p.map(x=>x.id===l.id?{...x,status:v}:x))} options={['Nuovo','Contattato','Qualificato','Perso']} style={{width:130,fontSize:11,padding:'5px 8px'}}/>
        <button onClick={()=>setLeads(p=>p.filter(x=>x.id!==l.id))} style={{background:C.redD,border:'none',color:C.red,borderRadius:8,padding:'5px 10px',cursor:'pointer',fontSize:12}}>✕</button>
      </Card>)}
    </div>
  </div>;
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
const TABS=[
  {id:'dashboard',icon:'◉',label:'Dashboard'},
  {id:'social',icon:'📣',label:'Social Hub'},
  {id:'leads',icon:'🎯',label:'Lead Tracker'},
  {id:'clients',icon:'👥',label:'CRM Clienti'},
  {id:'products',icon:'📦',label:'Prodotti'},
];

export default function App() {
  const [tab,setTab]=useState('dashboard');
  const [clients,setClients]=useState([]);
  const [leads,setLeads]=useState([]);

  useEffect(()=>{
    try {
      const c=localStorage.getItem('cf_clients'); if(c)setClients(JSON.parse(c));
      const l=localStorage.getItem('cf_leads'); if(l)setLeads(JSON.parse(l));
    }catch{}
  },[]);

  useEffect(()=>{try{localStorage.setItem('cf_clients',JSON.stringify(clients));}catch{}},[clients]);
  useEffect(()=>{try{localStorage.setItem('cf_leads',JSON.stringify(leads));}catch{}},[leads]);

  const today=leads.filter(l=>l.date===todayStr()).length;

  const pages={
    dashboard:<Dashboard clients={clients} leads={leads}/>,
    social:<SocialHub/>,
    leads:<Leads leads={leads} setLeads={setLeads}/>,
    clients:<CRM clients={clients} setClients={setClients}/>,
    products:<Products/>,
  };

  return (
    <div style={{display:'flex',minHeight:'100vh',background:C.bg,color:C.text,fontFamily:"'Outfit',sans-serif"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Outfit:wght@400;600;700;800&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        input,textarea,select{outline:none;font-family:'Outfit',sans-serif;}
        ::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-track{background:transparent;} ::-webkit-scrollbar-thumb{background:${C.border};border-radius:2px;}
      `}</style>

      {/* Sidebar */}
      <div style={{width:220,background:C.bgAlt,borderRight:`1px solid ${C.border}`,padding:'28px 12px',display:'flex',flexDirection:'column',gap:4,flexShrink:0}}>
        <div style={{padding:'0 8px',marginBottom:20}}>
          <div style={{fontFamily:"'Playfair Display',serif",fontWeight:900,color:C.goldL,fontSize:18,lineHeight:1.2}}>CF Advisor</div>
          <div style={{fontSize:10,color:C.muted,marginTop:2}}>Suite Professionale</div>
        </div>
        {TABS.map(t=><button key={t.id} onClick={()=>setTab(t.id)} style={{
          display:'flex',alignItems:'center',gap:10,padding:'11px 14px',borderRadius:12,
          background:tab===t.id?`${C.gold}18`:'transparent',
          border:`1px solid ${tab===t.id?C.gold+'44':'transparent'}`,
          color:tab===t.id?C.goldL:C.textD,cursor:'pointer',fontSize:13,fontWeight:tab===t.id?700:500,
          textAlign:'left',transition:'all .15s'
        }}>
          <span style={{fontSize:15}}>{t.icon}</span>
          <span>{t.label}</span>
          {t.id==='social'&&<span style={{marginLeft:'auto',background:C.green+'22',color:C.green,borderRadius:6,padding:'1px 6px',fontSize:9,fontWeight:700}}>LIVE</span>}
          {t.id==='leads'&&today>=1&&<span style={{marginLeft:'auto',background:C.green+'22',color:C.green,borderRadius:6,padding:'1px 6px',fontSize:9,fontWeight:700}}>✓</span>}
        </button>)}

        <div style={{marginTop:'auto',padding:'12px 8px',borderTop:`1px solid ${C.border}`}}>
          <div style={{fontSize:10,color:C.muted,marginBottom:6}}>Lead oggi</div>
          <div style={{display:'flex',alignItems:'center',gap:8}}>
            <div style={{flex:1,height:6,background:C.border,borderRadius:3,overflow:'hidden'}}>
              <div style={{width:`${Math.min(today/1*100,100)}%`,height:'100%',background:today>=1?C.green:C.gold,borderRadius:3,transition:'width .4s'}}/>
            </div>
            <span style={{fontSize:11,fontWeight:700,color:today>=1?C.green:C.textD}}>{today}/1</span>
          </div>
          <a href="/auth/setup" style={{display:'block',marginTop:10,fontSize:10,color:C.muted,textDecoration:'none',textAlign:'center'}}>
            ⚙️ Configura Social API
          </a>
        </div>
      </div>

      {/* Main */}
      <div style={{flex:1,padding:28,overflowY:'auto',maxHeight:'100vh'}}>
        {pages[tab]}
      </div>
    </div>
  );
}
