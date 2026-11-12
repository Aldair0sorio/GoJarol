export interface ExerciseOption {
  id: string; // ej. "A", "B", "C", "D"
  label?: string;
  text: string;
}

export interface ExerciseCardData {
  id: string;
  topicId?: string;
  subjectName: string; // ej: "Aritmética · Matemáticas"
  topicName: string; // ej: "Fracciones Equivalentes y Suma"
  step?: number;
  totalSteps?: number;
  question: string;
  readingText?: string;
  instruction: string;
  exerciseType?: 'multiple_choice' | 'fraction' | 'numeric' | 'percentage';
  difficulty?: string;
  options: ExerciseOption[];
  xpReward?: number;
  // La respuesta correcta NUNCA viene en este objeto para cumplir la regla pedagógica del reto
}

export interface AnswerFeedback {
  isCorrect: boolean;
  title: string;
  explanation: string;
  hint?: string;
  xpEarned: number;
  totalXp?: number;
  nextExercise?: ExerciseCardData;
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
