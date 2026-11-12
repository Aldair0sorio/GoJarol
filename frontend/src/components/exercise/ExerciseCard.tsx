import React, { useState } from 'react';
import type { ExerciseCardData, AnswerFeedback } from '../../types/chat';
import { apiService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { CheckCircle2, AlertCircle, ArrowRight, Lightbulb, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';

interface ExerciseCardProps {
  exercise: ExerciseCardData;
  onNextExercise?: () => void;
}

export const ExerciseCard: React.FC<ExerciseCardProps> = ({ exercise, onNextExercise }) => {
  const { addXP } = useAuth();
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<AnswerFeedback | null>(null);

  const handleSelectOption = async (optionId: string) => {
    if (feedback?.isCorrect) return; // Ya resuelto correctamente

    setSelectedOption(optionId);
    setIsSubmitting(true);

    try {
      // Regla pedagógica: La solución se valida en el backend/servicio determinista
      const result = await apiService.submitExerciseAnswer(exercise.id, optionId);
      setFeedback(result);

      if (result.isCorrect) {
        addXP(result.xpEarned);
        // Confeti festivo
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.7 },
          colors: ['#126B73', '#E76D55', '#E4AA50', '#DCEFEB'],
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-4 border border-[#E8E5DC] shadow-[0_4px_16px_rgba(10,29,44,0.06)] flex flex-col gap-3.5 w-full overflow-hidden mt-2">
      {/* Top Header Badge & Counter */}
      <div className="flex items-center justify-between">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#DCEFEB] text-[#126B73]">
          <span className="text-xs font-display font-bold uppercase tracking-wider">
            {exercise.subjectName} • {exercise.topicName}
          </span>
        </div>
        <span className="text-xs font-display font-semibold text-[#596B72]">
          {exercise.step} / {exercise.totalSteps}
        </span>
      </div>

      {/* Question Prompt */}
      <div>
        <h3 className="font-display font-bold text-base text-[#0A1D2C] leading-snug">
          {exercise.question}
        </h3>
        <p className="text-xs text-[#596B72] mt-0.5">
          {exercise.instruction}
        </p>
      </div>

      {/* Options Group */}
      <div className="flex flex-col gap-2" role="radiogroup" aria-label="Opciones de respuesta">
        {exercise.options.map((opt) => {
          const isSelected = selectedOption === opt.id;
          const isCorrect = feedback?.isCorrect && isSelected;
          const isWrong = feedback && !feedback.isCorrect && isSelected;

          return (
            <button
              key={opt.id}
              onClick={() => handleSelectOption(opt.id)}
              disabled={isSubmitting || feedback?.isCorrect}
              className={`w-full flex items-center justify-between p-3 rounded-xl text-left transition-all active:translate-y-[1px] ${
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
                <span className="font-display font-semibold text-sm">
                  {opt.text}
                </span>
              </div>

              {isSelected && (
                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    isCorrect
                      ? 'bg-emerald-100 text-emerald-800'
                      : isWrong
                      ? 'bg-rose-100 text-rose-800'
                      : 'bg-white/80 text-[#126B73]'
                  }`}
                >
                  {isCorrect ? '+ ' + (feedback?.xpEarned || 30) + ' XP' : 'Tu elección'}
                </span>
              )}
            </button>
          );
        })}
      </div>

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
            <p className="text-[#3F484A] leading-relaxed">
              {feedback.explanation}
            </p>
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
          onClick={onNextExercise}
          className="w-full h-11 bg-[#E76D55] text-white rounded-full font-display font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_3px_0_#711707] active:translate-y-0.5 active:shadow-[0_1px_0_#711707] transition-all cursor-pointer mt-1"
        >
          <Sparkles className="w-4 h-4 fill-white" />
          <span>Siguiente reto de fracciones</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
