import type { User } from '../types/auth';
import type { Subject, ClassGroup, StudentMastery } from '../types/curriculum';
import type { ExerciseCardData, AnswerFeedback } from '../types/chat';
import type { LeaderboardUser, DetailedStudent } from '../types/leagues';

export const MOCK_STUDENT: User = {
  id: 'usr_student_01',
  name: 'Emiliano Valdés',
  email: 'emiliano@estudiante.gob.mx',
  role: 'student',
  grade: '3° de Secundaria',
  school: 'Secundaria Técnica #26 · Veracruz',
  xp: 320,
  streakDays: 4,
  avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
};

export const MOCK_TEACHER: User = {
  id: 'usr_teacher_01',
  name: 'Prof. Laura Mendoza',
  email: 'laura.mendoza@msev.gob.mx',
  role: 'teacher',
  school: 'Secundaria Técnica #26 · Veracruz',
  avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
};

export const MOCK_SUBJECTS: Subject[] = [
  {
    id: 'aritmetica',
    name: 'Aritmética',
    iconName: 'Calculator',
    color: '#126B73',
    isAvailable: true,
    topics: [
      {
        id: 'fracciones',
        name: 'Fracciones (Suma y Resta)',
        description: 'Aprende a sumar y restar fracciones con igual y distinto denominador sin memorizar fórmulas.',
        isAvailable: true,
        progressPercent: 65,
      },
      {
        id: 'multiplicacion-fracciones',
        name: 'Multiplicación y División de Fracciones',
        description: 'Multiplicar en línea recta y el truco del sándwich.',
        isAvailable: false,
        progressPercent: 0,
      },
    ],
  },
  {
    id: 'algebra',
    name: 'Álgebra',
    iconName: 'Variable',
    color: '#E76D55',
    isAvailable: true,
    topics: [
      {
        id: 'ecuaciones-lineales',
        name: 'Ecuaciones de 1er Grado',
        description: 'Despejar la incógnita paso a paso como una balanza en equilibrio.',
        isAvailable: true,
        progressPercent: 20,
      },
    ],
  },
  {
    id: 'geometria',
    name: 'Geometría y Medición',
    iconName: 'Triangle',
    color: '#E4AA50',
    isAvailable: true,
    topics: [
      {
        id: 'pitagoras',
        name: 'Teorema de Pitágoras',
        description: 'Hipotenusas y catetos en triángulos rectángulos de la vida real.',
        isAvailable: true,
        progressPercent: 10,
      },
    ],
  },
  {
    id: 'espanol',
    name: 'Lengua y Comunicación',
    iconName: 'BookOpen',
    color: '#596B72',
    isAvailable: false,
    topics: [],
  },
  {
    id: 'historia',
    name: 'Historia de México',
    iconName: 'Landmark',
    color: '#596B72',
    isAvailable: false,
    topics: [],
  },
  {
    id: 'biologia',
    name: 'Biología y Ciencias',
    iconName: 'Microscope',
    color: '#596B72',
    isAvailable: false,
    topics: [],
  },
];

export const MOCK_EXERCISE_FRACTIONS_1: ExerciseCardData = {
  id: 'ex_frac_01',
  subjectName: 'Aritmética',
  topicName: 'Fracciones',
  step: 1,
  totalSteps: 3,
  question: '¿Cuánto es 3/4 + 1/4?',
  instruction: 'Elige la opción que represente el resultado simplificado:',
  options: [
    { id: 'A', text: '1/2' },
    { id: 'B', text: '1' },
    { id: 'C', text: '4/8' },
  ],
  xpReward: 30,
};

export const MOCK_EXERCISE_FRACTIONS_2: ExerciseCardData = {
  id: 'ex_frac_02',
  subjectName: 'Aritmética',
  topicName: 'Fracciones',
  step: 2,
  totalSteps: 3,
  question: 'Si una jícama se divide en 6 rebanadas iguales y te comes 2/6 y luego 3/6, ¿cuánto comiste en total?',
  instruction: 'Selecciona la fracción que representa lo que te comiste:',
  options: [
    { id: 'A', text: '5/6' },
    { id: 'B', text: '5/12' },
    { id: 'C', text: '1' },
  ],
  xpReward: 35,
};

export const MOCK_FEEDBACK_DB: Record<string, Record<string, AnswerFeedback>> = {
  ex_frac_01: {
    B: {
      isCorrect: true,
      title: '¡Exacto! ¡Bien rifado! 🦀✨',
      explanation: 'Como tienen el mismo denominador (4), solo sumamos los numeradores: 3 + 1 = 4. Por lo tanto 4/4 representa 1 entero completo.',
      xpEarned: 30,
    },
    A: {
      isCorrect: false,
      title: '¡Casi! Vamos a checarlo con calma 💡',
      explanation: 'Recuerda que cuando los denominadores son iguales (ambos son 4), se conserva el número de abajo y solo sumamos los de arriba (3 + 1 = 4).',
      hint: 'Pista: 4 rebanadas de 4 en una pizza forman la pizza entera.',
      xpEarned: 5,
    },
    C: {
      isCorrect: false,
      title: '¡Ojo con los denominadores! 🧐',
      explanation: 'Al sumar fracciones con el mismo denominador, ¡los números de abajo NO se suman! El 4 se mantiene constante.',
      hint: 'Pista: 3 cuartos más 1 cuarto son 4 cuartos.',
      xpEarned: 5,
    },
  },
  ex_frac_02: {
    A: {
      isCorrect: true,
      title: '¡Eso mero! ¡Ya le agarraste la onda! 🦀🎉',
      explanation: 'Sumaste 2/6 + 3/6 = 5/6 de la jícama. El denominador 6 se conservó porque todas las rebanadas son del mismo tamaño.',
      xpEarned: 35,
    },
    B: {
      isCorrect: false,
      title: '¡Cuidado con sumar los de abajo! 🍋',
      explanation: 'El tamaño de las rebanadas no cambia a doceavos. Solo sumamos cuántas rebanadas te comiste: 2 + 3 = 5 sobre 6.',
      hint: 'Pista: El plato sigue teniendo rebanadas de tamaño 1/6.',
      xpEarned: 5,
    },
    C: {
      isCorrect: false,
      title: 'Faltó un cachito para el entero 🌴',
      explanation: 'Para comerte la jícama entera tendrías que comer 6/6. Tú comiste 2 + 3 = 5 de las 6 rebanadas.',
      hint: 'Pista: 5/6 es casi un entero, pero le falta 1/6.',
      xpEarned: 5,
    },
  },
};

export const MOCK_CLASSES: ClassGroup[] = [
  {
    id: 'cls_01',
    name: '3° B · Matemáticas y Álgebra',
    teacherName: 'Prof. Laura Mendoza',
    code: 'JAROL-3B',
    studentCount: 32,
    subject: 'Aritmética y Álgebra',
    averageMastery: 74,
  },
  {
    id: 'cls_02',
    name: '2° A · Ciencias y Pensamiento Lógico',
    teacherName: 'Prof. Laura Mendoza',
    code: 'JAROL-2A',
    studentCount: 28,
    subject: 'Aritmética',
    averageMastery: 81,
  },
];

export const MOCK_STUDENT_DIAGNOSTICS: StudentMastery[] = [
  {
    studentId: 'st_01',
    studentName: 'Emiliano Valdés',
    completedExercises: 12,
    accuracy: 85,
    needsHelpWith: ['Suma con diferente denominador'],
    lastActive: 'Hace 10 min',
  },
  {
    studentId: 'st_02',
    studentName: 'Sofía Morales',
    completedExercises: 9,
    accuracy: 62,
    needsHelpWith: ['Simplificación de fracciones', 'Mínimo común múltiplo'],
    lastActive: 'Hoy, 2:15 PM',
  },
  {
    studentId: 'st_03',
    studentName: 'Mateo Hernández',
    completedExercises: 15,
    accuracy: 93,
    needsHelpWith: [],
    lastActive: 'Ayer',
  },
];

export const MOCK_LEADERBOARD: LeaderboardUser[] = [
  {
    rank: 1,
    id: 'lead_01',
    name: 'Mateo Hernández',
    school: 'Secundaria Técnica #26',
    xp: 450,
    streakDays: 7,
    avatarUrl: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
  },
  {
    rank: 2,
    id: 'lead_02',
    name: 'Sofía Morales',
    school: 'Secundaria Técnica #26',
    xp: 380,
    streakDays: 5,
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
  },
  {
    rank: 3,
    id: 'lead_03',
    name: 'Carlos Yépez',
    school: 'Telesecundaria Adolfo Ruiz',
    xp: 340,
    streakDays: 3,
    avatarUrl: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150&auto=format&fit=crop&q=80',
  },
  {
    rank: 4,
    id: 'usr_student_01',
    name: 'Emiliano Valdés (Tú)',
    school: 'Secundaria Técnica #26',
    xp: 320,
    streakDays: 4,
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    isCurrentUser: true,
  },
  {
    rank: 5,
    id: 'lead_05',
    name: 'Valeria Cruz',
    school: 'Bachillerato Veracruz',
    xp: 290,
    streakDays: 4,
    avatarUrl: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80',
  },
  {
    rank: 6,
    id: 'lead_06',
    name: 'Diego Rivas',
    school: 'Secundaria General #1',
    xp: 260,
    streakDays: 2,
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
  },
];

export const MOCK_DETAILED_STUDENTS: Record<string, DetailedStudent> = {
  st_01: {
    id: 'st_01',
    name: 'Emiliano Valdés',
    grade: '3° de Secundaria · Grupo B',
    school: 'Secundaria Técnica #26 · Veracruz',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    totalXP: 320,
    accuracy: 85,
    streakDays: 4,
    weakTopics: ['Suma de fracciones con diferente denominador'],
    masteredTopics: ['Suma con igual denominador', 'Identificación de partes (numerador y denominador)'],
    recentAttempts: [
      {
        id: 'att_01',
        exerciseTitle: 'Suma de fracciones 3/4 + 1/4',
        date: 'Hoy, hace 15 min',
        isCorrect: true,
        selectedOption: 'B) 1 entero',
        explanationGiven: 'Sumó correctamente numeradores manteniendo el denominador 4 y simplificó 4/4 = 1.',
      },
      {
        id: 'att_02',
        exerciseTitle: 'Problema de jícama en 6 rebanadas (2/6 + 3/6)',
        date: 'Hoy, hace 20 min',
        isCorrect: true,
        selectedOption: 'A) 5/6',
        explanationGiven: 'Resolvió el problema contextualizado sin alterar el denominador.',
      },
      {
        id: 'att_03',
        exerciseTitle: 'Suma con distinto denominador 1/2 + 1/4',
        date: 'Ayer, 4:30 PM',
        isCorrect: false,
        selectedOption: '2/6 (Sumó denominadores)',
        explanationGiven: 'Error común detectado: sumó numeradores y denominadores directos.',
        hintUsed: 'Jarol le explicó la analogía de convertir el medio vaso en dos cuartos.',
      },
    ],
  },
  st_02: {
    id: 'st_02',
    name: 'Sofía Morales',
    grade: '3° de Secundaria · Grupo B',
    school: 'Secundaria Técnica #26 · Veracruz',
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
    totalXP: 380,
    accuracy: 62,
    streakDays: 5,
    weakTopics: ['Simplificación a fracciones irreducibles', 'Mínimo común múltiplo'],
    masteredTopics: ['Identificación de numerador y denominador'],
    recentAttempts: [
      {
        id: 'att_04',
        exerciseTitle: 'Simplificación de 6/8',
        date: 'Hoy, 2:15 PM',
        isCorrect: false,
        selectedOption: '3/8 (Solo dividió numerador)',
        explanationGiven: 'Dividió el número superior entre 2 pero olvidó aplicar la misma división al denominador.',
        hintUsed: 'Jarol le recordó la regla de la balanza: lo que se le hace arriba se le hace abajo.',
      },
    ],
  },
  st_03: {
    id: 'st_03',
    name: 'Mateo Hernández',
    grade: '3° de Secundaria · Grupo B',
    school: 'Secundaria Técnica #26 · Veracruz',
    avatarUrl: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80',
    totalXP: 450,
    accuracy: 93,
    streakDays: 7,
    weakTopics: [],
    masteredTopics: ['Suma con igual denominador', 'Suma con diferente denominador', 'Multiplicación en línea recta'],
    recentAttempts: [
      {
        id: 'att_05',
        exerciseTitle: 'Despeje de fracción en ecuación x + 1/3 = 1',
        date: 'Ayer, 11:00 AM',
        isCorrect: true,
        selectedOption: 'x = 2/3',
        explanationGiven: 'Resolvió sin errores el despeje y la resta de fracciones.',
      },
    ],
  },
};

