import { useState, useEffect } from 'react';
import { dashboardAPI, transactionAPI, recurrenteAPI, transfertAPI, analyseAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const EUR = 655.957;
const fmtF = v => new Intl.NumberFormat('fr-FR').format(Math.round(Math.abs(v || 0))) + ' F';
const fmtE = v => Math.abs(v || 0).toFixed(2) + ' €';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [data, setData] = useState(null);
  const [txs, setTxs] = useState([]);
  const [analyse, setAnalyse] = useState(null);
  const [currency, setCurrency] = useState('FCFA');
  const [view, setView] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [form, setForm] = useState({ type_tx:'expense', category:'', label:'', montant_eur:'', date:new Date().toISOString().slice(0,10), note:'' });
  const [categories, setCategories] = useState([]);
  const [distAmt, setDistAmt] = useState('');
  const [distResult, setDistResult] = useState(null);
  const [transfertAmt, setTransfertAmt] = useState('');
  const [transfertResult, setTransfertResult] = useState(null);

  const fmt = v => currency === 'FCFA' ? fmtF(v) : fmtE(v);
  const showT = (msg, type='success') => { setToast({msg,type}); setTimeout(()=>setToast(null),3500); };

  const load = async () => {
    try {
      const [dash, txList, cats, anal] = await Promise.all([
        dashboardAPI.get(), transactionAPI.list(), 
        fetch(process.env.REACT_APP_API_URL+'/categories/', { headers: { Authorization:'Bearer '+localStorage.getItem('access_token') } }).then(r=>r.json()),
        analyseAPI.get()
      ]);
      setData(dash.data);
      setTxs(txList.data.results || txList.data);
      setCategories(Array.isArray(cats) ? cats : cats.results || []);
      setAnalyse(anal.data);
    } catch(e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const addTx = async () => {
    if (!form.label || !form.montant_eur) { showT('Remplis tous les champs.','error'); return; }
    try {
      await transactionAPI.create(form);
      showT('Transaction enregistrée ✓');
      setForm({ type_tx:'expense', category:categories[0]?.id||'', label:'', montant_eur:'', date:new Date().toISOString().slice(0,10), note:'' });
      load();
      if (form.type_tx === 'expense') setView('analyse');
    } catch(e) { showT('Erreur lors de l\'enregistrement.','error'); }
  };

  const doRepartir = async () => {
    try {
      const { data } = await transactionAPI.repartir(parseFloat(distAmt));
      setDistResult(data);
    } catch { showT('Erreur lors de la répartition.','error'); }
  };

  const doSimuler = async () => {
    try {
      const { data } = await transfertAPI.simuler(parseFloat(transfertAmt));
      setTransfertResult(data);
    } catch { showT('Erreur simulation.','error'); }
  };

  const healthColor = { excellent:'#4ade80', bon:'#fbbf24', critique:'#f87171' }[data?.health_level] || '#94a3b8';

  const S = {
    page: { minHeight:'100vh', background:'#080d1a', fontFamily:"'DM Sans','Segoe UI',sans-serif", color:'#e2e8f0', maxWidth:480, margin:'0 auto', position:'relative' },
    card: { background:'rgba(255,255,255,0.03)', borderRadius:16, padding:'14px 16px', border:'1px solid rgba(255,255,255,0.07)', marginBottom:12 },
    label: { fontSize:10, color:'#64748b', display:'block', marginBottom:5, textTransform:'uppercase', letterSpacing:1.2 },
    input: { width:'100%', background:'rgba(255,255,255,0.07)', border:'1px solid rgba(255,255,255,0.11)', borderRadius:11, padding:'11px 14px', color:'#fff', fontSize:14, outline:'none', boxSizing:'border-box' },
    select: { width:'100%', background:'rgba(255,255,255,0.07)', border:'1px solid rgba(255,255,255,0.11)', borderRadius:11, padding:'11px 14px', color:'#fff', fontSize:14, outline:'none', boxSizing:'border-box', colorScheme:'dark' },
    sectionTitle: { fontSize:11, fontWeight:800, color:'#64748b', letterSpacing:1.5, textTransform:'uppercase', marginBottom:10 },
    btn: (bg) => ({ padding:'11px 18px', borderRadius:12, border:'none', background:bg, color:'#fff', cursor:'pointer', fontWeight:800, fontSize:13 }),
  };

  if (loading) return (
    <div style={{ ...S.page, display:'flex', alignItems:'center', justifyContent:'center', height:'100vh' }}>
      <div style={{ textAlign:'center' }}>
        <div style={{ fontSize:48, marginBottom:16 }}>💰</div>
        <div style={{ fontSize:16, color:'#818cf8', fontWeight:700 }}>Chargement...</div>
      </div>
    </div>
  );

  return (
    <div style={S.page}>
      {/* BG glow */}
      <div style={{ position:'fixed',top:-80,left:-80,width:360,height:360,background:'radial-gradient(circle,rgba(99,102,241,0.18) 0%,transparent 70%)',pointerEvents:'none',zIndex:0 }}/>

      {/* Toast */}
      {toast && <div style={{ position:'fixed',top:16,left:'50%',transform:'translateX(-50%)',background:toast.type==='error'?'#ef4444':'#22c55e',color:'#fff',padding:'10px 22px',borderRadius:14,fontSize:13,fontWeight:700,zIndex:9999,whiteSpace:'nowrap' }}>{toast.msg}</div>}

      {/* Header */}
      <div style={{ padding:'18px 20px 0',display:'flex',justifyContent:'space-between',alignItems:'center',position:'relative',zIndex:1 }}>
        <div>
          <div style={{ fontSize:10,color:'#475569',letterSpacing:2,textTransform:'uppercase' }}>Wallet</div>
          <div style={{ fontSize:19,fontWeight:900,background:'linear-gradient(135deg,#818cf8,#e879f9)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent' }}>
            {user?.username} 🇨🇲→🇫🇷
          </div>
        </div>
        <div style={{ display:'flex',gap:8 }}>
          <button onClick={()=>setCurrency(c=>c==='FCFA'?'EUR':'FCFA')} style={{ ...S.btn('rgba(99,102,241,0.2)'),border:'1px solid rgba(99,102,241,0.4)',color:'#818cf8',padding:'6px 12px',borderRadius:20,fontSize:12 }}>
            {currency==='FCFA'?'🔁 €':'🔁 FCFA'}
          </button>
          <button onClick={logout} style={{ ...S.btn('rgba(239,68,68,0.15)'),border:'1px solid rgba(239,68,68,0.3)',color:'#f87171',padding:'6px 12px',borderRadius:20,fontSize:12 }}>⏻</button>
        </div>
      </div>

      {/* Balance Card */}
      {data && (
        <div style={{ margin:'14px 20px',background:'linear-gradient(135deg,#1a2035 0%,#2d1b69 100%)',borderRadius:22,padding:'20px 22px 16px',border:'1px solid rgba(129,140,248,0.3)',position:'relative',overflow:'hidden',zIndex:1 }}>
          <div style={{ position:'absolute',top:-30,right:-30,width:140,height:140,background:'radial-gradient(circle,rgba(232,121,249,0.25),transparent)',borderRadius:'50%' }}/>
          <div style={{ fontSize:10,color:'#94a3b8',letterSpacing:1.5,textTransform:'uppercase',marginBottom:3 }}>Solde total</div>
          <div style={{ fontSize:28,fontWeight:900,letterSpacing:-1 }}>{fmt(data.solde_eur)}</div>
          <div style={{ fontSize:11,color:'#475569',marginBottom:12 }}>{currency==='FCFA'?fmtE(data.solde_eur):fmtF(data.solde_eur)}</div>
          <div style={{ height:5,background:'rgba(255,255,255,0.08)',borderRadius:4,overflow:'hidden',marginBottom:5 }}>
            <div style={{ width:`${Math.min(data.pourcentage_capital,100)}%`,height:'100%',background:`linear-gradient(90deg,${healthColor},#818cf8)`,borderRadius:4 }}/>
          </div>
          <div style={{ display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:14 }}>
            <div style={{ display:'flex',alignItems:'center',gap:5 }}>
              <div style={{ width:7,height:7,borderRadius:'50%',background:healthColor,boxShadow:`0 0 8px ${healthColor}` }}/>
              <span style={{ fontSize:11,color:healthColor,fontWeight:700 }}>{(data.health_level||'').toUpperCase()} · {(data.pourcentage_capital||0).toFixed(1)}%</span>
            </div>
            <span style={{ fontSize:11,color:'#475569' }}>{fmt(data.solde_initial_eur)} initial</span>
          </div>
          <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:8 }}>
            <button onClick={()=>{setView('repartir')}} style={{ padding:'8px',borderRadius:11,border:'1px solid rgba(99,102,241,0.5)',background:'rgba(99,102,241,0.15)',color:'#818cf8',cursor:'pointer',fontSize:11,fontWeight:800 }}>💰 Répartir</button>
            <button onClick={()=>setView('transfert')} style={{ padding:'8px',borderRadius:11,border:'1px solid rgba(232,121,249,0.5)',background:'rgba(232,121,249,0.15)',color:'#e879f9',cursor:'pointer',fontSize:11,fontWeight:800 }}>🌍 Simuler transfert</button>
          </div>
        </div>
      )}

      {/* Quick stats */}
      {data && (
        <div style={{ display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:7,margin:'0 20px 12px',position:'relative',zIndex:1 }}>
          {[
            { label:'Revenus', v:data.total_revenus_eur, icon:'📈', color:'#4ade80' },
            { label:'Dépenses',v:data.total_depenses_eur,icon:'💸', color:'#f87171' },
            { label:'Famille', v:data.total_famille_eur, icon:'🌍', color:'#e879f9' },
            { label:'Épargne', v:data.total_epargne_eur, icon:'🏦', color:'#fbbf24' },
          ].map((s,i)=>(
            <div key={i} style={{ background:'rgba(255,255,255,0.04)',borderRadius:13,padding:'10px 5px',border:'1px solid rgba(255,255,255,0.06)',textAlign:'center' }}>
              <div style={{ fontSize:15,marginBottom:3 }}>{s.icon}</div>
              <div style={{ fontSize:10,fontWeight:800,color:s.color }}>{fmt(s.v)}</div>
              <div style={{ fontSize:9,color:'#475569',marginTop:2 }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Nav */}
      <div style={{ display:'flex',margin:'0 20px 12px',background:'rgba(255,255,255,0.04)',borderRadius:14,padding:4,gap:2,position:'relative',zIndex:1 }}>
        {[
          { id:'dashboard', label:'🏠' },
          { id:'add',       label:'➕' },
          { id:'history',   label:'🕐' },
          { id:'analyse',   label:'📊' },
          { id:'repartir',  label:'💰' },
          { id:'transfert', label:'🌍' },
        ].map(tab=>(
          <button key={tab.id} onClick={()=>setView(tab.id)} style={{ flex:1,padding:'8px 2px',borderRadius:10,border:'none',background:view===tab.id?'linear-gradient(135deg,#6366f1,#8b5cf6)':'transparent',color:view===tab.id?'#fff':'#475569',cursor:'pointer',fontSize:15 }}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── DASHBOARD VIEW ── */}
      {view==='dashboard' && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          {data?.alertes?.filter(a=>a.level==='danger').map((a,i)=>(
            <div key={i} style={{ background:'rgba(239,68,68,0.12)',border:'1px solid rgba(239,68,68,0.35)',borderRadius:13,padding:'11px 14px',marginBottom:10,fontSize:12,color:'#fca5a5',fontWeight:600 }}>{a.icon} {a.text}</div>
          ))}
          {/* Évolution mensuelle */}
          {data?.evolution_mensuelle?.length > 1 && (
            <div style={S.card}>
              <div style={S.sectionTitle}>📈 Évolution 6 derniers mois</div>
              <div style={{ display:'flex',gap:6,alignItems:'flex-end',height:70,marginBottom:8 }}>
                {data.evolution_mensuelle.map((m,i)=>{
                  const maxV = Math.max(...data.evolution_mensuelle.map(x=>Math.max(x.revenus,x.depenses)),1);
                  return (
                    <div key={i} style={{ flex:1,display:'flex',flexDirection:'column',alignItems:'center',gap:2 }}>
                      <div style={{ display:'flex',gap:2,alignItems:'flex-end',height:64 }}>
                        <div style={{ width:10,height:Math.round((m.revenus/maxV)*60)||2,background:'#4ade80',borderRadius:3 }}/>
                        <div style={{ width:10,height:Math.round((m.depenses/maxV)*60)||2,background:'#f87171',borderRadius:3 }}/>
                      </div>
                      <div style={{ fontSize:9,color:'#475569' }}>{m.label}</div>
                    </div>
                  );
                })}
              </div>
              <div style={{ display:'flex',gap:16,justifyContent:'center' }}>
                {[['#4ade80','Revenus'],['#f87171','Dépenses']].map(([c,l])=>(
                  <div key={l} style={{ display:'flex',alignItems:'center',gap:5 }}><div style={{ width:10,height:10,background:c,borderRadius:2 }}/><span style={{ fontSize:10,color:'#94a3b8' }}>{l}</span></div>
                ))}
              </div>
            </div>
          )}
          {/* Transactions récentes */}
          <div style={S.sectionTitle}>⚡ Transactions récentes</div>
          {txs.slice(0,6).map(t=>{
            const cat = categories.find(c=>c.id===t.category);
            return (
              <div key={t.id} style={{ display:'flex',alignItems:'center',gap:10,marginBottom:8,background:'rgba(255,255,255,0.03)',borderRadius:12,padding:'11px 13px',border:'1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ width:36,height:36,borderRadius:10,background:`${cat?.couleur||'#94a3b8'}22`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:17,flexShrink:0 }}>{cat?.icone||'💡'}</div>
                <div style={{ flex:1,minWidth:0 }}>
                  <div style={{ fontSize:12,fontWeight:700,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis' }}>{t.label}</div>
                  <div style={{ fontSize:10,color:'#475569' }}>{t.date}</div>
                </div>
                <div style={{ fontSize:13,fontWeight:800,color:t.type_tx==='income'?'#4ade80':'#f87171',flexShrink:0 }}>
                  {t.type_tx==='income'?'+':'-'}{fmt(parseFloat(t.montant_eur))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── ADD VIEW ── */}
      {view==='add' && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          <div style={S.card}>
            <div style={S.sectionTitle}>➕ Nouvelle transaction</div>
            <div style={{ display:'flex',gap:8,marginBottom:14,background:'rgba(255,255,255,0.05)',borderRadius:12,padding:4 }}>
              {['expense','income'].map(tp=>(
                <button key={tp} onClick={()=>setForm(f=>({...f,type_tx:tp}))} style={{ flex:1,padding:10,borderRadius:10,border:'none',background:form.type_tx===tp?(tp==='expense'?'#ef4444':'#22c55e'):'transparent',color:'#fff',cursor:'pointer',fontWeight:800,fontSize:13 }}>
                  {tp==='expense'?'💸 Dépense':'💰 Revenu'}
                </button>
              ))}
            </div>
            <div style={{ marginBottom:12 }}><label style={S.label}>Libellé *</label><input value={form.label} onChange={e=>setForm(f=>({...f,label:e.target.value}))} placeholder="Ex: Lidl courses..." style={S.input}/></div>
            <div style={{ marginBottom:12 }}><label style={S.label}>Montant (€) *</label><input value={form.montant_eur} onChange={e=>setForm(f=>({...f,montant_eur:e.target.value}))} type="number" placeholder="Ex: 35" style={S.input}/>{form.montant_eur&&<div style={{ fontSize:11,color:'#4ade80',marginTop:3 }}>≈ {fmtF(parseFloat(form.montant_eur)*EUR)}</div>}</div>
            <div style={{ marginBottom:12 }}><label style={S.label}>Catégorie *</label>
              <select value={form.category} onChange={e=>setForm(f=>({...f,category:e.target.value}))} style={S.select}>
                <option value="">-- Choisir --</option>
                {categories.filter(c=>form.type_tx==='income'?c.type_cat==='revenu':c.type_cat!=='revenu').map(c=>(
                  <option key={c.id} value={c.id}>{c.icone} {c.nom}</option>
                ))}
              </select>
            </div>
            <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:16 }}>
              <div><label style={S.label}>Date *</label><input value={form.date} onChange={e=>setForm(f=>({...f,date:e.target.value}))} type="date" style={{...S.input,colorScheme:'dark'}}/></div>
              <div><label style={S.label}>Note</label><input value={form.note} onChange={e=>setForm(f=>({...f,note:e.target.value}))} placeholder="Optionnel" style={S.input}/></div>
            </div>
            <button onClick={addTx} style={{...S.btn('linear-gradient(135deg,#6366f1,#8b5cf6)'),width:'100%',padding:14,fontSize:15}}>✓ Enregistrer</button>
          </div>
        </div>
      )}

      {/* ── HISTORY VIEW ── */}
      {view==='history' && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          <div style={S.sectionTitle}>Toutes les transactions ({txs.length})</div>
          {txs.map(t=>{
            const cat = categories.find(c=>c.id===t.category);
            return (
              <div key={t.id} style={{ display:'flex',alignItems:'center',gap:10,marginBottom:8,background:'rgba(255,255,255,0.03)',borderRadius:13,padding:'11px 13px',border:'1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ width:38,height:38,borderRadius:11,background:`${cat?.couleur||'#94a3b8'}22`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:18,flexShrink:0 }}>{cat?.icone||'💡'}</div>
                <div style={{ flex:1,minWidth:0 }}>
                  <div style={{ fontSize:12,fontWeight:700,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' }}>{t.label}</div>
                  <div style={{ fontSize:10,color:'#475569' }}>{t.date}{t.note?` · ${t.note}`:''}</div>
                </div>
                <div style={{ fontSize:13,fontWeight:800,color:t.type_tx==='income'?'#4ade80':'#f87171',flexShrink:0 }}>
                  {t.type_tx==='income'?'+':'-'}{fmt(parseFloat(t.montant_eur))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── ANALYSE VIEW ── */}
      {view==='analyse' && analyse && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          <div style={{ ...S.card,background:'linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.12))',border:'1px solid rgba(129,140,248,0.3)' }}>
            <div style={{ fontSize:14,fontWeight:900,marginBottom:12 }}>💡 Plan de structuration</div>
            <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:10,marginBottom:14 }}>
              {[
                { label:'Revenus', v:analyse.revenus_eur, color:'#4ade80' },
                { label:'Dépenses', v:analyse.depenses_eur, color:'#f87171' },
                { label:'Solde', v:analyse.solde_mois_eur, color:analyse.solde_mois_eur>=0?'#4ade80':'#f87171' },
              ].map((s,i)=>(
                <div key={i} style={{ textAlign:'center',background:'rgba(255,255,255,0.05)',borderRadius:12,padding:'10px 6px' }}>
                  <div style={{ fontSize:16,fontWeight:900,color:s.color }}>{fmt(s.v)}</div>
                  <div style={{ fontSize:10,color:'#475569',marginTop:3 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div style={S.sectionTitle}>🔍 Recommandations</div>
          {analyse.recommandations.map((r,i)=>(
            <div key={i} style={{ marginBottom:8,borderRadius:13,padding:'12px 14px',background:r.level==='danger'?'rgba(239,68,68,0.12)':r.level==='warn'?'rgba(251,191,36,0.1)':r.level==='good'?'rgba(34,197,94,0.1)':'rgba(99,102,241,0.1)',border:`1px solid ${r.level==='danger'?'rgba(239,68,68,0.3)':r.level==='warn'?'rgba(251,191,36,0.25)':r.level==='good'?'rgba(34,197,94,0.25)':'rgba(99,102,241,0.25)'}` }}>
              <div style={{ fontSize:12,fontWeight:700,lineHeight:1.5,color:r.level==='danger'?'#fca5a5':r.level==='warn'?'#fde68a':r.level==='good'?'#86efac':'#c4b5fd' }}>{r.icon} {r.text}</div>
            </div>
          ))}
          <div style={S.sectionTitle}>✅ Actions prioritaires</div>
          {analyse.actions_prioritaires.map((a,i)=>(
            <div key={i} style={{ display:'flex',gap:10,marginBottom:9,padding:'9px 12px',background:'rgba(255,255,255,0.04)',borderRadius:11 }}>
              <span style={{ fontSize:17 }}>{a.icon}</span>
              <span style={{ fontSize:12,fontWeight:600,color:'#94a3b8',lineHeight:1.5 }}>{a.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── REPARTIR VIEW ── */}
      {view==='repartir' && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          <div style={S.card}>
            <div style={{ fontSize:15,fontWeight:900,marginBottom:4 }}>💰 Répartition automatique</div>
            <div style={{ fontSize:12,color:'#64748b',marginBottom:16 }}>Entre un montant — il sera réparti selon tes charges fixes.</div>
            <div style={{ display:'flex',gap:10,marginBottom:14 }}>
              <input value={distAmt} onChange={e=>{setDistAmt(e.target.value);setDistResult(null);}} type="number" placeholder="Montant en €" style={{...S.input,flex:1}}/>
              <button onClick={doRepartir} style={S.btn('linear-gradient(135deg,#6366f1,#8b5cf6)')}>Calculer</button>
            </div>
            {distResult && (
              <>
                <div style={{ fontSize:11,color:'#94a3b8',marginBottom:10 }}>Répartition de {fmtE(distResult.montant_total_eur)} :</div>
                {distResult.repartition.map((d,i)=>(
                  <div key={i} style={{ display:'flex',alignItems:'center',gap:10,marginBottom:7,...S.card,padding:'10px 12px',marginBottom:7 }}>
                    <span style={{ fontSize:20,width:28,textAlign:'center' }}>{d.category_icone}</span>
                    <div style={{ flex:1 }}>
                      <div style={{ fontSize:13,fontWeight:700 }}>{d.category_nom}</div>
                      <div style={{ fontSize:10,color:'#475569' }}>{d.pourcentage}% · Budget : {fmtE(d.montant_budget_eur)}</div>
                    </div>
                    <div style={{ fontSize:13,fontWeight:800,color:'#4ade80' }}>{fmtE(d.montant_alloue_eur)}</div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      )}

      {/* ── TRANSFERT VIEW ── */}
      {view==='transfert' && (
        <div style={{ padding:'0 20px 80px',position:'relative',zIndex:1 }}>
          <div style={S.card}>
            <div style={{ fontSize:15,fontWeight:900,marginBottom:4 }}>🌍 Simulateur transfert famille 🇨🇲</div>
            <div style={{ fontSize:12,color:'#64748b',marginBottom:16 }}>Compare les prestataires en temps réel.</div>
            <div style={{ display:'flex',gap:10,marginBottom:14 }}>
              <input value={transfertAmt} onChange={e=>{setTransfertAmt(e.target.value);setTransfertResult(null);}} type="number" placeholder="Montant à envoyer (€)" style={{...S.input,flex:1}}/>
              <button onClick={doSimuler} style={S.btn('linear-gradient(135deg,#e879f9,#8b5cf6)')}>Simuler</button>
            </div>
            {transfertResult && transfertResult.resultats.map((p,i)=>(
              <div key={i} style={{ ...S.card,border:`1px solid ${p.is_best?'rgba(232,121,249,0.4)':'rgba(255,255,255,0.07)'}`,background:p.is_best?'rgba(232,121,249,0.08)':'rgba(255,255,255,0.03)',marginBottom:8 }}>
                <div style={{ display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:4 }}>
                  <div>
                    <span style={{ fontSize:13,fontWeight:800 }}>{p.name}</span>
                    {p.is_best&&<span style={{ marginLeft:8,fontSize:10,background:'rgba(232,121,249,0.3)',color:'#e879f9',padding:'2px 7px',borderRadius:6,fontWeight:800 }}>MEILLEUR</span>}
                  </div>
                  <div style={{ textAlign:'right' }}>
                    <div style={{ fontSize:15,fontWeight:900,color:'#4ade80' }}>{fmtF(p.montant_fcfa)}</div>
                    <div style={{ fontSize:10,color:'#475569' }}>reçu</div>
                  </div>
                </div>
                <div style={{ fontSize:11,color:'#64748b' }}>Frais : {p.frais_eur}€ · {p.delai}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style>{`input::placeholder,textarea::placeholder{color:#374151}::-webkit-scrollbar{width:0;height:0}*{-webkit-tap-highlight-color:transparent;box-sizing:border-box}`}</style>
    </div>
  );
}
