import React from 'react';
import { AccountMenu } from '../profile/AccountMenu';
import { useAuth } from '../../context/AuthContext';
import { getLeagueForXp } from '../../data/leagues';
import {
  MessageSquareText,
  Target,
  Trophy,
  Users2,
  TrendingUp,
  LayoutDashboard,
  GraduationCap,
  Sparkles,
  Flame,
} from 'lucide-react';

interface SidebarTab {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface DesktopSidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  onOpenProfile: () => void;
}

export const DesktopSidebar: React.FC<DesktopSidebarProps> = ({
  currentTab,
  onTabChange,
  onOpenProfile,
}) => {
  const { user, role } = useAuth();
  const leagueStatus = getLeagueForXp(user.xp || 0);

  const studentTabs: SidebarTab[] = [
    { id: 'chat', label: 'Tutor Jarol', icon: MessageSquareText, badge: 'IA' },
    { id: 'retos', label: 'Retos por Materia', icon: Target },
    { id: 'ligas', label: 'Ligas Veracruz', icon: Trophy, badge: leagueStatus.tier.name },
    { id: 'clases', label: 'Mis Clases', icon: Users2 },
    { id: 'progreso', label: 'Mi Progreso', icon: TrendingUp },
  ];

  const teacherTabs: SidebarTab[] = [
    { id: 'panel', label: 'Panel General', icon: LayoutDashboard },
    { id: 'clases', label: 'Mis Clases', icon: Users2 },
    { id: 'alumnos', label: 'Diagnóstico Alumnos', icon: GraduationCap },
  ];

  const tabs: SidebarTab[] = role === 'student' ? studentTabs : teacherTabs;

  return (
    <aside className="hidden md:flex flex-col w-64 lg:w-72 bg-white border-r border-[#E8E5DC] h-screen sticky top-0 shrink-0 p-4 justify-between z-30 shadow-xs">
      {/* Header del Sidebar: Logo y Mascota */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3 px-2 py-1">
          <div className="relative">
            <img
              src="/mascot/jarol-crab.png"
              alt="Jarol el Profe Cangrejo"
              className="w-11 h-11 object-contain rounded-full bg-[#126B73]/10 ring-2 ring-[#126B73]/20 shadow-xs"
            />
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white ring-1 ring-emerald-600/30"></span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-display font-bold text-xl text-[#0A1D2C] tracking-tight">
                Go Jarol
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-[#E76D55] text-white uppercase tracking-wider">
                Veracruz
              </span>
            </div>
            <p className="text-xs text-[#596B72] font-medium leading-none mt-0.5">
              Aprender a la jarocha
            </p>
          </div>
        </div>

        {/* Indicador de Racha / XP en Desktop */}
        {role === 'student' && (
          <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC]">
            <div className="flex items-center gap-1.5 text-xs font-display font-bold text-amber-700">
              <Flame className="w-4 h-4 text-amber-500 fill-amber-500" />
              <span>{user.streakDays || 1} días de racha</span>
            </div>
            <div className="flex items-center gap-1.5">
              <img
                src={leagueStatus.tier.imageUrl}
                alt={`Liga ${leagueStatus.tier.name}`}
                title={`Liga ${leagueStatus.tier.name}`}
                className="w-5 h-5 object-contain"
              />
              <div className="flex items-center gap-1 text-xs font-display font-extrabold text-[#126B73] bg-[#DCEFEB] px-2 py-0.5 rounded-full">
                <Sparkles className="w-3.5 h-3.5 text-[#E4AA50] fill-[#E4AA50]" />
                <span>{user.xp || 0} XP</span>
              </div>
            </div>
          </div>
        )}

        {/* Navegación Principal */}
        <nav className="flex flex-col gap-1.5 mt-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-display text-sm font-semibold transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#126B73] text-white shadow-[0_3px_0_#005158] translate-y-[-1px]'
                    : 'text-[#596B72] hover:bg-[#F7F5EF] hover:text-[#0A1D2C]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-5 h-5 ${
                      isActive ? 'stroke-[2.5px] text-white' : 'stroke-[2px]'
                    }`}
                  />
                  <span>{tab.label}</span>
                </div>

                {tab.badge && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-[#DCEFEB] text-[#126B73]'
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer del Sidebar: Perfil y Ajustes */}
      <div className="pt-3 border-t border-[#E8E5DC] flex flex-col gap-2">
        <AccountMenu onOpenProfile={onOpenProfile} />
      </div>
    </aside>
  );
};
