import { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import { AuthLayout, inputClass, linkClass, primaryClass } from '../../components/auth/AuthLayout';
import { PasswordField } from '../../components/auth/PasswordField';
import { GoogleSignInButton } from '../../components/auth/GoogleSignInButton';

export function LoginPage() {
  const { login } = useAuth(); const navigate = useNavigate(); const sending = useRef(false);
  const [identifier, setIdentifier] = useState(''); const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  return <AuthLayout title="Qué gusto verte" intro="Inicia sesión y continúa aprendiendo con Jarol.">
    <form aria-busy={busy} onSubmit={async event => {
      event.preventDefault(); if (sending.current) return; sending.current = true; setBusy(true); setError('');
      try {
        const result = await apiService.login({ username: identifier, password });
        if (result.success && result.user && result.token) { login(result.user, result.token); navigate('/chat', { replace: true }); }
        else { setError(result.error || 'Revisa tus datos.'); }
      } catch { setError('No pudimos iniciar sesión. Inténtalo de nuevo.'); }
      finally { sending.current = false; setBusy(false); }
    }}>
      <fieldset disabled={busy} className="space-y-5">
        <label className="block text-sm font-semibold">Correo o nombre de usuario<input required autoComplete="username" maxLength={254} value={identifier} onChange={e => setIdentifier(e.target.value)} className={inputClass}/></label>
        <PasswordField id="login-password" label="Contraseña" value={password} onChange={setPassword}/>
        <div className="text-right"><Link to="/recuperar-contrasena" className={`${linkClass} text-sm`}>¿Olvidaste tu contraseña?</Link></div>
        {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-900">{error}</p>}
        <button className={primaryClass}>{busy ? 'Iniciando sesión…' : 'Iniciar sesión'}</button>
      </fieldset>
    </form>
    <GoogleSignInButton askRoleIfNew/>
    <p className="mt-6 text-sm text-muted">¿Primera vez por aquí? <Link to="/registro" className={linkClass}>Crear cuenta</Link></p>
  </AuthLayout>;
}
