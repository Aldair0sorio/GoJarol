import React from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  MessageSquareText,
  Target,
  Trophy,
  Users2,
  TrendingUp,
  LayoutDashboard,
  GraduationCap,
} from 'lucide-react';

interface BottomNavProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentTab, onTabChange }) => {
  const { role } = useAuth();

  const studentTabs = [
    { id: 'chat', label: 'Jarol', icon: MessageSquareText },
    { id: 'retos', label: 'Retos', icon: Target },
    { id: 'ligas', label: 'Ligas', icon: Trophy },
    { id: 'clases', label: 'Clases', icon: Users2 },
    { id: 'progreso', label: 'Progreso', icon: TrendingUp },
  ];

  const teacherTabs = [
    { id: 'panel', label: 'Panel', icon: LayoutDashboard },
    { id: 'clases', label: 'Clases', icon: Users2 },
    { id: 'alumnos', label: 'Alumnos', icon: GraduationCap },
  ];

  const tabs = role === 'student' ? studentTabs : teacherTabs;

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-lg border-t border-[#E8E5DC] pb-safe px-3 py-1 shadow-[0_-4px_16px_rgba(10,29,44,0.04)]">
      <div className="max-w-md mx-auto flex items-center justify-around">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center justify-center flex-1 py-1.5 px-1 rounded-xl transition-all active:scale-95 ${
                isActive
                  ? 'text-[#126B73] font-bold'
                  : 'text-[#596B72] hover:text-[#0A1D2C]'
              }`}
            >
              <div
                className={`relative p-1 rounded-full transition-colors ${
                  isActive ? 'bg-[#DCEFEB]' : 'bg-transparent'
                }`}
              >
                <Icon
                  className={`w-5 h-5 ${
                    isActive ? 'stroke-[2.5px] text-[#126B73]' : 'stroke-[1.8px]'
                  }`}
                />
              </div>
              <span
                className={`text-[11px] font-display mt-0.5 tracking-tight ${
                  isActive ? 'font-bold text-[#126B73]' : 'font-medium'
                }`}
              >
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
