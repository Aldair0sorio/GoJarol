import { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import { defaultPathForRole } from '../../routing';
import { AuthLayout, inputClass, primaryClass, linkClass } from '../../components/auth/AuthLayout';
import { PasswordField } from '../../components/auth/PasswordField';
import { GoogleSignInButton } from '../../components/auth/GoogleSignInButton';
import { STATES } from '../../data/states';

export function RegisterPage() {
  const { login } = useAuth(); const navigate = useNavigate(); const sending = useRef(false);
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [fullName, setFullName] = useState(''); const [email, setEmail] = useState(''); const [username, setUsername] = useState('');
  const [nivel, setNivel] = useState<'secundaria' | 'bachillerato'>('secundaria'); const [grado, setGrado] = useState(1);
  const [estado, setEstado] = useState(''); const [password, setPassword] = useState(''); const [confirm, setConfirm] = useState('');
  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  return <AuthLayout title="Empieza con Go Jarol" intro="Crea tu cuenta para empezar a aprender con Jarol.">
    <form aria-busy={busy} onSubmit={async event => {
      event.preventDefault(); if (sending.current) return;
      if (password !== confirm) { setError('Las contraseñas no coinciden.'); return; }
      sending.current = true; setBusy(true); setError('');
      try {
        const result = await apiService.register({ username, fullName, email, password, passwordConfirm: confirm, role, nivel, grado, estado });
        if (result.success && result.user && result.token) {
          login(result.user, result.token);
          navigate(defaultPathForRole(result.user.role), { replace: true });
        } else setError(result.error || 'No se pudo crear tu cuenta.');
      } catch { setError('No pudimos confirmar el registro. Comprueba tu conexión.'); }
      finally { sending.current = false; setBusy(false); }
    }}>
      <fieldset disabled={busy} className="space-y-5">
        <legend className="mb-3 text-sm font-semibold">Quiero aprender o acompañar</legend>
        <div className="mb-6 grid grid-cols-2 gap-2">{(['student', 'teacher'] as const).map(value => <label key={value} className={`flex min-h-12 cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-sm ${role === value ? 'border-primary bg-primary-light' : 'border-subtle'}`}><input type="radio" name="role" value={value} checked={role === value} onChange={() => setRole(value)} className="accent-primary"/>{value === 'student' ? 'Estudiante' : 'Docente'}</label>)}</div>
        <label className="block text-sm font-semibold">Nombre completo<input required autoComplete="name" maxLength={150} value={fullName} onChange={e => setFullName(e.target.value)} className={inputClass}/></label>
        <label className="block text-sm font-semibold">Correo electrónico<input required type="email" autoComplete="email" maxLength={254} value={email} onChange={e => setEmail(e.target.value)} className={inputClass}/></label>
        <label className="block text-sm font-semibold">Nombre de usuario<input required autoComplete="username" maxLength={150} value={username} onChange={e => setUsername(e.target.value)} className={inputClass}/></label>
        {role === 'student' && <>
          <label className="block text-sm font-semibold">Nivel escolar<select value={nivel} onChange={e => { setNivel(e.target.value as typeof nivel); setGrado(1); }} className={inputClass}><option value="secundaria">Secundaria</option><option value="bachillerato">Bachillerato</option></select></label>
          <label className="block text-sm font-semibold">{nivel === 'secundaria' ? 'Año escolar' : 'Semestre'}<select value={grado} onChange={e => setGrado(Number(e.target.value))} className={inputClass}>
            {Array.from({ length: nivel === 'secundaria' ? 3 : 6 }, (_, i) => <option key={i+1} value={i+1}>{nivel === 'secundaria' ? ['Primero', 'Segundo', 'Tercero'][i] : `${i+1}° semestre`}</option>)}
          </select></label>
        </>}
        <label className="block text-sm font-semibold">Estado de residencia<select required autoComplete="address-level1" value={estado} onChange={e => setEstado(e.target.value)} className={inputClass}><option value="" disabled>Selecciona tu estado</option>{STATES.map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select></label>
        <PasswordField id="register-password" label="Contraseña" value={password} onChange={setPassword} newPassword/>
        <p id="password-help" className="text-xs leading-relaxed text-muted">Usa al menos 8 caracteres. Evita contraseñas comunes, solo números o tus datos personales.</p>
        <PasswordField id="register-confirm" label="Confirmar contraseña" value={confirm} onChange={setConfirm} newPassword/>
        {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-900">{error}</p>}
        <button className={primaryClass}>{busy ? 'Creando cuenta…' : 'Crear cuenta'}</button>
      </fieldset>
    </form>
    <GoogleSignInButton role={role} nivel={nivel} grado={grado}/>
    <p className="mt-6 text-sm text-muted">¿Ya tienes cuenta? <Link to="/login" className={linkClass}>Iniciar sesión</Link></p>
  </AuthLayout>;
}
