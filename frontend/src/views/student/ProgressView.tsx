import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { apiService, type StudentProgressSummary } from '../../services/api';
import { Flame, Sparkles, Award, Target, CheckCircle2, ArrowRight, BookOpen } from 'lucide-react';

interface ProgressViewProps {
  onPracticeTopic: (promptOrTopicName: string) => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({ onPracticeTopic }) => {
  const { user, updateUser } = useAuth();
  const [summary, setSummary] = useState<StudentProgressSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiService
      .getProgress()
      .then((data) => {
        setSummary(data);
        if (data.xp !== undefined && data.xp !== user.xp) {
          updateUser({ xp: data.xp, streakDays: data.streakDays });
        }
      })
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const xp = summary?.xp ?? user.xp ?? 0;
  const streakDays = summary?.streakDays ?? user.streakDays ?? 1;
  const level = Math.floor(xp / 100) + 1;
  const currentLevelXp = xp % 100;

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-3xl lg:max-w-4xl mx-auto w-full">
      {/* Perfil del Alumno Card */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex items-center gap-3 mb-4">
        <div className="relative">
          <img
            src={user.avatarUrl || '/mascot/jarol-crab.png'}
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
          <p className="text-xs text-[#596B72] truncate">{user.grade}</p>
          <span className="text-[11px] text-[#126B73] font-medium block truncate">
            {user.school || 'Veracruz'}
          </span>
        </div>

        {summary && (
          <div className="text-right hidden sm:block">
            <span className="text-xs font-display font-bold text-[#0A1D2C] block">
              {summary.completedCount} retos resueltos
            </span>
            <span className="text-[11px] text-[#596B72]">
              Precisión: {summary.accuracy}%
            </span>
          </div>
        )}
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
              {streakDays} {streakDays === 1 ? 'día' : 'días'}
            </span>
            <span className="text-[11px] font-medium text-amber-800">Racha activa</span>
          </div>
        </div>

        {/* Puntos de Experiencia */}
        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50 border border-teal-200 shadow-2xs flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#126B73] flex items-center justify-center text-white shadow-xs">
            <Sparkles className="w-5 h-5 fill-white" />
          </div>
          <div>
            <span className="font-display font-extrabold text-lg text-teal-950 block leading-none">
              {xp} XP
            </span>
            <span className="text-[11px] font-medium text-teal-800">Nivel {level}</span>
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

      {/* Dominio Real por Tema Curricular */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-[#126B73]" />
            <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
              Dominio por Tema (Evaluación Formativa Real)
            </h3>
          </div>
          {summary && (
            <span className="font-display font-bold text-xs text-[#126B73] bg-[#DCEFEB] px-2.5 py-0.5 rounded-full">
              {summary.completedCount} ejercicios completados
            </span>
          )}
        </div>

        {isLoading ? (
          <div className="py-6 text-center text-xs text-[#596B72]">
            Consultando tu historial de aprendizaje...
          </div>
        ) : (
          <div className="flex flex-col gap-2.5 pt-1">
            {(summary?.topics || []).map((t) => (
              <div
                key={t.topicId}
                className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] flex flex-col gap-2"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    {t.mastery >= 50 ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <BookOpen className="w-4 h-4 text-[#126B73] shrink-0" />
                    )}
                    <div className="min-w-0">
                      <span className="font-display font-bold text-xs text-[#0A1D2C] block truncate">
                        {t.name}
                      </span>
                      <span className="text-[10px] text-[#596B72]">
                        {t.subject} • {t.completedExercises}/{t.totalExercises} ejercicios • Nivel adaptativo {t.difficulty}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        t.status === 'Dominado'
                          ? 'bg-emerald-100 text-emerald-800'
                          : t.status === 'Requiere refuerzo'
                          ? 'bg-amber-100 text-amber-800'
                          : t.status === 'En curso'
                          ? 'bg-[#DCEFEB] text-[#126B73]'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {t.mastery}% • {t.status}
                    </span>

                    <button
                      onClick={() => onPracticeTopic(t.prompt)}
                      className="px-2.5 py-1 rounded-full bg-[#126B73] text-white font-display font-bold text-[10px] flex items-center gap-1 hover:bg-[#0f5960] cursor-pointer"
                    >
                      <span>Practicar</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div className="w-full h-1.5 bg-white rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#126B73] rounded-full transition-all duration-500"
                    style={{ width: `${t.mastery}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Botón general de reforzar con Jarol */}
        <button
          onClick={() =>
            onPracticeTopic('Ponme un ejercicio de fracciones')
          }
          className="mt-1 w-full py-2.5 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-2 shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all cursor-pointer"
        >
          <Award className="w-4 h-4" />
          <span>Continuar entrenando con Jarol</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
