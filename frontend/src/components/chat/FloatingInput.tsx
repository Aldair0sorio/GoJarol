import React, { useState } from 'react';
import { ArrowUp } from 'lucide-react';

interface FloatingInputProps {
  onSendMessage: (text: string) => void;
  isLoading?: boolean;
}

export const FloatingInput: React.FC<FloatingInputProps> = ({ onSendMessage, isLoading }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    onSendMessage(inputText.trim());
    setInputText('');
  };

  return (
    <div className="sticky bottom-14 inset-x-0 z-30 px-3 py-2 bg-gradient-to-t from-[#F7F5EF] via-[#F7F5EF]/90 to-transparent">
      <form
        onSubmit={handleSubmit}
        className="max-w-md mx-auto relative flex items-center bg-white rounded-full p-1.5 pl-4 border border-[#E8E5DC] shadow-[0_8px_20px_rgba(10,29,44,0.06),0_2px_0_#D2E5F9] focus-within:border-[#126B73] focus-within:shadow-[0_8px_24px_rgba(18,107,115,0.15),0_2px_0_#126B73] transition-all"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Pregúntale algo a Jarol..."
          disabled={isLoading}
          className="w-full bg-transparent text-sm text-[#0A1D2C] placeholder:text-[#596B72]/70 focus:outline-none pr-2"
        />

        <button
          type="submit"
          disabled={!inputText.trim() || isLoading}
          className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-[0_3px_0_#005158] active:translate-y-0.5 active:shadow-[0_1px_0_#005158] ${
            inputText.trim() && !isLoading
              ? 'bg-[#126B73] text-white cursor-pointer hover:bg-[#005158]'
              : 'bg-[#D2E5F9] text-[#596B72] cursor-not-allowed opacity-60'
          }`}
          aria-label="Enviar mensaje"
        >
          <ArrowUp className="w-5 h-5 stroke-[2.5px]" />
        </button>
      </form>
    </div>
  );
};
