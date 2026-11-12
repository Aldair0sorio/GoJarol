import { useEffect, useState } from 'react';
import type { BackendProfile } from '../types/auth';
import { getProfile, saveProfile, profileToUser } from '../services/api';
import { STATES } from '../data/states';
import { useAuth } from '../context/AuthContext';

export function ProfileView({ onBack }: { onBack: () => void }) {
  const { updateUser, logout } = useAuth();
  const [profile, setProfile] = useState<BackendProfile | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true); setError('');
    try { setProfile(await getProfile()); } catch { setError('No pudimos cargar tu perfil. Comprueba tu conexión e intenta de nuevo.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { document.getElementById('profile-heading')?.focus(); void load(); }, []);
  const fieldClass = 'mt-1 block min-h-11 w-full min-w-0 rounded-xl border border-[#D8E2DC] bg-white px-3 py-2 text-[#0A1D2C] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#126B73] disabled:bg-[#F7F5EF]';
  return <section aria-labelledby="profile-heading" className="mx-auto w-full max-w-3xl min-w-0 px-4 py-6 pb-28 sm:px-8 sm:py-10">
    <button onClick={onBack} className="mb-5 min-h-11 text-sm font-semibold text-[#126B73]">← Volver</button>
    <p className="text-xs font-bold uppercase tracking-widest text-[#126B73]">Tu cuenta</p>
    <h1 id="profile-heading" tabIndex={-1} className="mt-2 font-display text-3xl font-bold text-[#0A1D2C]">Mi perfil</h1>
    <p className="mt-2 text-sm text-[#596B72]">Tus datos, listos para seguir aprendiendo con Jarol.</p>
    {loading && <p role="status" className="py-8">Cargando tu información…</p>}
    {error && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-900">{error}</p>}
    {!loading && !profile && <button onClick={() => void load()} className="mt-4 min-h-11 rounded-xl bg-[#126B73] px-5 text-white">Volver a intentar</button>}
    {profile && !loading && <form className="mt-8" aria-busy={busy} onSubmit={async event => {
      event.preventDefault(); setBusy(true); setError(''); setNotice('');
      try {
        const data = await saveProfile({ first_name: profile.first_name, last_name: profile.last_name, alias: profile.alias, estado: profile.estado,
          ...(profile.rol === 'estudiante' ? { nivel: profile.nivel, grado: profile.grado } : {}) });
        setProfile(data); updateUser(profileToUser(data)); setNotice('Tus cambios se guardaron.');
      } catch (error) { setError(error instanceof Error ? error.message : 'No se pudieron guardar los cambios.'); }
      finally { setBusy(false); }
    }}>
      <fieldset disabled={busy} className="border-t border-[#E8E5DC] pt-5">
        <legend className="pr-4 font-display text-lg font-bold text-[#0A1D2C]">Información personal</legend>
        <div className="grid min-w-0 gap-5 sm:grid-cols-2">
          <label className="text-sm font-medium">Nombre(s)<input autoComplete="given-name" maxLength={150} value={profile.first_name} onChange={e => setProfile({ ...profile, first_name: e.target.value })} className={fieldClass}/></label>
          <label className="text-sm font-medium">Apellidos<input autoComplete="family-name" maxLength={150} value={profile.last_name} onChange={e => setProfile({ ...profile, last_name: e.target.value })} className={fieldClass}/></label>
          <label className="text-sm font-medium">Nombre para Jarol<input maxLength={50} value={profile.alias} onChange={e => setProfile({ ...profile, alias: e.target.value })} className={fieldClass}/></label>
          <label className="text-sm font-medium">Usuario<input value={profile.username} readOnly className={fieldClass}/></label>
          <label className="text-sm font-medium sm:col-span-2">Correo electrónico<input type="email" value={profile.email} readOnly className={fieldClass}/><span className="mt-1 block text-xs text-[#596B72]">El usuario y el correo no se editan desde esta sección.</span></label>
          <label className="text-sm font-medium">Estado de residencia<select value={profile.estado} className={fieldClass} onChange={e => setProfile({ ...profile, estado: e.target.value })}><option value="">Sin registrar</option>{STATES.map(([code, name]) => <option key={code} value={code}>{name}</option>)}</select></label>
          <p className="text-sm"><span className="block text-[#596B72]">Rol</span><span>{{ estudiante: 'Estudiante', docente: 'Docente', admin: 'Administrador' }[profile.rol]}</span></p>
        </div>
      </fieldset>
      <fieldset disabled={busy} className="mt-8 border-t border-[#E8E5DC] pt-5">
        <legend className="pr-4 font-display text-lg font-bold">Información académica</legend>
        {profile.rol === 'estudiante' ? <div className="grid gap-5 sm:grid-cols-2">
          <label className="text-sm font-medium">Nivel escolar<select required value={profile.nivel} className={fieldClass} onChange={e => setProfile({ ...profile, nivel: e.target.value as BackendProfile['nivel'], grado: null })}><option value="" disabled>Selecciona tu nivel</option><option value="secundaria">Secundaria</option><option value="bachillerato">Bachillerato</option></select></label>
          <label className="text-sm font-medium">{profile.nivel === 'bachillerato' ? 'Semestre' : 'Año escolar'}<select required value={profile.grado ?? ''} className={fieldClass} onChange={e => setProfile({ ...profile, grado: Number(e.target.value) })}><option value="" disabled>Selecciona una opción</option>{Array.from({ length: profile.nivel === 'bachillerato' ? 6 : 3 }, (_, i) => <option key={i} value={i+1}>{i+1}°</option>)}</select></label>
        </div> : <p className="text-sm text-[#596B72]">Los datos de tu rol se administran desde la institución.</p>}
      </fieldset>
      <div className="mt-6 flex flex-wrap items-center gap-4"><button disabled={busy} className="min-h-11 rounded-xl bg-[#126B73] px-5 font-semibold text-white hover:bg-[#005158] disabled:opacity-50">{busy ? 'Guardando…' : 'Guardar cambios'}</button><p role="status" className="text-sm text-[#126B73]">{notice}</p></div>
    </form>}
    <section className="mt-8 border-t border-[#E8E5DC] pt-5" aria-labelledby="security-heading"><h2 id="security-heading" className="font-display text-lg font-bold">Seguridad</h2><p className="mt-2 text-sm text-[#596B72]">El cambio y la recuperación de contraseña estarán disponibles en una próxima actualización.</p></section>
    <section className="mt-8 border-t border-[#E8E5DC] pt-5" aria-labelledby="session-heading"><h2 id="session-heading" className="font-display text-lg font-bold">Sesión</h2><button disabled={busy} className="mt-2 min-h-11 font-semibold text-[#126B73]" onClick={async () => { setBusy(true); try { await logout(); } catch { setError('No se pudo cerrar la sesión. Intenta de nuevo.'); } finally { setBusy(false); } }}>Cerrar sesión</button></section>
  </section>;
}
