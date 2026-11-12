import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Sparkles, GraduationCap, UserCheck, LogIn } from 'lucide-react';

interface AppHeaderProps {
  onOpenAuth?: () => void;
  onOpenProfile?: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({ onOpenAuth, onOpenProfile }) => {
  const { user, role, switchRole } = useAuth();

  return (
    <header className="md:hidden sticky top-0 inset-x-0 z-40 bg-[#F7F5EF]/90 backdrop-blur-md border-b border-[#E8E5DC] px-4 py-2.5">
      <div className="max-w-md mx-auto flex items-center justify-between">
        {/* Brand & Mascot */}
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <img
              src="/mascot/jarol-crab.png"
              alt="Jarol el Cangrejo Tutor"
              className="w-10 h-10 object-contain rounded-full bg-[#126B73]/10 ring-2 ring-[#126B73]/20 shadow-sm"
            />
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white ring-1 ring-emerald-600/30"></span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-display font-bold text-lg text-[#0A1D2C] tracking-tight leading-none">
                Go Jarol
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-[#E76D55] text-white uppercase tracking-wider">
                Veracruz
              </span>
            </div>
            <p className="text-xs text-[#596B72] font-medium leading-tight mt-0.5">
              {role === 'student' ? 'Tutor con IA Pedagógica' : 'Panel de Control Docente'}
            </p>
          </div>
        </div>

        {/* Right Action: XP Badge or Role Switcher */}
        <div className="flex items-center gap-2">
          {role === 'student' ? (
            <button
              onClick={onOpenProfile}
              title="Ver mi perfil y logros"
              className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#DCEFEB] border border-[#126B73]/20 shadow-xs hover:border-[#126B73] transition-colors cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#E4AA50] fill-[#E4AA50]" />
              <span className="font-display font-bold text-xs text-[#126B73]">
                {user.xp || 0} XP
              </span>
            </button>
          ) : (
            <button
              onClick={onOpenProfile}
              title="Ver perfil docente"
              className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#E76D55]/10 border border-[#E76D55]/30 hover:border-[#E76D55] transition-colors cursor-pointer"
            >
              <GraduationCap className="w-3.5 h-3.5 text-[#E76D55]" />
              <span className="font-display font-bold text-xs text-[#E76D55]">
                Docente
              </span>
            </button>
          )}

          {/* Login / Switch Account Button */}
          {onOpenAuth && (
            <button
              onClick={onOpenAuth}
              title="Iniciar sesión o registrar usuario"
              className="flex items-center justify-center p-1.5 rounded-lg bg-white border border-[#E8E5DC] text-[#596B72] hover:text-[#126B73] hover:border-[#126B73] transition-colors shadow-xs active:scale-95"
            >
              <LogIn className="w-4 h-4" />
            </button>
          )}

          {/* Quick Demo Switcher Button */}
          <button
            onClick={() => switchRole(role === 'student' ? 'teacher' : 'student')}
            title="Cambiar perspectiva para demostración"
            className="flex items-center justify-center p-1.5 rounded-lg bg-white border border-[#E8E5DC] text-[#596B72] hover:text-[#126B73] hover:border-[#126B73] transition-colors shadow-xs active:scale-95"
          >
            <UserCheck className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
