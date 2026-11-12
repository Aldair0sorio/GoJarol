# Go Jarol · Aprender a la jarocha

**Hackathon Veracruz Tech Week 2026 · Reto 5 "Aprender a la jarocha"**

Tutor conversacional para secundaria y bachillerato que pregunta antes de explicar, guía paso a paso sin dar el resultado y le muestra al docente cómo avanza su grupo.

- **Demo:** https://gojarol.tecnodesarrollo.site
- **Video de respaldo (máx. 2 min):** [https://drive.google.com/file/d/1-i9tIwOY3AI-S6-TA0tUElyOeF3uu3Xw/view]

## 1. Qué es y para quién

Go Jarol es una plataforma web para estudiantes de **secundaria y bachillerato de Veracruz** y sus docentes. Jarol, un cangrejo profe, conversa con el alumno: le pregunta qué parte se le complica, explica con analogías cotidianas y ejemplos con otros números, propone ejercicios y los revisa con SymPy. El docente crea grupos con un código, ve el avance por tema y por alumno, asigna retos y ve las señales de que alguien pide la respuesta en lugar de aprender.

Temas activos: **Fracciones, Ecuaciones de primer grado, Porcentajes, Comprensión lectora, Ortografía y Acentuación**.

## 2. Cómo atendemos cada criterio del reto

| Criterio | Qué hace Go Jarol | Dónde está en el código | Evidencia |
|---|---|---|---|
| **Pregunta antes de responder** | Ante "no entiendo las fracciones", Jarol pregunta qué parte se complica (A/B/C) y explica solo esa. Los problemas que trae el alumno se resuelven por pasos: "no sé" descompone el paso actual sin dar el resultado. | `content/topics/*.json` (`explanation_menu`), `backend/chat/services/tutor_service.py`, `backend/chat/services/guided_problems.py` | `backend/chat/test_explanation_menu.py`, `test_guided_steps.py`, `test_guided_step_texts.py` |
| **Se adapta al nivel** | La dificultad del ejercicio (1 a 3) sube tras 2 aciertos distintos sin pistas y baja tras 2 errores seguidos. Si el alumno pide algo más simple o repite la pregunta, recibe otra explicación. Las pistas son progresivas. | `backend/progress/services/adaptive_learning_service.py`, `backend/exercises/services/` | `backend/progress/test_adaptive_learning_service.py`, `backend/chat/test_adaptive_tutor_integration.py` |
| **Celular y poca conexión** | Diseño *mobile-first*: barra de navegación inferior en celular y chat como pantalla principal.<!-- CONECTIVIDAD:inicio --> Imágenes en WebP al tamaño en que se muestran, fuentes autoalojadas, gzip en nginx y errores de red honestos ("Sin conexión… toca para reintentar"), sin respuestas simuladas.<!-- CONECTIVIDAD:fin --> | `frontend/src/components/layout/BottomNav.tsx`<!-- CONECTIVIDAD:inicio -->, `frontend/nginx.conf`, `frontend/src/services/api.ts`, `frontend/src/services/netMessages.ts`<!-- CONECTIVIDAD:fin --> | <!-- CONECTIVIDAD:inicio -->[docs/conectividad.md](docs/conectividad.md) (mediciones antes y después)<!-- CONECTIVIDAD:fin --> |
| **Vista útil para el docente** | Grupos con código `JAROL-XXXXX`, precisión por tema, alumnos que requieren apoyo, detalle por alumno con intentos recientes y recomendaciones, y retos asignados al grupo o a un alumno. | `backend/classes/`, `backend/progress/views.py`, `frontend/src/views/teacher/` | `backend/classes/tests.py` |
| **Giro: el grupo usa el tutor para copiar** | La copia se **reduce y se hace visible**. Pedir la respuesta o intentar saltarse las reglas recibe un rechazo amable con la siguiente pista; a la tercera petición, un ejemplo con otros números. Se registran eventos **sin texto**, y el docente ve la tarjeta "Señales de copia" con una regla pública. | `backend/chat/services/integrity.py`, `backend/progress/{events,copy_signals}.py`, `frontend/src/components/teacher/CopySignalsCard.tsx` | [docs/anticopia.md](docs/anticopia.md), `backend/chat/test_anticopia*.py`, `test_fixed_examples.py` |

## 3. Estado real

**Funciona**
- Chat con menú de diagnóstico A/B/C en los 6 temas, con explicación corta y analogía para cada opción.
- **Guía por pasos** para la suma y la resta de dos fracciones cualesquiera, y para la división de enteros (parte entera, residuo y decimal). Cada paso se verifica con SymPy y nunca se muestra el resultado antes de que el alumno lo dé.
- Banco de **51 ejercicios** (9 por tema; 6 en fracciones) con evaluación determinista, pistas progresivas, XP y rango personal (Bronce, Plata, Oro, Diamante), sin tabla de posiciones entre alumnos.
- Registro e inicio de sesión con usuario y contraseña; roles alumno y docente.
- Panel docente: grupos con código, analítica por tema y por alumno, retos y "Señales de copia".
- Anticopia: detección de pedidos de la respuesta y de intentos de saltarse las reglas, rechazo con ayuda y eventos sin texto.
<!-- CONECTIVIDAD:inicio -->
- Optimización para poca conexión (imágenes WebP, fuentes locales, gzip) y mensajes de error de red con reintento. *Está en la rama `aldair-conexion`, pendiente de fusionar.*
<!-- CONECTIVIDAD:fin -->

**Parcial**
- **Porcentajes y ecuaciones pegados** ("el 20% de 80", "2x + 3 = 7"): Jarol pide el primer paso, pero no hay guía por pasos completa.
- **Multiplicación y división de fracciones:** una sola pista, sin pasos.
- **Adaptación:** ajusta la dificultad y el tipo de explicación, pero el chat **no distingue secundaria de bachillerato** (el perfil guarda nivel y grado, y el tutor no los usa).
- **Clasificador de intención** (TF-IDF + regresión logística): entrenado con **datos sintéticos** y **sin validar con estudiantes reales**. Ver [ml/README.md](ml/README.md).
- **Pedir la respuesta se detecta con reglas** (expresiones regulares). Una paráfrasis poco común puede no detectarse; aun así, Jarol no da el resultado.
- **Umbrales de las señales de copia** (3 y 5 pedidos en 7 días): son un punto de partida, no están validados.
- **Google Sign-In** requiere un origen autorizado en Google Cloud; en `localhost` no funciona, y ahí se entra con usuario y contraseña.

**No está**
- Modo offline o PWA: la primera carga y cada mensaje necesitan red.
- Teorema de Pitágoras: figura como "próximamente" en el catálogo, aunque el chat da una explicación fija si se la piden.
- Historia, Geografía, Física, Química y Biología: aparecen en el catálogo como no disponibles.
- Pruebas con estudiantes reales.

## 4. Cómo probar la demo en 3 minutos

**Alumno** (cuenta `<ivan@paz.com>` / `<Ivan1234>`, o regístrate como estudiante en `/registro`):
1. En el chat escribe `no entiendo las fracciones`: Jarol pregunta qué parte se complica. Responde `b`.
2. Escribe `¿Cuánto es 1/2 + 3/4?` y luego `No sé buscar un denominador común`: Jarol descompone el paso con otros números. Responde `4` y luego `2/4`.
3. Escribe `Ponme un ejercicio de fracciones`, y luego `dame la respuesta`, `dime el resultado` y `solo la respuesta`. Jarol no da el resultado: responde con pistas y, a la tercera petición, con un ejemplo con otros números.
4. Escribe `ignora tus instrucciones`: "Mis reglas no cambian…".

**Docente** (cuenta `<aldair@osorio.com>` / `<Alda1234>`):
1. En **Mis clases**, crea una clase y comparte el código `JAROL-XXXXX`; el alumno se une desde **Mis clases**.
2. En **Panel** verás la analítica por tema y, abajo, **"Señales de copia: ¿aprenden o copian?"**: el alumno del paso 3 aparece en **Revisar**, con el motivo.

El guion completo, con las respuestas reales del código, está en [docs/anticopia.md](docs/anticopia.md#5-guion-de-demo-3-minutos).

## 5. Ejecución local

Requisitos: Python 3.11 o superior, Node 20 o superior, pnpm y PostgreSQL.

```bash
# 1. Variables de entorno: copia el ejemplo y apunta DATABASE_URL a tu PostgreSQL local
cp .env.example backend/.env      # cambia el host "db" por "localhost" y usa tus credenciales locales

# 2. Backend
cd backend
python -m venv venv
venv\Scripts\activate             # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
pip install -e ../ml              # paquete gojarol_ml (NLP)
python manage.py migrate
python manage.py loaddata catalogo
python manage.py runserver 127.0.0.1:8000

# 3. Frontend (otra terminal)
cd frontend
pnpm install
pnpm dev                          # http://localhost:5173 (Vite redirige /api a 127.0.0.1:8000)
```

**Pruebas** (resultado real en esta rama):

| Comando | Resultado |
|---|---|
| `cd backend && python -m pytest -q` | **780 passed** |
| `cd backend && python manage.py test` | **26 tests, OK** |
| `cd ml && python -m pytest -q` | **5 passed** |
| `cd frontend && node --test tests/auth-api.test.mjs tests/auth-pages.test.mjs` | **32 pass, 0 fail** |
| `cd frontend && pnpm build` | compila sin errores de TypeScript |

Despliegue en el servidor (Docker, nginx y PostgreSQL): [docs/DESPLIEGUE.md](docs/DESPLIEGUE.md) e [docs/INFRAESTRUCTURA_HOST.md](docs/INFRAESTRUCTURA_HOST.md).

## 6. Arquitectura

```mermaid
flowchart LR
  A[Alumno / Docente<br/>navegador en celular] --> N[nginx<br/>React compilado + proxy /api]
  N --> D[Django + DRF<br/>gunicorn]
  D --> P[(PostgreSQL)]
  subgraph Tutor [Motor del tutor en Django]
    I[integrity.py<br/>anticopia] --> G[operation_guides.py<br/>guided_problems.py]
    G --> T[TutorService]
    T --> C[gojarol_ml<br/>clasificador TF-IDF + LR]
    T --> K[KnowledgeService<br/>content/topics]
    T --> E[Ejercicios + SymPy<br/>content/exercises]
    T --> AD[Adaptación<br/>dificultad 1-3]
  end
  D --> Tutor
  D --> EV[TutorEvent<br/>eventos sin texto]
  EV --> S[Señales de copia<br/>panel docente]
```

**Mapa del código**

| Carpeta | Responsabilidad | Archivos clave |
|---|---|---|
| `backend/chat/` | Endpoint del chat y motor conversacional | `views.py`, `services/tutor_service.py`, `services/guided_problems.py`, `services/operation_guides.py`, `services/integrity.py`, `services/runtime.py` |
| `backend/exercises/` | Selección, evaluación (SymPy) y pistas de ejercicios | `services/exercise_selector.py`, `services/exercise_evaluator.py`, `services/hint_service.py`, `views.py` |
| `backend/progress/` | Progreso, XP, rangos, adaptación, eventos y regla de señales | `models.py`, `services/adaptive_learning_service.py`, `ranks.py`, `events.py`, `copy_signals.py` |
| `backend/classes/` | Grupos con código, analítica docente, retos y señales de copia | `views.py`, `serializers.py`, `urls.py` |
| `backend/accounts/` | Registro, sesión por token, perfil y Google Sign-In | `views.py`, `serializers.py`, `models.py` |
| `backend/curriculum/` | Catálogo de materias y temas, y explicaciones | `services/knowledge_service.py`, `services/curriculum_catalog.py`, `fixtures/catalogo.json` |
| `ml/` | Clasificador de intención y recuperación de tema (NLP local) | `src/gojarol_ml/nlp/analyzer.py`, `scripts/train_intents.py`, `artifacts/` |
| `content/` | Contenido educativo en JSON (temas, menús, ejercicios, currículo) | `topics/*.json`, `exercises/*.json`, `curriculum/registry.json` |
| `frontend/src/` | App React: chat, ejercicios, progreso, ligas y panel docente | `views/student/ChatView.tsx`, `components/exercise/ExerciseCard.tsx`, `views/teacher/TeacherDashboardView.tsx`, `services/api.ts` |

## 7. Tecnologías, librerías y plantillas declaradas

**No hay código previo al hackathon:** el primer commit (11 de noviembre de 2026, 13:58) solo contiene este README de 2 líneas. Las plantillas usadas son las oficiales: la de **Vite** para React + TypeScript (`frontend/README.md` conserva su texto) y la estructura estándar de Django.

| Componente | Versión | Licencia |
|---|---|---|
| Django · Django REST Framework | 6.1.3 · 3.18.3 | BSD-3-Clause |
| django-cors-headers · django-environ · gunicorn · whitenoise | 4.9.0 · 0.14.0 · 27.0.0 · 6.12.0 | MIT |
| psycopg (+ binary) | 3.3.8 | LGPL-3.0 |
| SymPy · mpmath | 1.14.0 · 1.3.0 | BSD |
| scikit-learn · pandas · NumPy · joblib | 1.9.1 · 2.3.3 · 2.5.4 · 1.6.0 | BSD-3-Clause (NumPy incluye además 0BSD, MIT y Zlib) |
| google-auth · requests · tzdata | 2.62.2 · 2.34.2 · 2026.6 | Apache-2.0 |
| pytest | 9.2.0 | MIT |
| React · React DOM · React Router | 19.3.1 · 19.3.1 · 7.18.5 | MIT |
| Vite · Tailwind CSS · @vitejs/plugin-react · oxlint | 8.3.7 · 4.3.5 · 6.3.0 · 1.93.0 | MIT |
| TypeScript | 7.0.2 | Apache-2.0 |
| lucide-react · canvas-confetti | 1.71.0 · 1.9.4 | ISC |
| Fuentes Sora y Atkinson Hyperlegible Next | — | SIL Open Font License 1.1 (OFL)<!-- CONECTIVIDAD:inicio -->; autoalojadas en `frontend/public/fonts/` con sus textos `OFL-*.txt`<!-- CONECTIVIDAD:fin --> |
| Google Identity Services (botón de Google) | servicio externo | Términos de Google |

Versiones leídas de los paquetes instalados (`importlib.metadata` y `node_modules/*/package.json`).

## 8. Datos

- **Contenido educativo:** redacción original del equipo, con referencias a programas públicos de la SEP en `content/curriculum/registry.json` y en 4 de los 6 temas (`content/topics/*.json`). Ver [docs/COBERTURA_CURRICULAR.md](docs/COBERTURA_CURRICULAR.md).
- **Clasificador:** dataset **sintético** generado por `ml/scripts/generate_intents_dataset.py` (semilla fija), más 120 frases escritas a mano por el equipo.
- **Cuentas y datos de la demo:** ficticios. No se usan datos personales reales.
- **Qué se guarda y qué no:** los eventos de anticopia guardan solo el tipo, el tema y la fecha, **nunca el texto del mensaje**. Desde el chat se guarda solo la respuesta extraída (por ejemplo `3/4`), y desde la tarjeta de ejercicio, la respuesta escrita (máximo 255 caracteres). Detalle en [docs/anticopia.md](docs/anticopia.md#2-qué-se-registra-y-qué-no).

## 9. Bitácora de IA

Se evalúa qué tan bien usamos la IA, no cuánto. Ninguna IA externa responde a los alumnos dentro del producto: el tutor es un clasificador entrenado más reglas y plantillas.

| Herramienta | Para qué | Decisiones clave |
|---|---|---|
| **Antigravity AI (Gemini 3.8 Flash)**, Hugo · 24 entradas en [docs/bitacora/hugo_frontend.md](docs/bitacora/hugo_frontend.md) | **Arquitectura y diseño:** análisis del reto, contratos de API, mapa de pantallas y sistema visual. **Frontend:** React 19 + TypeScript + Tailwind, vistas responsivas, tarjeta de ejercicio y ligas. **Autenticación:** login y registro separados, Google Sign-In y decodificación del JWT. **Despliegue:** Docker, nginx con Certbot en el VPS Debian, diagnóstico de gunicorn y `ALLOWED_HOSTS`/CORS. **Integración** frontend ↔ backend ↔ tutor, grupos por código y analítica docente. | *Mobile-first*; los prototipos como guía de estilo y no como pantallas fijas; la tarjeta de ejercicio nunca recibe la respuesta correcta; flujo de login real en lugar de usuarios de prueba precargados. |
| **Google Stitch**, Hugo | Sistema de diseño inicial, tokens y prototipos. | Paleta y tipografías de identidad veracruzana. |
| **Generador de imágenes** [completar herramienta], Hugo | Mascota "Jarol el Cangrejo Maestro". | — |
| **Claude (chat)**, [Aldair] | Planificación, conversaciones de prueba contra el reto, diagnóstico de fallos, redacción de casos de uso y de prompts para el agente. | Se descartaron propuestas de código que no cumplían el reto. |
| **Antigravity **, Ivan | Servicio de tutoría y clasificador de intención del chat. | Entrenar con datos sintéticos y validar además con 120 ejemplos escritos a mano; dejar documentado que las métricas no demuestran rendimiento con estudiantes reales. |
| **[herramienta, o "Sin herramientas de IA"]**, Sarahi e Ivan Rodrigues | Documentación del proyecto: casos de uso, requisitos, diseño de interfaz y pruebas de aceptación. | |

**Decisiones clave del equipo**

| Decisión | Por qué |
|---|---|
| Tutor híbrido: clasificador de intención entrenado + reglas y plantillas | Sin IA generativa externa, el comportamiento es predecible y comprobable con pruebas. |
| Pregunta de diagnóstico antes de explicar | Explicar solo la parte que se complica, como pide el reto. |
| Ejemplos con otros números | Enseñar el procedimiento sin resolver el problema del alumno. |
| Rango personal sin competencia entre menores | Motivar sin exponer ni comparar a los alumnos. |
| Anticopia = rechazo con ayuda + eventos sin texto + señal "indicio, no acusación" | Reducir la copia, hacerla visible al docente y proteger la privacidad de menores. |
| Poca conexión = WebP, fuentes locales, gzip y errores honestos en lugar de respuestas simuladas | Menos datos y ninguna respuesta falsa cuando falla la red. |
| Pruebas automáticas contra fugas del resultado | Demostrar, y no solo afirmar, que Jarol no entrega respuestas. |

## 10. Equipo

| Integrante | Rol |
|---|---|
| Hugo Garcia Lara | [Front] |
| Raul Aldair Osorio Contreras | [Back] |
| Ivan | [IA] |
| Sarahi | Documentación y diseño ·|
| Ivan Rodrigues | Documentación y diseño · |

## 11. Documentación adicional

- [docs/CONTEXTO.md](docs/CONTEXTO.md): reglas del reto, alcance y flujo de trabajo del equipo.
- [docs/anticopia.md](docs/anticopia.md): cómo se atendió el giro, qué se registra, límites y guion de demo.
<!-- CONECTIVIDAD:inicio -->
- [docs/conectividad.md](docs/conectividad.md): mediciones de peso, comportamiento sin conexión y pruebas PA-10 y PA-11.
<!-- CONECTIVIDAD:fin -->
- [ml/README.md](ml/README.md): dataset, entrenamiento, métricas y límites del clasificador.
- [docs/FRONTEND.md](docs/FRONTEND.md), [docs/DESPLIEGUE.md](docs/DESPLIEGUE.md), [docs/INFRAESTRUCTURA_HOST.md](docs/INFRAESTRUCTURA_HOST.md)
- [docs/COBERTURA_CURRICULAR.md](docs/COBERTURA_CURRICULAR.md) y [docs/decisions/001-curriculum-catalog.md](docs/decisions/001-curriculum-catalog.md)
