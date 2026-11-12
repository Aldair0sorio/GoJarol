import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { X, Award, Sparkles, LogOut, CheckCircle2, UserCheck } from 'lucide-react';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenAuth: () => void;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose, onOpenAuth }) => {
  const { user, role, switchRole, logout, isAuthenticated } = useAuth();
  const [highContrast, setHighContrast] = useState(false);

  if (!isOpen) return null;

  const medals = [
    {
      title: 'Primer Reto Resuelto',
      desc: 'Completaste tu primer ejercicio guiado con Jarol.',
      icon: '🥇',
      unlocked: true,
    },
    {
      title: 'Racha de 4 Días',
      desc: 'Constancia diaria estudiando matemáticas.',
      icon: '🔥',
      unlocked: true,
    },
    {
      title: 'Orgullo Jarocho',
      desc: 'Resolviste el problema de las rebanadas de jícama.',
      icon: '🌴',
      unlocked: true,
    },
    {
      title: 'Maestro de Denominadores',
      desc: 'Domina la suma con diferente denominador.',
      icon: '🧠',
      unlocked: false,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-sm w-full max-h-[90vh] overflow-y-auto border border-[#E8E5DC] shadow-2xl flex flex-col animate-scaleUp">
        {/* Header */}
        <div className="sticky top-0 bg-[#F7F5EF] p-4 pb-2 border-b border-[#E8E5DC] flex items-center justify-between z-10">
          <h2 className="font-display font-extrabold text-base text-[#0A1D2C]">
            Mi Perfil y Logros
          </h2>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-3.5">
          {/* Tarjeta de Usuario */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex items-center gap-3">
            <img
              src={user.avatarUrl}
              alt={user.name}
              className="w-14 h-14 rounded-full object-cover ring-2 ring-[#126B73]/20"
            />
            <div className="flex-1 min-w-0">
              <span className="text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
                {role === 'student' ? 'Estudiante' : 'Docente'}
              </span>
              <h3 className="font-display font-bold text-sm text-[#0A1D2C] mt-1 truncate">
                {user.name}
              </h3>
              {user.email && (
                <div className="flex items-center gap-1 text-[11px] text-[#596B72] truncate my-0.5">
                  <svg className="w-3 h-3 shrink-0" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                    <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.27 21.41 7.34 24 12 24z"/>
                    <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.17 0 9.97 0 12s.45 3.83 1.25 5.42l4.03-3.15z"/>
                    <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.27 2.59 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                  </svg>
                  <span className="truncate">{user.email}</span>
                </div>
              )}
              <p className="text-xs text-[#596B72] truncate">
                {user.grade ? `${user.grade} · ` : ''}{user.school}
              </p>
            </div>
          </div>

          {/* Estadísticas de Logros */}
          {role === 'student' && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-1.5 px-1">
                <Award className="w-4 h-4 text-[#E4AA50]" />
                <span className="font-display font-bold text-xs text-[#0A1D2C]">
                  Medallas de Aprendizaje
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {medals.map((m, idx) => (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-xl border flex flex-col gap-1 ${
                      m.unlocked
                        ? 'bg-white border-[#E8E5DC] shadow-2xs'
                        : 'bg-white/60 border-dashed border-[#BEC8CA] opacity-60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xl">{m.icon}</span>
                      {m.unlocked && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      )}
                    </div>
                    <span className="font-display font-bold text-xs text-[#0A1D2C] leading-snug">
                      {m.title}
                    </span>
                    <p className="text-[10px] text-[#596B72] leading-tight">
                      {m.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Accesibilidad y Preferencias */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2">
            <span className="font-display font-bold text-xs text-[#0A1D2C]">
              Accesibilidad (WCAG AA)
            </span>
            <div className="flex items-center justify-between text-xs text-[#596B72]">
              <span>Contraste alto y texto grande</span>
              <button
                onClick={() => setHighContrast(!highContrast)}
                className={`w-9 h-5 rounded-full p-0.5 transition-colors cursor-pointer ${
                  highContrast ? 'bg-[#126B73]' : 'bg-slate-300'
                }`}
              >
                <div
                  className={`w-4 h-4 rounded-full bg-white transition-transform ${
                    highContrast ? 'translate-x-4' : 'translate-x-0'
                  }`}
                ></div>
              </button>
            </div>
          </div>

          {/* Acciones de Cuenta */}
          <div className="flex flex-col gap-2 pt-1">
            <button
              onClick={() => {
                onClose();
                onOpenAuth();
              }}
              className="w-full py-2.5 rounded-full border border-[#126B73] text-[#126B73] font-display font-bold text-xs flex items-center justify-center gap-1.5 hover:bg-[#DCEFEB]/40 transition-colors cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Cambiar o registrar otra cuenta</span>
            </button>

            <button
              onClick={() => {
                switchRole(role === 'student' ? 'teacher' : 'student');
                onClose();
              }}
              className="w-full py-2.5 rounded-full bg-[#F7F5EF] text-[#596B72] hover:text-[#0A1D2C] font-display font-semibold text-xs flex items-center justify-center gap-1.5 border border-[#E8E5DC] cursor-pointer"
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Cambiar a rol {role === 'student' ? 'Docente' : 'Estudiante'}</span>
            </button>

            {isAuthenticated && (
              <button
                onClick={() => {
                  logout();
                  onClose();
                  onOpenAuth();
                }}
                className="w-full py-2.5 rounded-full bg-red-50 hover:bg-red-100 text-red-600 font-display font-bold text-xs flex items-center justify-center gap-1.5 border border-red-200 transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Cerrar sesión</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
