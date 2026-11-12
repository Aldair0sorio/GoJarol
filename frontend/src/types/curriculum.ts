import type { StudentExerciseAttempt } from './leagues';

export interface Topic {
  id: string;
  name: string;
  description: string;
  isAvailable: boolean;
  progressPercent: number;
  prompt?: string;
}

export interface Subject {
  id: string;
  name: string;
  iconName: string;
  color: string;
  isAvailable: boolean;
  topics: Topic[];
}

export interface StudentTopicMetric {
  topicId: string;
  name: string;
  subject: string;
  mastery: number;
  accuracy: number;
  completedExercises: number;
  totalExercises: number;
  attempts: number;
  correctAttempts: number;
  hintsUsed: number;
  difficulty: number;
  status: 'Dominado' | 'En curso' | 'Requiere refuerzo' | 'Por iniciar';
  prompt: string;
}

export interface StudentMastery {
  studentId: string;
  studentName: string;
  email?: string;
  gradeLabel?: string;
  joinedAt?: string;
  completedExercises: number;
  totalAttempts?: number;
  accuracy: number;
  needsHelpWith: string[];
  masteredTopics?: string[];
  lastActive: string;
  xp?: number;
  streakDays?: number;
  hintsUsedTotal?: number;
  statusLabel?: 'Sin actividad' | 'Requiere apoyo' | 'Al corriente' | 'Destacado';
  topics?: StudentTopicMetric[];
  recentAttempts?: StudentExerciseAttempt[];
  recommendations?: string[];
}

export interface GroupTopicAnalytics {
  topicId: string;
  topicName: string;
  subjectName: string;
  activeStudents: number;
  masteredStudents: number;
  strugglingStudents: number;
  averageAccuracy: number;
  averageMastery: number;
  totalAttempts: number;
  totalHintsUsed: number;
  healthStatus: 'Sin datos' | 'Fortaleza' | 'En progreso' | 'Requiere refuerzo';
}

export interface ClassChallengeItem {
  id: string;
  topicId: string;
  topicName: string;
  subjectName: string;
  title: string;
  instructions: string;
  targetExercises: number;
  prompt: string;
  isPersonal: boolean;
  studentId?: string | null;
  studentName?: string | null;
  assignedCount: number;
  completedByCount: number;
  solvedCount: number;
  isCompleted: boolean;
  createdAt: string;
}

export interface ClassAnnouncementItem {
  id: string;
  title: string;
  message: string;
  authorName: string;
  createdAt: string;
}

export interface ClassGroup {
  id: string;
  name: string;
  teacherName: string;
  code: string;
  codeActive?: boolean;
  nivel?: 'secundaria' | 'bachillerato';
  grado?: number;
  subjectSlug?: string;
  studentCount: number;
  subject: string;
  averageMastery: number;
  totalCompletedExercises?: number;
  studentsAtRisk?: number;
  topicAnalytics?: GroupTopicAnalytics[];
  studentsDetail?: StudentMastery[];
  challenges?: ClassChallengeItem[];
  announcements?: ClassAnnouncementItem[];
  createdAt?: string;
}
