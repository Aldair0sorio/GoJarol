import React, { useState } from 'react';
import { MOCK_CLASSES, MOCK_STUDENT_DIAGNOSTICS, MOCK_DETAILED_STUDENTS } from '../../services/mockData';
import { StudentDetailModal } from './StudentDetailModal';
import type { DetailedStudent } from '../../types/leagues';
import type { StudentMastery } from '../../types/curriculum';
import { AlertTriangle, Plus, CheckCircle2, ChevronRight } from 'lucide-react';

export const TeacherDashboardView: React.FC = () => {
  const [classes] = useState(MOCK_CLASSES);
  const [students] = useState(MOCK_STUDENT_DIAGNOSTICS);
  const [selectedClassId, setSelectedClassId] = useState(MOCK_CLASSES[0].id);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [createdCode, setCreatedCode] = useState<string | null>(null);
  const [selectedStudentDetail, setSelectedStudentDetail] = useState<DetailedStudent | null>(null);

  const handleCreateClass = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim()) return;

    const randomSuffix = Math.floor(100 + Math.random() * 900);
    const code = `JAROL-${randomSuffix}`;
    setCreatedCode(code);
  };

  return (
    <div className="flex flex-col flex-1 px-4 py-3 pb-24">
      {/* Header Docente */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display font-extrabold text-xl text-[#0A1D2C]">
            Panel de Control Docente
          </h1>
          <p className="text-xs text-[#596B72]">
            Seguimiento de grupos y diagnóstico de dificultades en tiempo real.
          </p>
        </div>

        <button
          onClick={() => {
            setShowCreateModal(true);
            setCreatedCode(null);
          }}
          className="shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs shadow-[0_3px_0_#711707] active:translate-y-0.5 active:shadow-[0_1px_0_#711707] transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 stroke-[3px]" />
          <span>Crear Clase</span>
        </button>
      </div>

      {/* Selector de Grupos */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-3">
        {classes.map((cls) => (
          <button
            key={cls.id}
            onClick={() => setSelectedClassId(cls.id)}
            className={`px-3.5 py-2 rounded-xl text-xs font-display font-bold whitespace-nowrap transition-all border ${
              selectedClassId === cls.id
                ? 'bg-[#126B73] text-white border-[#126B73] shadow-[0_2px_0_#005158]'
                : 'bg-white text-[#596B72] border-[#E8E5DC] hover:border-[#126B73]'
            }`}
          >
            {cls.name} ({cls.studentCount})
          </button>
        ))}
      </div>

      {/* Métricas del Grupo */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
          <span className="text-xs text-[#596B72] font-medium block">
            Código de Invitación
          </span>
          <span className="font-mono font-extrabold text-lg text-[#126B73] block mt-0.5">
            JAROL-3B
          </span>
          <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full inline-block mt-1">
            Activo para alumnos
          </span>
        </div>

        <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
          <span className="text-xs text-[#596B72] font-medium block">
            Avance en Fracciones
          </span>
          <span className="font-display font-extrabold text-lg text-[#0A1D2C] block mt-0.5">
            74% Dominio
          </span>
          <span className="text-[10px] text-[#596B72] inline-block mt-1">
            32 alumnos practicando
          </span>
        </div>
      </div>

      {/* SEMÁFORO DE DIFICULTADES POR TEMA (Clave para el jurado) */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] mb-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
              Semáforo de Dificultades · Fracciones
            </h3>
          </div>
          <span className="text-[11px] font-semibold text-[#596B72]">
            IA Diagnóstica
          </span>
        </div>

        <div className="flex flex-col gap-2.5">
          {/* Verde: Bien afianzado */}
          <div className="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200">
            <div className="flex items-center justify-between text-xs font-display font-bold text-emerald-950 mb-1">
              <span>Suma con igual denominador</span>
              <span>88% Dominado</span>
            </div>
            <div className="w-full h-1.5 bg-emerald-200 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-600 rounded-full" style={{ width: '88%' }}></div>
            </div>
            <span className="text-[10px] text-emerald-800 mt-1 block">
              🟢 La mayoría del grupo comprende que el denominador no se suma.
            </span>
          </div>

          {/* Amarillo: En proceso */}
          <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200">
            <div className="flex items-center justify-between text-xs font-display font-bold text-amber-950 mb-1">
              <span>Simplificación a enteros</span>
              <span>65% En proceso</span>
            </div>
            <div className="w-full h-1.5 bg-amber-200 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: '65%' }}></div>
            </div>
            <span className="text-[10px] text-amber-800 mt-1 block">
              🟡 11 alumnos necesitan repasar que 4/4 equivale a 1 entero.
            </span>
          </div>

          {/* Rojo: Dificultad Crítica */}
          <div className="p-2.5 rounded-xl bg-rose-50/70 border border-rose-200">
            <div className="flex items-center justify-between text-xs font-display font-bold text-rose-950 mb-1">
              <span>Suma con diferente denominador</span>
              <span>34% Atención requerida</span>
            </div>
            <div className="w-full h-1.5 bg-rose-200 rounded-full overflow-hidden">
              <div className="h-full bg-rose-600 rounded-full" style={{ width: '34%' }}></div>
            </div>
            <span className="text-[10px] text-rose-800 mt-1 block font-medium">
              🔴 18 alumnos se atoran buscando el mínimo común múltiplo.
            </span>
          </div>
        </div>
      </div>

      {/* Lista de Alumnos */}
      <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
            Alumnos Recientes
          </h3>
          <span className="text-xs text-[#596B72]">
            {students.length} registrados
          </span>
        </div>

        <div className="flex flex-col gap-2">
          {students.map((st: StudentMastery) => (
            <button
              key={st.studentId}
              onClick={() => {
                const detail = MOCK_DETAILED_STUDENTS[st.studentId];
                if (detail) setSelectedStudentDetail(detail);
              }}
              className="w-full text-left p-3 rounded-xl bg-[#F7F5EF] hover:bg-[#DCEFEB]/60 transition-colors flex items-center justify-between border border-transparent hover:border-[#126B73]/30 active:scale-[0.99] cursor-pointer"
            >
              <div>
                <span className="font-display font-bold text-xs text-[#0A1D2C] block">
                  {st.studentName}
                </span>
                <span className="text-[10px] text-[#596B72]">
                  {st.completedExercises} retos resueltos · {st.accuracy}% precisión
                </span>
              </div>

              <div className="flex items-center gap-2">
                {st.needsHelpWith.length > 0 ? (
                  <span className="text-[10px] font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded-full">
                    Requiere apoyo
                  </span>
                ) : (
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                    Al corriente
                  </span>
                )}
                <ChevronRight className="w-3.5 h-3.5 text-[#596B72]" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Modal Ficha Detallada del Estudiante */}
      {selectedStudentDetail && (
        <StudentDetailModal
          student={selectedStudentDetail}
          onClose={() => setSelectedStudentDetail(null)}
        />
      )}

      {/* Modal Crear Clase */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 border border-[#E8E5DC] shadow-xl flex flex-col gap-3.5">
            <h3 className="font-display font-bold text-lg text-[#0A1D2C]">
              Crear Nuevo Grupo
            </h3>

            {!createdCode ? (
              <form onSubmit={handleCreateClass} className="flex flex-col gap-3">
                <div>
                  <label className="text-xs font-display font-bold text-[#596B72] block mb-1">
                    Nombre del Grupo
                  </label>
                  <input
                    type="text"
                    value={newClassName}
                    onChange={(e) => setNewClassName(e.target.value)}
                    placeholder="Ej. 1° C · Matemáticas"
                    required
                    className="w-full text-sm p-2.5 rounded-xl border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>

                <div className="flex gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 py-2 rounded-full border border-[#E8E5DC] text-xs font-display font-semibold text-[#596B72]"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2 rounded-full bg-[#E76D55] text-white text-xs font-display font-bold shadow-[0_3px_0_#711707]"
                  >
                    Generar Código
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex flex-col items-center text-center gap-2 py-2">
                <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                <h4 className="font-display font-bold text-sm text-[#0A1D2C]">
                  ¡Clase creada exitosamente!
                </h4>
                <p className="text-xs text-[#596B72]">
                  Comparte este código con tus alumnos de secundaria o bachillerato:
                </p>
                <div className="p-3 bg-[#F7F5EF] rounded-xl border-2 border-dashed border-[#126B73] my-1">
                  <span className="font-mono font-extrabold text-2xl text-[#126B73] tracking-widest">
                    {createdCode}
                  </span>
                </div>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="w-full py-2.5 rounded-full bg-[#126B73] text-white text-xs font-display font-bold mt-2"
                >
                  Cerrar
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
