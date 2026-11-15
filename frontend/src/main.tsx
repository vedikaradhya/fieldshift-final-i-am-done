import { FormEvent, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

// XSS Protection: Sanitize user input before rendering
const sanitize = (input: string): string => {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
};
type Farm = { id:number; name:string; area_hectares:number; latitude:number; longitude:number; current_crop?:string };
type Climate = { source:string; simulated:boolean; data:Array<{date:string;temperature_c:number;rainfall_mm:number;soil_moisture_pct:number}> };

function App() {
  const [token, setToken] = useState(localStorage.getItem('agrispace-token') ?? '');
  const [email, setEmail] = useState(''); const [password, setPassword] = useState('');
  const [name, setName] = useState(''); const [phone, setPhone] = useState('');
  const [farms, setFarms] = useState<Farm[]>([]); const [selected, setSelected] = useState<Farm>();
  const [climate, setClimate] = useState<Climate>(); const [status, setStatus] = useState('');
  const [authMode, setAuthMode] = useState<'signin' | 'register' | null>(null);
  const headers = () => ({ Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' });
  const totalArea = useMemo(() => farms.reduce((sum, farm) => sum + farm.area_hectares, 0), [farms]);
  const latest = climate?.data.at(-1);
  const load = async () => { if (!token) return; const response = await fetch(`${API}/farms`, {headers: headers()}); if (response.ok) { const data = await response.json(); setFarms(data); setSelected(current => data.find((f:Farm) => f.id === current?.id) ?? data[0]); } };
  useEffect(() => { load(); }, [token]);
  useEffect(() => { if (!selected) return; fetch(`${API}/farms/${selected.id}/climate`, {headers:headers()}).then(r => r.ok ? r.json() : undefined).then(setClimate).catch(() => setClimate(undefined)); }, [selected?.id]);
  const login = async (event:FormEvent) => { event.preventDefault(); setStatus(''); const response = await fetch(`${API}/auth/login`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({email,password})}); if (!response.ok) { const error = await response.json().catch(() => ({})); setStatus(error.detail || 'Sign in was unsuccessful. Check your details or register through the API.'); return; } const data = await response.json(); localStorage.setItem('agrispace-token', data.access_token); setToken(data.access_token); setAuthMode(null); setStatus(`Welcome back, ${data.user.name}.`); };
  const register = async (event:FormEvent) => { event.preventDefault(); setStatus(''); const response = await fetch(`${API}/auth/register`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name,email,password,phone:phone||null})}); if (!response.ok) { const error = await response.json().catch(() => ({})); if (Array.isArray(error.detail)) { setStatus(error.detail.map((e:any) => e.msg).join('. ')); } else { setStatus(error.detail || 'Registration was unsuccessful. This email may already be registered.'); } return; } const data = await response.json(); localStorage.setItem('agrispace-token', data.access_token); setToken(data.access_token); setAuthMode(null); setStatus(`Welcome to AgriSpace, ${data.user.name}.`); };
  const addDemoFarm = async () => { const payload={name:'Orchard North', latitude:28.6139, longitude:77.209, boundary:{type:'Polygon',coordinates:[[[77.209,28.614],[77.211,28.614],[77.211,28.616],[77.209,28.614]]]}, current_crop:'Pigeon pea'}; const response = await fetch(`${API}/farms`,{method:'POST',headers:headers(),body:JSON.stringify(payload)}); setStatus(response.ok ? 'Farm saved. Its environmental feed is shown as simulated until a live NASA source is configured.' : 'Unable to save the farm.'); if(response.ok) load(); };
  
  if (!token) {
    return (
      <>
        <nav className="landing-nav">
          <div className="brand"><i>●</i> AgriSpace</div>
          <div className="auth-buttons">
            <button className="secondary" onClick={() => setAuthMode('signin')}>Sign in</button>
            <button className="primary" onClick={() => setAuthMode('register')}>Create account</button>
          </div>
        </nav>
        <main className="landing">
          <section className="landing-hero">
            <div className="landing-content">
              <p className="overline">FARM INTELLIGENCE, THOUGHTFULLY MADE</p>
              <h1>See the signals<br/>behind your soil.</h1>
              <p className="intro">A calm, clear workspace for your farms, environmental observations, and seasonal decisions.</p>
              <div className="landing-cta">
                <button className="primary large" onClick={() => setAuthMode('register')}>Get started free</button>
                <button className="secondary large" onClick={() => setAuthMode('signin')}>Sign in</button>
              </div>
              <p className="fine-print">This local build uses transparent simulated data until an integration reports a live source.</p>
            </div>
            <aside className="landing-visual"><div className="orb"></div><p>Made for measured decisions.</p></aside>
          </section>
        </main>
        {authMode && (
          <div className="modal-overlay" onClick={() => setAuthMode(null)}>
            <div className="modal-card" onClick={e => e.stopPropagation()}>
              <button className="modal-close" onClick={() => setAuthMode(null)}>✕</button>
              <div className="brand"><i>●</i> AgriSpace</div>
              <h2>{authMode === 'signin' ? 'Welcome back' : 'Create your account'}</h2>
              <form onSubmit={authMode === 'signin' ? login : register}>
                {authMode === 'register' && (
                  <label>Full name<input value={name} onChange={e=>setName(e.target.value)} type="text" autoComplete="name" required /></label>
                )}
                <label>Email address<input value={email} onChange={e=>setEmail(e.target.value)} type="email" autoComplete={authMode === 'register' ? 'email' : 'username'} required /></label>
                <label>Password<input value={password} onChange={e=>setPassword(e.target.value)} type="password" autoComplete={authMode === 'register' ? 'new-password' : 'current-password'} required /></label>
                {authMode === 'register' && (
                  <label>Phone (optional)<input value={phone} onChange={e=>setPhone(e.target.value)} type="tel" autoComplete="tel" /></label>
                )}
                <button className="primary full-width">{authMode === 'signin' ? 'Sign in' : 'Create account'}</button>
              </form>
              <p className="modal-switch">
                {authMode === 'signin' ? "Don't have an account? " : "Already have an account? "}
                <button className="text-button" onClick={() => { setAuthMode(authMode === 'signin' ? 'register' : 'signin'); setStatus(''); }}>
                  {authMode === 'signin' ? 'Create one' : 'Sign in'}
                </button>
              </p>
              <p className="status" aria-live="polite" dangerouslySetInnerHTML={{ __html: sanitize(status) }}></p>
            </div>
          </div>
        )}
      </>
    );
  }
  return <main className="app-shell"><nav><div className="brand"><i>●</i> AgriSpace</div><div className="nav-links"><a className="active">Overview</a><a>Farms</a><a>Insights</a><a>Plans</a></div><button className="text-button" onClick={()=>{localStorage.removeItem('agrispace-token');setToken('')}}>Sign out</button></nav><header className="hero"><div><p className="overline">YOUR FARMING SPACE</p><h1>Good morning.</h1><p>Here's the latest picture across your land.</p></div><button className="primary" onClick={addDemoFarm}>Add a farm <span>＋</span></button></header><div className="source-note"><span className="pulse"></span><b>{climate?.simulated ? 'Demo data' : 'Live source'}</b><span>·</span> {climate?.source ?? 'Select a farm to load observations'}</div><section className="metrics"><article><small>Farms</small><strong>{farms.length}</strong><span>in your workspace</span></article><article><small>Land managed</small><strong>{totalArea.toFixed(2)} <em>ha</em></strong><span>mapped boundary area</span></article><article><small>Latest rainfall</small><strong>{latest ? `${latest.rainfall_mm}` : '—'} <em>mm</em></strong><span>{latest ? latest.date : 'waiting for a farm'}</span></article><article><small>Soil moisture</small><strong>{latest ? `${latest.soil_moisture_pct}` : '—'} <em>%</em></strong><span>simulated estimate</span></article></section><section className="content-grid"><article className="surface farms-panel"><div className="section-heading"><div><p className="overline">FARM PORTFOLIO</p><h2>Your places</h2></div><button className="text-button">View all</button></div>{farms.length ? <div className="farm-list">{farms.map(farm=><button className={`farm-row ${selected?.id===farm.id?'selected':''}`} onClick={()=>setSelected(farm)} key={farm.id}><span className="farm-icon">⌁</span><span><b>{farm.name}</b><small>{farm.current_crop ?? 'No active crop'} · {farm.area_hectares} ha</small></span><span className="chevron">›</span></button>)}</div> : <div className="empty"><span>⌁</span><h3>Begin with your first farm</h3><p>Map a boundary to organise observations and make plans around a specific place.</p><button className="primary" onClick={addDemoFarm}>Add demo farm</button></div>}</article><article className="surface conditions"><div className="section-heading"><div><p className="overline">CONDITIONS</p><h2>{selected?.name ?? 'Select a farm'}</h2></div><span className="tag">{climate?.simulated ? 'SIMULATED' : 'CURRENT'}</span></div>{latest ? <><div className="temperature"><strong>{latest.temperature_c}°</strong><span>Air temperature<br/><small>{latest.date}</small></span></div><div className="chart" aria-label="Rainfall trend">{climate?.data.map((point,index)=><span key={point.date} title={`${point.date}: ${point.rainfall_mm} mm`} style={{height:`${Math.max(10,point.rainfall_mm*7)}%`, opacity: .35 + index / (climate.data.length*1.5)}} />)}</div><div className="condition-footer"><span>Rainfall <b>{latest.rainfall_mm} mm</b></span><span>Moisture <b>{latest.soil_moisture_pct}%</b></span></div></> : <p className="muted">Choose a farm to see its data source and latest conditions.</p>}</article></section><section className="surface recommendation"><div><p className="overline">SEASONAL NUDGE</p><h2>Rotation planning is ready when you are.</h2><p>Explore crop choices with transparent scoring and clear limitations, based on your water availability, soil, and season.</p></div><button className="secondary">Explore plans <span>→</span></button></section><p className="status" aria-live="polite">{status}</p></main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
