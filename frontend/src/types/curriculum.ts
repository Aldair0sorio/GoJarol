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

export interface StudentMastery {
  studentId: string;
  studentName: string;
  completedExercises: number;
  accuracy: number;
  needsHelpWith: string[];
  lastActive: string;
  xp?: number;
}

export interface ClassGroup {
  id: string;
  name: string;
  teacherName: string;
  code: string;
  studentCount: number;
  subject: string;
  averageMastery: number;
  studentsDetail?: StudentMastery[];
}
