import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { StudentDetailModal } from './StudentDetailModal';
import type { DetailedStudent } from '../../types/leagues';
import type { ClassGroup, StudentMastery } from '../../types/curriculum';
import { AlertTriangle, Plus, CheckCircle2, ChevronRight, Users2 } from 'lucide-react';

export const TeacherDashboardView: React.FC = () => {
  const [classes, setClasses] = useState<ClassGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedClassId, setSelectedClassId] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClassName, setNewClassName] = useState('');
  const [newSubject, setNewSubject] = useState('aritmetica');
  const [newNivel, setNewNivel] = useState<'secundaria' | 'bachillerato'>('secundaria');
  const [newGrado, setNewGrado] = useState(3);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createdCode, setCreatedCode] = useState<string | null>(null);
  const [selectedStudentDetail, setSelectedStudentDetail] = useState<DetailedStudent | null>(null);

  const loadTeacherClasses = () => {
    setIsLoading(true);
    apiService
      .getClasses()
      .then((list) => {
        setClasses(list);
        if (list.length > 0 && !selectedClassId) {
          setSelectedClassId(list[0].id);
        }
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadTeacherClasses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeClass =
    classes.find((c) => c.id === selectedClassId) || classes[0] || null;
  const students: StudentMastery[] = activeClass?.studentsDetail || [];

  const totalCompletedExercises = students.reduce(
    (sum, s) => sum + (s.completedExercises || 0),
    0
  );
  const avgAccuracy =
    students.length > 0
      ? Math.round(students.reduce((sum, s) => sum + (s.accuracy || 0), 0) / students.length)
      : activeClass?.averageMastery || 0;

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim()) return;
    setCreateError(null);

    const res = await apiService.createClass({
      nombre: newClassName.trim(),
      subject: newSubject,
      nivel: newNivel,
      grado: newGrado,
    });

    if (res.success && res.classGroup) {
      setClasses((prev) => [res.classGroup!, ...prev]);
      setSelectedClassId(res.classGroup.id);
      setCreatedCode(res.classGroup.code);
      setNewClassName('');
    } else {
      setCreateError(res.error || 'No se pudo crear el grupo.');
    }
  };

  const openStudentModal = (st: StudentMastery) => {
    const detail: DetailedStudent = {
      id: st.studentId,
      name: st.studentName,
      avatarUrl: '/mascot/jarol-crab.png',
      grade: activeClass?.name || 'Estudiante inscrito',
      school: 'Veracruz',
      totalXP: st.xp ?? st.completedExercises * 30,
      streakDays: 1,
      accuracy: st.accuracy,
      weakTopics: st.needsHelpWith,
      masteredTopics:
        st.completedExercises > 0 && st.accuracy >= 70
          ? [activeClass?.subject || 'Fracciones y Álgebra']
          : [],
      recentAttempts:
        st.completedExercises > 0
          ? [
              {
                id: `att_${st.studentId}`,
                exerciseTitle: `Práctica adaptativa (${st.completedExercises} retos resueltos)`,
                date: st.lastActive || 'Reciente',
                isCorrect: st.accuracy >= 50,
                selectedOption: `${st.accuracy}% de precisión`,
                explanationGiven: 'Evaluado con el motor determinista SymPy y pistas graduales de Jarol.',
              },
            ]
          : [],
    };
    setSelectedStudentDetail(detail);
  };

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-4xl lg:max-w-5xl mx-auto w-full">
      {/* Header Docente */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display font-extrabold text-xl md:text-2xl text-[#0A1D2C]">
            Panel de Control Docente
          </h1>
          <p className="text-xs md:text-sm text-[#596B72]">
            Crea grupos reales en PostgreSQL y monitorea el avance de tus estudiantes con Jarol.
          </p>
        </div>

        <button
          onClick={() => {
            setShowCreateModal(true);
            setCreatedCode(null);
            setCreateError(null);
          }}
          className="shrink-0 flex items-center gap-1.5 px-3 md:px-4 py-2 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs md:text-sm shadow-[0_3px_0_#711707] active:translate-y-0.5 active:shadow-[0_1px_0_#711707] transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 stroke-[3px]" />
          <span>Crear Clase</span>
        </button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-[#596B72]">
          Cargando tus grupos desde la base de datos...
        </div>
      ) : classes.length === 0 ? (
        <div className="p-8 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col items-center text-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-[#DCEFEB] text-[#126B73] flex items-center justify-center">
            <Users2 className="w-6 h-6" />
          </div>
          <h3 className="font-display font-bold text-base text-[#0A1D2C]">
            Aún no has creado ningún grupo escolar
          </h3>
          <p className="text-xs text-[#596B72] max-w-md">
            Haz clic en <strong>Crear Clase</strong> para generar un código oficial <strong className="font-mono text-[#126B73]">JAROL-XXXXX</strong>. Cuando tus estudiantes se unan con ese código, aparecerán aquí automáticamente con sus diagnósticos de IA.
          </p>
          <button
            onClick={() => {
              setShowCreateModal(true);
              setCreatedCode(null);
            }}
            className="mt-1 px-4 py-2.5 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs shadow-[0_3px_0_#711707] cursor-pointer"
          >
            Crear mi primera clase
          </button>
        </div>
      ) : (
        <>
          {/* Selector de Grupos */}
          <div className="flex gap-2 overflow-x-auto pb-2 mb-3">
            {classes.map((cls) => (
              <button
                key={cls.id}
                onClick={() => setSelectedClassId(cls.id)}
                className={`px-3.5 py-2 rounded-xl text-xs font-display font-bold whitespace-nowrap transition-all border cursor-pointer ${
                  activeClass?.id === cls.id
                    ? 'bg-[#126B73] text-white border-[#126B73] shadow-[0_2px_0_#005158]'
                    : 'bg-white text-[#596B72] border-[#E8E5DC] hover:border-[#126B73]'
                }`}
              >
                {cls.name} ({cls.studentCount})
              </button>
            ))}
          </div>

          {/* Métricas del Grupo en 4 Columnas Responsive */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
              <span className="text-xs text-[#596B72] font-medium block">
                Código de Invitación
              </span>
              <span className="font-mono font-extrabold text-lg text-[#126B73] block mt-0.5">
                {activeClass?.code}
              </span>
              <span className="text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full inline-block mt-1">
                Activo para alumnos
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
              <span className="text-xs text-[#596B72] font-medium block">
                Materia Asignada
              </span>
              <span className="font-display font-extrabold text-base text-[#0A1D2C] block mt-0.5 truncate">
                {activeClass?.subject}
              </span>
              <span className="text-[10px] text-[#596B72] inline-block mt-1">
                {activeClass?.studentCount || 0} alumnos inscritos
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
              <span className="text-xs text-[#596B72] font-medium block">
                Precisión Promedio
              </span>
              <span className="font-display font-extrabold text-lg text-emerald-700 block mt-0.5">
                {avgAccuracy}%
              </span>
              <span className="text-[10px] text-[#596B72] inline-block mt-1">
                Evaluación formativa
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
              <span className="text-xs text-[#596B72] font-medium block">
                Retos Completados
              </span>
              <span className="font-display font-extrabold text-lg text-[#126B73] block mt-0.5">
                {totalCompletedExercises}
              </span>
              <span className="text-[10px] text-[#596B72] inline-block mt-1">
                En este grupo
              </span>
            </div>
          </div>

          {/* Grid de 2 Columnas en Desktop: Semáforo a la izquierda, Alumnos a la derecha */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 items-start">
            {/* SEMÁFORO DE DIFICULTADES POR TEMA */}
            <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                    Diagnóstico Pedagógico del Grupo
                  </h3>
                </div>
                <span className="text-[11px] font-semibold text-[#596B72]">
                  Motor IA + SymPy
                </span>
              </div>

              <div className="flex flex-col gap-2.5">
                <div className="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200">
                  <div className="flex items-center justify-between text-xs font-display font-bold text-emerald-950 mb-1">
                    <span>Fracciones y Porcentajes</span>
                    <span>Activo</span>
                  </div>
                  <span className="text-[11px] text-emerald-800 block">
                    🟢 Evaluación simbólica exacta con SymPy y pistas graduales activadas.
                  </span>
                </div>

                <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200">
                  <div className="flex items-center justify-between text-xs font-display font-bold text-amber-950 mb-1">
                    <span>Ecuaciones Lineales de 1er Grado</span>
                    <span>Adaptativo</span>
                  </div>
                  <span className="text-[11px] text-amber-800 block">
                    🟡 El tutor ajusta la dificultad (niveles 1 a 3) según la racha de aciertos de cada alumno.
                  </span>
                </div>

                <div className="p-2.5 rounded-xl bg-teal-50/70 border border-teal-200">
                  <div className="flex items-center justify-between text-xs font-display font-bold text-teal-950 mb-1">
                    <span>Comprensión Lectora, Ortografía y Acentuación</span>
                    <span>Activo</span>
                  </div>
                  <span className="text-[11px] text-teal-800 block">
                    🔵 Lecturas originales con retroalimentación formativa sin revelar la respuesta directa.
                  </span>
                </div>
              </div>
            </div>

            {/* Lista Real de Alumnos Inscritos */}
            <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                  Estudiantes Inscritos en {activeClass?.name}
                </h3>
                <span className="text-xs text-[#596B72]">
                  {students.length} {students.length === 1 ? 'inscrito' : 'inscritos'}
                </span>
              </div>

              {students.length === 0 ? (
                <div className="p-6 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl border border-dashed border-[#D8E2DC]">
                  Comparte el código <strong className="font-mono text-[#126B73]">{activeClass?.code}</strong> con tus alumnos para que se unan desde la pestaña <strong>Mis Clases</strong>.
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {students.map((st: StudentMastery) => (
                    <button
                      key={st.studentId}
                      onClick={() => openStudentModal(st)}
                      className="w-full text-left p-3 rounded-xl bg-[#F7F5EF] hover:bg-[#DCEFEB]/60 transition-colors flex items-center justify-between border border-transparent hover:border-[#126B73]/30 active:scale-[0.99] cursor-pointer"
                    >
                      <div>
                        <span className="font-display font-bold text-xs text-[#0A1D2C] block">
                          {st.studentName}
                        </span>
                        <span className="text-[10px] text-[#596B72]">
                          {st.completedExercises} retos resueltos · {st.accuracy}% precisión · {st.xp || 0} XP
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        {st.completedExercises === 0 ? (
                          <span className="text-[10px] font-bold text-slate-700 bg-slate-200 px-2 py-0.5 rounded-full">
                            Recién inscrito
                          </span>
                        ) : st.accuracy < 60 ? (
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
              )}
            </div>
          </div>
        </>
      )}

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
                    placeholder="Ej. 3° B · Matemáticas"
                    required
                    className="w-full text-sm p-2.5 rounded-xl border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>

                <div>
                  <label className="text-xs font-display font-bold text-[#596B72] block mb-1">
                    Materia Principal
                  </label>
                  <select
                    value={newSubject}
                    onChange={(e) => setNewSubject(e.target.value)}
                    className="w-full text-sm p-2.5 rounded-xl border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none bg-white"
                  >
                    <option value="aritmetica">Aritmética y Matemáticas</option>
                    <option value="algebra">Álgebra</option>
                    <option value="espanol">Español y Lenguajes</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-display font-bold text-[#596B72] block mb-1">
                      Nivel
                    </label>
                    <select
                      value={newNivel}
                      onChange={(e) => {
                        const nv = e.target.value as 'secundaria' | 'bachillerato';
                        setNewNivel(nv);
                        setNewGrado(1);
                      }}
                      className="w-full text-sm p-2.5 rounded-xl border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none bg-white"
                    >
                      <option value="secundaria">Secundaria</option>
                      <option value="bachillerato">Bachillerato</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-display font-bold text-[#596B72] block mb-1">
                      {newNivel === 'secundaria' ? 'Año' : 'Semestre'}
                    </label>
                    <select
                      value={newGrado}
                      onChange={(e) => setNewGrado(Number(e.target.value))}
                      className="w-full text-sm p-2.5 rounded-xl border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none bg-white"
                    >
                      {(newNivel === 'secundaria' ? [1, 2, 3] : [1, 2, 3, 4, 5, 6]).map(
                        (g) => (
                          <option key={g} value={g}>
                            {newNivel === 'secundaria' ? `${g}° año` : `${g}° semestre`}
                          </option>
                        )
                      )}
                    </select>
                  </div>
                </div>

                {createError && (
                  <p className="text-xs text-rose-700 bg-rose-50 p-2 rounded-lg border border-rose-200">
                    {createError}
                  </p>
                )}

                <div className="flex gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 py-2 rounded-full border border-[#E8E5DC] text-xs font-display font-semibold text-[#596B72] cursor-pointer"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2 rounded-full bg-[#E76D55] text-white text-xs font-display font-bold shadow-[0_3px_0_#711707] cursor-pointer"
                  >
                    Generar Código
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex flex-col items-center text-center gap-2 py-2">
                <CheckCircle2 className="w-10 h-10 text-emerald-600" />
                <h4 className="font-display font-bold text-sm text-[#0A1D2C]">
                  ¡Clase guardada en base de datos!
                </h4>
                <p className="text-xs text-[#596B72]">
                  Comparte este código oficial con tus estudiantes:
                </p>
                <div className="p-3 bg-[#F7F5EF] rounded-xl border-2 border-dashed border-[#126B73] my-1">
                  <span className="font-mono font-extrabold text-2xl text-[#126B73] tracking-widest">
                    {createdCode}
                  </span>
                </div>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="w-full py-2.5 rounded-full bg-[#126B73] text-white text-xs font-display font-bold mt-2 cursor-pointer"
                >
                  Listo
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
