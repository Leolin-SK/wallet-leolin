import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

const S = {
  page: { minHeight:'100vh', background:'#080d1a', display:'flex', alignItems:'center', justifyContent:'center', fontFamily:"'DM Sans','Segoe UI',sans-serif", padding:20 },
  card: { background:'rgba(255,255,255,0.04)', borderRadius:24, padding:'36px 32px', width:'100%', maxWidth:400, border:'1px solid rgba(129,140,248,0.3)', boxShadow:'0 24px 80px rgba(0,0,0,0.5)' },
  title: { fontSize:28, fontWeight:900, background:'linear-gradient(135deg,#818cf8,#e879f9)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', marginBottom:4 },
  subtitle: { fontSize:13, color:'#64748b', marginBottom:28 },
  label: { fontSize:11, color:'#64748b', display:'block', marginBottom:5, textTransform:'uppercase', letterSpacing:1.2 },
  input: { width:'100%', background:'rgba(255,255,255,0.07)', border:'1px solid rgba(255,255,255,0.11)', borderRadius:12, padding:'12px 16px', color:'#fff', fontSize:14, outline:'none', boxSizing:'border-box', marginBottom:14 },
  btn: { width:'100%', padding:14, borderRadius:12, border:'none', background:'linear-gradient(135deg,#6366f1,#8b5cf6)', color:'#fff', cursor:'pointer', fontSize:15, fontWeight:800 },
  err: { background:'rgba(239,68,68,0.15)', border:'1px solid rgba(239,68,68,0.3)', borderRadius:10, padding:'10px 14px', color:'#fca5a5', fontSize:12, marginBottom:14 },
  switch: { textAlign:'center', marginTop:18, fontSize:13, color:'#64748b' },
  link: { color:'#818cf8', cursor:'pointer', fontWeight:700, marginLeft:5 },
};

export default function LoginPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [form, setForm] = useState({ username:'', email:'', password:'', password2:'', first_name:'', last_name:'' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    setError(''); setLoading(true);
    try {
      if (mode === 'login') {
        await login(form.username, form.password);
      } else {
        await authAPI.register(form);
        await login(form.username, form.password);
      }
    } catch (e) {
      const data = e.response?.data;
      setError(data?.detail || data?.username?.[0] || data?.password?.[0] || 'Erreur. Vérifie tes identifiants.');
    }
    setLoading(false);
  };

  return (
    <div style={S.page}>
      <div style={S.card}>
        <div style={{ textAlign:'center', marginBottom:24 }}>
          <div style={{ fontSize:48, marginBottom:8 }}>💰</div>
          <div style={S.title}>Wallet Léolin</div>
          <div style={S.subtitle}>Gestion financière 🇨🇲 → 🇫🇷</div>
        </div>

        {error && <div style={S.err}>⚠️ {error}</div>}

        {mode === 'register' && (
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginBottom:0 }}>
            <div><label style={S.label}>Prénom</label><input value={form.first_name} onChange={e=>set('first_name',e.target.value)} placeholder="Léolin" style={S.input}/></div>
            <div><label style={S.label}>Nom</label><input value={form.last_name} onChange={e=>set('last_name',e.target.value)} placeholder="Kameni" style={S.input}/></div>
          </div>
        )}

        <label style={S.label}>Nom d'utilisateur</label>
        <input value={form.username} onChange={e=>set('username',e.target.value)} placeholder="leolin" style={S.input}/>

        {mode === 'register' && (
          <>
            <label style={S.label}>Email</label>
            <input value={form.email} onChange={e=>set('email',e.target.value)} placeholder="leolin@email.com" type="email" style={S.input}/>
          </>
        )}

        <label style={S.label}>Mot de passe</label>
        <input value={form.password} onChange={e=>set('password',e.target.value)} type="password" placeholder="••••••••" style={S.input}/>

        {mode === 'register' && (
          <>
            <label style={S.label}>Confirmer le mot de passe</label>
            <input value={form.password2} onChange={e=>set('password2',e.target.value)} type="password" placeholder="••••••••" style={S.input}/>
          </>
        )}

        <button onClick={handleSubmit} disabled={loading} style={{ ...S.btn, opacity:loading?0.6:1 }}>
          {loading ? '⏳ Chargement...' : mode === 'login' ? '🔐 Se connecter' : '✨ Créer mon compte'}
        </button>

        <div style={S.switch}>
          {mode === 'login' ? 'Pas encore de compte ?' : 'Déjà un compte ?'}
          <span style={S.link} onClick={() => { setMode(m => m === 'login' ? 'register' : 'login'); setError(''); }}>
            {mode === 'login' ? 'Créer un compte' : 'Se connecter'}
          </span>
        </div>
      </div>
    </div>
  );
}
