import {
  MOCK_FEEDBACK_DB,
  MOCK_EXERCISE_FRACTIONS_1,
  MOCK_EXERCISE_FRACTIONS_2,
  MOCK_SUBJECTS,
  MOCK_CLASSES,
} from './mockData';
import type { AnswerFeedback, ChatMessage, ExerciseCardData } from '../types/chat';
import type { Subject, ClassGroup, StudentMastery } from '../types/curriculum';
import type { User, BackendProfile, ProfileChanges } from '../types/auth';

const API_BASE = '/api/v1';

// Token storage
export const getAuthToken = () => localStorage.getItem('jarol_token');
export const setAuthToken = (token: string) => localStorage.setItem('jarol_token', token);
export const removeAuthToken = () => localStorage.removeItem('jarol_token');

function getAuthHeaders(includeJson = true): Record<string, string> {
  const headers: Record<string, string> = {};
  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }
  const token = getAuthToken();
  if (isBackendToken(token)) headers['Authorization'] = `Token ${token}`;
  return headers;
}

const SUBJECT_META: Record<string, { iconName: string; color: string }> = {
  aritmetica: { iconName: 'Calculator', color: 'teal' },
  algebra: { iconName: 'Variable', color: 'indigo' },
  espanol: { iconName: 'BookOpen', color: 'amber' },
  matematicas: { iconName: 'Compass', color: 'blue' },
  historia: { iconName: 'Landmark', color: 'rose' },
  geografia: { iconName: 'Globe', color: 'emerald' },
  fisica: { iconName: 'Atom', color: 'purple' },
  quimica: { iconName: 'FlaskConical', color: 'cyan' },
  biologia: { iconName: 'Dna', color: 'green' },
};

const TOPIC_DESCRIPTIONS: Record<string, { description: string; prompt: string }> = {
  mat_fracciones: {
    description: 'Suma, resta, simplificación y comparación de fracciones con pistas paso a paso.',
    prompt: 'Ponme un ejercicio de fracciones',
  },
  mat_porcentajes: {
    description: 'Cálculo de descuentos, incrementos y proporciones en situaciones cotidianas.',
    prompt: 'Ponme un ejercicio de porcentajes',
  },
  mat_ecuaciones: {
    description: 'Despeje de la incógnita x en ecuaciones lineales de primer grado con una o dos operaciones.',
    prompt: 'Ponme un ejercicio de ecuaciones',
  },
  esp_comprension: {
    description: 'Identificación de idea principal, información explícita e inferencias a partir de textos.',
    prompt: 'Ponme un ejercicio de comprensión lectora',
  },
  esp_ortografia: {
    description: 'Uso correcto de grafías (b/v, c/s/z, g/j) y signos de puntuación en contexto.',
    prompt: 'Ponme un ejercicio de ortografía',
  },
  esp_acentuacion: {
    description: 'Clasificación y tildación de palabras agudas, graves, esdrújulas y acento diacrítico.',
    prompt: 'Ponme un ejercicio de acentuación',
  },
};

export interface TopicProgressItem {
  topicId: string;
  name: string;
  subject: string;
  mastery: number;
  completedExercises: number;
  totalExercises: number;
  attempts: number;
  correctAttempts: number;
  difficulty: number;
  status: 'Dominado' | 'En curso' | 'Requiere refuerzo' | 'Por iniciar';
  prompt: string;
}

export interface StudentProgressSummary {
  xp: number;
  streakDays: number;
  completedCount: number;
  totalAttempts: number;
  accuracy: number;
  needsHelpWith: string[];
  topics: TopicProgressItem[];
}

export interface LeaderboardEntry {
  id: string;
  rank: number;
  name: string;
  username?: string;
  grade: string;
  xp: number;
  streakDays: number;
  isCurrentUser?: boolean;
}

function mapBackendClassToGroup(item: Record<string, unknown>): ClassGroup {
  const rawStudents = Array.isArray(item.students_detail) ? item.students_detail : [];
  const studentsDetail: StudentMastery[] = rawStudents.map((st: Record<string, unknown>) => ({
    studentId: String(st.id || ''),
    studentName: String(st.name || st.username || 'Estudiante'),
    completedExercises: Number(st.completedExercises || 0),
    accuracy: Number(st.accuracy || 0),
    needsHelpWith: Array.isArray(st.needsHelpWith)
      ? st.needsHelpWith.map(String)
      : ['Sin alertas activas'],
    lastActive: String(st.lastActive || 'Reciente'),
    xp: Number(st.xp || 0),
  }));

  const avgMastery =
    studentsDetail.length > 0
      ? Math.round(
          studentsDetail.reduce((acc, s) => acc + (s.accuracy || 0), 0) / studentsDetail.length
        )
      : 0;

  return {
    id: String(item.id || ''),
    name: String(item.nombre || item.name || 'Grupo Escolar'),
    teacherName: String(item.docente || item.teacherName || 'Docente'),
    code: String(item.codigo || item.code || ''),
    studentCount: Number(item.estudiantes ?? item.studentCount ?? studentsDetail.length),
    subject: String(item.subject_nombre || item.subject || 'Matemáticas y Español'),
    averageMastery: Number(item.averageMastery ?? avgMastery),
    studentsDetail,
  };
}

export const apiService = {
  /**
   * Inicia sesión o registra usuario mediante Google OAuth.
   */
  async loginWithGoogle(payload: {
    credential: string;
    role: 'student' | 'teacher';
    nivel?: 'secundaria' | 'bachillerato';
    grado?: number;
  }): Promise<{ success: boolean; token?: string; user?: User; error?: string }> {
    try {
      const res = await fetch(`${API_BASE}/auth/google/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: payload.credential,
          role: payload.role === 'teacher' ? 'docente' : 'estudiante', nivel: payload.nivel, grado: payload.grado }),
      });
      const data = await res.json();
      if (!res.ok || !isBackendToken(data.token) || !data.user?.id || !['estudiante', 'docente', 'admin'].includes(data.user.rol)) {
        return { success: false, error: data.error?.message || 'Google no pudo verificar tu cuenta. Usa tu contraseña o intenta de nuevo.' };
      }
      return { success: true, token: data.token, user: profileToUser(data.user) };
    } catch {
      return { success: false, error: 'No se pudo conectar con Google. No se inició ninguna sesión.' };
    }
  },

  /**
   * Inicia sesión tradicional con usuario/correo y contraseña.
   */
  async login(credentials: {
    username: string;
    password?: string;
  }): Promise<{ success: boolean; token?: string; user?: User; verificationRequired?: boolean; error?: string }> {
    try {
      const res = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: credentials.username.trim(),
          password: credentials.password || '',
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (!isBackendToken(data.token) || !data.user?.id || !['estudiante', 'docente', 'admin'].includes(data.user.rol)) {
          return { success: false, error: 'El servidor no devolvió una sesión válida.' };
        }
        setAuthToken(data.token);
        return { success: true, token: data.token, user: profileToUser(data.user) };
      } else {
        const err = await res.json().catch(() => ({}));
        const msg = err.error?.message || err.detail || 'Usuario o contraseña incorrectos.';
        return { success: false, verificationRequired: err.verification_required === true, error: msg };
      }
    } catch {
      return {
        success: false,
        error: 'No se pudo conectar con el servidor de autenticación.',
      };
    }
  },

  /**
   * Registra un nuevo estudiante o docente en el backend.
   */
  async register(payload: {
    username: string; email: string; password: string; passwordConfirm: string;
    fullName: string; role: 'student' | 'teacher'; nivel?: 'secundaria' | 'bachillerato';
    grado?: number; estado: string;
  }): Promise<{ success: boolean; verificationRequired?: boolean; emailSent?: boolean; error?: string }> {
    try {
      const response = await fetch(`${API_BASE}/auth/register/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: payload.username.trim(), email: payload.email.trim(),
          password: payload.password, password_confirm: payload.passwordConfirm, full_name: payload.fullName.trim(),
          rol: payload.role === 'teacher' ? 'docente' : 'estudiante', nivel: payload.nivel,
          grado: payload.grado, estado: payload.estado }),
      });
      const data = await response.json();
      if (response.ok && data.verification_required === true && data.email_sent === true) {
        return { success: true, verificationRequired: true, emailSent: true };
      }
      return { success: false, verificationRequired: data.account_created === true,
        emailSent: false, error: authError(data, 'No se pudo crear la cuenta.') };
    } catch {
      return { success: false, error: 'No pudimos confirmar el registro. Comprueba tu conexión; antes de repetirlo puedes solicitar un reenvío.' };
    }
  },

  /**
   * Envía la respuesta de un ejercicio interactivo (opción múltiple o respuesta abierta evaluada con SymPy).
   */
  async submitExerciseAnswer(exerciseId: string, answerOrOptionId: string): Promise<AnswerFeedback> {
    try {
      const res = await fetch(`${API_BASE}/exercises/${exerciseId}/answer/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          answer: answerOrOptionId,
          option_id: answerOrOptionId,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        return {
          isCorrect: Boolean(data.isCorrect ?? data.is_correct),
          title:
            data.title ||
            data.feedback_title ||
            (data.isCorrect ? '¡Exacto! ¡Bien rifado! 🦀' : '¡Casi! Analicemos este paso 💡'),
          explanation: data.explanation || data.feedback || '',
          hint: data.hint || undefined,
          xpEarned: Number(data.xpEarned ?? data.xp_earned ?? 0),
          totalXp:
            data.totalXp !== undefined && data.totalXp !== null
              ? Number(data.totalXp)
              : undefined,
          nextExercise: data.nextExercise || undefined,
        };
      }
    } catch {
      // Fallback local si el backend no está corriendo
    }

    const exerciseFeedback = MOCK_FEEDBACK_DB[exerciseId];
    if (exerciseFeedback && exerciseFeedback[answerOrOptionId]) {
      return exerciseFeedback[answerOrOptionId];
    }

    return {
      isCorrect: false,
      title: '¡Revisemos este paso! 💡',
      explanation: 'Sigue analizando el problema con las pistas de Jarol.',
      xpEarned: 0,
    };
  },

  /**
   * Solicita una pista progresiva del motor pedagógico para el ejercicio activo.
   */
  async requestExerciseHint(
    exerciseId: string,
    hintsUsed = 0
  ): Promise<{ hint: string; strategy?: string; hintsUsed: number }> {
    try {
      const res = await fetch(`${API_BASE}/exercises/${exerciseId}/hint/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ hints_used: hintsUsed }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          hint: data.hint || 'Revisa los datos principales del enunciado e identifica qué operación relaciona las cantidades.',
          strategy: data.strategy,
          hintsUsed: Number(data.hintsUsed ?? hintsUsed + 1),
        };
      }
    } catch {
      // fallback
    }
    return {
      hint: 'Analiza primero qué datos te da el problema y qué operación te permite despejar o simplificar el resultado.',
      hintsUsed: hintsUsed + 1,
    };
  },

  /**
   * Reinicia el contexto de conversación del tutor ("Nueva duda") conservando el progreso y XP.
   */
  async resetChatContext(): Promise<void> {
    try {
      await fetch(`${API_BASE}/chat/messages/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ reset: true }),
      });
    } catch {
      // ignore
    }
  },

  /**
   * Envía un mensaje en la conversación con el tutor IA Jarol.
   */
  async sendChatMessage(
    text: string,
    history: ChatMessage[] = []
  ): Promise<{
    replyText: string;
    exercise?: ExerciseCardData;
    xpEarned?: number;
    totalXp?: number;
  }> {
    try {
      const res = await fetch(`${API_BASE}/chat/messages/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ message: text }),
      });

      if (res.ok) {
        const data = await res.json();
        return {
          replyText: data.reply || data.message,
          exercise: data.exercise || undefined,
          xpEarned: Number(data.xpEarned || 0),
          totalXp:
            data.totalXp !== undefined && data.totalXp !== null
              ? Number(data.totalXp)
              : undefined,
        };
      }
    } catch {
      // Fallback local si el contenedor backend no responde
    }

    const lower = text.toLowerCase();
    if (
      lower.includes('fraccion') ||
      lower.includes('quebrado') ||
      lower.includes('practicar') ||
      lower.includes('suma')
    ) {
      const hasFirstExercise = history.some((m) => m.exercise?.id === 'ex_frac_01');
      const nextExercise = hasFirstExercise ? MOCK_EXERCISE_FRACTIONS_2 : MOCK_EXERCISE_FRACTIONS_1;

      return {
        replyText: hasFirstExercise
          ? '¡Vientos! Aquí va otro reto para afianzar lo aprendido. Recuerda fijarte si los denominadores son iguales:'
          : 'Para sumar fracciones con el mismo denominador, sumas los numeradores y conservas el denominador. Si tienen distinto denominador, primero conviértelas a fracciones equivalentes.',
        exercise: nextExercise,
      };
    }

    return {
      replyText:
        'Puedo explicarte paso a paso temas de **Fracciones**, **Porcentajes**, **Ecuaciones Lineales**, **Comprensión Lectora**, **Ortografía** o **Acentuación**, o ponerte un reto interactivo. ¿Con cuál empezamos?',
    };
  },

  /**
   * Obtiene el catálogo de materias y temas desde el backend y lo cruza con el progreso real del alumno.
   */
  async getSubjects(): Promise<Subject[]> {
    try {
      const [subjRes, progRes] = await Promise.all([
        fetch(`${API_BASE}/subjects/`, { headers: getAuthHeaders(false) }),
        fetch(`${API_BASE}/progress/me/`, { headers: getAuthHeaders(false) }),
      ]);

      const progressMap: Record<string, number> = {};
      if (progRes.ok) {
        const progData = await progRes.json();
        if (Array.isArray(progData.topics)) {
          for (const t of progData.topics) {
            progressMap[t.topicId] = Number(t.mastery || 0);
          }
        }
      }

      if (subjRes.ok) {
        const data = await subjRes.json();
        if (Array.isArray(data) && data.length > 0) {
          return data.map((s: Record<string, unknown>) => {
            const slug = String(s.slug || s.id || 'materia');
            const meta = SUBJECT_META[slug] || { iconName: 'BookOpen', color: 'teal' };
            const rawTopics = Array.isArray(s.topics) ? s.topics : [];
            return {
              id: slug,
              name: String(s.nombre || s.name || slug),
              iconName: meta.iconName,
              color: meta.color,
              isAvailable: Boolean(s.disponible ?? s.isAvailable),
              topics: rawTopics.map((t: Record<string, unknown>) => {
                const tSlug = String(t.slug || t.id || '');
                const tInfo = TOPIC_DESCRIPTIONS[tSlug] || {
                  description: 'Contenido curricular en preparación para próximas versiones.',
                  prompt: `Explícame el tema de ${String(t.nombre || t.name || tSlug)}`,
                };
                return {
                  id: tSlug,
                  name: String(t.nombre || t.name || tSlug),
                  description: tInfo.description,
                  isAvailable: Boolean(t.disponible ?? t.isAvailable),
                  progressPercent: progressMap[tSlug] ?? 0,
                  prompt: tInfo.prompt,
                };
              }),
            };
          });
        }
      }
    } catch {
      // fallback
    }
    return MOCK_SUBJECTS;
  },

  /**
   * Obtiene el progreso real del estudiante autenticado.
   */
  async getProgress(): Promise<StudentProgressSummary> {
    try {
      const res = await fetch(`${API_BASE}/progress/me/`, {
        headers: getAuthHeaders(false),
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // fallback
    }
    return {
      xp: 0,
      streakDays: 1,
      completedCount: 0,
      totalAttempts: 0,
      accuracy: 0,
      needsHelpWith: [],
      topics: Object.entries(TOPIC_DESCRIPTIONS).map(([topicId, info]) => ({
        topicId,
        name: topicId,
        subject: topicId.startsWith('mat_') ? 'Matemáticas' : 'Español',
        mastery: 0,
        completedExercises: 0,
        totalExercises: 9,
        attempts: 0,
        correctAttempts: 0,
        difficulty: 1,
        status: 'Por iniciar',
        prompt: info.prompt,
      })),
    };
  },

  /**
   * Obtiene la tabla de clasificación (Liga) con usuarios reales registrados en PostgreSQL.
   */
  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    try {
      const res = await fetch(`${API_BASE}/progress/leaderboard/`, {
        headers: getAuthHeaders(false),
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          return data;
        }
      }
    } catch {
      // fallback
    }
    return [];
  },

  /**
   * Obtiene las clases del docente o en las que está inscrito el alumno.
   */
  async getClasses(): Promise<ClassGroup[]> {
    try {
      const res = await fetch(`${API_BASE}/classes/`, {
        headers: getAuthHeaders(false),
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          return data.map((item) => mapBackendClassToGroup(item));
        }
      }
    } catch {
      // fallback
    }
    return MOCK_CLASSES;
  },

  /**
   * Crea una nueva clase (exclusivo para Docentes).
   */
  async createClass(payload: {
    nombre: string;
    subject?: string;
    nivel?: 'secundaria' | 'bachillerato';
    grado?: number;
  }): Promise<{ success: boolean; classGroup?: ClassGroup; error?: string }> {
    try {
      const res = await fetch(`${API_BASE}/classes/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          nombre: payload.nombre.trim(),
          subject: payload.subject || 'aritmetica',
          nivel: payload.nivel || 'secundaria',
          grado: payload.grado || 3,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          success: true,
          classGroup: mapBackendClassToGroup(data),
        };
      } else {
        const err = await res.json().catch(() => ({}));
        return {
          success: false,
          error: err.detail || err.error?.message || 'No se pudo crear la clase.',
        };
      }
    } catch {
      return {
        success: false,
        error: 'Error de conexión al crear la clase.',
      };
    }
  },

  /**
   * Unirse a una clase con código JAROL-XXXXX.
   */
  async joinClassWithCode(
    code: string
  ): Promise<{ success: boolean; message: string; classGroup?: ClassGroup }> {
    const cleanCode = code.trim().toUpperCase();
    try {
      const res = await fetch(`${API_BASE}/classes/join/`, {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ codigo: cleanCode }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          success: true,
          message: `¡Te uniste con éxito a la clase "${data.nombre || cleanCode}"!`,
          classGroup: mapBackendClassToGroup(data),
        };
      } else {
        const errData = await res.json().catch(() => ({}));
        const errMsg =
          errData.error?.message ||
          errData.detail ||
          'El código no existe o no tienes una sesión de estudiante activa.';
        return { success: false, message: errMsg };
      }
    } catch {
      return {
        success: false,
        message: 'Error de red al verificar el código de clase.',
      };
    }
  },

  /**
   * Obtener perfil del usuario activo desde el backend.
   */
  async getProfile(): Promise<User> {
    return profileToUser(await getProfile());
  },
};

export class ProfileApiError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}

async function profileRequest(path: string, method = 'GET', body?: ProfileChanges): Promise<Response> {
  const response = await fetch(`${API_BASE}/auth/${path}/`, {
    method, headers: getAuthHeaders(), credentials: 'same-origin',
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const message = Object.values(data).flat().filter(v => typeof v === 'string').join(' ');
    throw new ProfileApiError(response.status, message || 'No se pudo completar la solicitud. Intenta de nuevo.');
  }
  return response;
}
export async function getProfile(): Promise<BackendProfile> {
  return (await profileRequest('me')).json();
}
export async function saveProfile(changes: ProfileChanges): Promise<BackendProfile> {
  return (await profileRequest('me', 'PATCH', changes)).json();
}
export async function endSession(): Promise<void> { await profileRequest('logout', 'POST'); }
export function profileToUser(profile: BackendProfile): User {
  return { id: String(profile.id), name: [profile.first_name, profile.last_name].filter(Boolean).join(' ') || profile.alias || profile.username,
    email: profile.email, role: profile.rol === 'estudiante' ? 'student' : profile.rol === 'docente' ? 'teacher' : 'admin',
    grade: profile.nivel ? `${profile.grado ?? '—'}° ${profile.nivel === 'bachillerato' ? 'semestre de Bachillerato' : 'de Secundaria'}` : '',
    xp: profile.xp, streakDays: profile.streak_days };
}

export function isBackendToken(token: unknown): token is string {
  return typeof token === 'string' && /^[a-f0-9]{40}$/.test(token);
}

function authError(data: Record<string, unknown>, fallback: string): string {
  const error = data.error as { message?: string } | undefined;
  if (error?.message) return error.message;
  return Object.entries(data).filter(([, value]) => Array.isArray(value) || typeof value === 'string')
    .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(' ') : value}`).join(' ') || fallback;
}
export async function verifyEmail(uid: string, token: string): Promise<void> {
  await verificationRequest('verify-email', { uid, token });
}
export class VerificationApiError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}
export async function resendVerification(email: string): Promise<void> {
  await verificationRequest('resend-verification', { email });
}
async function verificationRequest(path: string, body: Record<string, string>): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/${path}/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new VerificationApiError(response.status, authError(data, 'No se pudo completar la solicitud.'));
}
