import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Flame, Sparkles, Award, Target, CheckCircle2, ArrowRight } from 'lucide-react';

interface ProgressViewProps {
  onPracticeTopic: (topicName: string) => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({ onPracticeTopic }) => {
  const { user } = useAuth();

  const level = Math.floor((user.xp || 0) / 100) + 1;
  const currentLevelXp = (user.xp || 0) % 100;

  return (
    <div className="flex flex-col flex-1 px-4 py-3 pb-24">
      {/* Perfil del Alumno Card */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex items-center gap-3 mb-4">
        <div className="relative">
          <img
            src={user.avatarUrl}
            alt={user.name}
            className="w-14 h-14 rounded-full object-cover ring-2 ring-[#126B73]/20"
          />
          <span className="absolute -bottom-1 -right-1 bg-[#126B73] text-white text-[10px] font-display font-bold px-1.5 py-0.2 rounded-full border border-white">
            Nv. {level}
          </span>
        </div>

        <div className="flex-1 min-w-0">
          <h2 className="font-display font-bold text-base text-[#0A1D2C] truncate">
            {user.name}
          </h2>
          <p className="text-xs text-[#596B72] truncate">
            {user.grade}
          </p>
          <span className="text-[11px] text-[#126B73] font-medium block truncate">
            {user.school}
          </span>
        </div>
      </div>

      {/* Gamificación: Racha y XP */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Racha */}
        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 shadow-2xs flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#E4AA50] flex items-center justify-center text-white shadow-xs">
            <Flame className="w-6 h-6 fill-white" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg text-amber-950 block leading-none">
              {user.streakDays || 1} días
            </span>
            <span className="text-[11px] font-medium text-amber-800">
              Racha activa
            </span>
          </div>
        </div>

        {/* Puntos de Experiencia */}
        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50 border border-teal-200 shadow-2xs flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#126B73] flex items-center justify-center text-white shadow-xs">
            <Sparkles className="w-5 h-5 fill-white" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg text-teal-950 block leading-none">
              {user.xp || 0} XP
            </span>
            <span className="text-[11px] font-medium text-teal-800">
              Nivel {level}
            </span>
          </div>
        </div>
      </div>

      {/* Barra de progreso de nivel */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9] mb-4">
        <div className="flex items-center justify-between text-xs font-display font-semibold mb-1.5">
          <span className="text-[#0A1D2C]">Progreso a Nivel {level + 1}</span>
          <span className="text-[#126B73]">{currentLevelXp} / 100 XP</span>
        </div>
        <div className="w-full h-3 bg-[#DCEFEB] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#126B73] rounded-full transition-all duration-500 shadow-xs"
            style={{ width: `${currentLevelXp}%` }}
          ></div>
        </div>
      </div>

      {/* Dominio de Fracciones (Tema Estrella) */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-[#126B73]" />
            <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
              Dominio en Fracciones
            </h3>
          </div>
          <span className="font-display font-bold text-xs text-[#126B73] bg-[#DCEFEB] px-2 py-0.5 rounded-full">
            65% Logrado
          </span>
        </div>

        {/* Competencias */}
        <div className="flex flex-col gap-2 pt-1">
          <div className="flex items-center gap-2 text-xs text-[#0A1D2C]">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Suma de fracciones con igual denominador</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-[#0A1D2C]">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Identificación de partes (numerador y denominador)</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-[#596B72]">
            <div className="w-4 h-4 rounded-full border-2 border-amber-400 shrink-0 flex items-center justify-center text-[10px] text-amber-700 font-bold">
              !
            </div>
            <span>Por reforzar: Suma con diferente denominador</span>
          </div>
        </div>

        {/* Botón de reforzar con Jarol */}
        <button
          onClick={() => onPracticeTopic('Quiero reforzar suma de fracciones con diferente denominador')}
          className="mt-1 w-full py-2.5 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-2 shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all cursor-pointer"
        >
          <Award className="w-4 h-4" />
          <span>Reforzar con Jarol ahora</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
