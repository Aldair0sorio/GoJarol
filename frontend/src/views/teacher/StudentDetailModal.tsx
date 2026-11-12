import React from 'react';
import type { DetailedStudent } from '../../types/leagues';
import { X, CheckCircle2, AlertTriangle, Lightbulb, Sparkles, Flame, Send } from 'lucide-react';

interface StudentDetailModalProps {
  student: DetailedStudent;
  onClose: () => void;
}

export const StudentDetailModal: React.FC<StudentDetailModalProps> = ({ student, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border border-[#E8E5DC] shadow-2xl flex flex-col animate-scaleUp">
        {/* Header con botón de cerrar */}
        <div className="sticky top-0 bg-[#F7F5EF] p-4 pb-2 border-b border-[#E8E5DC] flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <img
              src={student.avatarUrl}
              alt={student.name}
              className="w-12 h-12 rounded-full object-cover ring-2 ring-[#126B73]/30"
            />
            <div>
              <h2 className="font-display font-extrabold text-base text-[#0A1D2C]">
                {student.name}
              </h2>
              <span className="text-xs text-[#596B72] block">
                {student.grade} · {student.school}
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:text-[#0A1D2C] active:scale-95 transition-transform"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Contenido con Scroll */}
        <div className="p-4 flex flex-col gap-3.5">
          {/* Métricas del Estudiante */}
          <div className="grid grid-cols-3 gap-2">
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Precisión</span>
              <span className="font-display font-extrabold text-base text-emerald-700">
                {student.accuracy}%
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Total XP</span>
              <div className="flex items-center justify-center gap-1 font-display font-extrabold text-base text-[#126B73]">
                <Sparkles className="w-3.5 h-3.5 text-[#E4AA50] fill-[#E4AA50]" />
                <span>{student.totalXP}</span>
              </div>
            </div>
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Racha</span>
              <div className="flex items-center justify-center gap-1 font-display font-extrabold text-base text-amber-700">
                <Flame className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                <span>{student.streakDays}d</span>
              </div>
            </div>
          </div>

          {/* Estado de Competencias en Fracciones */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2">
            <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C]">
              Diagnóstico Pedagógico de Jarol
            </h3>

            {/* Dominadas */}
            <div className="flex flex-col gap-1.5">
              <span className="text-[11px] font-semibold text-emerald-800">
                Competencias consolidadas:
              </span>
              {student.masteredTopics.map((topic, i) => (
                <div key={i} className="flex items-start gap-1.5 text-xs text-[#0A1D2C]">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{topic}</span>
                </div>
              ))}
            </div>

            {/* Débiles */}
            {student.weakTopics.length > 0 && (
              <div className="flex flex-col gap-1.5 pt-2 border-t border-[#E8E5DC]">
                <span className="text-[11px] font-semibold text-rose-800">
                  Conceptos en riesgo detectados:
                </span>
                {student.weakTopics.map((topic, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-xs text-rose-900 bg-rose-50 p-2 rounded-lg border border-rose-200">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                    <span>{topic}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Historial de Intentos y Retroalimentación de Jarol */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2.5">
            <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C]">
              Intentos Recientes en Ejercicios
            </h3>

            <div className="flex flex-col gap-2">
              {student.recentAttempts.map((att) => (
                <div
                  key={att.id}
                  className={`p-3 rounded-xl border text-xs flex flex-col gap-1.5 ${
                    att.isCorrect
                      ? 'bg-emerald-50/50 border-emerald-200'
                      : 'bg-amber-50/60 border-amber-200'
                  }`}
                >
                  <div className="flex items-center justify-between font-display font-bold">
                    <span className="text-[#0A1D2C]">{att.exerciseTitle}</span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full ${
                        att.isCorrect
                          ? 'bg-emerald-200 text-emerald-900'
                          : 'bg-rose-200 text-rose-900'
                      }`}
                    >
                      {att.isCorrect ? 'Correcto' : 'Error'}
                    </span>
                  </div>

                  <p className="text-[#596B72]">
                    Opción marcada: <strong className="text-[#0A1D2C]">{att.selectedOption}</strong>
                  </p>

                  <p className="text-[#3F484A] text-[11px] leading-relaxed">
                    {att.explanationGiven}
                  </p>

                  {att.hintUsed && (
                    <div className="flex items-center gap-1.5 text-[11px] text-amber-900 bg-amber-100/70 p-1.5 rounded-md">
                      <Lightbulb className="w-3 h-3 text-amber-700 shrink-0" />
                      <span>{att.hintUsed}</span>
                    </div>
                  )}

                  <span className="text-[10px] text-[#596B72] mt-0.5">
                    {att.date}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Acciones del Docente */}
          <button
            onClick={() => {
              alert(`¡Reto de refuerzo en fracciones asignado a ${student.name}!`);
              onClose();
            }}
            className="w-full py-3 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-2 shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all cursor-pointer"
          >
            <Send className="w-4 h-4" />
            <span>Asignar reto de refuerzo personalizado</span>
          </button>
        </div>
      </div>
    </div>
  );
};
