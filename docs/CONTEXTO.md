# GO JAROL · CONTEXTO GENERAL DEL EQUIPO
Hackathon Veracruz Tech Week 2026 · Reto 5 "Aprender a la jarocha" · 24 horas

Léanlo completo antes de empezar. La visión completa del producto está en docs/CONTEXTO.md; este documento dice qué hacemos realmente en 24 horas y cómo trabajamos juntos.

## 1. Equipo y responsabilidades
| Persona | Área | Carpeta |
|---|---|---|
| Aldair | Backend (Django, PostgreSQL, API, motor educativo) | backend/ |
| Ivan (GitHub: ivan2729i) | ML/NLP (dataset, entrenamiento, inferencia) | ml/ |
| Hugo | Frontend (React, vistas, integración con la API) | frontend/ |
| Sarahi e Ivan Rodrigues | Documentación y diseño | docs/ y design/ |

Documentación: README final, Bitácora de IA consolidada, ficha de una página, guion del demo.
Diseño: identidad visual, mockups de las pantallas clave para Hugo, mascota Jarol, portada de la ficha.
El reparto entre Sarahi e Ivan Rodrigues lo deciden ellos y lo anotan aquí: [pendiente].

## 2. Qué construimos
Go Jarol es una plataforma web para estudiantes de secundaria y bachillerato en Veracruz. Incluye un tutor conversacional (Jarol) que pregunta antes de responder, se adapta al nivel del alumno, funciona bien en celular y con poca conexión, y da a los docentes una vista del avance de su grupo.

## 3. Reglas del evento (nos descalifican si las rompemos)
- Cierre de código y entrega: jueves 12, 10:30 h, por formulario. Después no se aceptan cambios.
- Puntos de control: miércoles 17:00 y 20:30, con al menos un commit en cada uno. El historial de Git cuenta como evidencia, así que cada integrante debe tener commits propios.
- Jueves 7:00: el reto recibe un requisito nuevo que debe aparecer en el demo. Hay que dejar capacidad para integrarlo.
- Jurado: 8 minutos, 4 de demo en vivo y 4 de preguntas. Presentaciones jueves de 11:00 a 13:00.
- Entregables: repositorio, README, enlace a la demo, video de respaldo (máx. 2 min) y ficha de una página.
- IA permitida; se evalúa qué tan bien la usamos. Obligatoria una Bitácora de IA en el README: herramientas usadas, para qué y decisiones clave.
- Cualquier integrante debe poder explicar cualquier parte del proyecto. Si nadie puede explicar una parte central, nos descalifican.
- Se permiten librerías y plantillas públicas si las declaramos en el README. No se vale traer un proyecto hecho.
- Solo datos públicos, de ejemplo o sintéticos. Cero datos personales reales.
- No presentar como funcional algo que no lo es.

## 4. Regla pedagógica (la dijo el asesor del evento)
Jarol NO resuelve problemas ni da el resultado de una operación. Solo explica el tema y guía. Si el alumno trae un problema con quebrados, Jarol explica cómo se suman, restan, multiplican y dividen quebrados, pero no resuelve ese problema.

Cómo lo cumplimos:
- Explica con un ejemplo resuelto con OTROS números y le pregunta al alumno cómo aplicarlo a su caso.
- Antes de explicar, pregunta qué sabe el alumno.
- Si el alumno se atora, cambia de estrategia (otro ejemplo, analogía, paso previo). Las pistas no revelan la respuesta.
- SymPy solo VERIFICA lo que el alumno escribe, nunca resuelve para mostrar.
- La solución de un ejercicio activo nunca sale del backend: no llega al frontend ni al generador de respuestas.

## 5. Alcance del demo (cerrado)
Solo 3 materias activas, con un tema cada una:
- Aritmética → Fracciones (tema estrella: se construye primero y de punta a punta)
- Álgebra → Ecuaciones lineales
- Matemáticas → Teorema de Pitágoras

Las otras 6 materias (Español, Historia, Geografía, Física, Química, Biología) aparecen como "Próximamente". Los tres temas son numéricos, para verificar respuestas de forma determinista.

Pantallas del demo: registro y login, chat con Jarol con tarjetas de ejercicio, mi progreso y, para el docente, crear clase con código, ver estudiantes y dificultades por tema.
Si sobra tiempo: ligas simplificadas, PWA con caché, un tema teórico pequeño.
Después del hackatón: las 9 materias completas, embeddings, panel de administración propio.

Flujo que debe funcionar de punta a punta: el estudiante se registra, abre el chat, pregunta sobre un tema, Jarol le pregunta qué sabe, explica con ejemplo, propone un ejercicio, el alumno responde, el sistema verifica, da pistas o felicita, se actualiza su perfil y su XP, y el docente ve el avance.

## 6. Stack
| Área | Tecnologías |
|---|---|
| Frontend | React + TypeScript, Vite, pnpm (no npm), Tailwind CSS local, Lucide React |
| Backend | Python, Django, Django REST Framework, PostgreSQL, Django ORM, API REST versionada, django-environ, django-cors-headers, SymPy |
| ML/NLP | Python, scikit-learn (TF-IDF + Logistic Regression), joblib, SymPy |
| Despliegue | Servidor Debian de un compañero: nginx + gunicorn + PostgreSQL. Docker solo si el equipo lo decide; nadie lo necesita para programar |

Restricciones:
- Nada de APIs externas de IA (OpenAI, Gemini, Claude) en el producto. El NLP es local.
- No entrenamos un modelo generativo: es un clasificador de intenciones entrenado + un motor conversacional por reglas y plantillas. Así lo decimos en el demo.
- Sin CDNs para dependencias esenciales: Tailwind, iconos y fuentes van locales.
- Sin Redis, Celery ni microservicios.
- Arquitectura: monolito modular Django con frontend React desacoplado.

## 7. Identidad visual (diseño y frontend)
- Mobile-first, navegación inferior en celular, chat como elemento central, accesibilidad WCAG AA como objetivo, estados de carga, error y sin conexión.
- Paleta: fondo #F7F5EF, superficies #FFFFFF, azul tinta #0B1E2D, verde mar #126B73, coral #E76D55, verde suave #DCEFEB, texto secundario #596B72, amarillo cálido #E4AA50.
- Tipografía: Sora (encabezados) y Atkinson Hyperlegible (contenido), alojadas localmente.
- Concepto: educación, orientación, cercanía y referencias sutiles a Veracruz. Sin dashboard genérico ni copia de Duolingo.
- Diseño entrega a Hugo: mockups de las pantallas del demo (registro, chat con tarjeta de ejercicio, progreso, panel docente), exportados en design/, y la mascota Jarol en formato web ligero (SVG o PNG optimizado).
- Prioridad de diseño: primero el chat y la tarjeta de ejercicio, porque son el núcleo del demo.

## 8. Estructura del repositorio
    GoJarol/
    ├── README.md        (con la Bitácora de IA)
    ├── .gitignore  .gitattributes  .env.example
    ├── docs/            (CONTEXTO.md, EQUIPO.md, contratos, bitacora/)
    ├── design/          (mockups, mascota, assets exportados)
    ├── ml/              (Ivan)
    ├── backend/         (Aldair)
    └── frontend/        (Hugo)

Cada persona es dueña de su carpeta. No se edita la carpeta de otro sin avisar.

## 9. Contratos entre equipos
Se acuerdan ANTES de integrar. Si alguien necesita cambiar uno, avisa al grupo.

NLP (ml/ → backend): analyze_message(message, context) devuelve
{ "intent", "intent_confidence", "subject", "topic", "topic_score", "needs_clarification", "topic_available" }
Mientras el modelo real se entrena, Ivan entrega una versión 0 por palabras clave con la misma firma.

API (backend → frontend), PROPUESTA a confirmar:
- Prefijo /api/v1/, JSON, autenticación por token en el encabezado Authorization.
- Errores con formato único: { "error": { "code": "...", "message": "..." } }
- POST auth/register/ y auth/login/ (devuelven token y usuario), GET auth/me/
- GET subjects/ (las 9 materias, con campo disponible)
- POST chat/messages/ (mensaje del alumno; devuelve respuesta de Jarol, ejercicio activo SIN solución, e intención y tema detectados)
- POST exercises/{id}/answer/ (devuelve si es correcta, retroalimentación, pista y XP ganado)
- GET progress/me/, POST classes/, POST classes/join/ (con código), GET classes/{id}/overview/
- GET health/ responde { "status": "ok" }
Mientras el backend no esté listo, Hugo trabaja con datos simulados en una carpeta de mocks, con la misma forma que el contrato.

## 10. Flujo de Git (todos, incluida documentación y diseño)
- main siempre debe funcionar. Nadie trabaja directo en main.
- Cada quien trabaja en una rama propia con prefijo de su área (backend-..., ml-..., frontend-..., docs-..., design-...), solo dentro de su carpeta.
- Ciclo: git pull → trabajar → git status → git add . → git commit -m "..." → git push → Pull Request → merge → avisar en el grupo.
- Ramas de vida corta (1 a 2 horas). Commits pequeños y frecuentes, con mensaje que diga qué hiciste.
- Antes de mezclar, la app debe correr (para diseño y documentación: que no rompan nada fuera de sus carpetas).
- Archivos compartidos (README.md, .gitignore, .env.example): una sola persona los edita a la vez y avisa. El README lo edita documentación; los demás le pasan sus notas.
- Alarmas a las 16:45 y 20:15: todos hacen commit y push.
- Si hay un conflicto, no entrar en pánico: avisar en el grupo.

## 11. Secretos y entorno
- Nunca se sube .env. Se sube .env.example, con valores de ejemplo.
- Se usa PostgreSQL. La conexión va en DATABASE_URL del .env de cada quien.
- Cada laptop tiene su propia base de datos. Los datos iniciales (materias y temas) van en una fixture o comando de carga para que todos arranquen igual.
- Todos deben usar la misma versión de Python y de scikit-learn, porque los modelos joblib de Ivan fallan al cargar con versiones distintas. [Versión acordada: ___]
- Los assets de diseño deben pesar poco: la plataforma es para celulares con poca conexión.

## 12. Bitácora de IA
Cada integrante anota en docs/bitacora/[nombre].md: herramienta usada, para qué y qué decidió (incluye IA para diseño, textos, código o dataset). Al final, documentación la consolida en el README.

## 13. Plan de tiempo
- 17:00 punto de control
- 17:00 a 20:15: Fracciones de punta a punta (registro, chat con Jarol, ejercicio, verificación, XP). Diseño entrega mockups del chat y del ejercicio a Hugo.
- 20:30 punto de control
- Noche: temas 2 y 3, panel docente, pulido en celular, primer despliegue de prueba, descanso por turnos. Documentación avanza README, ficha y guion del demo.
- Jueves 7:00: requisito nuevo
- 8:00 a 9:30: congelar funciones, video de respaldo, ficha, README final
- 10:30: entrega

## 14. Pendientes por confirmar
- Versión de Python común y versión de Node
- Contratos de API y NLP (sección 9)
- Herramienta de diseño y formato de entrega a Hugo
- Si el servidor es accesible desde internet (el jurado debe abrir el demo) y si habrá HTTPS
- Si usaremos Docker en el despliegue o instalamos directo en Debian
- Reparto entre Sarahi e Ivan Rodrigues

## 15. Instrucciones para cualquier asistente de código o de texto
Somos principiantes: explica cada archivo y decisión en lenguaje sencillo, haz cambios pequeños que podamos probar y no agregues dependencias innecesarias. Respeta docs/CONTEXTO.md y este documento. No inventes contenido académico ni métricas de modelos. Distingue entre funcionalidad real, simulada y pendiente. No cambies contratos compartidos sin avisar. Trabaja solo en la carpeta del dueño. Nunca expongas secretos ni la solución de un ejercicio activo.