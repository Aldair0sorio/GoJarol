import type { ClassChallengeItem, StudentTopicMetric } from './curriculum';

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
  topicId?: string;
  topicName?: string;
  exerciseId?: string;
  exerciseTitle: string;
  date: string;
  isCorrect: boolean;
  selectedOption: string;
  explanationGiven: string;
  hintUsed?: string | null;
}

export interface DetailedStudent {
  id: string;
  classId?: string;
  name: string;
  email?: string;
  grade: string;
  school: string;
  avatarUrl: string;
  joinedAt?: string;
  lastActive?: string;
  totalXP: number;
  accuracy: number;
  streakDays: number;
  completedExercises?: number;
  totalAttempts?: number;
  hintsUsedTotal?: number;
  statusLabel?: string;
  weakTopics: string[];
  masteredTopics: string[];
  topics?: StudentTopicMetric[];
  recommendations?: string[];
  recentAttempts: StudentExerciseAttempt[];
  assignedChallenges?: ClassChallengeItem[];
}
