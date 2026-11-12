import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessage, ExerciseCardData } from '../../types/chat';
import { apiService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { JarolBubble } from '../../components/chat/JarolBubble';
import { UserBubble } from '../../components/chat/UserBubble';
import { FloatingInput } from '../../components/chat/FloatingInput';
import { PromptSuggestions } from '../../components/chat/PromptSuggestions';
import { ExerciseCard } from '../../components/exercise/ExerciseCard';
import { RotateCcw } from 'lucide-react';

interface ChatViewProps {
  initialPrompt?: string | null;
  onPromptConsumed?: () => void;
}

export const ChatView: React.FC<ChatViewProps> = ({ initialPrompt, onPromptConsumed }) => {
  const { user, isAuthenticated, updateUser, addXP } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const { replyText, exercise, xpEarned, totalXp } = await apiService.sendChatMessage(
        text,
        messages
      );

      if (totalXp !== undefined) {
        updateUser({ xp: totalXp });
      } else if (xpEarned && xpEarned > 0) {
        addXP(xpEarned);
      }

      const jarolMsg: ChatMessage = {
        id: `msg_j_${Date.now()}`,
        sender: 'jarol',
        text: replyText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        exercise,
      };

      setMessages((prev) => [...prev, jarolMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (initialPrompt) {
      handleSendMessage(initialPrompt);
      onPromptConsumed?.();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPrompt]);

  const handleNextExercise = (nextEx?: ExerciseCardData, topicName?: string) => {
    if (nextEx) {
      const jarolMsg: ChatMessage = {
        id: `msg_j_${Date.now()}`,
        sender: 'jarol',
        text: `¡Vientos! Aquí tienes el siguiente reto de **${nextEx.topicName}** (nivel ${nextEx.difficulty || 'Básico'}). Analízalo paso a paso:`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        exercise: nextEx,
      };
      setMessages((prev) => [...prev, jarolMsg]);
    } else {
      handleSendMessage(`Ponme otro ejercicio de ${topicName || 'este tema'}`);
    }
  };

  const handleResetChat = () => {
    setMessages([]);
    apiService.resetChatContext();
  };

  return (
    <div className="flex flex-col flex-1 pb-20 md:pb-6 max-w-md md:max-w-2xl lg:max-w-3xl mx-auto w-full">
      {/* Botón de limpiar chat si hay mensajes */}
      {messages.length > 0 && (
        <div className="flex justify-end px-4 pt-2">
          <button
            onClick={handleResetChat}
            className="flex items-center gap-1 text-[11px] font-display font-medium text-[#596B72] hover:text-[#126B73] px-2 py-1 rounded-full bg-white border border-[#E8E5DC] shadow-2xs cursor-pointer"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Nueva duda</span>
          </button>
        </div>
      )}

      {/* Hero inicial cuando no hay mensajes */}
      {messages.length === 0 && (
        <div className="flex flex-col items-center text-center px-4 pt-4 pb-2 select-none animate-fadeIn">
          {/* Mascota Jarol en tamaño destacado con micro-pill */}
          <div className="relative w-36 h-36 mb-2 flex items-center justify-center">
            <div className="absolute inset-0 bg-[#DCEFEB]/60 rounded-full blur-md"></div>
            <img
              src="/mascot/jarol-crab.png"
              alt="Jarol el Profe Cangrejo"
              className="relative w-32 h-32 object-contain drop-shadow-[0_8px_16px_rgba(10,29,44,0.1)] hover:scale-105 transition-transform"
            />
            <span className="absolute top-1 -right-1 inline-flex items-center px-2 py-0.5 rounded-full bg-[#E76D55] text-white font-display text-[11px] font-bold shadow-[0_2px_0_#711707]">
              ¡De volada! 🦀
            </span>
          </div>

          <h1 className="font-display font-extrabold text-2xl text-[#0A1D2C] tracking-tight">
            {isAuthenticated ? `¡Quiúbole, ${user.name.split(' ')[0]}! Soy Jarol` : '¡Quiúbole! Soy Jarol'}
          </h1>
          <h2 className="font-display font-semibold text-sm text-[#126B73] mt-0.5">
            ¿Qué vamos a aprender hoy?
          </h2>
          <p className="text-xs text-[#596B72] mt-1 max-w-[320px]">
            Pregúntame sobre Fracciones, Ecuaciones, Porcentajes, Comprensión Lectora, Ortografía o Acentuación. Te guío con pistas sin regalarte la respuesta.
          </p>

          <PromptSuggestions onSelectPrompt={handleSendMessage} />
        </div>
      )}

      {/* Lista de mensajes */}
      <div className="flex flex-col px-3 py-2 space-y-2">
        {messages.map((msg) => (
          <React.Fragment key={msg.id}>
            {msg.sender === 'jarol' ? (
              msg.exercise ? (
                <div className="w-full max-w-[96%] my-1">
                  <ExerciseCard
                    exercise={msg.exercise}
                    onNextExercise={(nextEx) =>
                      handleNextExercise(nextEx, msg.exercise?.topicName)
                    }
                  />
                </div>
              ) : (
                <JarolBubble text={msg.text} timestamp={msg.timestamp} />
              )
            ) : (
              <UserBubble text={msg.text} timestamp={msg.timestamp} />
            )}
          </React.Fragment>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs font-display text-[#126B73] p-3 bg-white/70 rounded-2xl w-fit border border-[#E8E5DC]">
            <span className="animate-spin text-base">🦀</span>
            <span>Jarol está analizando tu mensaje...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Barra de entrada de texto flotante */}
      <FloatingInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};
