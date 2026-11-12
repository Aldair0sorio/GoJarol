export interface ExerciseOption {
  id: string; // ej. "A", "B", "C"
  text: string;
}

export interface ExerciseCardData {
  id: string;
  subjectName: string; // ej: "Aritmética"
  topicName: string; // ej: "Fracciones"
  step: number; // 1
  totalSteps: number; // 3
  question: string; // "¿Cuánto es 3/4 + 1/4?"
  instruction: string; // "Elige la opción que represente el resultado simplificado:"
  options: ExerciseOption[];
  xpReward: number; // 25
  // La respuesta correcta NUNCA viene en este objeto para cumplir la regla pedagógica del reto
}

export interface AnswerFeedback {
  isCorrect: boolean;
  title: string; // ej. "¡Exacto! ¡Bien rifado! 🦀" o "¡Casi! Vamos a revisarlo"
  explanation: string; // Explicación pedagógica paso a paso
  hint?: string; // Pista si se equivocó
  xpEarned: number;
}

export interface ChatMessage {
  id: string;
  sender: 'jarol' | 'user';
  text: string;
  timestamp: string;
  exercise?: ExerciseCardData;
  feedback?: AnswerFeedback;
  selectedOptionId?: string;
  isAnswerSubmitted?: boolean;
}
