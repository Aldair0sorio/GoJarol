import React, { useState } from 'react';
import type { ClassGroup } from '../../types/curriculum';
import { X, Users2, BookOpen, Bell, ArrowRight, CheckCircle2 } from 'lucide-react';

interface ClassDetailModalProps {
  cls: ClassGroup;
  onClose: () => void;
  onStartExercise?: (topicPrompt: string) => void;
}

export const ClassDetailModal: React.FC<ClassDetailModalProps> = ({
  cls,
  onClose,
  onStartExercise,
}) => {
  const [activeTab, setActiveTab] = useState<'retos' | 'alumnos' | 'avisos'>('retos');
  const classmates = cls.studentsDetail || [];

  const assignedChallenges = [
    {
      title: 'Fracciones Equivalentes y Suma',
      desc: 'Ejercicios adaptativos evaluados simbólicamente con SymPy.',
      prompt: 'Explícame cómo sumar fracciones y ponme un ejercicio',
      xp: '+30 XP',
    },
    {
      title: 'Ecuaciones Lineales de Primer Grado',
      desc: 'Despeje de la incógnita x paso a paso con pistas graduales.',
      prompt: 'Ponme un ejercicio de ecuaciones de primer grado',
      xp: '+30 XP',
    },
    {
      title: 'Comprensión Lectora y Acentuación',
      desc: 'Lecturas originales con identificación de idea principal e inferencias.',
      prompt: 'Dame un reto de comprensión lectora',
      xp: '+30 XP',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border border-[#E8E5DC] shadow-2xl flex flex-col animate-scaleUp">
        {/* Header */}
        <div className="sticky top-0 bg-[#F7F5EF] p-4 pb-2 border-b border-[#E8E5DC] flex items-center justify-between z-10">
          <div>
            <span className="text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
              {cls.subject}
            </span>
            <h2 className="font-display font-extrabold text-base text-[#0A1D2C] mt-1">
              {cls.name}
            </h2>
            <p className="text-xs text-[#596B72]">
              Docente: <strong className="text-[#0A1D2C]">{cls.teacherName}</strong> · Código:{' '}
              <span className="font-mono font-bold text-[#126B73]">{cls.code}</span>
            </p>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:text-[#0A1D2C] active:scale-95 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pestañas internas */}
        <div className="flex border-b border-[#E8E5DC] bg-white px-3 pt-2">
          <button
            onClick={() => setActiveTab('retos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === 'retos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Retos ({assignedChallenges.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('alumnos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === 'alumnos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <Users2 className="w-3.5 h-3.5" />
            <span>Compañeros ({classmates.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('avisos')}
            className={`flex-1 py-2 text-xs font-display font-bold flex items-center justify-center gap-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === 'avisos'
                ? 'border-[#126B73] text-[#126B73]'
                : 'border-transparent text-[#596B72] hover:text-[#0A1D2C]'
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Avisos</span>
          </button>
        </div>

        {/* Contenido según pestaña */}
        <div className="p-4 flex flex-col gap-3">
          {activeTab === 'retos' && (
            <div className="flex flex-col gap-2.5">
              {assignedChallenges.map((ch, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] shadow-2xs flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-bold text-[#E76D55] uppercase">
                        Práctica activa
                      </span>
                      <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                        {ch.title}
                      </h3>
                      <p className="text-xs text-[#596B72] mt-0.5">{ch.desc}</p>
                    </div>
                    <span className="text-xs font-bold text-[#126B73] bg-[#DCEFEB] px-2 py-0.5 rounded-full shrink-0">
                      {ch.xp}
                    </span>
                  </div>

                  <button
                    onClick={() => {
                      onClose();
                      if (onStartExercise) onStartExercise(ch.prompt);
                    }}
                    className="w-full mt-1 py-2 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-1.5 shadow-[0_2px_0_#005158] active:translate-y-0.5 cursor-pointer"
                  >
                    <span>Resolver con Jarol</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'alumnos' && (
            <div className="flex flex-col gap-2">
              {classmates.length === 0 ? (
                <div className="p-4 text-center text-xs text-[#596B72] bg-white rounded-xl border border-[#E8E5DC]">
                  Sé el primero en completar ejercicios en este grupo.
                </div>
              ) : (
                classmates.map((mate) => (
                  <div
                    key={mate.studentId}
                    className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-[#DCEFEB] text-[#126B73] font-display font-bold text-xs flex items-center justify-center uppercase">
                        {mate.studentName[0] || 'E'}
                      </div>
                      <div>
                        <span className="font-display font-bold text-xs text-[#0A1D2C] block">
                          {mate.studentName}
                        </span>
                        <span className="text-[10px] text-[#596B72]">
                          {mate.completedExercises} retos resueltos · {mate.accuracy}% precisión
                        </span>
                      </div>
                    </div>

                    <span className="text-xs font-display font-semibold text-[#126B73]">
                      {mate.xp || 0} XP
                    </span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'avisos' && (
            <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#126B73]" />
                <span className="font-display font-bold text-xs text-[#0A1D2C]">
                  Bienvenida de {cls.teacherName}
                </span>
              </div>
              <p className="text-xs text-[#3F484A] leading-relaxed">
                "¡Bienvenidos al grupo {cls.name}! Utilicen el tutor Jarol para practicar y pedir pistas paso a paso. Todos los ejercicios que resuelvan se registrarán automáticamente en nuestro seguimiento grupal."
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
