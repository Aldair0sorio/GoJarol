import React, { useEffect, useMemo, useState } from 'react';
import { apiService } from '../../services/api';
import { StudentDetailModal } from './StudentDetailModal';
import type { DetailedStudent } from '../../types/leagues';
import type { ClassGroup, StudentMastery } from '../../types/curriculum';
import {
  AlertTriangle,
  Plus,
  CheckCircle2,
  ChevronRight,
  Users2,
  Copy,
  Check,
  PauseCircle,
  PlayCircle,
  RefreshCw,
  Trash2,
  Edit3,
  Search,
  Target,
  BarChart3,
  Send,
  GraduationCap,
} from 'lucide-react';

interface TeacherDashboardViewProps {
  activeTab?: 'panel' | 'clases' | 'alumnos';
  onTabChange?: (tab: 'panel' | 'clases' | 'alumnos') => void;
}

const TOPIC_OPTIONS = [
  { id: 'mat_fracciones', label: 'Fracciones Equivalentes y Suma' },
  { id: 'mat_ecuaciones', label: 'Ecuaciones Lineales de 1er Grado' },
  { id: 'mat_porcentajes', label: 'Porcentajes y Proporcionalidad' },
  { id: 'esp_comprension', label: 'Comprensión Lectora' },
  { id: 'esp_ortografia', label: 'Ortografía Puntual y Grafías' },
  { id: 'esp_acentuacion', label: 'Reglas de Acentuación' },
];

export const TeacherDashboardView: React.FC<TeacherDashboardViewProps> = ({
  activeTab = 'panel',
  onTabChange,
}) => {
  const [classes, setClasses] = useState<ClassGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedClassId, setSelectedClassId] = useState<string>('');

  // Crear / Editar clase
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingClass, setEditingClass] = useState<ClassGroup | null>(null);
  const [newClassName, setNewClassName] = useState('');
  const [newSubject, setNewSubject] = useState('matematicas');
  const [newNivel, setNewNivel] = useState<'secundaria' | 'bachillerato'>('secundaria');
  const [newGrado, setNewGrado] = useState(3);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createdCode, setCreatedCode] = useState<string | null>(null);

  // Copiar código / feedback
  const [copiedClassId, setCopiedClassId] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<{ ok: boolean; text: string } | null>(null);

  // Modal alumno
  const [selectedStudentDetail, setSelectedStudentDetail] = useState<DetailedStudent | null>(null);

  // Filtros en pestaña "Diagnóstico Alumnos"
  const [studentSearch, setStudentSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<
    'todos' | 'Requiere apoyo' | 'Sin actividad' | 'Al corriente' | 'Destacado'
  >('todos');
  const [studentSort, setStudentSort] = useState<'priority' | 'xp' | 'completed' | 'name'>('priority');
  const [scopeAllClasses, setScopeAllClasses] = useState(false);

  // Formulario de Reto Grupal (pestaña Mis Clases)
  const [chalTopicId, setChalTopicId] = useState('mat_fracciones');
  const [chalTitle, setChalTitle] = useState('');
  const [chalInstructions, setChalInstructions] = useState('');
  const [chalTarget, setChalTarget] = useState(2);
  const [chalSubmitting, setChalSubmitting] = useState(false);

  const [confirmDeleteClassId, setConfirmDeleteClassId] = useState<string | null>(null);

  const loadTeacherClasses = () => {
    setIsLoading(true);
    apiService
      .getClasses()
      .then((list) => {
        setClasses(list);
        if (list.length > 0 && (!selectedClassId || !list.some((c) => c.id === selectedClassId))) {
          setSelectedClassId(list[0].id);
        }
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadTeacherClasses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const syncClassInState = (updated: ClassGroup) => {
    setClasses((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
  };

  const activeClass =
    classes.find((c) => c.id === selectedClassId) || classes[0] || null;
  const students: StudentMastery[] = activeClass?.studentsDetail || [];

  const totalCompletedExercises =
    activeClass?.totalCompletedExercises ??
    students.reduce((sum, s) => sum + (s.completedExercises || 0), 0);
  const avgAccuracy = activeClass?.averageMastery ?? 0;
  const studentsAtRisk =
    activeClass?.studentsAtRisk ??
    students.filter((s) => s.statusLabel === 'Requiere apoyo').length;

  const showTempMessage = (ok: boolean, text: string) => {
    setActionMsg({ ok, text });
    setTimeout(() => setActionMsg(null), 3500);
  };

  const copyInviteCode = (cls: ClassGroup, withMessage = false) => {
    const content = withMessage
      ? `Únete a mi clase "${cls.name}" en Go Jarol con el código: ${cls.code}`
      : cls.code;
    navigator.clipboard?.writeText(content).catch(() => {});
    setCopiedClassId(cls.id);
    setTimeout(() => setCopiedClassId(null), 2000);
    showTempMessage(true, withMessage ? 'Mensaje de invitación copiado.' : `Código ${cls.code} copiado.`);
  };

  const openCreateModal = () => {
    setEditingClass(null);
    setNewClassName('');
    setNewSubject('matematicas');
    setNewNivel('secundaria');
    setNewGrado(3);
    setCreatedCode(null);
    setCreateError(null);
    setShowCreateModal(true);
  };

  const openEditModal = (cls: ClassGroup) => {
    setEditingClass(cls);
    setNewClassName(cls.name);
    setNewSubject(cls.subjectSlug === 'espanol' ? 'espanol' : 'matematicas');
    setNewNivel(cls.nivel || 'secundaria');
    setNewGrado(cls.grado || 3);
    setCreatedCode(null);
    setCreateError(null);
    setShowCreateModal(true);
  };

  const handleSaveClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newClassName.trim()) return;
    setCreateError(null);

    if (editingClass) {
      const res = await apiService.updateClass(editingClass.id, {
        nombre: newClassName.trim(),
        subject: newSubject,
        nivel: newNivel,
        grado: newGrado,
      });
      if (res.success && res.classGroup) {
        syncClassInState(res.classGroup);
        setShowCreateModal(false);
        showTempMessage(true, `Grupo "${res.classGroup.name}" actualizado.`);
      } else {
        setCreateError(res.error || 'No se pudo actualizar el grupo.');
      }
      return;
    }

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

  const handleToggleCodeActive = async (cls: ClassGroup) => {
    const nextState = !(cls.codeActive ?? true);
    const res = await apiService.updateClass(cls.id, { codigo_activo: nextState });
    if (res.success && res.classGroup) {
      syncClassInState(res.classGroup);
      showTempMessage(
        true,
        nextState
          ? `Código ${cls.code} activado para recibir inscripciones.`
          : `Código ${cls.code} pausado temporalmente.`
      );
    } else {
      showTempMessage(false, res.error || 'Error al cambiar estado del código.');
    }
  };

  const handleRegenerateCode = async (cls: ClassGroup) => {
    const res = await apiService.updateClass(cls.id, { regenerate_code: true });
    if (res.success && res.classGroup) {
      syncClassInState(res.classGroup);
      showTempMessage(true, `Nuevo código generado: ${res.classGroup.code}`);
    } else {
      showTempMessage(false, res.error || 'No se pudo regenerar el código.');
    }
  };

  const handleDeleteClass = async (classId: string) => {
    const res = await apiService.deleteClass(classId);
    setConfirmDeleteClassId(null);
    if (res.success) {
      const remaining = classes.filter((c) => c.id !== classId);
      setClasses(remaining);
      if (selectedClassId === classId) {
        setSelectedClassId(remaining[0]?.id || '');
      }
      showTempMessage(true, 'Clase eliminada de la base de datos.');
    } else {
      showTempMessage(false, res.error || 'No se pudo eliminar la clase.');
    }
  };

  const handleRemoveStudent = async (classId: string, studentId: string) => {
    const res = await apiService.removeStudentFromClass(classId, studentId);
    if (res.success) {
      loadTeacherClasses();
      showTempMessage(true, 'Alumno dado de baja del grupo.');
    } else {
      showTempMessage(false, res.error || 'No se pudo remover al estudiante.');
    }
  };

  const handleCreateGroupChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeClass) return;
    setChalSubmitting(true);
    const topicLabel = TOPIC_OPTIONS.find((t) => t.id === chalTopicId)?.label || chalTopicId;
    const res = await apiService.assignClassChallenge(activeClass.id, {
      topic_id: chalTopicId,
      title: chalTitle.trim() || `Práctica grupal: ${topicLabel}`,
      instructions:
        chalInstructions.trim() ||
        `Resuelve al menos ${chalTarget} ejercicios de ${topicLabel} con apoyo paso a paso de Jarol.`,
      target_exercises: chalTarget,
    });
    setChalSubmitting(false);
    if (res.success && res.classGroup) {
      syncClassInState(res.classGroup);
      setChalTitle('');
      setChalInstructions('');
      showTempMessage(true, 'Reto asignado a todo el grupo.');
    } else {
      showTempMessage(false, res.error || 'No se pudo asignar el reto.');
    }
  };

  const handleDeleteChallenge = async (challengeId: string) => {
    if (!activeClass) return;
    const res = await apiService.deleteClassChallenge(activeClass.id, challengeId);
    if (res.success && res.classGroup) {
      syncClassInState(res.classGroup);
      showTempMessage(true, 'Reto eliminado.');
    }
  };

  const openStudentModal = (st: StudentMastery, classRef?: ClassGroup) => {
    const cls = classRef || activeClass;
    const detail: DetailedStudent = {
      id: st.studentId,
      classId: cls?.id,
      name: st.studentName,
      email: st.email,
      avatarUrl: '/mascot/jarol-crab.png',
      grade: st.gradeLabel || 'Estudiante inscrito',
      school: cls?.name || 'Veracruz',
      joinedAt: st.joinedAt,
      lastActive: st.lastActive,
      totalXP: st.xp ?? 0,
      streakDays: st.streakDays ?? 1,
      accuracy: st.accuracy,
      completedExercises: st.completedExercises,
      totalAttempts: st.totalAttempts,
      hintsUsedTotal: st.hintsUsedTotal,
      statusLabel: st.statusLabel,
      weakTopics: st.needsHelpWith,
      masteredTopics: st.masteredTopics || [],
      topics: st.topics || [],
      recommendations: st.recommendations || [],
      recentAttempts: st.recentAttempts || [],
    };
    setSelectedStudentDetail(detail);
  };

  // Alumnos filtrados para pestaña "Diagnóstico Alumnos"
  const filteredDirectory = useMemo(() => {
    const sourceItems: Array<{ st: StudentMastery; cls: ClassGroup }> = scopeAllClasses
      ? classes.flatMap((c) => (c.studentsDetail || []).map((st) => ({ st, cls: c })))
      : activeClass
        ? (activeClass.studentsDetail || []).map((st) => ({ st, cls: activeClass }))
        : [];

    const query = studentSearch.trim().toLowerCase();
    const filtered = sourceItems.filter(({ st }) => {
      const matchesQuery =
        !query ||
        st.studentName.toLowerCase().includes(query) ||
        (st.email || '').toLowerCase().includes(query);
      const matchesStatus = statusFilter === 'todos' || st.statusLabel === statusFilter;
      return matchesQuery && matchesStatus;
    });

    const priorityScore = (st: StudentMastery) => {
      if (st.statusLabel === 'Requiere apoyo') return 0;
      if (st.statusLabel === 'Sin actividad') return 1;
      if (st.statusLabel === 'Al corriente') return 2;
      return 3;
    };

    filtered.sort((a, b) => {
      if (studentSort === 'priority') {
        const diff = priorityScore(a.st) - priorityScore(b.st);
        if (diff !== 0) return diff;
        return a.st.accuracy - b.st.accuracy;
      }
      if (studentSort === 'xp') return (b.st.xp || 0) - (a.st.xp || 0);
      if (studentSort === 'completed') return b.st.completedExercises - a.st.completedExercises;
      return a.st.studentName.localeCompare(b.st.studentName);
    });

    return filtered;
  }, [classes, activeClass, scopeAllClasses, studentSearch, statusFilter, studentSort]);

  const tabMap = {
    panel: {
      title: 'Panel General Docente',
      subtitle: 'Diagnóstico grupal en tiempo real y alertas tempranas.',
    },
    clases: {
      title: 'Mis Clases y Códigos',
      subtitle: 'Administra códigos de acceso y asigna retos grupales.',
    },
    alumnos: {
      title: 'Diagnóstico de Alumnos',
      subtitle: 'Analiza el desempeño individual, historial de errores y asigna refuerzos.',
    },
  };
  const resolvedTab: 'panel' | 'clases' | 'alumnos' =
    activeTab === 'clases' || activeTab === 'alumnos' ? activeTab : 'panel';
  const tabMeta = tabMap[resolvedTab];

  return (
    <div className="flex flex-col flex-1 px-4 md:px-8 py-4 pb-24 md:pb-8 max-w-md md:max-w-4xl lg:max-w-5xl mx-auto w-full">
      {/* Header Docente */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div>
          <h1 className="font-display font-extrabold text-xl md:text-2xl text-[#0A1D2C]">
            {tabMeta.title}
          </h1>
          <p className="text-xs md:text-sm text-[#596B72]">{tabMeta.subtitle}</p>
        </div>

        <button
          onClick={openCreateModal}
          className="shrink-0 flex items-center gap-1.5 px-3 md:px-4 py-2 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs md:text-sm shadow-[0_3px_0_#711707] active:translate-y-0.5 active:shadow-[0_1px_0_#711707] transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5 stroke-[3px]" />
          <span>Crear Clase</span>
        </button>
      </div>

      {actionMsg && (
        <div
          className={`mb-3 px-3.5 py-2 rounded-xl text-xs font-medium border flex items-center justify-between ${
            actionMsg.ok
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <span>{actionMsg.text}</span>
        </div>
      )}

      {isLoading ? (
        <div className="p-8 text-center text-sm text-[#596B72]">
          Cargando tus grupos y analíticas desde PostgreSQL...
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
            Haz clic en <strong>Crear Clase</strong> para generar un código{' '}
            <strong className="font-mono text-[#126B73]">JAROL-XXXXX</strong>. Cuando tus estudiantes se unan desde{' '}
            <strong>Mis Clases</strong>, verás su precisión, tema por tema e historial real aquí.
          </p>
          <button
            onClick={openCreateModal}
            className="mt-1 px-4 py-2.5 rounded-full bg-[#E76D55] text-white font-display font-bold text-xs shadow-[0_3px_0_#711707] cursor-pointer"
          >
            Crear mi primera clase
          </button>
        </div>
      ) : (
        <>
          {/* Selector de Grupos */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-3">
            {classes.map((cls) => (
              <button
                key={cls.id}
                onClick={() => {
                  setSelectedClassId(cls.id);
                  setScopeAllClasses(false);
                }}
                className={`px-3.5 py-2 rounded-xl text-xs font-display font-bold whitespace-nowrap transition-all border cursor-pointer flex items-center gap-1.5 ${
                  !scopeAllClasses && activeClass?.id === cls.id
                    ? 'bg-[#126B73] text-white border-[#126B73] shadow-[0_2px_0_#005158]'
                    : 'bg-white text-[#596B72] border-[#E8E5DC] hover:border-[#126B73]'
                }`}
              >
                <span>{cls.name}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    !scopeAllClasses && activeClass?.id === cls.id
                      ? 'bg-white/20 text-white'
                      : 'bg-[#F7F5EF] text-[#596B72]'
                  }`}
                >
                  {cls.studentCount}
                </span>
              </button>
            ))}

            {activeTab === 'alumnos' && classes.length > 1 && (
              <button
                onClick={() => setScopeAllClasses(true)}
                className={`px-3.5 py-2 rounded-xl text-xs font-display font-bold whitespace-nowrap transition-all border cursor-pointer ${
                  scopeAllClasses
                    ? 'bg-[#E76D55] text-white border-[#E76D55]'
                    : 'bg-white text-[#596B72] border-[#E8E5DC] hover:border-[#E76D55]'
                }`}
              >
                Todos mis grupos
              </button>
            )}
          </div>

          {/* ================================================================= */}
          {/* PESTAÑA 1: PANEL GENERAL                                          */}
          {/* ================================================================= */}
          {activeTab === 'panel' && activeClass && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#596B72] font-medium">Código de Clase</span>
                    <button
                      onClick={() => copyInviteCode(activeClass)}
                      title="Copiar código"
                      className="text-[#126B73] hover:bg-[#DCEFEB] p-1 rounded-md cursor-pointer"
                    >
                      {copiedClassId === activeClass.id ? (
                        <Check className="w-3.5 h-3.5" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                  <span className="font-mono font-extrabold text-lg text-[#126B73] block mt-0.5">
                    {activeClass.code}
                  </span>
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full inline-block mt-1 ${
                      activeClass.codeActive ?? true
                        ? 'text-emerald-700 bg-emerald-50'
                        : 'text-amber-700 bg-amber-50'
                    }`}
                  >
                    {activeClass.codeActive ?? true ? 'Activo para alumnos' : 'Inscripción pausada'}
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
                  <span className="text-xs text-[#596B72] font-medium block">
                    Grupo y Materia
                  </span>
                  <span className="font-display font-extrabold text-base text-[#0A1D2C] block mt-0.5 truncate">
                    {activeClass.subject}
                  </span>
                  <span className="text-[10px] text-[#596B72] inline-block mt-1">
                    {activeClass.studentCount} {activeClass.studentCount === 1 ? 'alumno' : 'alumnos'} ·{' '}
                    {activeClass.grado}°{' '}
                    {activeClass.nivel === 'bachillerato' ? 'Bachillerato' : 'Secundaria'}
                  </span>
                </div>

                <div className="p-3.5 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9]">
                  <span className="text-xs text-[#596B72] font-medium block">
                    Precisión Grupal
                  </span>
                  <span className="font-display font-extrabold text-lg text-emerald-700 block mt-0.5">
                    {avgAccuracy}%
                  </span>
                  <span className="text-[10px] text-[#596B72] inline-block mt-1">
                    {studentsAtRisk > 0
                      ? `${studentsAtRisk} alumno(s) con apoyo pendiente`
                      : 'Evaluación formativa real'}
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
                    {(activeClass.challenges || []).length} retos asignados al grupo
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 items-start">
                {/* Diagnóstico Pedagógico REAL del Grupo por Tema */}
                <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-1.5">
                      <BarChart3 className="w-4 h-4 text-[#126B73]" />
                      <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                        Diagnóstico Real del Grupo por Tema
                      </h3>
                    </div>
                    <span className="text-[11px] font-semibold text-[#596B72]">
                      Calculado desde BD
                    </span>
                  </div>

                  <div className="flex flex-col gap-2.5">
                    {(activeClass.topicAnalytics || []).map((t) => {
                      const badgeCls =
                        t.healthStatus === 'Requiere refuerzo'
                          ? 'bg-rose-50/80 border-rose-200 text-rose-950'
                          : t.healthStatus === 'Fortaleza'
                            ? 'bg-emerald-50/80 border-emerald-200 text-emerald-950'
                            : t.healthStatus === 'En progreso'
                              ? 'bg-amber-50/70 border-amber-200 text-amber-950'
                              : 'bg-[#F7F5EF] border-[#E8E5DC] text-[#0A1D2C]';

                      const pillCls =
                        t.healthStatus === 'Requiere refuerzo'
                          ? 'bg-rose-200 text-rose-900'
                          : t.healthStatus === 'Fortaleza'
                            ? 'bg-emerald-200 text-emerald-900'
                            : t.healthStatus === 'En progreso'
                              ? 'bg-amber-200 text-amber-900'
                              : 'bg-slate-200 text-slate-700';

                      return (
                        <div key={t.topicId} className={`p-3 rounded-xl border ${badgeCls}`}>
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <span className="text-xs font-display font-bold truncate">
                              {t.topicName}
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${pillCls}`}>
                              {t.healthStatus}
                            </span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] opacity-85">
                            <span>
                              {t.activeStudents === 0
                                ? 'Sin intentos aún en este grupo'
                                : `${t.activeStudents} activo(s) · ${t.averageAccuracy}% precisión · ${t.strugglingStudents} en riesgo · ${t.totalHintsUsed} pistas`}
                            </span>
                            {onTabChange && (
                              <button
                                onClick={() => {
                                  setChalTopicId(t.topicId);
                                  onTabChange('clases');
                                }}
                                className="text-[10px] font-display font-bold text-[#126B73] hover:underline shrink-0 cursor-pointer"
                              >
                                + Asignar
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Lista rápida de Alumnos Inscritos */}
                <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9]">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                      Estudiantes en {activeClass.name}
                    </h3>
                    {onTabChange && students.length > 0 && (
                      <button
                        onClick={() => onTabChange('alumnos')}
                        className="text-xs font-display font-bold text-[#126B73] hover:underline cursor-pointer"
                      >
                        Análisis completo →
                      </button>
                    )}
                  </div>

                  {students.length === 0 ? (
                    <div className="p-6 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl border border-dashed border-[#D8E2DC] flex flex-col items-center gap-2">
                      <span>
                        Comparte el código{' '}
                        <strong className="font-mono text-[#126B73]">{activeClass.code}</strong> con tus
                        estudiantes para que se unan desde <strong>Mis Clases</strong>.
                      </span>
                      <button
                        onClick={() => copyInviteCode(activeClass, true)}
                        className="px-3 py-1.5 rounded-full bg-white border border-[#126B73] text-[#126B73] font-display font-bold text-[11px] flex items-center gap-1 cursor-pointer"
                      >
                        <Copy className="w-3 h-3" />
                        <span>Copiar invitación</span>
                      </button>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2">
                      {students.map((st) => (
                        <button
                          key={st.studentId}
                          onClick={() => openStudentModal(st, activeClass)}
                          className="w-full text-left p-3 rounded-xl bg-[#F7F5EF] hover:bg-[#DCEFEB]/60 transition-colors flex items-center justify-between border border-transparent hover:border-[#126B73]/30 active:scale-[0.99] cursor-pointer"
                        >
                          <div className="min-w-0">
                            <span className="font-display font-bold text-xs text-[#0A1D2C] block truncate">
                              {st.studentName}
                            </span>
                            <span className="text-[10px] text-[#596B72] block truncate">
                              {st.completedExercises} resueltos · {st.accuracy}% precisión ·{' '}
                              {st.xp || 0} XP · {st.lastActive}
                            </span>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                st.statusLabel === 'Requiere apoyo'
                                  ? 'text-rose-700 bg-rose-100'
                                  : st.statusLabel === 'Sin actividad'
                                    ? 'text-slate-700 bg-slate-200'
                                    : st.statusLabel === 'Destacado'
                                      ? 'text-emerald-800 bg-emerald-100'
                                      : 'text-[#126B73] bg-[#DCEFEB]'
                              }`}
                            >
                              {st.statusLabel || 'Al corriente'}
                            </span>
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

          {/* ================================================================= */}
          {/* PESTAÑA 2: MIS CLASES (Gestión, Códigos, Retos grupales)          */}
          {/* ================================================================= */}
          {activeTab === 'clases' && activeClass && (
            <div className="flex flex-col gap-4">
              {/* Tarjeta principal de administración de la clase seleccionada */}
              <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#DCEFEB] text-[#126B73]">
                      {activeClass.subject}
                    </span>
                    <span className="text-[11px] text-[#596B72]">
                      {activeClass.grado}°{' '}
                      {activeClass.nivel === 'bachillerato' ? 'Bachillerato' : 'Secundaria'}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        activeClass.codeActive ?? true
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {activeClass.codeActive ?? true ? 'Inscripciones abiertas' : 'Código pausado'}
                    </span>
                  </div>
                  <h2 className="font-display font-extrabold text-lg text-[#0A1D2C] mt-1">
                    {activeClass.name}
                  </h2>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-[#596B72]">Código de acceso:</span>
                    <span className="font-mono font-extrabold text-sm text-[#126B73] bg-[#F7F5EF] px-2.5 py-0.5 rounded-lg border border-[#E8E5DC]">
                      {activeClass.code}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => copyInviteCode(activeClass, true)}
                    className="px-3 py-1.5 rounded-xl bg-[#126B73] text-white font-display font-bold text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    {copiedClassId === activeClass.id ? (
                      <Check className="w-3.5 h-3.5" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                    <span>Copiar invitación</span>
                  </button>

                  <button
                    onClick={() => handleToggleCodeActive(activeClass)}
                    className="px-3 py-1.5 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] text-[#0A1D2C] font-display font-semibold text-xs flex items-center gap-1.5 hover:border-[#126B73] cursor-pointer"
                  >
                    {activeClass.codeActive ?? true ? (
                      <>
                        <PauseCircle className="w-3.5 h-3.5 text-amber-600" />
                        <span>Pausar código</span>
                      </>
                    ) : (
                      <>
                        <PlayCircle className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Reactivar código</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleRegenerateCode(activeClass)}
                    className="px-3 py-1.5 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] text-[#0A1D2C] font-display font-semibold text-xs flex items-center gap-1.5 hover:border-[#126B73] cursor-pointer"
                  >
                    <RefreshCw className="w-3.5 h-3.5 text-[#126B73]" />
                    <span>Regenerar</span>
                  </button>

                  <button
                    onClick={() => openEditModal(activeClass)}
                    className="px-3 py-1.5 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] text-[#0A1D2C] font-display font-semibold text-xs flex items-center gap-1.5 hover:border-[#126B73] cursor-pointer"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Editar</span>
                  </button>

                  {confirmDeleteClassId === activeClass.id ? (
                    <div className="flex items-center gap-1.5 bg-rose-50 px-2.5 py-1 rounded-xl border border-rose-200">
                      <span className="text-[11px] font-semibold text-rose-800">¿Borrar grupo?</span>
                      <button
                        onClick={() => handleDeleteClass(activeClass.id)}
                        className="px-2 py-0.5 rounded bg-rose-600 text-white text-[11px] font-bold cursor-pointer"
                      >
                        Sí
                      </button>
                      <button
                        onClick={() => setConfirmDeleteClassId(null)}
                        className="px-2 py-0.5 rounded bg-white text-[11px] border border-[#E8E5DC] cursor-pointer"
                      >
                        No
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmDeleteClassId(activeClass.id)}
                      className="px-3 py-1.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 font-display font-semibold text-xs flex items-center gap-1.5 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Eliminar</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {/* Asignar y ver Retos del Grupo */}
                <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col gap-3">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-[#126B73]" />
                    <h3 className="font-display font-bold text-sm text-[#0A1D2C]">
                      Retos y Tareas Asignadas ({(activeClass.challenges || []).length})
                    </h3>
                  </div>

                  <form
                    onSubmit={handleCreateGroupChallenge}
                    className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] flex flex-col gap-2"
                  >
                    <span className="text-[11px] font-display font-bold text-[#0A1D2C]">
                      Asignar nuevo reto a todo el grupo
                    </span>
                    <div className="grid grid-cols-3 gap-2">
                      <select
                        value={chalTopicId}
                        onChange={(e) => setChalTopicId(e.target.value)}
                        className="col-span-2 text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                      >
                        {TOPIC_OPTIONS.map((t) => (
                          <option key={t.id} value={t.id}>
                            {t.label}
                          </option>
                        ))}
                      </select>
                      <select
                        value={chalTarget}
                        onChange={(e) => setChalTarget(Number(e.target.value))}
                        className="text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                      >
                        {[1, 2, 3, 4, 5].map((n) => (
                          <option key={n} value={n}>
                            Meta: {n}
                          </option>
                        ))}
                      </select>
                    </div>
                    <input
                      type="text"
                      value={chalTitle}
                      onChange={(e) => setChalTitle(e.target.value)}
                      placeholder="Título del reto (opcional)"
                      className="text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                    />
                    <input
                      type="text"
                      value={chalInstructions}
                      onChange={(e) => setChalInstructions(e.target.value)}
                      placeholder="Indicaciones para tus alumnos (opcional)"
                      className="text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                    />
                    <button
                      type="submit"
                      disabled={chalSubmitting}
                      className="py-2 rounded-full bg-[#126B73] text-white text-xs font-display font-bold flex items-center justify-center gap-1.5 shadow-[0_2px_0_#005158] cursor-pointer disabled:opacity-50"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>{chalSubmitting ? 'Asignando...' : 'Asignar Reto al Grupo'}</span>
                    </button>
                  </form>

                  {(activeClass.challenges || []).length === 0 ? (
                    <p className="text-xs text-[#596B72] text-center py-3">
                      Aún no hay retos asignados en este grupo.
                    </p>
                  ) : (
                    <div className="flex flex-col gap-2">
                      {(activeClass.challenges || []).map((ch) => (
                        <div
                          key={ch.id}
                          className="p-3 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] flex items-start justify-between gap-2"
                        >
                          <div className="min-w-0">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              <span className="font-display font-bold text-xs text-[#0A1D2C]">
                                {ch.title}
                              </span>
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  ch.isPersonal
                                    ? 'bg-[#E76D55]/15 text-[#E76D55]'
                                    : 'bg-[#DCEFEB] text-[#126B73]'
                                }`}
                              >
                                {ch.isPersonal ? `Para ${ch.studentName}` : 'Todo el grupo'}
                              </span>
                            </div>
                            <p className="text-[11px] text-[#596B72] mt-0.5">{ch.instructions}</p>
                            <span className="text-[10px] font-semibold text-[#126B73] block mt-1">
                              Avance: {ch.completedByCount}/{ch.assignedCount} completaron (meta:{' '}
                              {ch.targetExercises} ej.) · {ch.createdAt}
                            </span>
                          </div>
                          <button
                            onClick={() => handleDeleteChallenge(ch.id)}
                            title="Eliminar reto"
                            className="p-1.5 text-[#596B72] hover:text-rose-600 cursor-pointer shrink-0"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ================================================================= */}
          {/* PESTAÑA 3: DIAGNÓSTICO ALUMNOS (Directorio, Filtros y Análisis)   */}
          {/* ================================================================= */}
          {activeTab === 'alumnos' && (
            <div className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] flex flex-col gap-3.5">
              {/* Buscador + filtros + orden */}
              <div className="flex flex-col md:flex-row gap-2.5 md:items-center justify-between">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-[#596B72] absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={studentSearch}
                    onChange={(e) => setStudentSearch(e.target.value)}
                    placeholder="Buscar estudiante por nombre o correo..."
                    className="w-full text-xs pl-9 pr-3 py-2 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={studentSort}
                    onChange={(e) =>
                      setStudentSort(e.target.value as 'priority' | 'xp' | 'completed' | 'name')
                    }
                    className="text-xs px-3 py-2 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none font-display font-medium"
                  >
                    <option value="priority">Orden: Prioridad de apoyo</option>
                    <option value="xp">Orden: Mayor XP</option>
                    <option value="completed">Orden: Más retos resueltos</option>
                    <option value="name">Orden: Alfabético (A-Z)</option>
                  </select>
                </div>
              </div>

              {/* Chips de estado */}
              <div className="flex gap-1.5 flex-wrap">
                {(
                  [
                    'todos',
                    'Requiere apoyo',
                    'Sin actividad',
                    'Al corriente',
                    'Destacado',
                  ] as const
                ).map((st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-3 py-1 rounded-full text-[11px] font-display font-bold border transition-colors cursor-pointer ${
                      statusFilter === st
                        ? 'bg-[#126B73] text-white border-[#126B73]'
                        : 'bg-[#F7F5EF] text-[#596B72] border-[#E8E5DC] hover:border-[#126B73]'
                    }`}
                  >
                    {st === 'todos' ? 'Todos' : st}
                  </button>
                ))}
              </div>

              {/* Lista de estudiantes analizada */}
              {filteredDirectory.length === 0 ? (
                <div className="p-8 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl border border-dashed border-[#D8E2DC] flex flex-col items-center gap-2">
                  <GraduationCap className="w-6 h-6 text-[#126B73]" />
                  <span>
                    {students.length === 0
                      ? 'Todavía no hay alumnos inscritos en este grupo.'
                      : 'No hay alumnos que coincidan con tu búsqueda o filtro.'}
                  </span>
                </div>
              ) : (
                <div className="flex flex-col gap-2.5">
                  {filteredDirectory.map(({ st, cls }) => (
                    <div
                      key={`${cls.id}-${st.studentId}`}
                      className="p-3.5 rounded-xl bg-[#F7F5EF] border border-[#E8E5DC] hover:border-[#126B73]/50 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-display font-bold text-sm text-[#0A1D2C]">
                            {st.studentName}
                          </span>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              st.statusLabel === 'Requiere apoyo'
                                ? 'bg-rose-100 text-rose-800'
                                : st.statusLabel === 'Sin actividad'
                                  ? 'bg-slate-200 text-slate-700'
                                  : st.statusLabel === 'Destacado'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : 'bg-[#DCEFEB] text-[#126B73]'
                            }`}
                          >
                            {st.statusLabel || 'Al corriente'}
                          </span>
                          {scopeAllClasses && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white border border-[#E8E5DC] text-[#596B72]">
                              {cls.name}
                            </span>
                          )}
                        </div>

                        <p className="text-[11px] text-[#596B72] mt-0.5">
                          {st.gradeLabel || 'Estudiante'}
                          {st.email ? ` · ${st.email}` : ''} · Última act.: {st.lastActive}
                        </p>

                        <div className="flex flex-wrap gap-3 mt-1.5 text-[11px] font-medium text-[#0A1D2C]">
                          <span>
                            Precisión: <strong>{st.accuracy}%</strong>
                          </span>
                          <span>
                            Retos resueltos: <strong>{st.completedExercises}</strong> (
                            {st.totalAttempts ?? st.completedExercises} intentos)
                          </span>
                          <span>
                            XP: <strong className="text-[#126B73]">{st.xp || 0}</strong>
                          </span>
                          <span>
                            Pistas: <strong>{st.hintsUsedTotal ?? 0}</strong>
                          </span>
                        </div>

                        {st.needsHelpWith.length > 0 && (
                          <div className="flex items-center gap-1 mt-1.5 text-[11px] text-rose-800">
                            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                            <span>Reforzar: {st.needsHelpWith.join(', ')}</span>
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => openStudentModal(st, cls)}
                        className="shrink-0 px-3.5 py-2 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-1.5 shadow-[0_2px_0_#005158] cursor-pointer"
                      >
                        <span>Ver análisis y asignar</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Modal Ficha Detallada del Estudiante */}
      {selectedStudentDetail && (
        <StudentDetailModal
          student={selectedStudentDetail}
          classId={selectedStudentDetail.classId || activeClass?.id}
          onClose={() => setSelectedStudentDetail(null)}
          onClassUpdated={syncClassInState}
          onRemoveStudent={handleRemoveStudent}
        />
      )}

      {/* Modal Crear o Editar Clase */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 border border-[#E8E5DC] shadow-xl flex flex-col gap-3.5">
            <h3 className="font-display font-bold text-lg text-[#0A1D2C]">
              {editingClass ? `Editar Grupo: ${editingClass.name}` : 'Crear Nuevo Grupo'}
            </h3>

            {!createdCode ? (
              <form onSubmit={handleSaveClass} className="flex flex-col gap-3">
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
                    <option value="matematicas">Matemáticas</option>
                    <option value="espanol">Español</option>
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
                      {(newNivel === 'secundaria' ? [1, 2, 3] : [1, 2, 3, 4, 5, 6]).map((g) => (
                        <option key={g} value={g}>
                          {newNivel === 'secundaria' ? `${g}° año` : `${g}° semestre`}
                        </option>
                      ))}
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
                    {editingClass ? 'Guardar Cambios' : 'Generar Código'}
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
