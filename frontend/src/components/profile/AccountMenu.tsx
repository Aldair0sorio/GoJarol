import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export function AccountMenu({ onOpenProfile }: { onOpenProfile: () => void }) {
  const { user, logout } = useAuth();
  const ref = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const closeOutside = (event: PointerEvent) => {
      if (ref.current && event.target instanceof Node && !ref.current.contains(event.target)) ref.current.open = false;
    };
    document.addEventListener('pointerdown', closeOutside);
    return () => document.removeEventListener('pointerdown', closeOutside);
  }, []);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const initials = user.name.trim().split(/\s+/).slice(0, 2).map(word => word[0]).join('').toUpperCase();
  return <details ref={ref} className="relative" onKeyDown={event => {
    if (event.key === 'Escape' && ref.current) { ref.current.open = false; ref.current.querySelector('summary')?.focus(); }
  }}>
    <summary className="flex min-h-11 max-w-48 cursor-pointer list-none items-center gap-2 rounded-xl px-2 text-[#0A1D2C] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#126B73]" aria-label={`Cuenta de ${user.name}`}>
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#DCEFEB] font-bold text-[#126B73]" aria-hidden="true">{user.avatarUrl && !user.avatarUrl.startsWith('/mascot/') ? <img src={user.avatarUrl} alt="" className="h-9 w-9 rounded-full object-cover"/> : initials || 'J'}</span>
      <span className="truncate text-sm font-semibold">{user.name}</span><span aria-hidden="true">⌄</span>
    </summary>
    <div className="absolute right-0 z-50 mt-2 w-56 max-w-[85vw] rounded-xl border border-[#E8E5DC] bg-white p-2 shadow-lg">
      <button className="min-h-11 w-full rounded-lg px-3 text-left text-sm hover:bg-[#F7F5EF]" onClick={() => { if(ref.current) ref.current.open=false; onOpenProfile(); }}>Mi perfil</button>
      <button disabled={busy} className="min-h-11 w-full rounded-lg px-3 text-left text-sm text-[#126B73] hover:bg-[#F7F5EF] disabled:opacity-50" onClick={async () => {
        setBusy(true); setError(''); try { await logout(); } catch { setError('No se pudo cerrar la sesión. Intenta de nuevo.'); } finally { setBusy(false); }
      }}>{busy ? 'Cerrando sesión…' : 'Cerrar sesión'}</button>
      {error && <p role="alert" className="p-2 text-sm text-red-800">{error}</p>}
    </div>
  </details>;
}
