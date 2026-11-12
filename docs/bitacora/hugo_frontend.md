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

### Entrada 12 · 11 de Noviembre de 2026 (20:25 - 20:32)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Fusión de la rama `main` hacia `hugo-dev` e implementación completa de la autenticación con Google (Google Sign-In / OAuth).

- **Para qué se usaron**:
  - Sincronización y resolución limpia del merge conflict de dependencias en `backend/requirements.txt` integrando el stack de Django 6 con el módulo pedagógico y NLP local de Machine Learning.
  - Implementación del botón y flujo de autenticación con Google en [`AuthModal.tsx`](frontend/src/components/auth/AuthModal.tsx), incluyendo el logotipo SVG oficial, integración de Google Identity Services (GIS), y selector de cuentas institucionales de Veracruz (`@estudiantes.sev.gob.mx` y `@docentes.sev.gob.mx`).
  - Creación del método `loginWithGoogle` en [`api.ts`](frontend/src/services/api.ts) y persistencia de sesión en [`AuthContext.tsx`](frontend/src/context/AuthContext.tsx).
  - Creación del endpoint `POST /api/v1/auth/google/` en Django ([`backend/accounts/views.py`](backend/accounts/views.py) y [`urls.py`](backend/accounts/urls.py)) que decodifica credenciales de Google, gestiona la creación idempotente del usuario en PostgreSQL y expide tokens de autenticación de DRF.
  - Pruebas unitarias de autenticación Google añadidas en [`backend/accounts/tests.py`](backend/accounts/tests.py).

- **Decisiones clave tomadas**:
  - Se habilitó tanto el soporte para tokens reales de Google Identity Services como un selector ágil de cuentas institucionales veracruzanas con avatares reales para facilitar las demostraciones en vivo ante el jurado del hackathon sin depender de bloqueos por popups externos.
  - El perfil (`ProfileModal.tsx`) muestra el distintivo y correo oficial de Google con el que el usuario inició sesión.

- **Archivos creados / modificados**:
  - `backend/accounts/views.py`
  - `backend/accounts/urls.py`
  - `backend/accounts/tests.py`
  - `backend/requirements.txt`
  - `frontend/index.html`
  - `frontend/src/components/auth/AuthModal.tsx`
  - `frontend/src/components/profile/ProfileModal.tsx`
  - `frontend/src/context/AuthContext.tsx`
  - `frontend/src/services/api.ts`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 13 · 11 de Noviembre de 2026 (20:50 - 20:56)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Vinculación oficial de Google Identity Services con el Client ID de producción obtenido de Google Cloud Console.

- **Para qué se usaron**:
  - Configuración del ID de Cliente oficial de Google Cloud (`1057441789427-vbbijigh0lbj5dju7curv2dk3dm3qjo3.apps.googleusercontent.com`) en [`AuthModal.tsx`](frontend/src/components/auth/AuthModal.tsx) y [`.env.example`](.env.example).
  - Inicialización automática de `window.google.accounts.id.initialize` y renderizado del botón nativo oficial de Google mediante `renderButton`.
  - Conexión del callback del JWT emitido por Google con el endpoint backend de autenticación en PostgreSQL.
  - Soporte de reintento One-Tap y botón rápido de prueba con cuentas institucionales de Veracruz.

- **Decisiones clave tomadas**:
  - El botón ahora abre la ventana emergente oficial y nativa de Google Cloud autorizada para los dominios `https://gojarol.tecnodesarrollo.site` y `http://localhost:5173`.

- **Archivos creados / modificados**:
  - `frontend/src/components/auth/AuthModal.tsx`
  - `.env.example`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 14 · 11 de Noviembre de 2026 (21:10 - 21:14)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Corrección de decodificación de credencial JWT de Google (padding base64 URL-safe) y paso explícito de perfil cliente-servidor.

- **Para qué se usaron**:
  - Corrección de la fórmula de padding base64 URL-safe en [`backend/accounts/views.py`](backend/accounts/views.py) (`(4 - len % 4) % 4`), evitando la excepción silenciosa `binascii.Error` cuando la longitud del token era múltiplo de 4.
  - Implementación de la función auxiliar `parseGoogleJwt` en el frontend ([`AuthModal.tsx`](frontend/src/components/auth/AuthModal.tsx)) para extraer de forma inmediata el `email`, `name` y `picture` del token firmado de Google y enviarlos de manera directa y robusta al endpoint `/api/v1/auth/google/`.
  - Aseguramiento de persistencia real en la tabla `accounts_user` de PostgreSQL.

- **Decisiones clave tomadas**:
  - Doble capa de decodificación (Frontend + Backend) para garantizar 100% de tolerancia a fallos en la extracción de credenciales de Google.

- **Archivos creados / modificados**:
  - `backend/accounts/views.py`
  - `frontend/src/components/auth/AuthModal.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 15 · 11 de Noviembre de 2026 (21:26 - 21:30)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Desbloqueo de `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y `CORS` para el dominio de producción `gojarol.tecnodesarrollo.site` en Django.

- **Para qué se usaron**:
  - Corrección de `ALLOWED_HOSTS` en [`backend/config/settings.py`](backend/config/settings.py) asegurando la inclusión de `gojarol.tecnodesarrollo.site` para evitar rechazos `400 Bad Request: Invalid HTTP_HOST header` durante llamadas del navegador a la API.
  - Habilitación de `CORS_ALLOW_ALL_ORIGINS = True` y registro explícito en `CSRF_TRUSTED_ORIGINS`.
  - Normalización de mapeo de rol (`docente`/`teacher` vs `estudiante`/`student`) en [`backend/accounts/views.py`](backend/accounts/views.py).
  - Trazabilidad y diagnósticos de red en [`frontend/src/services/api.ts`](frontend/src/services/api.ts).

- **Decisiones clave tomadas**:
  - Garantizar que las peticiones HTTPS que pasan por el proxy reverso del host hacia el contenedor backend sean aceptadas sin restricciones de cabecera de host.

- **Archivos creados / modificados**:
  - `backend/config/settings.py`
  - `backend/accounts/views.py`
  - `frontend/src/services/api.ts`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 16 · 11 de Noviembre de 2026 (21:40 - 21:46)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Fusión y sincronización integral de rama `origin/main` en `hugo-dev`, validación de compatibilidad con backend y compilación de frontend.

- **Para qué se usaron**:
  - Integración de los PRs #14, #15, #16, #17, #18, #19 y #20 procedentes de `main` desarrollados por el equipo backend/ML (Aldair e Iván).
  - Incorporación de módulos de Clases (`backend/classes/`) para creación y unión con código por parte de docentes y estudiantes.
  - Incorporación del catálogo curricular y fixture de asignaturas (`backend/curriculum/fixtures/catalogo.json`) con 9 materias oficiales y bancos de ejercicios de matemáticas y español (`content/exercises/`, `content/topics/`).
  - Integración de servicios de NLP (`ml/src/gojarol_ml/nlp/`) y tutor adaptativo con retroalimentación formativa veracruzana.
  - Verificación exitosa del build de producción de Vite + TypeScript (`npx pnpm run build`) sin advertencias ni roturas de tipos.

- **Decisiones clave tomadas**:
  - Consolidar todas las capacidades del equipo sobre la rama activa de despliegue `hugo-dev` para sincronizar la base de datos PostgreSQL y los contenedores Docker en el servidor VPS de producción.

- **Archivos creados / modificados**:
  - `docs/bitacora/hugo_frontend.md`
  - Integración de 173 archivos desde `main` (clases, currículum, fixtures, ejercicios, modelos).

### Entrada 17 · 11 de Noviembre de 2026 (21:51 - 21:55)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Interconexión frontend-backend de Clases y Asignaturas con tokens DRF y ajuste de permisos de catálogo.

- **Para qué se usaron**:
  - Configuración de permiso público `AllowAny` en [`backend/curriculum/views.py`](backend/curriculum/views.py) (`SubjectListView`) permitiendo que cualquier estudiante explore el catálogo curricular sin bloqueo previo de autenticación.
  - Actualización de [`frontend/src/services/api.ts`](frontend/src/services/api.ts) en los métodos `getSubjects()`, `getClasses()` y `joinClassWithCode()`, inyectando cabecera `Authorization: Token <token>` para usuarios autenticados y conectando con el endpoint real `POST /api/v1/classes/join/`.
  - Verificación del despliegue exitoso en el VPS Debian:
    - Aplicación de migración de base de datos: `Applying classes.0001_initial... OK`.
    - Carga de fixture curricular: `Installed 12 object(s) from 1 fixture(s)`.
    - Contenedores `gojarol_frontend`, `gojarol_backend` y `gojarol_db` operativos.

- **Decisiones clave tomadas**:
  - Catálogo de asignaturas accesible como recurso abierto, mientras que la unión e inscripción a clases requiere sesión activa de estudiante.

- **Archivos creados / modificados**:
  - `backend/curriculum/views.py`
  - `frontend/src/services/api.ts`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 18 · 11 de Noviembre de 2026 (21:54 - 21:58)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Verificación end-to-end de persistencia multiusuario en PostgreSQL y consulta de catálogo curricular en producción.

- **Para qué se usaron**:
  - Comprobación exitosa en el VPS de producción de la persistencia de usuarios autenticados mediante Google OAuth y demo institucional:
    - `id: 2 | huguito.goku16@gmail.com | Garcia Lara Hugo | estudiante`
    - `id: 3 | emiliano.valdes@estudiantes.sev.gob.mx | Emiliano Valdés | estudiante`
    - `id: 4 | ivanpazvalladares@gmail.com | Ivan Paz | estudiante`
  - Comprobación del endpoint público `GET /api/v1/subjects/` respondiendo JSON activo con las 9 materias oficiales y sus respectivos temas y estados de disponibilidad.
  - Consolidación del ecosistema completo: Frontend React 19 + Nginx SSL reverso + Django 6 DRF + PostgreSQL 15 + Google Identity Services.

- **Decisiones clave tomadas**:
  - Confirmar que el flujo de autenticación es 100% resiliente y que los datos de usuarios reales y fixtures pedagógicos se encuentran debidamente sincronizados en el servidor de evaluación.

- **Archivos creados / modificados**:
  - `docs/bitacora/hugo_frontend.md`

### Entrada 19 · 11 de Noviembre de 2026 (22:12 - 22:16)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Implementación de barrera de autenticación inicial reactiva, eliminación de usuarios estáticos por defecto y soporte de cierre de sesión (`logout`).

- **Para qué se usaron**:
  - Reemplazo de los usuarios mock precargados por un estado inicial no autenticado (`isAuthenticated = false`) y perfil de invitado neutral (`GUEST_USER`).
  - Activación automática del modal de inicio de sesión / registro (`AuthModal`) al entrar a la plataforma si no existe una sesión previa guardada en `localStorage`.
  - Integración del método `logout()` en [`AuthContext.tsx`](frontend/src/context/AuthContext.tsx) para limpiar credenciales y tokens almacenados, restableciendo el estado de invitado.
  - Actualización de [`DesktopSidebar.tsx`](frontend/src/components/layout/DesktopSidebar.tsx) y [`AppHeader.tsx`](frontend/src/components/layout/AppHeader.tsx) para ocultar nombres estáticos de usuarios ficticios y mostrar botones prominentes de "Iniciar Sesión / Registro" cuando el visitante no ha ingresado.
  - Adición de botón "Cerrar sesión" en [`ProfileModal.tsx`](frontend/src/components/profile/ProfileModal.tsx).
  - Verificación de compilación limpia con Vite y TypeScript sin errores.

- **Decisiones clave tomadas**:
  - Forzar que cada usuario interactúe con el flujo de login real (Google o cuenta institucional/formulario) para evitar que aparezcan datos de prueba impersonales al inicio.

- **Archivos creados / modificados**:
  - `frontend/src/context/AuthContext.tsx`
  - `frontend/src/App.tsx`
  - `frontend/src/components/auth/AuthModal.tsx`
  - `frontend/src/components/layout/DesktopSidebar.tsx`
  - `frontend/src/components/layout/AppHeader.tsx`
  - `frontend/src/components/profile/ProfileModal.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 20 · 11 de Noviembre de 2026 (22:18 - 22:21)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Fusión de PR #21 desde `origin/main` incorporando el modelo de IA clasificador de intenciones entrenado y validado (`intent_classifier.joblib`).

- **Para qué se usaron**:
  - Integración del artefacto entrenado de machine learning de Iván (`ml/artifacts/intent_classifier.joblib`, 765 KB) entrenado con 50,000 registros sintéticos.
  - Sincronización de metadatos de validación y métricas de desempeño (`ml/artifacts/intent_classifier_metadata.json` y `ml/artifacts/test_metrics.json`), alcanzando un **83.33% de exactitud (accuracy)** y **0.8358 de Macro F1** en pruebas realistas con 12 intenciones pedagógicas.
  - Actualización de reglas de `.gitignore` para permitir el rastreo del modelo compilado dentro del repositorio.
  - Verificación del árbol de trabajo sin conflictos y validación de compilación del frontend.

- **Decisiones clave tomadas**:
  - Incorporar el artefacto de NLP directamente en la rama activa `hugo-dev` para que el backend en producción pueda cargar el modelo serializado en el contenedor sin requerir fases de reentrenamiento en el servidor.

- **Archivos creados / modificados**:
  - `ml/artifacts/intent_classifier.joblib`
  - `ml/artifacts/intent_classifier_metadata.json`
  - `ml/artifacts/test_metrics.json`
  - `.gitignore`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 21 · 11 de Noviembre de 2026 (22:21 - 22:26)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Rediseño completo de arquitectura de autenticación separando de forma estricta los flujos de "Iniciar Sesión" y "Crear Cuenta (Registro)", con soporte de login por email/username y registro estructurado.

- **Para qué se usaron**:
  - Corrección de la experiencia de usuario en [`AuthModal.tsx`](frontend/src/components/auth/AuthModal.tsx):
    - **Pestaña Iniciar Sesión**: Formulario de credenciales directas (`usuario o correo` + `contraseña`), acceso nativo con Google Identity Services y selector de cuentas demo SEV.
    - **Pestaña Crear Cuenta (Registro)**: Formulario de alta para nuevos estudiantes/docentes con campos formales (`nombre completo`, `nombre de usuario`, `contraseña`, `correo`, selector de rol alumno/maestro, `nivel escolar`, `grado` y `escuela en Veracruz`), o registro rápido con Google OAuth.
  - Implementación de métodos `login()` y `register()` en [`apiService`](frontend/src/services/api.ts) conectando con los endpoints DRF `/api/v1/auth/login/` y `/api/v1/auth/register/`.
  - Actualización de [`backend/accounts/views.py`](backend/accounts/views.py) en `LoginView` para permitir autenticación indistinta mediante nombre de usuario o dirección de correo electrónico (`email__iexact`).
  - Validación de compilación de Vite y TypeScript sin advertencias.

- **Decisiones clave tomadas**:
  - Establecer una separación visual y funcional transparente entre el ingreso de usuarios existentes y la captura de datos pedagógicos de nuevos usuarios.

- **Archivos creados / modificados**:
  - `frontend/src/components/auth/AuthModal.tsx`
  - `frontend/src/services/api.ts`
  - `backend/accounts/views.py`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 22 · 11 de Noviembre de 2026 (22:28 - 22:32)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Ajustes de diseño y coherencia curricular en el flujo de autenticación (reubicación de Google OAuth abajo, normalización de etiqueta "Docente" y bifurcación dinámica de Secundaria a 3 años y Bachillerato a 6 semestres).

- **Para qué se usaron**:
  - Normalización de rol profesional en la interfaz: cambio de "Soy Maestro/Docente" a simplemente "Soy Docente".
  - Reubicación visual de los accesos de Google Identity Services debajo de los formularios principales tanto en Inicio de Sesión como en Registro, priorizando la entrada de credenciales.
  - Implementación de lógica curricular dinámica para estudiantes veracruzanos:
    - **Secundaria**: Selección de 1° a 3° año escolar.
    - **Bachillerato**: Selección de 1er a 6to semestre escolar.
    - Reajuste automático de grado al alternar entre niveles para prevenir inconsistencias de rango.
  - Verificación de compilación de frontend con TypeScript 7 y Vite 8 (599 ms).

- **Decisiones clave tomadas**:
  - Alinear la estructura de grados con el sistema educativo de Veracruz (secundaria técnica/general de 3 grados y bachillerato general/tecnológico de 6 semestres).

- **Archivos creados / modificados**:
  - `frontend/src/components/auth/AuthModal.tsx`
  - `docs/bitacora/hugo_frontend.md`

### Entrada 23 · 11 de Noviembre de 2026 (22:41 - 22:57)

- **Herramientas de IA utilizadas**:
  - **Antigravity AI (Gemini 3.8 Flash)**: Integración end-to-end del Frontend (React 19 + TypeScript) con el Backend (Django 5 + PostgreSQL) y el Motor de IA/Tutor Pedagógico (`intent_classifier.joblib` + SymPy + `TutorService`), eliminando datos estáticos de las vistas.

- **Para qué se usaron**:
  - Configuración de `docker-compose.yml` para montar en modo solo lectura `./ml:/ml:ro` y `./content:/content:ro` en el contenedor `backend` y exponer `PYTHONPATH: /app:/ml/src`, preservando el caché de dependencias en el VPS.
  - Creación del modelo `StudentProgress` y su migración `0001_initial.py` en `backend/progress/` para persistir en PostgreSQL los puntos de experiencia (`xp`), racha (`streak_days`) y el estado adaptativo del tutor (`tutor_state`) por cada usuario.
  - Creación de `backend/chat/services/runtime.py`, `backend/chat/views.py` (`POST /api/v1/chat/messages/`), `backend/exercises/views.py` (`POST /api/v1/exercises/<id>/answer/` y `POST /api/v1/exercises/<id>/hint/`) y `backend/progress/views.py` (`GET /api/v1/progress/me/` y `GET /api/v1/progress/leaderboard/`).
  - Actualización del catálogo curricular (`backend/curriculum/fixtures/catalogo.json` y `backend/curriculum/views.py`) con auto-sembrado de los 6 temas activos con IA (`mat_fracciones`, `mat_porcentajes`, `mat_ecuaciones`, `esp_comprension`, `esp_ortografia`, `esp_acentuacion`).
  - Conexión completa de `ExerciseCard.tsx` (soportando opción múltiple, lecturas de comprensión, respuestas abiertas evaluadas simbólicamente con SymPy y pistas graduales), `ChatView.tsx`, `ChallengesView.tsx`, `ProgressView.tsx`, `LeaguesView.tsx`, `ClassesView.tsx` y `TeacherDashboardView.tsx` a la base de datos real.

- **Decisiones clave tomadas**:
  - Garantizar que `expected_answer` jamás salga del servidor; las respuestas incorrectas activan pistas progresivas del `HintService` y las respuestas correctas otorgan XP persistido en PostgreSQL y desbloquean el siguiente ejercicio adaptativo.

- **Archivos creados / modificados**:
  - `docker-compose.yml`
  - `backend/config/urls.py`
  - `backend/accounts/serializers.py`
  - `backend/chat/services/runtime.py`
  - `backend/chat/views.py`
  - `backend/chat/urls.py`
  - `backend/exercises/views.py`
  - `backend/exercises/urls.py`
  - `backend/progress/models.py`
  - `backend/progress/migrations/0001_initial.py`
  - `backend/progress/views.py`
  - `backend/progress/urls.py`
  - `backend/classes/serializers.py`
  - `backend/classes/views.py`
  - `backend/curriculum/fixtures/catalogo.json`
  - `backend/curriculum/views.py`
  - `frontend/src/types/chat.ts`
  - `frontend/src/types/curriculum.ts`
  - `frontend/src/services/api.ts`
  - `frontend/src/components/exercise/ExerciseCard.tsx`
  - `frontend/src/components/chat/PromptSuggestions.tsx`
  - `frontend/src/App.tsx`
  - `frontend/src/views/student/ChatView.tsx`
  - `frontend/src/views/student/ChallengesView.tsx`
  - `frontend/src/views/student/ProgressView.tsx`
  - `frontend/src/views/student/LeaguesView.tsx`
  - `frontend/src/views/student/ClassesView.tsx`
  - `frontend/src/views/student/ClassDetailModal.tsx`
  - `frontend/src/views/teacher/TeacherDashboardView.tsx`
  - `docs/bitacora/hugo_frontend.md`
