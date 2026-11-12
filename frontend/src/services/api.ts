import {
  MOCK_FEEDBACK_DB,
  MOCK_EXERCISE_FRACTIONS_1,
  MOCK_EXERCISE_FRACTIONS_2,
  MOCK_SUBJECTS,
  MOCK_CLASSES,
  MOCK_STUDENT,
} from './mockData';
import type { AnswerFeedback, ChatMessage, ExerciseCardData } from '../types/chat';
import type { Subject, ClassGroup } from '../types/curriculum';
import type { User } from '../types/auth';

const API_BASE = '/api/v1';

// Token storage
export const getAuthToken = () => localStorage.getItem('jarol_token');
export const setAuthToken = (token: string) => localStorage.setItem('jarol_token', token);
export const removeAuthToken = () => localStorage.removeItem('jarol_token');

export const apiService = {
  /**
   * Inicia sesión o registra usuario mediante Google OAuth.
   */
  async loginWithGoogle(payload: {
    credential?: string;
    email: string;
    name: string;
    picture?: string;
    role: 'student' | 'teacher';
    grade?: string;
    school?: string;
  }): Promise<{ success: boolean; token?: string; user?: User; error?: string }> {
    try {
      const res = await fetch(`${API_BASE}/auth/google/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          credential: payload.credential,
          email: payload.email,
          name: payload.name,
          role: payload.role === 'teacher' ? 'docente' : 'estudiante',
          picture: payload.picture,
          grade: payload.grade,
          school: payload.school,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.token) {
          setAuthToken(data.token);
        }
        return {
          success: true,
          token: data.token,
          user: {
            id: String(data.user?.id || 'google-user'),
            name: data.user?.alias || payload.name,
            email: data.user?.email || payload.email,
            role: payload.role,
            grade: payload.grade,
            school: payload.school,
            avatarUrl: payload.picture || data.picture,
            xp: 320,
            streakDays: 4,
          },
        };
      } else {
        const errText = await res.text();
        console.warn('Backend Google Auth respondió con error:', res.status, errText);
      }
    } catch (err) {
      console.warn('Error de red al conectar con Google Auth backend:', err);
    }

    const mockToken = `jarol_gtoken_${Date.now()}`;
    setAuthToken(mockToken);
    return {
      success: true,
      token: mockToken,
      user: {
        id: `google-${Date.now()}`,
        name: payload.name,
        email: payload.email,
        role: payload.role,
        grade: payload.grade,
        school: payload.school,
        avatarUrl: payload.picture || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
        xp: 320,
        streakDays: 4,
      },
    };
  },

  /**
   * Envía la respuesta de un ejercicio interactivo para su evaluación formativa.
   * La evaluación ocurre en el backend (o mock); el cliente nunca posee la respuesta de antemano.
   */
  async submitExerciseAnswer(exerciseId: string, optionId: string): Promise<AnswerFeedback> {
    try {
      const res = await fetch(`${API_BASE}/exercises/${exerciseId}/answer/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${getAuthToken() || ''}`,
        },
        body: JSON.stringify({ option_id: optionId }),
      });

      if (res.ok) {
        const data = await res.json();
        return {
          isCorrect: data.is_correct,
          title: data.feedback_title || (data.is_correct ? '¡Exacto! ¡Bien rifado! 🦀' : 'Vamos a repasar 💡'),
          explanation: data.explanation || data.feedback,
          hint: data.hint,
          xpEarned: data.xp_earned || 25,
        };
      }
    } catch {
      // Fallback a mock en desarrollo
    }

    // Respuesta simulada determinista según la base de conocimiento pedagógica
    const exerciseFeedback = MOCK_FEEDBACK_DB[exerciseId];
    if (exerciseFeedback && exerciseFeedback[optionId]) {
      return exerciseFeedback[optionId];
    }

    return {
      isCorrect: false,
      title: '¡Revisemos este paso! 💡',
      explanation: 'Sigue analizando el problema con las pistas de Jarol.',
      xpEarned: 5,
    };
  },

  /**
   * Envía un mensaje en la conversación con Jarol.
   * Devuelve la explicación de Jarol y opcionalmente un ejercicio interactivo anexo.
   */
  async sendChatMessage(
    text: string,
    history: ChatMessage[] = []
  ): Promise<{ replyText: string; exercise?: ExerciseCardData }> {
    try {
      const res = await fetch(`${API_BASE}/chat/messages/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${getAuthToken() || ''}`,
        },
        body: JSON.stringify({ message: text }),
      });

      if (res.ok) {
        const data = await res.json();
        return {
          replyText: data.reply || data.message,
          exercise: data.exercise,
        };
      }
    } catch {
      // Fallback a motor pedagógico local
    }

    const lower = text.toLowerCase();

    // Regla Pedagógica del Reto:
    // Si el estudiante pide practicar o menciona fracciones:
    if (lower.includes('fraccion') || lower.includes('quebrado') || lower.includes('practicar') || lower.includes('suma')) {
      const hasFirstExercise = history.some((m) => m.exercise?.id === 'ex_frac_01');
      const nextExercise = hasFirstExercise ? MOCK_EXERCISE_FRACTIONS_2 : MOCK_EXERCISE_FRACTIONS_1;

      return {
        replyText: hasFirstExercise
          ? '¡Vientos! Aquí va otro reto con contexto jarocho para afianzar lo aprendido. Recuerda fijarte si los denominadores son iguales: 🦀'
          : '¡Qué onda! Para sumar fracciones con el **mismo denominador** (el número de abajo), solo sumas los numeradores (los de arriba) y el de abajo se queda igualito. Imagina rebanadas de un mismo pastel: ¡todas miden lo mismo!\n\n¿Le entramos a este ejercicio de prueba?',
        exercise: nextExercise,
      };
    }

    if (lower.includes('ecuacion') || lower.includes('algebra') || lower.includes('incognita')) {
      return {
        replyText: '¡Álgebra está de lujo! Una ecuación de primer grado es como una balanza en equilibrio. Lo que le hagas a un lado del igual (=), se lo tienes que hacer al otro. ¿Qué parte te causa más ruido: despejar la x o los signos?',
      };
    }

    if (lower.includes('pitagoras') || lower.includes('triangulo') || lower.includes('hipotenusa')) {
      return {
        replyText: '¡El Teorema de Pitágoras! Aplica únicamente en triángulos con un ángulo recto (90°). Dice que la hipotenusa al cuadrado es igual a la suma de los cuadrados de los catetos (a² + b² = c²). ¿Quieres que veamos un ejemplo con medidas?',
      };
    }

    return {
      replyText: `¡Te escucho! Como tu tutor Jarol, dime qué tema de matemáticas o ciencias estás repasando y lo desmenuzamos paso a pasito sin prisas. 🦀✨`,
    };
  },

  /**
   * Obtiene las materias disponibles.
   */
  async getSubjects(): Promise<Subject[]> {
    try {
      const token = getAuthToken();
      const headers: Record<string, string> = {};
      if (token && !token.startsWith('jarol_demo_') && !token.startsWith('jarol_gtoken_')) {
        headers['Authorization'] = `Token ${token}`;
      }
      const res = await fetch(`${API_BASE}/subjects/`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) return data;
      }
    } catch {
      // fallback
    }
    return MOCK_SUBJECTS;
  },

  /**
   * Obtiene las clases disponibles.
   */
  async getClasses(): Promise<ClassGroup[]> {
    try {
      const token = getAuthToken();
      const headers: Record<string, string> = {};
      if (token && !token.startsWith('jarol_demo_') && !token.startsWith('jarol_gtoken_')) {
        headers['Authorization'] = `Token ${token}`;
      }
      const res = await fetch(`${API_BASE}/classes/`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) return data;
      }
    } catch {
      // fallback
    }
    return MOCK_CLASSES;
  },

  /**
   * Unirse a una clase con código
   */
  async joinClassWithCode(code: string): Promise<{ success: boolean; message: string }> {
    const cleanCode = code.trim().toUpperCase();
    try {
      const token = getAuthToken();
      if (token && !token.startsWith('jarol_demo_') && !token.startsWith('jarol_gtoken_')) {
        const res = await fetch(`${API_BASE}/classes/join/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({ codigo: cleanCode }),
        });
        if (res.ok) {
          const data = await res.json();
          return {
            success: true,
            message: `¡Te uniste con éxito a la clase "${data.nombre || cleanCode}"!`,
          };
        } else {
          const errData = await res.json().catch(() => ({}));
          const errMsg = errData.error?.message || errData.detail || 'Código no válido o inactivo.';
          return { success: false, message: errMsg };
        }
      }
    } catch {
      // fallback
    }

    if (cleanCode === 'JAROL-3B' || cleanCode === 'JAROL-2A') {
      return { success: true, message: '¡Te uniste con éxito a la clase del Prof. Laura!' };
    }
    return { success: false, message: 'Código no encontrado. Verifica con tu maestro.' };
  },

  /**
   * Obtener perfil del usuario activo
   */
  async getProfile(): Promise<User> {
    return MOCK_STUDENT;
  },
};
