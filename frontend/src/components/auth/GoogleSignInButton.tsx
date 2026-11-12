import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiService, getAuthConfig, resolveGoogleClientId } from '../../services/api';

interface GoogleIdentityApi {
  initialize: (options: { client_id: string; callback: (response: { credential?: string }) => void; auto_select: boolean }) => void;
  renderButton: (element: HTMLElement, options: Record<string, unknown>) => void;
}
declare global { interface Window { google?: { accounts: { id: GoogleIdentityApi } } } }

export function GoogleSignInButton({ role = 'student', nivel = 'secundaria', grado = 1 }: {
  role?: 'student' | 'teacher'; nivel?: 'secundaria' | 'bachillerato'; grado?: number;
}) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const container = useRef<HTMLDivElement>(null);
  const busy = useRef(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [unavailable, setUnavailable] = useState(false);
  const [clientId, setClientId] = useState<string | null>(null);
  const [checkingConfig, setCheckingConfig] = useState(true);
  useEffect(() => {
    let active = true;
    getAuthConfig().then(config => {
      if (!active) return;
      const id = resolveGoogleClientId(config, import.meta.env.VITE_GOOGLE_CLIENT_ID);
      setClientId(id); setUnavailable(!id);
    }).catch(() => { if (active) setUnavailable(true); })
      .finally(() => { if (active) setCheckingConfig(false); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (!clientId) return;
    let active = true;
    const init = () => {
      if (!active || !container.current || !window.google?.accounts.id) return false;
      try {
      window.google.accounts.id.initialize({ client_id: clientId, auto_select: false, callback: async response => {
        if (!active || busy.current || !response.credential) return;
        busy.current = true; setLoading(true); setError('');
        try {
          const result = await apiService.loginWithGoogle({ credential: response.credential!, role, nivel, grado });
          if (!active) return;
          if (!result.success || !result.user || !result.token) { setError(result.error || 'No pudimos verificar tu identidad.'); return; }
          login(result.user, result.token); localStorage.setItem('jarol_is_google', 'true'); navigate('/chat', { replace: true });
        } catch { if (active) setError('No se pudo iniciar sesión con Google.'); }
        finally { busy.current = false; if (active) setLoading(false); }
      } });
      container.current.replaceChildren();
      window.google.accounts.id.renderButton(container.current, { type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', width: Math.max(220, Math.min(container.current.clientWidth || 320, 340)) });
      setUnavailable(false); return true;
      } catch { setUnavailable(true); return false; }
    };
    // GIS may arrive after React; retry for a bounded period, never simulate success.
    let attempts = 0;
    if (init()) return () => { active = false; };
    const timer = window.setInterval(() => {
      if (init()) clearInterval(timer);
      else if (++attempts >= 20) { clearInterval(timer); if (active) setUnavailable(true); }
    }, 250);
    return () => { active = false; clearInterval(timer); };
  }, [clientId, role, nivel, grado, navigate]);
  return <div className="mt-6 border-t border-subtle pt-5">
    <p className="mb-3 text-sm font-semibold text-ink">Continuar con Google</p>
    {clientId && <div ref={container} className={`min-h-11 overflow-hidden ${loading ? 'pointer-events-none opacity-60' : ''}`} inert={loading} aria-busy={loading}/>}
    {checkingConfig && <p role="status" className="text-sm text-muted">Consultando disponibilidad de Google…</p>}
    {loading && <p role="status" className="mt-2 text-sm text-muted">Verificando tu identidad…</p>}
    {unavailable && <p role="status" className="text-sm text-muted">Google no está disponible ahora. Puedes usar tu usuario y contraseña.</p>}
    {error && <p role="alert" className="mt-2 text-sm text-red-800">{error}</p>}
  </div>;
}
