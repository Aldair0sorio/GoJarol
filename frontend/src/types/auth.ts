export type UserRole = 'student' | 'teacher' | 'admin';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  grade?: string; // Ej: "3° de Secundaria" o "Bachillerato 2do semestre"
  school?: string;
  xp?: number;
  streakDays?: number;
  avatarUrl?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}
