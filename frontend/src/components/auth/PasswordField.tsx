import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { inputClass } from './AuthLayout';

export function PasswordField({ id, label, value, onChange, newPassword = false }: {
  id: string; label: string; value: string; onChange: (value: string) => void; newPassword?: boolean;
}) {
  const [visible, setVisible] = useState(false);
  return <div><label htmlFor={id} className="text-sm font-semibold">{label}</label><div className="relative">
    <input id={id} required type={visible ? 'text' : 'password'} autoComplete={newPassword ? 'new-password' : 'current-password'}
      value={value} onChange={event => onChange(event.target.value)} className={`${inputClass} pr-14`}/>
    <button type="button" aria-controls={id} aria-pressed={visible} aria-label={`${visible ? 'Ocultar' : 'Mostrar'} ${label.toLowerCase()}`}
      onClick={() => setVisible(!visible)} className="absolute right-1 top-0 flex h-12 w-12 items-center justify-center rounded-lg text-primary focus-visible:outline-2 focus-visible:outline-primary">
      {visible ? <EyeOff size={20} aria-hidden="true"/> : <Eye size={20} aria-hidden="true"/>}
    </button>
  </div></div>;
}
