import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiService, getAuthConfig, resolveGoogleClientId } from '../../services/api';
import { defaultPathForRole } from '../../routing';
import { inputClass, primaryClass, linkClass } from './AuthLayout';

interface GoogleIdentityApi {
  initialize: (options: { client_id: string; callback: (response: { credential?: string }) => void; auto_select: boolean }) => void;
  renderButton: (element: HTMLElement, options: Record<string, unknown>) => void;
}
declare global { interface Window { google?: { accounts: { id: GoogleIdentityApi } } } }

export function GoogleSignInButton({ role = 'student', nivel = 'secundaria', grado = 1, askRoleIfNew = false }: {
  role?: 'student' | 'teacher'; nivel?: 'secundaria' | 'bachillerato'; grado?: number; askRoleIfNew?: boolean;
}) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const container = useRef<HTMLDivElement>(null);
  const busy = useRef(false);
  const optionsRef = useRef({ role, nivel, grado, askRoleIfNew });
  optionsRef.current = { role, nivel, grado, askRoleIfNew };

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [unavailable, setUnavailable] = useState(false);
  const [clientId, setClientId] = useState<string | null>(null);
  const [checkingConfig, setCheckingConfig] = useState(true);

  const [pendingCredential, setPendingCredential] = useState<string | null>(null);
  const [pendingProfile, setPendingProfile] = useState<{ email?: string; name?: string } | null>(null);
  const [chosenRole, setChosenRole] = useState<'student' | 'teacher'>('student');
  const [chosenNivel, setChosenNivel] = useState<'secundaria' | 'bachillerato'>('secundaria');
  const [chosenGrado, setChosenGrado] = useState(1);

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
    if (!clientId || pendingCredential) return;
    let active = true;
    const init = () => {
      if (!active || !container.current || !window.google?.accounts.id) return false;
      try {
        window.google.accounts.id.initialize({
          client_id: clientId,
          auto_select: false,
          callback: async response => {
            if (!active || busy.current || !response.credential) return;
            const currentOpts = optionsRef.current;
            busy.current = true; setLoading(true); setError('');
            try {
              const result = await apiService.loginWithGoogle(
                currentOpts.askRoleIfNew
                  ? { credential: response.credential, requireRole: true }
                  : { credential: response.credential, role: currentOpts.role, nivel: currentOpts.nivel, grado: currentOpts.grado },
              );
              if (!active) return;
              if (result.needsRole) {
                setPendingCredential(response.credential);
                setPendingProfile(result.pendingProfile || null);
                return;
              }
              if (!result.success || !result.user || !result.token) {
                setError(result.error || 'No pudimos verificar tu identidad.');
                return;
              }
              login(result.user, result.token);
              localStorage.setItem('jarol_is_google', 'true');
              navigate(defaultPathForRole(result.user.role), { replace: true });
            } catch {
              if (active) setError('No se pudo iniciar sesión con Google.');
            } finally {
              busy.current = false;
              if (active) setLoading(false);
            }
          },
        });
        container.current.replaceChildren();
        window.google.accounts.id.renderButton(container.current, {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          width: Math.max(220, Math.min(container.current.clientWidth || 320, 340)),
        });
        setUnavailable(false);
        return true;
      } catch {
        setUnavailable(true);
        return false;
      }
    };
    // GIS may arrive after React; retry for a bounded period, never simulate success.
    let attempts = 0;
    if (init()) return () => { active = false; };
    const timer = window.setInterval(() => {
      if (init()) clearInterval(timer);
      else if (++attempts >= 20) { clearInterval(timer); if (active) setUnavailable(true); }
    }, 250);
    return () => { active = false; clearInterval(timer); };
  }, [clientId, pendingCredential, navigate, login]);

  const completeGoogleRegistration = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!pendingCredential || busy.current) return;
    busy.current = true; setLoading(true); setError('');
    try {
      const result = await apiService.loginWithGoogle({
        credential: pendingCredential,
        role: chosenRole,
        ...(chosenRole === 'student' ? { nivel: chosenNivel, grado: chosenGrado } : {}),
      });
      if (!result.success || !result.user || !result.token) {
        setError(result.error || 'No pudimos completar tu registro con Google.');
        setPendingCredential(null);
        setPendingProfile(null);
        return;
      }
      login(result.user, result.token);
      localStorage.setItem('jarol_is_google', 'true');
      navigate(defaultPathForRole(result.user.role), { replace: true });
    } catch {
      setError('No se pudo completar tu registro con Google.');
    } finally {
      busy.current = false;
      setLoading(false);
    }
  };

  if (pendingCredential) {
    return (
      <form onSubmit={completeGoogleRegistration} className="mt-6 rounded-2xl border border-subtle bg-canvas p-4 space-y-4">
        <div>
          <p className="text-sm font-bold text-ink">
            ¡Hola{pendingProfile?.name ? `, ${pendingProfile.name}` : ''}! Completa tu cuenta con Google
          </p>
          <p className="mt-1 text-xs text-muted">
            Es la primera vez que usas este correo{pendingProfile?.email ? ` (${pendingProfile.email})` : ''}. Elige cómo vas a entrar a Go Jarol:
          </p>
        </div>

        <fieldset disabled={loading} className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {(['student', 'teacher'] as const).map(value => (
              <label
                key={value}
                className={`flex min-h-12 cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium ${
                  chosenRole === value ? 'border-primary bg-primary-light' : 'border-subtle bg-white'
                }`}
              >
                <input
                  type="radio"
                  name="google-role"
                  value={value}
                  checked={chosenRole === value}
                  onChange={() => setChosenRole(value)}
                  className="accent-primary"
                />
                {value === 'student' ? 'Soy Estudiante' : 'Soy Docente'}
              </label>
            ))}
          </div>

          {chosenRole === 'student' && (
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-xs font-semibold">
                Nivel escolar
                <select
                  value={chosenNivel}
                  onChange={e => { setChosenNivel(e.target.value as 'secundaria' | 'bachillerato'); setChosenGrado(1); }}
                  className={inputClass}
                >
                  <option value="secundaria">Secundaria</option>
                  <option value="bachillerato">Bachillerato</option>
                </select>
              </label>
              <label className="block text-xs font-semibold">
                {chosenNivel === 'secundaria' ? 'Año escolar' : 'Semestre'}
                <select
                  value={chosenGrado}
                  onChange={e => setChosenGrado(Number(e.target.value))}
                  className={inputClass}
                >
                  {Array.from({ length: chosenNivel === 'secundaria' ? 3 : 6 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {chosenNivel === 'secundaria' ? ['Primero', 'Segundo', 'Tercero'][i] : `${i + 1}° semestre`}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}

          {error && <p role="alert" className="text-sm text-red-800">{error}</p>}

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <button type="submit" disabled={loading} className={primaryClass}>
              {loading ? 'Creando cuenta…' : `Entrar como ${chosenRole === 'teacher' ? 'Docente' : 'Estudiante'}`}
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => { setPendingCredential(null); setPendingProfile(null); setError(''); }}
              className={`${linkClass} justify-center px-3 text-sm`}
            >
              Cancelar
            </button>
          </div>
        </fieldset>
      </form>
    );
  }

  return <div className="mt-6 border-t border-subtle pt-5">
    <p className="mb-3 text-sm font-semibold text-ink">Continuar con Google</p>
    {clientId && <div ref={container} className={`min-h-11 overflow-hidden ${loading ? 'pointer-events-none opacity-60' : ''}`} inert={loading} aria-busy={loading}/>}
    {checkingConfig && <p role="status" className="text-sm text-muted">Consultando disponibilidad de Google…</p>}
    {loading && <p role="status" className="mt-2 text-sm text-muted">Verificando tu identidad…</p>}
    {unavailable && <p role="status" className="text-sm text-muted">Google no está disponible ahora. Puedes usar tu usuario y contraseña.</p>}
    {error && <p role="alert" className="mt-2 text-sm text-red-800">{error}</p>}
  </div>;
}
