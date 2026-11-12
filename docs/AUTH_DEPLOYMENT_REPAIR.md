# Reparación de contratos de autenticación, Google y SMTP

## Hallazgos y alcance de la comprobación

Rama local: `ivan-dev`, base `65388e2` (fase 2), inicialmente sin cambios locales.
Suite inicial: 388 aprobadas. No se cambió NLP, TutorService, ejercicios ni progreso.
No se crearon migraciones ni se modificaron 0002/0003.

Defectos reproducibles en código:

- GoogleSignInButton devolvía `null` sin VITE_GOOGLE_CLIENT_ID, ocultando toda la opción.
- authError concatenaba campos desconocidos del backend. Una respuesta antigua
  `{token: <token DRF>, user: ...}` terminaba imprimiendo el token como error.
- El registro podía enviar datos a un backend anterior que creaba una cuenta/sesión
  sin verificación, aunque el frontend rechazara después el resultado.
- Los fallos SMTP se rechazaban correctamente pero no tenían una clasificación
  operativa segura; un FRONTEND_URL de localhost podía generar enlaces inútiles
  fuera de desarrollo.

Consultas públicas de solo lectura a `https://gojarol.tecnodesarrollo.site`:

- `/api/v1/health/`: 200.
- `/api/v1/auth/verify-email/` y `/resend-verification/`: OPTIONS 404.
- `/api/v1/auth/me/`: OPTIONS 401, Allow GET/HEAD/OPTIONS, sin PATCH.
- `/api/v1/auth/register/`: OPTIONS 200, Allow POST/OPTIONS.
- `/api/v1/auth/config/`: GET 404 (el endpoint se incorpora en esta reparación).
- El primer bundle público consultado, index-C67TbKF7.js, no incluía las claves
  verification_required/email_sent/account_created. Una consulta posterior devolvió
  otro nombre de asset. No se identificó el commit o la imagen exacta mediante HTTP.

La interfaz/API publicadas en ese dominio no corresponden a la fase 2 local.
Una respuesta antigua con token es compatible con el incidente descrito y se
reprodujo en pruebas de regresión, pero no se envió un registro a producción para
obtener un token real. No se confirma aquí el token concreto expuesto ni se infieren
migraciones aplicadas a partir de una ruta HTTP. `jarol.tecnodesarrollo.site` no fue
accesible en la consulta. Si la aplicación afectada usa otro dominio, repetir estas
comprobaciones allí.

No se obtuvo acceso administrativo al servidor, al proveedor SMTP o a Google Cloud.
Localmente faltaban VITE_GOOGLE_CLIENT_ID, GOOGLE_CLIENT_ID, MAIL_HOST, MAIL_PORT,
MAIL_USERNAME, MAIL_PASSWORD, MAIL_USE_TLS, DEFAULT_FROM_EMAIL y FRONTEND_URL.
Esto describe el entorno local, no el contenido del .env del servidor. El daemon
Docker local no estaba disponible; no se validó una construcción de imagen Docker.

## Correcciones

`GET /api/v1/auth/config/` expone únicamente el contrato de autenticación v2, el modo
email_verification y el Client ID público de Google, sin credenciales SMTP. Usa
Cache-Control no-store. El cliente consulta ese contrato antes de registrar o iniciar
Google: ante 404, respuesta antigua o contrato incorrecto, no envía contraseñas ni
credenciales a esos endpoints. Nunca acepta un token como registro verificado.
Si el backend cambia entre la comprobación y el POST y devuelve token/user, también
rechaza la respuesta sin guardarla ni mostrarla.

Los mensajes de error proceden de textos controlados por el frontend, códigos
conocidos y etiquetas de campos permitidos. No se reflejan valores, claves desconocidas,
error.message, detail ni respuestas crudas. Esto cubre registro, login, Google,
verificación y errores del perfil.

Login/registro muestran siempre la sección «Continuar con Google». El botón real de
Google Identity Services se renderiza solo con configuración válida y SDK disponible;
de lo contrario se informa que Google no está disponible, sin botón simulado.
GOOGLE_CLIENT_ID del backend es obligatorio; su valor público puede cargarse durante
la ejecución mediante /auth/config/ si faltó VITE_GOOGLE_CLIENT_ID al compilar.
Si VITE_GOOGLE_CLIENT_ID está definido, debe coincidir; una discrepancia deshabilita
Google. No se utiliza un proveedor React adicional ni se hardcodean Client IDs.
La verificación por google-auth y el vínculo por sub permanecen intactos.

El HTML de entrada Nginx se revalida; los assets con hash conservan su caché larga.
No se cambió el diseño de los formularios.

SMTP mantiene MAILERS de Django 6.1, STARTTLS y el proveedor externo configurado.
Se registran solo códigos seguros como smtp_authentication_failed, smtp_sender_refused,
smtp_connection_failed o smtp_tls_failed; no el texto del proveedor, destinatarios,
credenciales ni enlaces. Fuera de DEBUG, FRONTEND_URL debe ser un origen HTTPS sin
rutas/query/fragmento y sin localhost/127.0.0.1/::1. Un envío fallido sigue dejando
la cuenta pendiente y permite reintentar con los límites existentes.

## Verificación administrativa sin revelar secretos

En el servidor, desde el directorio que contiene docker-compose.yml y el .env real:

```sh
docker compose images
docker compose ps
docker inspect --format '{{.Image}}' gojarol_backend
docker inspect --format '{{.Image}}' gojarol_frontend
docker compose exec -T backend python manage.py showmigrations accounts
docker compose exec -T backend python manage.py diagnose_auth
```

No publicar `docker inspect` completo, `docker compose config`, env, correos .eml
o logs sin revisar: pueden contener secretos. diagnose_auth imprime presencia de
configuración efectiva, estado de 0002/0003 y número de cuentas pendientes; no valores
secretos. Que MAIL_PORT aparezca presente no demuestra que se configuró explícitamente:
también puede proceder del valor por defecto.

El servicio backend recibe `.env` mediante env_file. El frontend no recibe esas
variables SMTP: VITE_GOOGLE_CLIENT_ID se interpola como build arg, no durante la
ejecución de Nginx. Cambiar solo el .env no actualiza contenedores existentes ni un
bundle ya compilado. En Compose, `command: gunicorn ...` sustituye el CMD del Dockerfile
y no aplica migraciones automáticamente.

Configurar fuera de Git, con los valores reales del proveedor existente:

```dotenv
MAIL_HOST=servidor_smtp_actual
MAIL_PORT=587
MAIL_USERNAME=usuario_smtp_actual
MAIL_PASSWORD=clave_smtp_actual
MAIL_USE_TLS=True
DEFAULT_FROM_EMAIL="Go Jarol <no.reply.trees.25@gmail.com>"
FRONTEND_URL=https://dominio-publico-real
GOOGLE_CLIENT_ID=cliente_web_real.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=cliente_web_real.apps.googleusercontent.com
```

No dejar MAIL_BACKEND de archivo/consola/locmem en producción. No usar puerto 465
con STARTTLS ni asumir Gmail SMTP. El proveedor debe autorizar expresamente el
remitente no.reply.trees.25@gmail.com; puede requerir validarlo en su panel.
En producción fijar DEBUG=False; el ejemplo del repositorio conserva DEBUG=True
exclusivamente como configuración de desarrollo.

## Prueba SMTP real, solicitada explícitamente por el responsable

```sh
# Conecta, negocia STARTTLS y autentica. NO envía mensajes.
docker compose exec -T backend python manage.py diagnose_auth --smtp-check

# Envía una prueba real, sin tokens, solo a una dirección bajo control del responsable.
docker compose exec -T backend python manage.py diagnose_auth --send-to correo_controlado@ejemplo.com
```

La conexión no comprueba permiso del remitente. SMTP_MESSAGE accepted significa
aceptación por el relay, no llegada a la bandeja: comprobar recepción/spam y los
registros del proveedor (rebotes, bloqueo de remitente o supresiones). No activar
debug SMTP ni copiar respuestas crudas en soporte. Después probar un registro nuevo,
confirmar que nace pending sin token y abrir su enlace; repetir reenvío tras 60 segundos.
Un backend antiguo no creaba la verificación, así que configurar SMTP por sí solo
no soluciona la incompatibilidad de versiones.

## Actualización coordinada (instrucciones; no ejecutadas)

Revisar código/configuración y respaldar la base. Una vez autorizada la actualización:

```sh
docker compose build --no-cache backend frontend
docker compose run --rm backend python manage.py migrate accounts --plan
# Solo tras revisar el plan aditivo:
docker compose run --rm backend python manage.py migrate accounts 0003_registration_verification --noinput
docker compose up -d --no-deps --force-recreate backend frontend
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py diagnose_auth
curl -fsS https://dominio-publico-real/api/v1/auth/config/
```

No se requieren migraciones nuevas en esta reparación; revisar 0002 y 0003 en el
servidor. El GET final debe informar auth_contract_version=2 y registration_mode=
email_verification. Revisar todos los upstreams/réplicas y purgar HTML antiguo en
CDN/proxy si existe; comprobar que /login referencia el asset reconstruido.
La actualización del código local no modifica el servidor.

En Google Cloud comprobar cliente de aplicación web, orígenes JavaScript autorizados
y disponibilidad del SDK GIS en el navegador. Probar una cuenta auténtica. Las pruebas
locales de google-auth con RSA/certificados controlados no validan Google real.

## Revocación de un token realmente expuesto

No se revocó ninguna sesión remota en esta ejecución. Si el equipo confirma que una
cadena mostrada era un token DRF vigente, debe revocar ese token y solicitar login
de nuevo; eliminarlo solo de la pantalla no lo invalida. No enviarlo por chat ni usarlo
como argumento de shell/historial. Desde una shell Django administrativa interactiva:

```python
from getpass import getpass
from rest_framework.authtoken.models import Token
key = getpass('Token expuesto (entrada oculta): ')
item = Token.objects.select_related('user').filter(key=key).first()
print(item.user.username if item else 'No existe un token vigente con ese valor')
# Confirmar la cuenta con el responsable antes de revocar:
if item and input('Escribe REVOCAR para invalidar esa sesión: ') == 'REVOCAR':
    item.delete()
del key, item
```

El token DRF se comparte por usuario; revocarlo afecta sus sesiones con ese token.
Revisar si se copió a capturas/logs y retirar esas copias. Auditar las cuentas creadas
durante el incidente: un registro antiguo pudo crearlas sin verificación. No marcar
todas las cuentas legacy como pending ni borrar usuarios: identificar las afectadas,
revisar duplicados y, con autorización, exigir verificación solo a esas cuentas y
revocar sus tokens. La migración 0003 conserva legacy para no bloquear usuarios previos.

## Pruebas reproducibles

Con el entorno Python del proyecto y PYTHONPATH=backend;ml/src:

```text
python -m pytest -q -p no:cacheprovider
```

Desde frontend:

```text
node --test tests/auth-api.test.mjs tests/auth-pages.test.mjs
node node_modules/typescript/bin/tsc -b
node node_modules/vite/bin/vite.js build
```

Las pruebas locales usan base y correo de pruebas, y transporte SMTP controlado.
No se enviaron correos reales ni se validó una cuenta auténtica de Google.

## Resultado final y archivos

- Suite completa: **400 aprobadas**, sin fallos (base inicial: 388).
- Frontend: **30 aprobadas**, TypeScript correcto y compilación Vite correcta.
- Django check sin problemas; makemigrations accounts --check --dry-run sin diferencias.
- Una ejecución de pruebas se bloqueó en reverse DNS al generar Message-ID y se
  interrumpió; otra ejecución auxiliar se interrumpió por lentitud. No se contabilizan
  como aprobadas. La fixture de correo ahora fija un hostname de pruebas. La base en
  memoria usa un hasher rápido únicamente para pruebas; un caso separado ejecuta
  registro, confirmación y login con PBKDF2. Los hashers de la aplicación no cambiaron.
- No se ejecutaron migraciones de la aplicación, commits, push ni despliegues.
  Los procesos de validación iniciados en esta revisión terminaron o se detuvieron.

Archivos modificados: frontend/src/services/api.ts,
frontend/src/components/auth/GoogleSignInButton.tsx, frontend/nginx.conf,
frontend/tests/auth-api.test.mjs, frontend/tests/auth-pages.test.mjs;
backend/accounts/views.py, urls.py, email_verification.py, test_registration.py,
test_profile_api.py; .env.example y docs/AUTH_PHASE2.md.

Archivos nuevos: backend/accounts/management/__init__.py,
backend/accounts/management/commands/__init__.py,
backend/accounts/management/commands/diagnose_auth.py y este documento.
