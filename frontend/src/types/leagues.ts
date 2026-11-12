export interface LeaderboardUser {
  rank: number;
  id: string;
  name: string;
  school: string;
  xp: number;
  avatarUrl: string;
  isCurrentUser?: boolean;
  streakDays: number;
}

export interface StudentExerciseAttempt {
  id: string;
  exerciseTitle: string;
  date: string;
  isCorrect: boolean;
  selectedOption: string;
  explanationGiven: string;
  hintUsed?: string;
}

export interface DetailedStudent {
  id: string;
  name: string;
  grade: string;
  school: string;
  avatarUrl: string;
  totalXP: number;
  accuracy: number;
  streakDays: number;
  weakTopics: string[];
  masteredTopics: string[];
  recentAttempts: StudentExerciseAttempt[];
}
