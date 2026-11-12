# Autenticación y verificación de correo — fase 2

## Flujo y compatibilidad

La SPA utiliza BrowserRouter, ya incluido en las dependencias. Las rutas públicas
son `/login`, `/registro`, `/verificacion-pendiente`, `/verificar-correo/:uid/:token`,
`/verificacion-exitosa`, `/verificacion-invalida` y `/recuperar-contrasena`.
La última solo informa de la fase 3, sin simular recuperación ni envío de correo.

`/` redirige a `/login` o `/chat` después de recuperar la sesión desde `/auth/me/`.
Un usuario autenticado no permanece en login/registro. Las rutas privadas son
`/chat`, `/perfil`, `/retos`, `/ligas`, `/clases`, `/progreso`, `/panel`, `/alumnos`;
se conservan las restricciones por rol. No se interpreta `next` ni ningún destino
externo. El chat se conserva montado al consultar el perfil. Nginx ya tiene
`try_files ... /index.html`, necesario para recargar rutas de BrowserRouter.

El endpoint `/api/v1/chat/messages/` también exige autenticación. El acceso invitado
de la fase anterior se retiró intencionalmente al convertir el chat en ruta privada.
Los usuarios pendientes son rechazados por la autenticación de tokens del backend.

Los antiguos modales de autenticación y perfil se retiraron, junto con el cambio
local de rol de demostración. AccountMenu y ProfileView se conservan. El perfil
consulta datos reales y permite editar residencia; correo, estado de verificación,
rol y permisos no son editables. El registro docente no otorga privilegios de
administrador ni cambia el filtrado existente de clases por docente propietario.

La migración aditiva `0003_registration_verification` depende de
`0002_googleidentity`. Añade residencia, estado/fecha de verificación y el registro
privado de tokens y límites. Las cuentas previas conservan `legacy`, su acceso,
contraseñas, roles y vínculos Google. `legacy` no significa correo verificado.
No se limpian ni fusionan duplicados anteriores. La unicidad case-insensitive se
aplica a correos de cuentas nuevas pendientes/verificadas mediante un índice
condicional; además se rechazan coincidencias con cuentas anteriores al registrar.
Se probó la migración 0002 → 0003 conservando usuarios y el `sub`, en SQLite en memoria.

Las cuentas por contraseña nacen `pending`. No reciben token al registrarse y no
pueden usar tokens API hasta verificar. Después quedan `verified`; deben iniciar
sesión normalmente. Google mantiene firma/audiencia/emisor/vigencia/correo verificado
mediante google-auth y la identidad estable `sub`, sin vinculación por correo.
Una cuenta nueva creada por Google queda verificada por los claims confiables.
No se validó con una cuenta Google real.

## Contratos HTTP

Todos los endpoints usan `/api/v1/auth/`:

| Endpoint | Contrato |
| --- | --- |
| POST `register/` | `full_name`, `email`, `username`, `rol` estudiante/docente, `nivel`, `grado`, `estado`, `password`, `password_confirm`. Estudiantes: secundaria años 1–3, bachillerato semestres 1–6. Docentes sin nivel/grado obligatorio. |
| POST `login/` | `username` (usuario o correo), `password`. Responde token/usuario; 403 si está pendiente. |
| POST `google/` | Credencial GIS verificada por backend, con rol inicial permitido. No cambió su contrato seguro. |
| POST `verify-email/` | `uid`, `token`. 200 confirma; 400 inválido, caducado o ya consumido. No entrega sesión. |
| POST `resend-verification/` | `email`. 202 genérico; 429 límite; 503 fallo real del envío. |
| GET/PATCH `me/` | Perfil propio; incluye `estado`, `email_status`. PATCH conserva lista explícita de campos editables. |
| POST `logout/` | Revoca el token existente; el sistema sigue usando un token DRF por cuenta. |

Estado usa códigos estables 01–32 y las 32 etiquetas solicitadas; no existe un campo
oculto obligatorio de escuela/municipio. La tabla de frontend coincide con
`accounts/regions.py` y se reutiliza en registro/perfil.

El registro responde 201 con `verification_required=true`, `email_sent=true`.
Si SMTP falla, conserva la cuenta pendiente y devuelve 503 con `account_created=true`
y `email_sent=false`; React permite solicitar el reenvío sin inventar una sesión.

Los tokens tienen 256 bits de entropía, caducan en 24 horas y solo se guardan como
SHA-256. La confirmación usa comparación constante y bloqueo transaccional del usuario.
Un reenvío correcto rota el token; uno fallido conserva el último token válido.
El enlace procede exclusivamente de `FRONTEND_URL`, nunca de Host ni del cliente.
La página requiere confirmar mediante POST para evitar consumir enlaces con escáneres
de correo. La política `no-referrer` evita enviar el enlace a recursos externos.

Límites persistentes por cuenta: 60 segundos entre intentos de envío, máximo 5/hora,
incluidos fallos SMTP. También hay límite DRF de 20 peticiones/hora por IP para
confirmación/reenvío. El contador por cuenta funciona entre workers y reinicios;
el límite IP usa la caché Django configurada (actualmente local por proceso).
El registro añade un límite de 10 solicitudes/hora por IP en esa misma caché.
Para un límite IP global se necesita una caché compartida y límites del proxy.

## Configuración SMTP

Django instalado: **6.1.3**. Se usa `MAILERS['default']`, conforme a la
[documentación oficial](https://docs.djangoproject.com/en/6.1/topics/email/), con el
backend SMTP de Django y opciones explícitas. Las variables son:

```dotenv
MAIL_HOST=servidor_smtp_actual
MAIL_PORT=587
MAIL_USERNAME=usuario_smtp_actual
MAIL_PASSWORD=clave_smtp_actual
MAIL_USE_TLS=True
DEFAULT_FROM_EMAIL="Go Jarol <no.reply.trees.25@gmail.com>"
FRONTEND_URL=https://dominio-real-de-go-jarol
```

Se usa STARTTLS y `use_ssl=False`, con timeout de 10 segundos. No se configura
Gmail como servidor ni un proveedor nuevo. El equipo debe introducir host y
credenciales reales fuera de Git y confirmar en el proveedor existente que
`no.reply.trees.25@gmail.com` está autorizado como remitente. Puede requerir verificar
esa dirección en su panel; cambiar DEFAULT_FROM_EMAIL no concede esa autorización.
No había ninguna de las seis variables MAIL/DEFAULT_FROM_EMAIL en el entorno revisado,
por lo que no se pudo comprobar la autorización ni enviar un correo externo.

Para desarrollo sin SMTP, usar `DEBUG=True` y:

```dotenv
MAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
FRONTEND_URL=http://localhost:5173
```

Esto escribe correos de prueba en `backend/dev-emails/` (ignorado por Git).
Contienen enlaces privados: no servir ese directorio públicamente ni compartirlo.
Las pruebas automatizadas usan locmem. Un backend distinto de SMTP se rechaza con
DEBUG=False. En modo SMTP no se sustituye un fallo por consola, archivo ni éxito falso.
La aceptación por el relay no garantiza la llegada a bandeja de entrada.

Google requiere `GOOGLE_CLIENT_ID` en Django y `VITE_GOOGLE_CLIENT_ID` al compilar
React, con el mismo cliente web público. Dockerfile/Compose ahora pasan este último
como argumento de compilación; las credenciales SMTP nunca se pasan al frontend.

## Puesta en marcha por el equipo

1. Revisar los cambios y la configuración, conservar copia de la base y aplicar
   0002 y 0003 en el entorno autorizado antes de ejecutar el backend actualizado.
   Esta ejecución no migró la base de la aplicación ni producción.
2. Preparar SMTP y la dirección de remitente autorizada; fijar FRONTEND_URL al origen
   HTTPS real, sin ruta, query ni fragmento.
3. Actualizar backend y reconstruir frontend juntos. Mantener el fallback SPA de Nginx.
4. Probar registro de estudiante/docente con correos reales, entrega y spam, enlace
   válido/caducado, reenvío, fallo SMTP, login, perfil, chat y logout. Comprobar Google
   con una cuenta auténtica y sus orígenes autorizados antes de darlo por validado.

## Validación y límites

Base inicial: 312 pruebas aprobadas. Se prueban los contratos mediante APIClient,
registro/verificación/login/perfil/chat/logout, 32 entidades, validación de campos,
tokens inválidos/caducados/reutilizados, límites, duplicados, fallos SMTP y compatibilidad
de migraciones. El transporte SMTP de Django también se prueba con conexión simulada
para comprobar STARTTLS, autenticación y remitente; no es un envío externo.

Se comprobó HTTP local usando Vite con su proxy real a Django y una base SQLite
temporal aislada: registro 201 sin token, login pendiente 403, confirmación 200,
reutilización 400, login/perfil/PATCH 200, tres mensajes con NLP real y logout 204;
el token revocado devolvió 401. El correo se capturó en archivo local de pruebas.
No fue una prueba visual ni una entrega SMTP real.

Las pruebas frontend ejecutan el cliente API, las reglas reales de rutas y renderizan
las páginas React para revisar formularios, orden, enlaces, etiquetas y opciones.
El navegador no pudo inicializarse (`failed to write kernel assets`). No se comprobaron
visualmente tamaños 320/390/768/1024/1440, teclado real, lector de pantalla, popup Google,
contraste renderizado, consola ni desbordamientos. Hacer esas comprobaciones antes
de dar por terminada la revisión visual.

La fase 3 debe implementar recuperación/cambio de contraseña y sustituir la página
informativa actual de `/recuperar-contrasena`. No se añadieron simulaciones de ese flujo.

Resultado final: **388 pruebas de backend aprobadas**, **22 pruebas frontend aprobadas**,
TypeScript sin errores y Vite compilado. Los checks de Django no detectaron problemas,
y `makemigrations accounts --check --dry-run` no detectó diferencias. `git diff --check`
pasó. Los dos servidores temporales de la prueba HTTP se detuvieron y se comprobó que
8000/5173 dejaron de responder. No se hicieron commits, push, despliegues ni migraciones
sobre la base de la aplicación. Continúa la rama `ivan-dev` con los cambios locales anteriores.

## Archivos de esta fase

- Backend: accounts/models.py, serializers.py, views.py, urls.py, authentication.py,
  email_verification.py, regions.py, migrations/0003_registration_verification.py,
  test_registration.py, test_profile_api.py; config/settings.py; chat/views.py
  (solo el permiso de autenticación del endpoint, sin cambiar el motor educativo).
- Frontend: App.tsx, routing.ts, context/AuthContext.tsx, services/api.ts,
  types/auth.ts, data/states.ts, views/ProfileView.tsx, views/auth/LoginPage.tsx,
  RegisterPage.tsx, VerificationPages.tsx; components/auth/AuthLayout.tsx,
  PasswordField.tsx, GoogleSignInButton.tsx; layout/AppHeader.tsx y DesktopSidebar.tsx.
- Retirados: components/auth/AuthModal.tsx y components/profile/ProfileModal.tsx.
- Pruebas frontend: tests/auth-api.test.mjs, auth-pages.test.mjs, auth-pages-entry.ts.
- Configuración/documentación: .env.example, .gitignore, docker-compose.yml,
  frontend/Dockerfile, frontend/index.html y este documento. La migración 0002 y
  las correcciones anteriores de OAuth, cabeceras y pistas se conservaron.
