import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';

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
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  useEffect(() => {
    if (!clientId) return;
    let active = true;
    const init = () => {
      if (!active || !container.current || !window.google?.accounts.id) return false;
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
      window.google.accounts.id.renderButton(container.current, { type: 'standard', theme: 'outline', size: 'large', text: 'continue_with', width: Math.min(container.current.clientWidth, 340) });
      setUnavailable(false); return true;
    };
    // GIS may arrive after React; retry for a bounded period, never simulate success.
    let attempts = 0;
    const timer = window.setInterval(() => {
      if (init()) clearInterval(timer);
      else if (++attempts >= 20) { clearInterval(timer); if (active) setUnavailable(true); }
    }, 250);
    init();
    return () => { active = false; clearInterval(timer); };
  }, [clientId, role, nivel, grado, navigate]);
  if (!clientId) return null;
  return <div className="mt-6 border-t border-subtle pt-5">
    <div ref={container} className={`min-h-11 overflow-hidden ${loading ? 'pointer-events-none opacity-60' : ''}`} inert={loading} aria-busy={loading}/>
    {loading && <p role="status" className="mt-2 text-sm text-muted">Verificando tu identidad…</p>}
    {unavailable && <p role="status" className="text-sm text-muted">Google no está disponible ahora. Puedes usar tu usuario y contraseña.</p>}
    {error && <p role="alert" className="mt-2 text-sm text-red-800">{error}</p>}
  </div>;
}
