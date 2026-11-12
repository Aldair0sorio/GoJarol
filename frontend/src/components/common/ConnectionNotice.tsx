import React from 'react';
import { RotateCcw, WifiOff } from 'lucide-react';

interface ConnectionNoticeProps {
  text: string;
  /** Si existe, todo el aviso es un botón ("Toca para reintentar"). */
  onRetry?: () => void;
  className?: string;
}

/** Aviso de conexión: claro, sin inventar datos. Solo clases de Tailwind locales. */
export const ConnectionNotice: React.FC<ConnectionNoticeProps> = ({ text, onRetry, className = '' }) => {
  const body = (
    <>
      <WifiOff className="w-4 h-4 shrink-0 mt-0.5 text-amber-700" aria-hidden="true" />
      <span className="min-w-0 break-words text-left">{text}</span>
      {onRetry && <RotateCcw className="w-3.5 h-3.5 shrink-0 mt-0.5 text-amber-700" aria-hidden="true" />}
    </>
  );
  const base = `flex items-start gap-2 w-full px-3 py-2.5 rounded-xl border border-amber-300 bg-amber-50 text-xs text-amber-950 ${className}`;

  return onRetry ? (
    <button type="button" onClick={onRetry} role="alert" className={`${base} cursor-pointer hover:bg-amber-100 active:translate-y-[1px]`}>
      {body}
    </button>
  ) : (
    <div role="alert" className={base}>
      {body}
    </div>
  );
};

/** Indicador discreto cuando el navegador reporta que no hay conexión. */
export const OfflineBadge: React.FC = () => (
  <span
    role="status"
    className="inline-flex items-center gap-1 text-[11px] font-display font-bold px-2.5 py-1 rounded-full bg-[#0A1D2C] text-white"
  >
    <WifiOff className="w-3 h-3" aria-hidden="true" />
    Sin conexión
  </span>
);
