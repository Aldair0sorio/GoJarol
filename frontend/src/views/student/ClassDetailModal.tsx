import React, { useState } from 'react';
import { apiService } from '../../services/api';
import type { ClassGroup } from '../../types/curriculum';
import {
  X,
  Users2,
  BookOpen,
  ArrowRight,
  LogOut,
  Sparkles,
} from 'lucide-react';

interface ClassDetailModalProps {
  cls: ClassGroup;
  onClose: () => void;
  onStartExercise?: (topicPrompt: string) => void;
  onLeftClass?: (classId: string) => void;
}

export const ClassDetailModal: React.FC<ClassDetailModalProps> = ({
  cls,
  onClose,
  onStartExercise,
  onLeftClass,
}) => {
  const [activeTab, setActiveTab] = useState<'retos' | 'alumnos'>('retos');
  const [leaving, setLeaving] = useState(false);
  const [confirmLeave, setConfirmLeave] = useState(false);

  const classmates = cls.studentsDetail || [];
  const challenges = cls.challenges || [];

  const handleLeave = async () => {
    setLeaving(true);
    const res = await apiService.leaveClass(cls.id);
    setLeaving(false);
    if (res.success) {
      if (onLeftClass) onLeftClass(cls.id);
      onClose();
    }
  };

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
            <span>Retos ({challenges.length})</span>
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
        </div>

        {/* Contenido según pestaña */}
        <div className="p-4 flex flex-col gap-3">
          {activeTab === 'retos' && (
            <div className="flex flex-col gap-2.5">
              {challenges.length === 0 ? (
                <div className="p-4 rounded-xl bg-white border border-[#E8E5DC] text-center flex flex-col gap-2">
                  <Sparkles className="w-6 h-6 text-[#126B73] mx-auto" />
                  <p className="text-xs text-[#596B72]">
                    Tu docente aún no ha asignado retos específicos en este grupo. Puedes adelantar
                    practicando {cls.subject} con Jarol.
                  </p>
                  <button
                    onClick={() => {
                      onClose();
                      if (onStartExercise) {
                        onStartExercise(`Ponme un ejercicio de ${cls.subject}`);
                      }
                    }}
                    className="mt-1 py-2 px-4 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <span>Practicar {cls.subject} con Jarol</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                challenges.map((ch) => {
                  const pct = Math.min(
                    100,
                    Math.round((ch.solvedCount / Math.max(ch.targetExercises, 1)) * 100)
                  );
                  return (
                    <div
                      key={ch.id}
                      className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] shadow-2xs flex flex-col gap-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span
                              className={`text-[10px] font-bold uppercase ${
                                ch.isPersonal ? 'text-[#E76D55]' : 'text-[#126B73]'
                              }`}
                            >
                              {ch.isPersonal ? 'Reto personalizado para ti' : 'Reto del grupo'}
                            </span>
                            <span className="text-[10px] text-[#596B72]">· {ch.createdAt}</span>
                          </div>
                          <h3 className="font-display font-bold text-sm text-[#0A1D2C] mt-0.5">
                            {ch.title}
                          </h3>
                          {ch.instructions && (
                            <p className="text-xs text-[#596B72] mt-0.5">{ch.instructions}</p>
                          )}
                        </div>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                            ch.isCompleted
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-[#DCEFEB] text-[#126B73]'
                          }`}
                        >
                          {ch.isCompleted
                            ? 'Completado ✓'
                            : `${ch.solvedCount}/${ch.targetExercises} ej.`}
                        </span>
                      </div>

                      <div className="w-full h-1.5 bg-[#F7F5EF] rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            ch.isCompleted ? 'bg-emerald-600' : 'bg-[#126B73]'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>

                      {!ch.isCompleted && (
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
                      )}
                    </div>
                  );
                })
              )}
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
                          {mate.completedExercises} retos resueltos · {mate.accuracy}% precisión ·{' '}
                          {mate.lastActive}
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

          {/* Salir de la clase */}
          {onLeftClass && (
            <div className="pt-2 border-t border-[#E8E5DC]">
              {confirmLeave ? (
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-xs">
                  <span className="text-rose-800 font-medium">¿Salir de {cls.name}?</span>
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => setConfirmLeave(false)}
                      className="px-2.5 py-1 rounded-lg bg-white border border-[#E8E5DC] text-[#596B72] cursor-pointer"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleLeave}
                      disabled={leaving}
                      className="px-2.5 py-1 rounded-lg bg-rose-600 text-white font-bold cursor-pointer"
                    >
                      {leaving ? 'Saliendo...' : 'Sí, salir'}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmLeave(true)}
                  className="w-full py-2 rounded-full text-xs font-display font-semibold text-rose-700 hover:bg-rose-50 flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Salir de este grupo</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
