import React, { useEffect, useState } from 'react';
import type { Subject } from '../../types/curriculum';
import { apiService } from '../../services/api';
import {
  Calculator,
  Variable,
  Compass,
  BookOpen,
  Landmark,
  Atom,
  FlaskConical,
  Dna,
  Globe,
  ArrowRight,
  Lock,
} from 'lucide-react';

interface ChallengesViewProps {
  onStartTopic: (promptOrTopicName: string) => void;
}

const COLOR_MAP: Record<string, string> = {
  teal: '#126B73',
  indigo: '#4F46E5',
  amber: '#D97706',
  blue: '#2563EB',
  rose: '#E11D48',
  emerald: '#059669',
  purple: '#7C3AED',
  cyan: '#0891B2',
  green: '#16A34A',
};

export const ChallengesView: React.FC<ChallengesViewProps> = ({ onStartTopic }) => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiService
      .getSubjects()
      .then(setSubjects)
      .finally(() => setIsLoading(false));
  }, []);

  const getIcon = (name: string) => {
    switch (name) {
      case 'Calculator':
        return <Calculator className="w-5 h-5 text-white" />;
      case 'Variable':
        return <Variable className="w-5 h-5 text-white" />;
      case 'Compass':
        return <Compass className="w-5 h-5 text-white" />;
      case 'BookOpen':
        return <BookOpen className="w-5 h-5 text-white" />;
      case 'Landmark':
        return <Landmark className="w-5 h-5 text-white" />;
      case 'Globe':
        return <Globe className="w-5 h-5 text-white" />;
      case 'Atom':
        return <Atom className="w-5 h-5 text-white" />;
      case 'FlaskConical':
        return <FlaskConical className="w-5 h-5 text-white" />;
      case 'Dna':
        return <Dna className="w-5 h-5 text-white" />;
      default:
        return <Calculator className="w-5 h-5 text-white" />;
    }
  };

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-4xl lg:max-w-5xl mx-auto w-full">
      {/* Header */}
      <div className="mb-4">
        <h1 className="font-display font-extrabold text-xl md:text-2xl text-[#0A1D2C]">
          Retos por Materia
        </h1>
        <p className="text-xs md:text-sm text-[#596B72]">
          Elige un tema del catálogo curricular para practicar con ejercicios adaptativos y pistas de Jarol.
        </p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm font-display text-[#596B72]">
          Cargando catálogo curricular desde el servidor...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
          {subjects.map((sub) => {
            const bgHex = COLOR_MAP[sub.color] || sub.color || '#126B73';
            return (
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
                      style={{ backgroundColor: bgHex }}
                    >
                      {getIcon(sub.iconName)}
                    </div>

                    <div>
                      <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                        {sub.name}
                      </h3>
                      <span className="text-[11px] font-medium text-[#596B72]">
                        {sub.isAvailable
                          ? `${sub.topics.filter((t) => t.isAvailable).length} temas activos con IA`
                          : 'Plan de estudios SEP / DGB'}
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
                        className="flex items-center justify-between p-2.5 rounded-xl bg-[#F7F5EF] hover:bg-[#DCEFEB]/60 transition-colors gap-2"
                      >
                        <div className="min-w-0 pr-2 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-display font-bold text-xs text-[#0A1D2C] truncate">
                              {top.name}
                            </span>
                            {top.progressPercent > 0 && (
                              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
                                {top.progressPercent}%
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-[#596B72] line-clamp-1">
                            {top.description}
                          </p>
                        </div>

                        {top.isAvailable ? (
                          <button
                            onClick={() =>
                              onStartTopic(
                                top.prompt || `Explícame ${top.name} y ponme un ejercicio`
                              )
                            }
                            className="shrink-0 px-3 py-1.5 rounded-full bg-[#126B73] text-white font-display font-bold text-[11px] flex items-center gap-1 shadow-[0_2px_0_#005158] active:translate-y-0.5 active:shadow-none transition-all cursor-pointer"
                          >
                            <span>Practicar</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        ) : (
                          <span className="text-[10px] font-semibold text-[#596B72] px-2 py-1">
                            Próximamente
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
