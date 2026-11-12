import React, { useState } from 'react';
import type { ExerciseCardData, AnswerFeedback } from '../../types/chat';
import { apiService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import {
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Lightbulb,
  Sparkles,
  BookOpen,
  Send,
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { ConnectionNotice } from '../common/ConnectionNotice';
import { failureNotice } from '../../services/netMessages';

interface ExerciseCardProps {
  exercise: ExerciseCardData;
  onNextExercise?: (nextExercise?: ExerciseCardData) => void;
}

export const ExerciseCard: React.FC<ExerciseCardProps> = ({ exercise, onNextExercise }) => {
  const { addXP, updateUser } = useAuth();
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [openAnswer, setOpenAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<AnswerFeedback | null>(null);
  const [hintsList, setHintsList] = useState<string[]>([]);
  const [isLoadingHint, setIsLoadingHint] = useState(false);
  // Aviso de conexión: qué falló y cómo reintentarlo (la respuesta escrita se conserva en openAnswer).
  const [netError, setNetError] = useState<{ text: string; retry?: () => void } | null>(null);

  const isMultipleChoice =
    exercise.exerciseType === 'multiple_choice' ||
    (Array.isArray(exercise.options) && exercise.options.length > 0);

  const submitAnswer = async (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || feedback?.isCorrect || isSubmitting) return;

    setSelectedOption(trimmed);
    setIsSubmitting(true);
    setNetError(null);

    try {
      const response = await apiService.submitExerciseAnswer(exercise.id, trimmed);
      if (!response.ok) {
        // Sin evaluación del servidor: ni correcto ni incorrecto, ni XP.
        const notice = failureNotice(response.reason, 'respuesta');
        setSelectedOption(null);
        setNetError({ text: notice.text, retry: notice.canRetry ? () => submitAnswer(trimmed) : undefined });
        return;
      }
      const result = response.feedback;
      setFeedback(result);

      if (result.isCorrect) {
        if (result.totalXp !== undefined) {
          updateUser({ xp: result.totalXp });
        } else if (result.xpEarned > 0) {
          addXP(result.xpEarned);
        }
        confetti({
          particleCount: 55,
          spread: 65,
          origin: { y: 0.7 },
          colors: ['#126B73', '#E76D55', '#E4AA50', '#DCEFEB'],
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRequestHint = async () => {
    if (isLoadingHint || feedback?.isCorrect) return;
    setIsLoadingHint(true);
    setNetError(null);
    try {
      const res = await apiService.requestExerciseHint(exercise.id, hintsList.length);
      if (!res.ok) {
        const notice = failureNotice(res.reason, 'pista');
        setNetError({ text: notice.text, retry: notice.canRetry ? handleRequestHint : undefined });
        return;
      }
      if (res.hint) {
        setHintsList((prev) =>
          prev.includes(res.hint) ? prev : [...prev, res.hint]
        );
      }
    } finally {
      setIsLoadingHint(false);
    }
  };

  const placeholderByType = () => {
    // Ejemplos de formato que no coinciden con ninguna respuesta del banco (lo verifica el backend).
    if (exercise.exerciseType === 'fraction') return 'Ej. 5/7 o 2/9';
    if (exercise.exerciseType === 'percentage') return 'Ej. 45 o 45%';
    return 'Ej. 11 o x = 11';
  };

  return (
    <div className="bg-white rounded-2xl p-4 border border-[#E8E5DC] shadow-[0_4px_16px_rgba(10,29,44,0.06)] flex flex-col gap-3.5 w-full overflow-hidden mt-2">
      {/* Top Header Badge & Difficulty */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#DCEFEB] text-[#126B73]">
          <span className="text-xs font-display font-bold uppercase tracking-wider">
            {exercise.subjectName} • {exercise.topicName}
          </span>
        </div>
        <span className="text-xs font-display font-semibold text-[#596B72] bg-[#F7F5EF] px-2.5 py-0.5 rounded-full border border-[#E8E5DC]">
          {exercise.difficulty
            ? `Nivel ${exercise.difficulty}`
            : `${exercise.step || 1} / ${exercise.totalSteps || 3}`}
        </span>
      </div>

      {/* Optional Reading Text (for Reading Comprehension) */}
      {exercise.readingText && (
        <div className="bg-[#F7F5EF] border border-[#E8E5DC] rounded-xl p-3.5 text-xs md:text-sm text-[#0A1D2C] leading-relaxed">
          <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-[#126B73] mb-1.5">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Lectura de análisis</span>
          </div>
          <p className="italic text-[#2C3E46]">"{exercise.readingText}"</p>
        </div>
      )}

      {/* Question Prompt */}
      <div>
        <h3 className="font-display font-bold text-base text-[#0A1D2C] leading-snug">
          {exercise.question}
        </h3>
        <p className="text-xs text-[#596B72] mt-0.5">{exercise.instruction}</p>
      </div>

      {/* Multiple Choice Options OR Open SymPy Input */}
      {isMultipleChoice ? (
        <div className="flex flex-col gap-2" role="radiogroup" aria-label="Opciones de respuesta">
          {exercise.options.map((opt) => {
            const isSelected = selectedOption === opt.id;
            const isCorrect = feedback?.isCorrect && isSelected;
            const isWrong = feedback && !feedback.isCorrect && isSelected;

            return (
              <button
                key={opt.id}
                onClick={() => submitAnswer(opt.id)}
                disabled={isSubmitting || feedback?.isCorrect}
                className={`w-full flex items-center justify-between p-3 rounded-xl text-left transition-all active:translate-y-[1px] cursor-pointer ${
                  isCorrect
                    ? 'bg-emerald-50 border-2 border-emerald-500 shadow-[0_2px_0_#059669] text-emerald-900'
                    : isWrong
                    ? 'bg-rose-50 border-2 border-rose-400 shadow-[0_2px_0_#e11d48] text-rose-900'
                    : isSelected
                    ? 'bg-[#DCEFEB] border-2 border-[#126B73] shadow-[0_2px_0_#126B73] text-[#126B73]'
                    : 'bg-white border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9] text-[#0A1D2C] hover:bg-[#F7F5EF]'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 font-display font-bold text-xs ${
                      isCorrect
                        ? 'bg-emerald-500 text-white'
                        : isWrong
                        ? 'bg-rose-500 text-white'
                        : isSelected
                        ? 'bg-[#126B73] text-white'
                        : 'bg-[#F7F5EF] text-[#596B72]'
                    }`}
                  >
                    {isCorrect ? '✓' : opt.id}
                  </div>
                  <span className="font-display font-semibold text-sm">{opt.text}</span>
                </div>

                {isSelected && (
                  <span
                    className={`text-[11px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                      isCorrect
                        ? 'bg-emerald-100 text-emerald-800'
                        : isWrong
                        ? 'bg-rose-100 text-rose-800'
                        : 'bg-white/80 text-[#126B73]'
                    }`}
                  >
                    {isCorrect ? `+${feedback?.xpEarned || 30} XP` : 'Tu elección'}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitAnswer(openAnswer);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={openAnswer}
            onChange={(e) => setOpenAnswer(e.target.value)}
            disabled={isSubmitting || feedback?.isCorrect}
            placeholder={placeholderByType()}
            className="flex-1 h-11 px-3.5 rounded-xl bg-[#F7F5EF] border border-[#D8E2DC] text-sm font-semibold text-[#0A1D2C] placeholder:text-[#8E9B9E] focus:outline-none focus:border-[#126B73] focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={!openAnswer.trim() || isSubmitting || feedback?.isCorrect}
            className="h-11 px-4 rounded-xl bg-[#126B73] text-white font-display font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 shadow-[0_2px_0_#0A1D2C] hover:bg-[#0f5960] disabled:opacity-40 cursor-pointer transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Comprobar</span>
          </button>
        </form>
      )}

      {/* Aviso de conexión: la respuesta no se evaluó; se puede reintentar */}
      {netError && <ConnectionNotice text={netError.text} onRetry={netError.retry} />}

      {/* Progressive Hints Section */}
      {!feedback?.isCorrect && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={handleRequestHint}
              disabled={isLoadingHint}
              className="inline-flex items-center gap-1.5 text-xs font-display font-bold text-[#126B73] hover:text-[#0A1D2C] bg-[#F7F5EF] hover:bg-[#DCEFEB] px-3 py-1.5 rounded-full border border-[#D8E2DC] transition-colors cursor-pointer"
            >
              <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
              <span>
                {isLoadingHint
                  ? 'Pensando pista...'
                  : hintsList.length === 0
                  ? 'Pedir una pista paso a paso'
                  : `Pedir otra pista (${hintsList.length})`}
              </span>
            </button>
          </div>

          {hintsList.length > 0 && (
            <div className="flex flex-col gap-1.5">
              {hintsList.map((h, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-xs text-amber-950 bg-amber-50/90 border border-amber-200 px-3 py-2 rounded-xl"
                >
                  <Lightbulb className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Pista {i + 1}: </span>
                    <span>{h}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Feedback Banner (Formative & Pedagogical) */}
      {feedback && (
        <div
          className={`p-3.5 rounded-xl border flex items-start gap-2.5 ${
            feedback.isCorrect
              ? 'bg-[#DCEFEB]/60 border-[#126B73]/30 text-[#0A1D2C]'
              : 'bg-amber-50/90 border-amber-200 text-amber-950'
          }`}
        >
          {feedback.isCorrect ? (
            <CheckCircle2 className="w-5 h-5 text-[#126B73] shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          )}

          <div className="flex flex-col gap-1 text-xs">
            <span className="font-display font-bold text-sm text-[#0A1D2C]">
              {feedback.title}
            </span>
            <p className="text-[#3F484A] leading-relaxed">{feedback.explanation}</p>
            {feedback.hint && (
              <div className="mt-1 flex items-center gap-1.5 text-amber-800 bg-amber-100/70 px-2 py-1 rounded-md font-medium">
                <Lightbulb className="w-3.5 h-3.5 shrink-0" />
                <span>{feedback.hint}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Next Step Progression Action */}
      {feedback?.isCorrect && onNextExercise && (
        <button
          onClick={() => onNextExercise(feedback.nextExercise)}
          className="w-full h-11 bg-[#E76D55] text-white rounded-full font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_3px_0_#711707] active:translate-y-0.5 active:shadow-[0_1px_0_#711707] transition-all cursor-pointer mt-1"
        >
          <Sparkles className="w-4 h-4 fill-white" />
          <span>Siguiente reto de {exercise.topicName}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
