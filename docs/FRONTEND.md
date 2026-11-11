# Documentación de Frontend · Go Jarol

## 1. Visión General
El frontend de **Go Jarol** es una plataforma web interactiva con enfoque mobile-first desarrollada para estudiantes de secundaria y bachillerato en el estado de Veracruz. Su núcleo es un tutor conversacional pedagógico ("Jarol") que dialoga, evalúa conocimientos previos, explica con analogías y ejemplos, y propone ejercicios interactivos sin resolverlos directamente.

---

## 2. Mapa Integral de Interfaces (Arquitectura de 18 Interfaces por Rol)

La plataforma contempla un modelo completo de 18 interfaces funcionales distribuidas en 3 roles principales y pantallas compartidas, optimizadas mediante componentes reutilizables:

### 1. Alumno (7 interfaces)
| # | Interfaz | Ruta | Función Principal |
|---|---|---|---|
| 1 | **Chat con Jarol** *(Core MVP)* | `/chat` | Conversación pedagógica, preguntas previas, explicaciones y resolución de ejercicios. |
| 2 | **Retos** *(MVP)* | `/retos` | Catálogo de materias (Fracciones activo) para explorar y resolver retos. |
| 3 | **Ligas** | `/ligas` | Clasificación semanal, división, posición y recompensas de XP. |
| 4 | **Mis clases** *(MVP)* | `/clases` | Clases inscritas con opción de unirse mediante código de docente. |
| 5 | **Detalle de clase** | `/clases/:id` | Progreso grupal, tareas y compañeros dentro de la clase. |
| 6 | **Mi progreso** *(MVP)* | `/progreso` | Competencias dominadas, historial de ejercicios y temas por reforzar. |
| 7 | **Mi perfil** | `/perfil` | Datos personales, grado escolar (secundaria/bachillerato) y ajustes. |

### 2. Maestro (5 interfaces)
| # | Interfaz | Ruta | Función Principal |
|---|---|---|---|
| 8 | **Panel general** *(MVP)* | `/docente` | Dashboard con métricas globales de grupos, alumnos activos y semáforo de dificultades. |
| 9 | **Mis clases** *(MVP)* | `/docente/clases` | Creación y administración de grupos (generador de códigos únicos). |
| 10 | **Detalle de clase** | `/docente/clases/:id` | Pestañas con lista de alumnos, competencias del grupo, retos asignados y conversaciones. |
| 11 | **Detalle de estudiante** | `/docente/estudiante/:id` | Diagnóstico individual del alumno, ejercicios resueltos y áreas de oportunidad. |
| 12 | **Mi perfil docente** | `/docente/perfil` | Información del profesor, escuela y configuración de cuenta. |

### 3. Administrador (6 interfaces - Post-Hackathon)
| # | Interfaz | Ruta | Función Principal |
|---|---|---|---|
| 13 | **Resumen general** | `/admin` | Métricas de uso y estado global de la plataforma. |
| 14 | **Usuarios y roles** | `/admin/usuarios` | Gestión de cuentas, altas/bajas de docentes y alumnos. |
| 15 | **Materias y temas** | `/admin/catalogo` | Catálogo de disciplinas, niveles y orden curricular. |
| 16 | **Contenidos educativos** | `/admin/contenidos` | Gestor de explicaciones, ejercicios, opciones y pistas de SymPy/NLP. |
| 17 | **Gestión de clases** | `/admin/clases` | Supervisión general de aulas creadas. |
| 18 | **Incidencias** | `/admin/incidencias` | Monitoreo de desclasificaciones o errores del chatbot. |

### 4. Interfaces Compartidas y Reutilizables
| Interfaz | Roles que la comparten | Comportamiento |
|---|---|---|
| **Inicio de sesión** (`/login`) | Alumno, Maestro, Admin | Formulario único que redirige según el rol en el token JWT. |
| **Registro** (`/registro`) | Alumno, Maestro | Flujo unificado con selector de rol y verificación docente. |
| **Mis clases / Detalle** | Alumno y Maestro | Misma plantilla de tarjetas con botones de acción diferenciados (unirse vs. crear). |
| **Progreso / Perfil** | Alumno y Maestro | Mismo sistema de cards visuales con datos y permisos según rol. |

### 5. Prioridades Críticas del Hackathon (MVP 24 Horas)
Para maximizar el impacto con el jurado sin perder tiempo en paneles de administración secundarios, el desarrollo se enfoca en:
1. **Chat con Jarol** (con tarjeta interactiva de fracciones).
2. **Retos** (catálogo de materias).
3. **Mi progreso** (XP, nivel y temas).
4. **Mis clases / Unirse** (estudiante).
5. **Panel general y Mis clases** (docente).

---

## 3. Navegación por Rol (Barra Inferior Mobile-First)

- **Alumno**: `[ Jarol (Chat) ]` · `[ Retos ]` · `[ Clases ]` · `[ Progreso ]`
- **Maestro**: `[ Panel ]` · `[ Clases ]` · `[ Alumnos ]` · `[ Perfil ]`
- **Admin**: `[ Resumen ]` · `[ Usuarios ]` · `[ Contenidos ]` · `[ Más ]`

---

## 4. Stack Tecnológico
- **Framework & Lenguaje**: React 18+ con TypeScript.
- **Bundler & Build Tool**: Vite.
- **Gestor de Paquetes**: `pnpm`.
- **Enrutador**: React Router DOM v6 con rutas protegidas por rol.
- **Estilos**: Tailwind CSS local (cero CDNs externos).
- **Tipografías**: Sora (encabezados, badges, botones) + Atkinson Hyperlegible Next (lectura y fórmulas).
- **Iconografía**: Lucide React.

---

## 5. Sistema de Diseño ("Tactile Modernism")
- **Fondo / Canvas**: `#F7F5EF` / `#F7F9FF` (acabado tipo papel que previene fatiga visual).
- **Superficies**: `#FFFFFF` con sutil borde `#D2E5F9` / `#E8E5DC`.
- **Primario (Teal)**: `#126B73` (sombra física `#005158`).
- **Secundario (Coral)**: `#E76D55` (sombra física `#711707`).
- **Acento (Amarillo cálido)**: `#E4AA50` (pistas, rachas, XP).
- **Texto / Ink**: `#0A1D2C` (máximo contraste y legibilidad WCAG AA).

---

## 6. Estructura del Proyecto en `frontend/`
```
frontend/
├── public/
│   └── mascot/                # Jarol el Cangrejo (optimizado)
├── src/
│   ├── components/
│   │   ├── chat/              # ChatFeed, JarolBubble, UserBubble, FloatingInput
│   │   ├── exercise/          # ExerciseCard, OptionRadio, FeedbackBanner
│   │   ├── layout/            # AppHeader, BottomNav (por rol), MainContainer
│   │   ├── classes/           # ClassCard, JoinClassModal, CreateClassModal
│   │   ├── progress/          # XPBar, StreakCard, TopicMasteryList
│   │   └── ui/                # TactileButton, Badge, Card, Modal
│   ├── context/
│   │   └── AuthContext.tsx    # Manejo de sesión (alumno vs. docente)
│   ├── routes/
│   │   └── AppRouter.tsx      # Configuración de rutas y guards de rol
│   ├── services/
│   │   ├── api.ts             # Cliente HTTP /api/v1/ con token
│   │   ├── mockData.ts        # Datos simulados de fracciones, clases y progreso
│   │   └── chatService.ts     # Adaptador de conversación (Mock vs. Django)
│   ├── types/                 # Interfaces TS (User, Role, Exercise, Chat, Class)
│   ├── views/
│   │   ├── auth/              # LoginView, RegisterView
│   │   ├── student/           # ChatView, ChallengesView, ClassesView, ProgressView, ProfileView
│   │   └── teacher/           # TeacherDashboardView, TeacherClassesView
│   ├── App.tsx
│   └── main.tsx
├── Dockerfile                 # Multi-stage Nginx para Debian
├── nginx.conf                 # Configuración de proxy SPA y /api/v1/
├── tailwind.config.js
└── package.json
```
