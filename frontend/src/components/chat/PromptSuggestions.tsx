import React from 'react';
import { Sparkles } from 'lucide-react';

interface PromptSuggestionsProps {
  onSelectPrompt: (prompt: string) => void;
}

export const PromptSuggestions: React.FC<PromptSuggestionsProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    'Explícame cómo sumar fracciones y ponme un ejercicio',
    'Ponme un ejercicio de ecuaciones de primer grado',
    'Explícame cómo calcular porcentajes y ponme un reto',
    'Dame un reto de comprensión lectora',
    'Ayúdame a practicar reglas de acentuación y ortografía',
  ];

  return (
    <div className="flex flex-col gap-2 w-full my-3">
      <div className="flex items-center gap-1.5 px-1 text-xs font-display font-semibold text-[#596B72]">
        <Sparkles className="w-3.5 h-3.5 text-[#E4AA50]" />
        <span>Sugerencias para empezar con la IA de Jarol:</span>
      </div>

      <div className="flex flex-col gap-2">
        {suggestions.map((text, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(text)}
            className="w-full text-left px-3.5 py-2.5 bg-white text-[#0A1D2C] rounded-xl border border-[#E8E5DC] shadow-[0_2px_0_#D2E5F9] hover:border-[#126B73] hover:text-[#126B73] active:translate-y-0.5 active:shadow-none transition-all text-xs font-display font-medium cursor-pointer"
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
};
