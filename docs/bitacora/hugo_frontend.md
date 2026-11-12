# Bitácora de Inteligencia Artificial · Frontend (Hugo)

Registro obligatorio de uso de herramientas de Inteligencia Artificial para el Reto 5 "Aprender a la jarocha" (Hackathon Veracruz Tech Week 2026).

---

## Estructura de Registro

Para cada sesión o iteración se documenta:
1. **Herramienta de IA**: Nombre del modelo/asistente.
2. **Propósito / Para qué**: Tarea concreta asignada.
3. **Decisiones Clave**: Criterios adoptados, descartados o adaptados a partir de las sugerencias de la IA.
4. **Impacto en el Código / Producto**: Archivos y componentes resultantes.

---

## Entradas de la Bitácora

### Entrada 1 · 11 de Noviembre de 2026 (17:15 - 17:30)

- **Herramientas de IA utilizadas**:
  - **Google Stitch**: Generación del sistema de diseño inicial, tokens de diseño y prototipos interactivos (`go_jarol_conversational_edtech`).
  - **Antigravity AI (Gemini 3.8 Flash)**: Asistente de arquitectura, análisis del contexto del hackathon, especificación de diseño (`DESIGN.md`), contratos de API y estructuración del frontend.
  - **Generador de imagen/diseño**: Creación de la mascota oficial ("Jarol el Cangrejo Maestro" con guayabera, lentes y sombrero jarocho).

- **Para qué se usaron**:
  - Análisis del reglamento, alcance (tema estrella: Aritmética → Fracciones) y restricción pedagógica (Jarol **nunca** resuelve ejercicios ni entrega respuestas finales).
  - Extracción y normalización de la paleta identitaria de Veracruz (`#F7F5EF`, `#126B73`, `#E76D55`, `#E4AA50`, etc.) y tipografías (**Sora** + **Atkinson Hyperlegible Next**).
  - Definición de la interacción física ("Tactile Modernism" con sombras sólidas 3D estilo Duolingo).
  - Planificación de la capa de mocks desacoplada del backend `/api/v1/`.

- **Decisiones clave tomadas**:
  1. **Mobile-First real**: El jurado y los usuarios objetivo son estudiantes de secundaria y bachillerato en Veracruz que usan celular con conexión inestable; la vista y navegación se optimizan para < 768px con columnas centradas en desktop.
  2. **No copiar pantallas ciegamente**: Los prototipos de Stitch sirven como guía de **estilo, tokens y componentes interactivos** (tarjetas de ejercicio, feedback banners, burbujas de chat asimétricas), no como pantallas rígidas monolíticas.
  3. **Aislamiento por mocks de API**: Implementar un cliente de API con adaptador intercambiable (Mock vs. Real Django) para no bloquear el desarrollo mientras el backend en Django de Aldair se despliega.
  4. **Componentes pedagógicos desacoplados**: La tarjeta de ejercicio no contendrá la respuesta correcta en el estado inicial del cliente; solo se enviará la opción elegida al endpoint `/api/v1/exercises/{id}/answer/` respetando la regla pedagógica.

- **Archivos creados / modificados**:
  - `docs/bitacora/hugo_frontend.md`
  - `docs/FRONTEND.md`

### Entrada 2 · 11 de Noviembre de 2026 (17:25 - 17:35)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Definición de estrategia de despliegue en servidor Debian y dockerización de la arquitectura.

- **Para qué se usaron**:
  - Elaboración de la guía de despliegue para producción en Debian (`docs/DESPLIEGUE.md`).
  - Configuración del flujo de entrega para el servidor del equipo, asegurando compatibilidad tanto por contenedores Docker (Nginx multi-stage + Gunicorn + PostgreSQL) como por instalación nativa en el sistema operativo.

- **Decisiones clave tomadas**:
  1. **Estrategia dual de despliegue**: Se documentó Docker Compose como vía principal para estandarizar entornos entre desarrolladores y el servidor Debian, pero dejando la alternativa nativa con Nginx y Systemd si el servidor no tiene Docker.
  2. **Multi-stage build para el Frontend**: Uso de Node 20 en la etapa de compilación y Nginx Alpine en la etapa final para generar una imagen ultra ligera (< 30 MB) que no consume recursos excesivos en el servidor del hackathon.
  3. **Proxy inverso integrado**: Nginx se encarga de servir la SPA en `/` y redirigir `/api/v1/` hacia el backend en Django/Gunicorn, eliminando problemas de CORS en producción y garantizando que las recargas de ruta funcionen sin error 404.

- **Archivos creados / modificados**:
  - `docs/DESPLIEGUE.md`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 3 · 11 de Noviembre de 2026 (17:30 - 17:35)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Definición del mapa integral de arquitectura de navegación (18 interfaces distribuidas por roles).

- **Para qué se usaron**:
  - Estructuración de las interfaces y rutas para los 3 roles de usuario: **Alumno (7)**, **Maestro (5)**, **Administrador (6)** y **Pantallas Compartidas (5)**.
  - Priorización explícita del alcance para el Hackathon de 24 horas, identificando la matriz de vistas reutilizables (misma base de diseño con variaciones de permisos).

- **Decisiones clave tomadas**:
  1. **Enfoque en el MVP sin perder la visión completa**: Para el demo de 24 horas se priorizan: *Chat con Jarol*, *Retos*, *Mi progreso*, *Mis clases* (Alumno) y *Panel docente* (Maestro). Las interfaces de Administrador quedan modeladas a nivel de catálogo/rutas para fases posteriores.
  2. **Reutilización inteligente de componentes**: Diseñar layouts modulares compartidos (`ClassCard`, `ProgressCard`, `AuthForm`) para que las 18 interfaces se resuelvan con un número compacto de componentes de alta calidad sin duplicar código.
  3. **Barra de navegación inferior adaptativa**: Barra mobile-first que cambia dinámicamente según el rol autenticado (`Alumno`: Jarol, Retos, Clases, Progreso; `Maestro`: Panel, Clases, Alumnos, Perfil).

- **Archivos creados / modificados**:
  - `docs/FRONTEND.md`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 4 · 11 de Noviembre de 2026 (17:35 - 17:42)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Inicialización del proyecto Frontend con Vite + React 19 + TypeScript + Tailwind CSS v4, e implementación del MVP del Hackathon.

- **Para qué se usaron**:
  - Creación del entorno `frontend/` mediante `pnpm` y configuración del pipeline de estilos sin dependencias de CDNs externos.
  - Implementación del sistema de diseño táctil 3D con tokens veracruzanos (`#F7F5EF`, `#126B73`, `#E76D55`, `#E4AA50`, `#0A1D2C`) y tipografías Sora + Atkinson Hyperlegible Next.
  - Implementación del núcleo conversacional con Jarol (`ChatView`, `JarolBubble`, `UserBubble`, `FloatingInput`, `PromptSuggestions`).
  - Creación de la tarjeta interactiva de fracciones (`ExerciseCard`) con validación formativa determinista, pistas pedagógicas sin revelar la solución de antemano y micro-feedback con confeti.
  - Creación del panel docente (`TeacherDashboardView`) con semáforo de dificultades en fracciones y generador de códigos de clase.
  - Implementación del selector instantáneo de roles en cabecera (`AuthContext`) para que el presentador pueda alternar entre Estudiante y Docente en segundos frente al jurado.
  - Creación del `Dockerfile` multi-stage y `nginx.conf` para despliegue en servidor Debian.

- **Decisiones clave tomadas**:
  1. **Strict TypeScript & VerbatimModuleSyntax**: Se aseguró compatibilidad tipada estricta (`import type`) en todos los contratos para evitar caídas en tiempo de ejecución.
  2. **Regla pedagógica protegida en el cliente**: Las opciones de ejercicios de fracciones se envían a evaluar al backend/servicio (`apiService.submitExerciseAnswer`); el objeto inicial del ejercicio no expone la respuesta correcta en el frontend.
  3. **Conmutador de perspectiva en caliente**: El botón de cabecera permite cambiar entre la experiencia de alumno y la vista de maestro en tiempo real, maximizando los 4 minutos de demostración en vivo.

- **Archivos creados / modificados**:
  - `frontend/src/` (App.tsx, index.css, vite.config.ts, context, components, views, services, types)
  - `frontend/Dockerfile` & `frontend/nginx.conf`
  - `frontend/public/mascot/jarol-crab.png`
  - `docs/FRONTEND.md`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 5 · 11 de Noviembre de 2026 (17:45 - 17:50)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Expansión de interfaces clave del sistema (Ligas Semanales, Detalle Diagnóstico del Estudiante y Modal de Autenticación/Registro).

- **Para qué se usaron**:
  - Creación de la vista de **Ligas Semanales (`LeaguesView.tsx`)**: Podio Top 3 (Oro, Plata, Bronce), división regional veracruzana ("División Sotavento · Plata"), contador de días para el cierre de liga y llamada a la acción para ganar XP con fracciones.
  - Creación de la **Ficha Diagnóstica del Estudiante (`StudentDetailModal.tsx`)**: Integración con el panel docente permitiendo al maestro abrir el perfil de Emiliano, Sofía o Mateo y revisar sus competencias consolidadas, áreas en riesgo y el historial de intentos con la retroalimentación y pistas dadas por Jarol.
  - Creación del **Modal de Autenticación y Registro (`AuthModal.tsx`)**: Selector de rol (Alumno / Maestro), selección de grado escolar (1°-3° Secundaria / Bachillerato) y escuela de procedencia en Veracruz.
  - Integración en la barra de navegación inferior móvil (`BottomNav`) agregando la pestaña **Ligas** con icono de trofeo.

- **Decisiones clave tomadas**:
  1. **Gamificación pedagógica contextualizada**: Las ligas agrupan a alumnos por divisiones locales veracruzanas para fomentar el sentido de pertenencia sin generar ansiedad competitiva nociva.
  2. **Trazabilidad pedagógica para el jurado**: Al pulsar sobre cualquier alumno en el panel docente, el jurado puede ver exactamente por qué Jarol detectó un concepto en riesgo (ej. *sumó denominadores directos 2/6 en vez de buscar equivalencias*), demostrando la regla pedagógica del reto en acción.
  3. **Flujo de acceso flexible**: Se permite al usuario o evaluador registrarse desde cero o usar el atajo de cambio rápido en cabecera para agilizar el tiempo durante la presentación.

- **Archivos creados / modificados**:
  - `frontend/src/views/student/LeaguesView.tsx`
  - `frontend/src/views/teacher/StudentDetailModal.tsx`
  - `frontend/src/components/auth/AuthModal.tsx`
  - `frontend/src/types/leagues.ts`
  - `frontend/src/services/mockData.ts`
  - `frontend/src/components/layout/BottomNav.tsx`
  - `frontend/src/components/layout/AppHeader.tsx`
  - `frontend/src/App.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 6 · 11 de Noviembre de 2026 (17:50 - 17:56)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Implementación de vistas de Detalle de Clase, Perfil con Logros/Medallas y cierre del ciclo completo de interfaces.

- **Para qué se usaron**:
  - Creación del **Detalle de Clase (`ClassDetailModal.tsx`)**: Pestañas de *Retos Asignados* (Suma y resta de fracciones con enlace directo a resolver con Jarol), *Compañeros de Salón* y *Avisos Docentes*.
  - Creación del **Modal de Perfil y Medallas (`ProfileModal.tsx`)**: Vitrina de medallas (*"Primer Reto Resuelto"*, *"Racha de 4 Días"*, *"Orgullo Jarocho"*), controles de accesibilidad WCAG AA (alto contraste) y opciones de cambio de cuenta.
  - Conexión de aperturas modales con la barra de navegación y la cabecera.

- **Decisiones clave tomadas**:
  1. **Consistencia en navegación modal**: Los detalles de clase y de perfil se presentan en hojas modales centradas sobre el canvas `#F7F5EF` con sombras profundas, facilitando la navegación sin perder el contexto del chat o de la lista de clases.
  2. **Interconexión directa de flujos**: Al ver el reto de fracciones dentro de la clase, el estudiante puede dar clic en *"Resolver con Jarol"* y ser llevado directamente a la conversación guiada.

- **Archivos creados / modificados**:
  - `frontend/src/views/student/ClassDetailModal.tsx`
  - `frontend/src/components/profile/ProfileModal.tsx`
  - `frontend/src/views/student/ClassesView.tsx`
  - `frontend/src/components/layout/AppHeader.tsx`
  - `frontend/src/App.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 7 · 11 de Noviembre de 2026 (18:05 - 18:08)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Ajuste de infraestructura y orquestación con la IA de administración del servidor Debian (Reverse Proxy nativo multi-sitio).

- **Para qué se usaron**:
  - Creación del archivo oficial `docker-compose.yml` en la raíz del proyecto.
  - Ajuste de mapeo de puertos del contenedor frontend hacia `127.0.0.1:3000:80` para no colisionar con los puertos 80 y 443 del Nginx nativo del host.
  - Aislamiento estricto del backend Django en la red interna de Docker (`expose: - "8000"` sin exponer puertos al host) para no chocar con el puerto 8000 ocupado por otro servicio del VPS.
  - Actualización de `frontend/nginx.conf` con `proxy_pass http://backend:8000;` para que el proxy interno resuelva por DNS interno de Docker.

- **Decisiones clave tomadas**:
  1. **Seguridad por loopback (`127.0.0.1`)**: El frontend no se abre directamente a internet en el puerto 3000, sino únicamente al loopback local para que el Nginx nativo del servidor Debian gestione el dominio y los certificados SSL.
  2. **Zero port collision**: Se garantizó que ningún puerto de GoJarol (80, 443, 8000) colisione con los servicios existentes del servidor de producción.

- **Archivos creados / modificados**:
  - `docker-compose.yml`
  - `frontend/nginx.conf`
  - `docs/DESPLIEGUE.md`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 8 · 11 de Noviembre de 2026 (18:18 - 18:22)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Formalización del Contexto Maestro de Infraestructura del Host Debian VPS e integración con Nginx multi-dominio con Certbot.

- **Para qué se usaron**:
  - Creación del documento normativo [`docs/INFRAESTRUCTURA_HOST.md`](docs/INFRAESTRUCTURA_HOST.md).
  - Validación minuciosa de las 4 reglas maestras del servidor (Zero puertos públicos en Docker, binding loopback en 3000, aislamiento estricto de backend/db sin `ports`, Nginx nativo como terminador SSL, rutas relativas y credenciales protegidas en `.env`).
  - Elaboración de la configuración de Virtual Host Nginx para el host VPS para facilitar la labor de la IA de despliegue.

- **Decisiones clave tomadas**:
  1. **Alineación total con Tonalkab y proyectos existentes**: El contenedor de Go Jarol respeta íntegramente los puertos 8000 (API Tonalkab) y 8080 (Admin Tonalkab), operando exclusivamente en `127.0.0.1:3000:80`.
  2. **Persistencia y documentación permanente**: Se dejó constancia técnica en `docs/` para que cualquier compañero o agente que trabaje en el repo no altere accidentalmente la configuración de red del servidor de producción.

- **Archivos creados / modificados**:
  - `docs/INFRAESTRUCTURA_HOST.md`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 9 · 11 de Noviembre de 2026 (18:43 - 18:48)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Implementación de arquitectura responsiva integral para Tablet y Computadora (Desktop).

- **Para qué se usaron**:
  - Creación del componente de navegación lateral para escritorio [`DesktopSidebar.tsx`](frontend/src/components/layout/DesktopSidebar.tsx) que se activa automáticamente en pantallas medianas y grandes (`md:` y `lg:`).
  - Adaptación de la cabecera móvil (`AppHeader.tsx`) y de la barra inferior móvil (`BottomNav.tsx`) para ocultarse limpiamente en pantallas de escritorio sin duplicar controles.
  - Expansión de cuadrículas de contenido: retos por materia en 2 columnas, métricas docentes en 4 columnas, y semáforo de dificultades en paralelo con la lista de alumnos en desktop.
  - Centrado de lectura fluido para el chat conversacional con Jarol (`max-w-3xl`) e input flotante adaptativo al pie de pantalla.

- **Decisiones clave tomadas**:
  1. **Dualidad Mobile-First y Desktop-Rich**: Se mantuvo la experiencia ágil en celular para los estudiantes con conexión inestable, y se dotó a la vista de escritorio de una estructura estilo aplicación moderna (Slack / Notion) ideal para la proyección en proyector o laptop ante el jurado.
  2. **Persistencia de la interacción táctil**: Los botones de acción, selector de rol y tarjetas conservan su profundidad física 3D en todas las resoluciones.

- **Archivos creados / modificados**:
  - `frontend/src/components/layout/DesktopSidebar.tsx`
  - `frontend/src/components/layout/AppHeader.tsx`
  - `frontend/src/components/layout/BottomNav.tsx`
  - `frontend/src/components/chat/FloatingInput.tsx`
  - `frontend/src/views/student/ChatView.tsx`
  - `frontend/src/views/student/ChallengesView.tsx`
  - `frontend/src/views/student/ClassesView.tsx`
  - `frontend/src/views/student/ProgressView.tsx`
  - `frontend/src/views/student/LeaguesView.tsx`
  - `frontend/src/views/teacher/TeacherDashboardView.tsx`
  - `frontend/src/App.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 10 · 11 de Noviembre de 2026 (19:50 - 19:55)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Configuración de infraestructura contenerizada para el Backend Django, PostgreSQL y preparación del manual técnico de despliegue para el VPS multi-tenant Debian.

- **Para qué se usaron**:
  - Creación de [`backend/Dockerfile`](backend/Dockerfile) con imagen ligera `python:3.11-slim`, incluyendo la inyección del módulo local de Machine Learning (`ml/`) y los tópicos curriculares (`content/`).
  - Creación de [`backend/requirements.txt`](backend/requirements.txt) con dependencias completas (Django, DRF, Gunicorn, WhiteNoise, Psycopg2-binary, SymPy, Scikit-learn, Pandas, Joblib).
  - Actualización del archivo de orquestación [`docker-compose.yml`](docker-compose.yml) configurando el servicio de base de datos PostgreSQL 15 alpine aislado en la red interna `gojarol_net` y el backend en WSGI con Gunicorn (`config.wsgi:application`).
  - Síntesis y documentación técnica del backend, modelo de datos relacional y procedimiento de migración para el asistente de despliegue en el servidor de producción.

- **Decisiones clave tomadas**:
  - Aislamiento estricto de la base de datos y backend: solo el frontend expone al loopback (`127.0.0.1:3000`), protegiendo los puertos 8000 (ocupado por Tonalkab) y 80/443 (dueño Nginx nativo).
  - Persistencia de datos en volumen Docker nombrado `postgres_data`.

- **Archivos creados / modificados**:
  - `backend/Dockerfile`
  - `backend/requirements.txt`
  - `docker-compose.yml`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 11 · 11 de Noviembre de 2026 (20:20 - 20:25)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Diagnóstico en vivo de logs de producción, resolución del error de arranque de Gunicorn (`core.wsgi` vs `config.wsgi`) y verificación de despliegue integral.

- **Para qué se usaron**:
  - Análisis del traceback de logs de `gojarol_backend` identificando la discrepancia entre el módulo WSGI de Django (`core.wsgi` referenciado en compose vs `config.wsgi` real).
  - Guía de ejecución del comando de sustitución `sed` y orquestación con Docker Compose.
  - Ejecución de migraciones de base de datos PostgreSQL (`accounts`, `curriculum`, `authtoken`, `contenttypes`, etc.).
  - Ejecución de `collectstatic` en contenedor backend (157 archivos estáticos copiados a `/app/staticfiles`).
  - Verificación exitosa del endpoint de salud `HTTP/1.1 200 OK {"status": "ok"}` en `http://127.0.0.1:3000/api/v1/health/` y HTTPS activo con Certbot en producción.

- **Decisiones clave tomadas**:
  - Despliegue 100% operativo en producción (`https://gojarol.tecnodesarrollo.site`) con arquitectura full-stack desacoplada y segura.

- **Archivos creados / modificados**:
  - `docker-compose.yml`
  - `docs/bitacora/hugo_frontend.md`
