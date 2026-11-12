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

export interface BackendProfile {
  id: number; username: string; first_name: string; last_name: string; alias: string;
  email: string; rol: 'estudiante' | 'docente' | 'admin';
  estado: string; email_status: 'legacy' | 'pending' | 'verified';
  nivel: '' | 'secundaria' | 'bachillerato'; grado: number | null;
  xp: number; streak_days: number;
}
export type ProfileChanges = Pick<BackendProfile, 'first_name' | 'last_name' | 'alias'> &
  Partial<Pick<BackendProfile, 'nivel' | 'grado' | 'estado'>>;
