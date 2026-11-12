# Resolución del merge ivan-dev ← origin/main db5151d

Se continuó el merge existente: HEAD de ivan-dev 3426559, MERGE_HEAD db5151d.
No se inició otro merge, no se abortó, no se hizo reset, commit ni push.

## Ocho conflictos

| Archivo | Resolución |
| --- | --- |
| backend/accounts/urls.py | Se conservan config, registro, login, Google, verificación, reenvío, perfil y logout. Se mantienen demo/switch-role como rutas de compatibilidad que no emiten sesiones ni permiten cambiar roles. |
| backend/accounts/views.py | Se mantiene el flujo seguro de ivan-dev: SMTP, estado pendiente, google-auth/sub, colisiones y perfil. El demo público de main responde 410 y switch-role exige sesión y responde 403; no crean usuarios, tokens ni mutan roles. |
| backend/progress/views.py | Se conserva el diagnóstico enriquecido de main: ExerciseAttempt, historial, pistas, fechas, aciertos y estadísticas. resolve_user_for_request solo acepta request.user autenticado; resolve_progress_for_request reutiliza esa identidad, ignorando cabeceras/cuerpo manipulables. |
| frontend/nginx.conf | Se combina la ubicación exacta /index.html de main con las cabeceras no-cache/always y el fallback SPA; se conserva el proxy /api/ y la caché de assets con hash. |
| frontend/src/App.tsx | Se mantienen BrowserRouter, login/registro independientes, verificación, perfil y rutas privadas. Se añaden activeTab y onTabChange del nuevo TeacherDashboardView para panel/clases/alumnos, conservando el chat montado al abrir perfil. |
| frontend/src/components/auth/AuthModal.tsx | Se conserva la eliminación. Se inspeccionó la versión de main: sus campos pertinentes ya existen en las páginas nuevas; no se reintroducen parsing de JWT como prueba de identidad, demos públicos, contraseñas por defecto ni cambios arbitrarios de rol. |
| frontend/src/context/AuthContext.tsx | Se conserva el contexto seguro: bootstrap con /me/, tokens reales, carga, datos del backend y logout con revocación. No se reactiva la sesión desde un flag Google o un usuario cacheado ni se autentica por correo del cliente. El problema de usuario docente/legacy incompleto se evita recuperando un perfil real antes de montar las vistas privadas. |
| frontend/src/services/api.ts | Se combinan los nuevos tipos/mapeadores y métodos de clases, retos, avisos, alumnos y analítica de main con los contratos seguros de autenticación, /auth/config/, perfil y errores sin secretos. Se retiran los clientes demo/role-switch obsoletos; las vistas nuevas no los utilizan. |

## Funcionalidades de main conservadas

Administración de clases, códigos de ingreso (pausar/regenerar), matrícula idempotente,
baja de estudiantes, avisos, retos de grupo/personales, analítica docente, detalle
de alumnos, historial ExerciseAttempt, correct_attempts y recomendaciones. Se conservan
los componentes React y tipos nuevos, los cambios de conversación/ejercicios, la
agrupación del catálogo en Matemáticas/Español, el ejemplo actualizado de fracciones
y el módulo de rangos por XP (bronce/plata/oro/diamante).

Se conservan las migraciones de main classes/0002 y progress/0002 y las de ivan-dev
accounts/0002–0003; pertenecen a aplicaciones distintas y el grafo no tiene conflictos.
No se generaron migraciones adicionales.

Docker conserva los cinco intentos de migración y collectstatic de main, el argumento
Google de frontend y las variables del backend. Se corrige el guard de arranque:
si fallan los cinco intentos, no se ejecuta Gunicorn. No se ejecutó Docker ni se
aplicaron migraciones sobre la base de la aplicación en esta resolución.

## Pruebas e integración

Se adaptó el setup de las pruebas de clases al contrato real de registro → correo
en memoria → verificación → login, sin debilitar las aserciones de clases/analítica.
Las pruebas antiguas que exigían Google sin credencial firmada ahora comprueban el
rechazo sin crear cuentas/tokens. La suite criptográfica de ivan-dev sigue comprobando
Google válido, firmas falsas y expiración con claves/certificados controlados.

Se añadieron pruebas de rangos, de privacidad/persistencia del historial del chat y
de los mapeadores frontend de clases/analítica. Reenviar una respuesta al chat sin
ejercicio activo no vuelve a registrar el ejercicio completado ni suma XP.

Resultados:

- Pytest completo, incluidos los tests.py de Django: **415 aprobadas**.
- Runner de Django para las seis aplicaciones: **5 aprobadas** (subconjunto de las anteriores).
- Frontend: **32 aprobadas**.
- TypeScript y Vite: correctos.
- Django check con config.settings y base aislada: sin problemas.
- makemigrations --check --dry-run: sin cambios; MigrationLoader sin conflictos.
- No hay validación nueva de Google auténtico, SMTP externo, producción ni navegador.
  Los correos y las bases usados para validar son de pruebas.

Comandos reproducibles, con PYTHONPATH=backend;ml/src y el entorno del proyecto:

```text
python -m pytest -q -p no:cacheprovider -o "python_files=test_*.py *_test.py tests.py"
```

El runner de Django se ejecutó importando accounts.test_profile_api para configurar
SQLite en memoria y llamando a call_command('test', 'accounts', 'classes', 'chat',
'curriculum', 'exercises', 'progress'). No se usó la base definida en el .env real.

Desde frontend:

```text
node --test tests/auth-api.test.mjs tests/auth-pages.test.mjs
node node_modules/typescript/bin/tsc -b
node node_modules/vite/bin/vite.js build
```

El merge se deja preparado para el commit manual; MERGE_HEAD debe seguir presente.
