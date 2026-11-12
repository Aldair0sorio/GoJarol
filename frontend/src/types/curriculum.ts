export interface Topic {
  id: string;
  name: string;
  description: string;
  isAvailable: boolean; // Solo Fracciones en el demo
  progressPercent: number;
}

export interface Subject {
  id: string;
  name: string;
  iconName: string;
  color: string;
  isAvailable: boolean;
  topics: Topic[];
}

export interface ClassGroup {
  id: string;
  name: string;
  teacherName: string;
  code: string;
  studentCount: number;
  subject: string;
  averageMastery: number; // Porcentaje de dominio (ej. 78%)
}

export interface StudentMastery {
  studentId: string;
  studentName: string;
  completedExercises: number;
  accuracy: number;
  needsHelpWith: string[]; // ej. ["Suma con diferente denominador"]
  lastActive: string;
}
