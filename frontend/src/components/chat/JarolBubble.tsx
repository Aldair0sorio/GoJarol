import React from 'react';

interface JarolBubbleProps {
  text: string;
  timestamp?: string;
  badge?: string;
}

function renderFormattedText(raw: string): React.ReactNode {
  // Limpiar delimitadores LaTeX simples si existen y renderizar **negritas**
  const cleaned = raw.replace(/\$([^$]+)\$/g, '$1');
  const parts = cleaned.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return (
        <strong key={idx} className="font-display font-bold text-[#0A1D2C]">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <React.Fragment key={idx}>{part}</React.Fragment>;
  });
}

export const JarolBubble: React.FC<JarolBubbleProps> = ({ text, timestamp, badge }) => {
  return (
    <div className="flex items-start gap-2.5 w-full max-w-[92%] my-1">
      {/* Avatar de Jarol */}
      <div className="relative shrink-0 mt-0.5">
        <img
          src="/mascot/jarol-crab.png"
          alt="Jarol el Profe Cangrejo"
          className="w-9 h-9 rounded-full object-contain p-0.5 bg-[#DCEFEB] ring-2 ring-[#126B73]/20 shadow-xs"
        />
        <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-[#126B73] rounded-full border border-white"></div>
      </div>

      {/* Burbuja */}
      <div className="flex flex-col items-start min-w-0">
        <div className="bg-white text-[#0A1D2C] px-4 py-3 rounded-2xl rounded-tl-sm border border-[#E8E5DC] shadow-[0_2px_8px_rgba(10,29,44,0.04)] leading-relaxed text-sm">
          {badge && (
            <span className="inline-block text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#E76D55]/15 text-[#E76D55] mb-1.5">
              {badge}
            </span>
          )}
          <p className="whitespace-pre-line text-[#0A1D2C]">
            {renderFormattedText(text)}
          </p>
        </div>

        {timestamp && (
          <span className="text-[10px] text-[#596B72] mt-1 ml-1 font-medium">
            {timestamp}
          </span>
        )}
      </div>
    </div>
  );
};
