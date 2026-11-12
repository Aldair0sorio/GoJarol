import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import type { ClassGroup } from '../../types/curriculum';
import type { DetailedStudent } from '../../types/leagues';
import {
  X,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Sparkles,
  Flame,
  Send,
  BookOpen,
  Clock,
  Target,
  Trash2,
} from 'lucide-react';

const TOPIC_OPTIONS = [
  { id: 'mat_fracciones', label: 'Fracciones Equivalentes y Suma' },
  { id: 'mat_ecuaciones', label: 'Ecuaciones Lineales de 1er Grado' },
  { id: 'mat_porcentajes', label: 'Porcentajes y Proporcionalidad' },
  { id: 'esp_comprension', label: 'Comprensión Lectora' },
  { id: 'esp_ortografia', label: 'Ortografía Puntual y Grafías' },
  { id: 'esp_acentuacion', label: 'Reglas de Acentuación' },
];

interface StudentDetailModalProps {
  student: DetailedStudent;
  classId?: string;
  onClose: () => void;
  onClassUpdated?: (updatedClass: ClassGroup) => void;
  onRemoveStudent?: (classId: string, studentId: string) => void;
}

export const StudentDetailModal: React.FC<StudentDetailModalProps> = ({
  student,
  classId,
  onClose,
  onClassUpdated,
  onRemoveStudent,
}) => {
  const [detail, setDetail] = useState<DetailedStudent>(student);
  const [loadingLive, setLoadingLive] = useState(Boolean(classId));

  // Formulario real de reto personalizado
  const [showAssignForm, setShowAssignForm] = useState(false);
  const defaultWeakTopic =
    student.topics?.find((t) => t.status === 'Requiere refuerzo')?.topicId || 'mat_fracciones';
  const [assignTopicId, setAssignTopicId] = useState(defaultWeakTopic);
  const [assignTitle, setAssignTitle] = useState('');
  const [assignNotes, setAssignNotes] = useState('');
  const [assignTarget, setAssignTarget] = useState(2);
  const [assignSubmitting, setAssignSubmitting] = useState(false);
  const [assignFeedback, setAssignFeedback] = useState<{ ok: boolean; msg: string } | null>(null);
  const [confirmRemove, setConfirmRemove] = useState(false);

  const effectiveClassId = classId || student.classId;

  useEffect(() => {
    setDetail(student);
    if (!effectiveClassId) {
      setLoadingLive(false);
      return;
    }
    let mounted = true;
    setLoadingLive(true);
    apiService
      .getStudentAnalysis(effectiveClassId, student.id)
      .then((fresh) => {
        if (mounted && fresh) {
          setDetail(fresh);
          const weak = fresh.topics?.find((t) => t.status === 'Requiere refuerzo')?.topicId;
          if (weak) setAssignTopicId(weak);
        }
      })
      .finally(() => {
        if (mounted) setLoadingLive(false);
      });
    return () => {
      mounted = false;
    };
  }, [effectiveClassId, student]);

  const handleAssignPersonalChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!effectiveClassId) return;
    setAssignSubmitting(true);
    setAssignFeedback(null);

    const topicName =
      TOPIC_OPTIONS.find((t) => t.id === assignTopicId)?.label || assignTopicId;
    const res = await apiService.assignClassChallenge(effectiveClassId, {
      topic_id: assignTopicId,
      student_id: detail.id,
      title: assignTitle.trim() || `Refuerzo personalizado: ${topicName}`,
      instructions:
        assignNotes.trim() ||
        `Practica ${topicName} con Jarol y pide pistas paso a paso si te atoras.`,
      target_exercises: assignTarget,
    });

    setAssignSubmitting(false);
    if (res.success && res.classGroup) {
      if (onClassUpdated) onClassUpdated(res.classGroup);
      setAssignFeedback({
        ok: true,
        msg: `Reto asignado en PostgreSQL a ${detail.name}. Ya le aparece en su pestaña Mis Clases.`,
      });
      setShowAssignForm(false);
      setAssignTitle('');
      setAssignNotes('');
      const refreshed = await apiService.getStudentAnalysis(effectiveClassId, detail.id);
      if (refreshed) setDetail(refreshed);
    } else {
      setAssignFeedback({
        ok: false,
        msg: res.error || 'No se pudo asignar el reto.',
      });
    }
  };

  const topics = detail.topics || [];
  const attempts = detail.recentAttempts || [];
  const recs = detail.recommendations || [];
  const assignedChallenges = detail.assignedChallenges || [];

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-3">
      <div className="bg-[#F7F5EF] rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto border border-[#E8E5DC] shadow-2xl flex flex-col animate-scaleUp">
        {/* Header */}
        <div className="sticky top-0 bg-[#F7F5EF] p-4 pb-3 border-b border-[#E8E5DC] flex items-center justify-between z-10">
          <div className="flex items-center gap-3 min-w-0">
            <img
              src={detail.avatarUrl || '/mascot/jarol-crab.png'}
              alt={detail.name}
              className="w-12 h-12 rounded-full object-cover ring-2 ring-[#126B73]/30 shrink-0"
            />
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="font-display font-extrabold text-base text-[#0A1D2C] truncate">
                  {detail.name}
                </h2>
                {detail.statusLabel && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      detail.statusLabel === 'Requiere apoyo'
                        ? 'bg-rose-100 text-rose-800'
                        : detail.statusLabel === 'Destacado'
                          ? 'bg-emerald-100 text-emerald-800'
                          : detail.statusLabel === 'Sin actividad'
                            ? 'bg-slate-200 text-slate-700'
                            : 'bg-[#DCEFEB] text-[#126B73]'
                    }`}
                  >
                    {detail.statusLabel}
                  </span>
                )}
              </div>
              <span className="text-xs text-[#596B72] block truncate">
                {detail.grade} · {detail.school}
              </span>
              {detail.email && (
                <span className="text-[11px] text-[#596B72] block truncate">{detail.email}</span>
              )}
              <div className="flex items-center gap-3 text-[10px] text-[#596B72] mt-0.5">
                {detail.joinedAt && <span>Inscrito: {detail.joinedAt}</span>}
                {detail.lastActive && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Última act.: {detail.lastActive}
                  </span>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-[#E8E5DC] flex items-center justify-center text-[#596B72] hover:text-[#0A1D2C] active:scale-95 transition-transform cursor-pointer shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 flex flex-col gap-3.5">
          {loadingLive && (
            <div className="text-[11px] text-[#126B73] bg-[#DCEFEB]/50 px-3 py-1.5 rounded-lg text-center font-medium">
              Actualizando métricas en tiempo real desde PostgreSQL...
            </div>
          )}

          {/* Métricas principales */}
          <div className="grid grid-cols-4 gap-2">
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Precisión</span>
              <span
                className={`font-display font-extrabold text-base ${
                  detail.accuracy >= 70
                    ? 'text-emerald-700'
                    : detail.accuracy > 0
                      ? 'text-amber-700'
                      : 'text-slate-600'
                }`}
              >
                {detail.accuracy}%
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Resueltos</span>
              <span className="font-display font-extrabold text-base text-[#0A1D2C]">
                {detail.completedExercises ?? 0}
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Total XP</span>
              <div className="flex items-center justify-center gap-1 font-display font-extrabold text-base text-[#126B73]">
                <Sparkles className="w-3.5 h-3.5 text-[#E4AA50] fill-[#E4AA50]" />
                <span>{detail.totalXP}</span>
              </div>
            </div>
            <div className="p-2.5 rounded-xl bg-white border border-[#E8E5DC] text-center">
              <span className="text-[10px] text-[#596B72] font-medium block">Racha / Pistas</span>
              <div className="flex items-center justify-center gap-1 font-display font-extrabold text-xs text-amber-700 mt-1">
                <Flame className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                <span>{detail.streakDays}d</span>
                <span className="text-[#596B72] font-normal">· {detail.hintsUsedTotal ?? 0}p</span>
              </div>
            </div>
          </div>

          {/* Recomendaciones pedagógicas */}
          {recs.length > 0 && (
            <div className="p-3 rounded-xl bg-[#DCEFEB]/55 border border-[#126B73]/25 flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-xs font-display font-bold text-[#0A1D2C]">
                <Lightbulb className="w-3.5 h-3.5 text-[#126B73]" />
                <span>Análisis y Recomendación Pedagógica</span>
              </div>
              {recs.map((rec, i) => (
                <p key={i} className="text-[11px] text-[#0A1D2C] leading-relaxed">
                  • {rec}
                </p>
              ))}
            </div>
          )}

          {/* Dominio tema por tema */}
          {topics.length > 0 && (
            <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C] flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5 text-[#126B73]" />
                  <span>Desempeño por Tema</span>
                </h3>
                <span className="text-[10px] text-[#596B72]">
                  {detail.totalAttempts ?? 0} intentos totales
                </span>
              </div>

              <div className="flex flex-col gap-2">
                {topics.map((t) => (
                  <div
                    key={t.topicId}
                    className="p-2.5 rounded-lg bg-[#F7F5EF] border border-[#E8E5DC] flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <span className="font-display font-bold text-xs text-[#0A1D2C] block truncate">
                          {t.name}
                        </span>
                        <span className="text-[10px] text-[#596B72]">
                          {t.completedExercises}/{t.totalExercises} retos · {t.correctAttempts}/
                          {t.attempts} aciertos ({t.accuracy}%) · Nv. {t.difficulty}
                          {t.hintsUsed > 0 ? ` · ${t.hintsUsed} pistas` : ''}
                        </span>
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                          t.status === 'Dominado'
                            ? 'bg-emerald-100 text-emerald-800'
                            : t.status === 'Requiere refuerzo'
                              ? 'bg-rose-100 text-rose-800'
                              : t.status === 'En curso'
                                ? 'bg-[#DCEFEB] text-[#126B73]'
                                : 'bg-slate-200 text-slate-600'
                        }`}
                      >
                        {t.status}
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-white rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          t.status === 'Requiere refuerzo'
                            ? 'bg-rose-500'
                            : t.status === 'Dominado'
                              ? 'bg-emerald-600'
                              : 'bg-[#126B73]'
                        }`}
                        style={{ width: `${t.mastery}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Competencias consolidadas y débiles */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2">
            <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C]">
              Resumen de Competencias
            </h3>

            <div className="flex flex-col gap-1">
              <span className="text-[11px] font-semibold text-emerald-800">
                Competencias consolidadas:
              </span>
              {detail.masteredTopics.length === 0 ? (
                <span className="text-[11px] text-[#596B72] italic">
                  Aún no completa el 75% de dominio en ningún tema.
                </span>
              ) : (
                detail.masteredTopics.map((topic, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-xs text-[#0A1D2C]">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{topic}</span>
                  </div>
                ))
              )}
            </div>

            <div className="flex flex-col gap-1 pt-2 border-t border-[#E8E5DC]">
              <span className="text-[11px] font-semibold text-rose-800">
                Temas que requieren apoyo:
              </span>
              {detail.weakTopics.length === 0 ? (
                <span className="text-[11px] text-emerald-700 font-medium">
                  Sin rezagos críticos detectados hasta ahora.
                </span>
              ) : (
                detail.weakTopics.map((topic, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-1.5 text-xs text-rose-900 bg-rose-50 p-2 rounded-lg border border-rose-200"
                  >
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                    <span>{topic}</span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Retos asignados a este alumno */}
          {assignedChallenges.length > 0 && (
            <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2">
              <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C] flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-[#126B73]" />
                <span>Retos Asignados al Alumno</span>
              </h3>
              {assignedChallenges.map((ch) => (
                <div
                  key={ch.id}
                  className="p-2.5 rounded-lg bg-[#F7F5EF] border border-[#E8E5DC] flex items-center justify-between gap-2 text-xs"
                >
                  <div className="min-w-0">
                    <span className="font-display font-bold text-[#0A1D2C] block truncate">
                      {ch.title}{' '}
                      {ch.isPersonal && (
                        <span className="text-[10px] text-[#E76D55]">(Personalizado)</span>
                      )}
                    </span>
                    <span className="text-[10px] text-[#596B72]">
                      {ch.topicName} · Meta: {ch.solvedCount}/{ch.targetExercises} ejercicios
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                      ch.isCompleted
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {ch.isCompleted ? 'Completado' : 'Pendiente'}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Historial real cronológico de intentos */}
          <div className="p-3.5 rounded-xl bg-white border border-[#E8E5DC] flex flex-col gap-2.5">
            <h3 className="font-display font-bold text-xs uppercase tracking-wider text-[#0A1D2C]">
              Historial Real de Intentos ({attempts.length})
            </h3>

            {attempts.length === 0 ? (
              <div className="p-4 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl border border-dashed border-[#D8E2DC]">
                Este alumno aún no ha enviado respuestas en ejercicios interactivos.
              </div>
            ) : (
              <div className="flex flex-col gap-2 max-h-64 overflow-y-auto pr-1">
                {attempts.map((att) => (
                  <div
                    key={att.id}
                    className={`p-3 rounded-xl border text-xs flex flex-col gap-1 ${
                      att.isCorrect
                        ? 'bg-emerald-50/50 border-emerald-200'
                        : 'bg-amber-50/60 border-amber-200'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 font-display font-bold">
                      <span className="text-[#0A1D2C]">{att.exerciseTitle}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full shrink-0 ${
                          att.isCorrect
                            ? 'bg-emerald-200 text-emerald-900'
                            : 'bg-rose-200 text-rose-900'
                        }`}
                      >
                        {att.isCorrect ? 'Correcto' : 'Incorrecto'}
                      </span>
                    </div>

                    <p className="text-[#596B72] text-[11px]">
                      Respuesta enviada:{' '}
                      <strong className="text-[#0A1D2C]">{att.selectedOption}</strong>
                      {att.topicName ? ` · ${att.topicName}` : ''}
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

                    <span className="text-[10px] text-[#596B72]">{att.date}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {assignFeedback && (
            <div
              className={`p-2.5 rounded-xl text-xs font-medium border ${
                assignFeedback.ok
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
            >
              {assignFeedback.msg}
            </div>
          )}

          {/* Formulario real para asignar reto personalizado */}
          {showAssignForm ? (
            <form
              onSubmit={handleAssignPersonalChallenge}
              className="p-3.5 rounded-xl bg-white border-2 border-[#126B73]/40 flex flex-col gap-2.5"
            >
              <span className="font-display font-bold text-xs text-[#0A1D2C]">
                Nuevo reto personalizado para {detail.name}
              </span>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-bold text-[#596B72] block mb-1">
                    Tema a reforzar
                  </label>
                  <select
                    value={assignTopicId}
                    onChange={(e) => setAssignTopicId(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                  >
                    {TOPIC_OPTIONS.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-[#596B72] block mb-1">
                    Meta de ejercicios
                  </label>
                  <select
                    value={assignTarget}
                    onChange={(e) => setAssignTarget(Number(e.target.value))}
                    className="w-full text-xs p-2 rounded-lg border border-[#E8E5DC] bg-white focus:border-[#126B73] focus:outline-none"
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>
                        {n} {n === 1 ? 'ejercicio' : 'ejercicios'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <input
                type="text"
                value={assignTitle}
                onChange={(e) => setAssignTitle(e.target.value)}
                placeholder="Título opcional (ej. Repaso de suma de quebrados)"
                className="w-full text-xs p-2 rounded-lg border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
              />

              <textarea
                value={assignNotes}
                onChange={(e) => setAssignNotes(e.target.value)}
                rows={2}
                placeholder="Nota para el alumno (ej. Practica primero igual denominador antes de pasar al siguiente nivel)"
                className="w-full text-xs p-2 rounded-lg border border-[#E8E5DC] focus:border-[#126B73] focus:outline-none"
              />

              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setShowAssignForm(false)}
                  className="flex-1 py-2 rounded-full border border-[#E8E5DC] text-xs font-display font-semibold text-[#596B72] cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={assignSubmitting}
                  className="flex-1 py-2 rounded-full bg-[#126B73] text-white text-xs font-display font-bold shadow-[0_2px_0_#005158] cursor-pointer disabled:opacity-50"
                >
                  {assignSubmitting ? 'Guardando...' : 'Guardar y Asignar'}
                </button>
              </div>
            </form>
          ) : (
            <div className="flex flex-col gap-2">
              {effectiveClassId && (
                <button
                  onClick={() => setShowAssignForm(true)}
                  className="w-full py-3 rounded-full bg-[#126B73] text-white font-display font-bold text-xs flex items-center justify-center gap-2 shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] transition-all cursor-pointer"
                >
                  <Send className="w-4 h-4" />
                  <span>Asignar reto de refuerzo personalizado</span>
                </button>
              )}

              {effectiveClassId && onRemoveStudent && (
                confirmRemove ? (
                  <div className="flex items-center justify-between gap-2 p-2.5 rounded-xl bg-rose-50 border border-rose-200">
                    <span className="text-[11px] text-rose-800 font-medium">
                      ¿Dar de baja a {detail.name} de este grupo?
                    </span>
                    <div className="flex gap-1.5">
                      <button
                        onClick={() => setConfirmRemove(false)}
                        className="px-2.5 py-1 rounded-lg bg-white border border-[#E8E5DC] text-[11px] font-semibold text-[#596B72] cursor-pointer"
                      >
                        No
                      </button>
                      <button
                        onClick={() => {
                          onRemoveStudent(effectiveClassId, detail.id);
                          onClose();
                        }}
                        className="px-2.5 py-1 rounded-lg bg-rose-600 text-white text-[11px] font-bold cursor-pointer"
                      >
                        Sí, remover
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmRemove(true)}
                    className="w-full py-2 rounded-full border border-rose-200 text-rose-700 hover:bg-rose-50 font-display font-semibold text-xs flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Remover alumno de la clase</span>
                  </button>
                )
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
