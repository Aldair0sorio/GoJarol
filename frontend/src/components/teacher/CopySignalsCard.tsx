import React, { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Info, RefreshCw, ShieldCheck } from 'lucide-react';
import { apiService } from '../../services/api';
import type { CopySignalStudent, CopySignalsReport } from '../../types/copySignals';

interface CopySignalsCardProps {
  classId: string;
}

type LoadState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; report: CopySignalsReport };

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

const SignalBadge: React.FC<{ signal: CopySignalStudent['copySignal'] }> = ({ signal }) =>
  signal === 'revisar' ? (
    <span className="inline-flex items-center gap-1 shrink-0 text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
      <AlertTriangle className="w-3 h-3" aria-hidden="true" />
      Revisar
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 shrink-0 text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
      <CheckCircle2 className="w-3 h-3" aria-hidden="true" />
      OK
    </span>
  );

/** Tarjeta del panel docente: ¿el grupo aprende con Jarol o le pide la respuesta? */
export const CopySignalsCard: React.FC<CopySignalsCardProps> = ({ classId }) => {
  // El panel monta la tarjeta con key={classId}: al cambiar de clase empieza otra vez en "cargando".
  const [state, setState] = useState<LoadState>({ status: 'loading' });

  const fetchReport = useCallback(
    () =>
      apiService
        .getCopySignals(classId)
        .then((result): LoadState =>
          result.ok ? { status: 'ready', report: result.report } : { status: 'error', message: result.error }
        ),
    [classId]
  );

  useEffect(() => {
    let active = true;
    fetchReport().then((next) => {
      if (active) setState(next);
    });
    return () => {
      active = false;
    };
  }, [fetchReport]);

  const load = () => {
    setState({ status: 'loading' });
    fetchReport().then(setState);
  };

  return (
    <section
      aria-labelledby="copy-signals-title"
      className="p-4 rounded-2xl bg-white border border-[#E8E5DC] shadow-[0_3px_0_#D2E5F9] min-w-0"
    >
      <div className="flex items-start gap-2 mb-1">
        <ShieldCheck className="w-4 h-4 text-[#126B73] shrink-0 mt-0.5" aria-hidden="true" />
        <h3 id="copy-signals-title" className="font-display font-bold text-sm text-[#0A1D2C] min-w-0">
          Señales de copia: ¿aprenden o copian?
        </h3>
      </div>
      <p className="text-[11px] text-[#596B72] mb-3">
        Últimos 7 días. Jarol no da resultados: aquí ves cuántas veces se pidió la respuesta directa frente a lo que
        cada alumno resolvió por su cuenta. Una señal es un indicio para conversar, no una acusación.
      </p>

      {state.status === 'loading' && (
        <div className="p-4 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl" role="status">
          Cargando señales del grupo…
        </div>
      )}

      {state.status === 'error' && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex flex-col gap-2" role="alert">
          <span>{state.message}</span>
          <button
            type="button"
            onClick={load}
            className="self-start inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-white border border-rose-300 font-display font-bold text-[11px] cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" aria-hidden="true" />
            Reintentar
          </button>
        </div>
      )}

      {state.status === 'ready' && <CopySignalsBody report={state.report} />}
    </section>
  );
};

const CopySignalsBody: React.FC<{ report: CopySignalsReport }> = ({ report }) => {
  const { totals, students } = report;
  const hasSignals =
    totals.answerRequests + totals.bypassAttempts + totals.stepsSolved + totals.hintsUsed > 0;

  const totalItems = [
    { label: 'Para conversar', value: totals.studentsToReview, strong: totals.studentsToReview > 0 },
    { label: 'Pidieron la respuesta directa', value: totals.answerRequests },
    { label: 'Intentos de saltarse las reglas', value: totals.bypassAttempts },
    { label: 'Pasos resueltos por su cuenta', value: totals.stepsSolved },
    { label: 'Pistas pedidas', value: totals.hintsUsed },
  ];

  return (
    <div className="flex flex-col gap-3 min-w-0">
      {!hasSignals ? (
        <div className="p-4 text-center text-xs text-[#596B72] bg-[#F7F5EF] rounded-xl border border-dashed border-[#D8E2DC]">
          Aún no hay señales en los últimos 7 días
        </div>
      ) : (
        <>
          <dl className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {totalItems.map((item) => (
              <div
                key={item.label}
                className={`p-2.5 rounded-xl border min-w-0 ${
                  item.strong ? 'bg-amber-50 border-amber-200' : 'bg-[#F7F5EF] border-[#E8E5DC]'
                }`}
              >
                <dt className="text-[10px] leading-tight text-[#596B72] break-words">{item.label}</dt>
                <dd className="font-display font-extrabold text-lg text-[#0A1D2C]">{item.value}</dd>
              </div>
            ))}
          </dl>

          <ul className="flex flex-col gap-2" aria-label="Señales por alumno">
            {students.map((st) => (
              <li
                key={st.id}
                className={`p-3 rounded-xl border min-w-0 ${
                  st.copySignal === 'revisar' ? 'bg-amber-50/60 border-amber-200' : 'bg-[#F7F5EF] border-transparent'
                }`}
              >
                <div className="flex items-center justify-between gap-2 min-w-0">
                  <span className="font-display font-bold text-xs text-[#0A1D2C] truncate min-w-0">{st.name}</span>
                  <SignalBadge signal={st.copySignal} />
                </div>
                <p className="text-[11px] text-[#596B72] mt-1 break-words">
                  {plural(st.answerRequests, 'pedido de respuesta', 'pedidos de respuesta')} ·{' '}
                  {plural(st.bypassAttempts, 'intento de saltar reglas', 'intentos de saltar reglas')} ·{' '}
                  {plural(st.stepsSolved, 'paso resuelto', 'pasos resueltos')} ·{' '}
                  {plural(st.hintsUsed, 'pista', 'pistas')}
                </p>
                {st.copySignal === 'revisar' && (
                  <p className="text-[11px] text-amber-900 mt-1 break-words">
                    {st.reason} Conversa con el alumno sobre qué paso se le complica.
                  </p>
                )}
              </li>
            ))}
          </ul>
        </>
      )}

      <div className="p-3 rounded-xl bg-[#DCEFEB]/50 border border-[#126B73]/20 text-[11px] text-[#0A1D2C] flex gap-2">
        <Info className="w-3.5 h-3.5 text-[#126B73] shrink-0 mt-0.5" aria-hidden="true" />
        <div className="min-w-0 break-words">
          <strong className="font-display">¿Cómo se calcula?</strong> {report.rule}
          <span className="block mt-1 text-[#596B72]">{report.privacyNote}</span>
        </div>
      </div>

      {report.recommendations.length > 0 && (
        <div className="min-w-0">
          <h4 className="font-display font-bold text-xs text-[#0A1D2C] mb-1">Recomendaciones</h4>
          <ul className="list-disc pl-4 flex flex-col gap-1 text-[11px] text-[#596B72]">
            {report.recommendations.map((rec) => (
              <li key={rec} className="break-words">
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
