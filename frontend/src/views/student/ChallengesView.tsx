import React, { useEffect, useState } from 'react';
import type { Subject } from '../../types/curriculum';
import { apiService } from '../../services/api';
import { Calculator, Variable, Triangle, BookOpen, Landmark, Microscope, ArrowRight, Lock } from 'lucide-react';

interface ChallengesViewProps {
  onStartTopic: (topicName: string) => void;
}

export const ChallengesView: React.FC<ChallengesViewProps> = ({ onStartTopic }) => {
  const [subjects, setSubjects] = useState<Subject[]>([]);

  useEffect(() => {
    apiService.getSubjects().then(setSubjects);
  }, []);

  const getIcon = (name: string) => {
    switch (name) {
      case 'Calculator': return <Calculator className="w-5 h-5 text-white" />;
      case 'Variable': return <Variable className="w-5 h-5 text-white" />;
      case 'Triangle': return <Triangle className="w-5 h-5 text-white" />;
      case 'BookOpen': return <BookOpen className="w-5 h-5 text-white" />;
      case 'Landmark': return <Landmark className="w-5 h-5 text-white" />;
      case 'Microscope': return <Microscope className="w-5 h-5 text-white" />;
      default: return <Calculator className="w-5 h-5 text-white" />;
    }
  };

  return (
    <div className="flex flex-col flex-1 px-4 py-3 pb-24">
      {/* Header */}
      <div className="mb-4">
        <h1 className="font-display font-extrabold text-xl text-[#0A1D2C]">
          Retos por Materia
        </h1>
        <p className="text-xs text-[#596B72]">
          Prueba tus conocimientos con ejercicios interactivos y retroalimentación de Jarol.
        </p>
      </div>

      {/* Grid de Materias */}
      <div className="flex flex-col gap-3">
        {subjects.map((sub) => (
          <div
            key={sub.id}
            className={`p-4 rounded-2xl border transition-all ${
              sub.isAvailable
                ? 'bg-white border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]'
                : 'bg-white/60 border-dashed border-[#BEC8CA] opacity-75'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shadow-xs"
                  style={{ backgroundColor: sub.color }}
                >
                  {getIcon(sub.iconName)}
                </div>

                <div>
                  <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                    {sub.name}
                  </h3>
                  <span className="text-[11px] font-medium text-[#596B72]">
                    {sub.isAvailable ? `${sub.topics.length} temas disponibles` : 'Plan de estudios SEP'}
                  </span>
                </div>
              </div>

              {!sub.isAvailable && (
                <span className="inline-flex items-center gap-1 text-[10px] font-display font-bold px-2 py-0.5 rounded-full bg-slate-100 text-[#596B72] border border-slate-200">
                  <Lock className="w-2.5 h-2.5" />
                  Próximamente
                </span>
              )}
            </div>

            {/* Temas si están disponibles */}
            {sub.isAvailable && sub.topics.length > 0 && (
              <div className="mt-3 pt-3 border-t border-[#E8E5DC] flex flex-col gap-2">
                {sub.topics.map((top) => (
                  <div
                    key={top.id}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-[#F7F5EF] hover:bg-[#DCEFEB]/60 transition-colors"
                  >
                    <div className="min-w-0 pr-2">
                      <span className="font-display font-bold text-xs text-[#0A1D2C] block truncate">
                        {top.name}
                      </span>
                      <p className="text-[11px] text-[#596B72] line-clamp-1">
                        {top.description}
                      </p>
                    </div>

                    <button
                      onClick={() => onStartTopic(top.name)}
                      className="shrink-0 px-3 py-1.5 rounded-full bg-[#126B73] text-white font-display font-bold text-[11px] flex items-center gap-1 shadow-[0_2px_0_#005158] active:translate-y-0.5 active:shadow-none transition-all cursor-pointer"
                    >
                      <span>Practicar</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
