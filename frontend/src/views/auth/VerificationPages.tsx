import { useRef, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { AuthLayout, inputClass, linkClass, primaryClass } from '../../components/auth/AuthLayout';
import { resendVerification, verifyEmail, VerificationApiError } from '../../services/api';

export function VerificationPendingPage() {
  const { state } = useLocation();
  const [email, setEmail] = useState(typeof state?.email === 'string' ? state.email : '');
  const [busy, setBusy] = useState(false); const sending = useRef(false);
  const [error, setError] = useState(typeof state?.deliveryError === 'string' ? state.deliveryError : '');
  const [message, setMessage] = useState(state?.sent === true ? 'Enviamos tu enlace. Revisa tu bandeja de entrada y la carpeta de spam.' : 'Introduce tu correo para solicitar un enlace de verificación.');
  return <AuthLayout title="Revisa tu correo" intro="Confirma que el correo es tuyo para entrar a Go Jarol. El enlace caduca en 24 horas.">
    <p role="status" className="mb-6 text-sm leading-relaxed text-muted">{message}</p>
    <form aria-busy={busy} onSubmit={async event => {
      event.preventDefault(); if (sending.current) return;
      sending.current = true; setBusy(true); setError(''); setMessage('');
      try { await resendVerification(email); setMessage('Si hay una cuenta pendiente con ese correo, enviamos un enlace. Revisa también spam.'); }
      catch (error) { setError(error instanceof Error ? error.message : 'No se pudo enviar el correo.'); }
      finally { sending.current = false; setBusy(false); }
    }}><fieldset disabled={busy} className="space-y-5"><label className="block text-sm font-semibold">Correo electrónico<input required type="email" autoComplete="email" maxLength={254} value={email} onChange={e => setEmail(e.target.value)} className={inputClass}/></label>
      {error && <p role="alert" className="text-sm text-red-800">{error}</p>}
      <button className={primaryClass}>{busy ? 'Enviando…' : 'Reenviar correo'}</button><p className="text-xs text-muted">Espera un minuto entre envíos. Puedes solicitar hasta cinco por hora.</p></fieldset></form>
    <Link to="/login" className={`${linkClass} mt-5`}>Volver a iniciar sesión</Link>
  </AuthLayout>;
}

export function VerifyEmailPage() {
  const { uid = '', token = '' } = useParams(); const navigate = useNavigate(); const sending = useRef(false);
  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  // An explicit POST avoids consuming tokens in email link scanners or StrictMode effects.
  return <AuthLayout title="Confirma tu correo" intro="Estás a un paso de empezar a aprender con Jarol.">
    <button disabled={busy} className={primaryClass} onClick={async () => {
      if (sending.current) return; sending.current = true; setBusy(true); setError('');
      try { await verifyEmail(uid, token); navigate('/verificacion-exitosa', { replace: true }); }
      catch (error) {
        if (error instanceof VerificationApiError && error.status === 400) navigate('/verificacion-invalida', { replace: true });
        else setError(error instanceof Error ? error.message : 'No se pudo verificar.');
      }
      finally { sending.current = false; setBusy(false); }
    }}>{busy ? 'Confirmando…' : 'Confirmar mi correo'}</button>
    {error && <div className="mt-5"><p role="alert" className="text-sm text-red-800">{error}</p><Link to="/verificacion-pendiente" className={linkClass}>Solicitar un enlace nuevo</Link></div>}
  </AuthLayout>;
}

export function VerificationSuccessPage() {
  return <AuthLayout title="Tu correo está confirmado" intro="Ya puedes iniciar sesión y comenzar una conversación con Jarol."><Link to="/login" className={`${primaryClass} block text-center`}>Iniciar sesión</Link></AuthLayout>;
}

export function VerificationInvalidPage() {
  return <AuthLayout title="Este enlace ya no es válido" intro="Puede haber caducado, haberse usado o haber sido reemplazado por un correo más reciente."><Link to="/verificacion-pendiente" className={`${primaryClass} block text-center`}>Solicitar un enlace nuevo</Link><Link to="/login" className={`${linkClass} mt-4`}>Volver al inicio de sesión</Link></AuthLayout>;
}

export function RecoveryPlaceholderPage() {
  return <AuthLayout title="Recuperar contraseña" intro="La recuperación por correo estará disponible en la siguiente actualización."><p className="text-sm leading-relaxed text-muted">Esta página todavía no envía correos para cambiar contraseñas. Si registraste tu cuenta con Google, usa el botón de Google para entrar.</p><Link to="/login" className={`${linkClass} mt-4 inline-block`}>Volver al inicio de sesión</Link></AuthLayout>;
}
