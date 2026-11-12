# Corrección de seguridad previa a la fase 2

## Identidad y sesiones

El navegador envía la credencial de Google Identity Services al endpoint existente
`POST /api/v1/auth/google/`. El backend utiliza `google.oauth2.id_token.verify_oauth2_token`
para verificar firma, audiencia, emisor y vigencia; también exige correo verificado,
un identificador `sub` válido y fechas de emisión/expiración válidas. Los errores de
verificación no crean usuarios, vínculos ni tokens. La caída del servicio de
verificación devuelve 503, sin recurrir a datos enviados por React.

`GoogleIdentity` conserva el identificador estable del proveedor, un usuario único
y el correo verificado al vincular. No se unen cuentas por coincidencia de correo.
Un correo ya existente o un cambio de correo de una identidad vinculada requiere
revisión y devuelve 409. Las cuentas antiguas creadas mediante el flujo inseguro no
se vinculan automáticamente: requieren su acceso original o un futuro procedimiento
de recuperación/vinculación que pruebe la titularidad. No hay tal procedimiento nuevo
en esta fase. El cliente no puede asignar rol administrador ni cambiar el rol existente.

React ya no decodifica el JWT para establecer identidad ni fabrica usuarios/tokens
de demostración. Login, registro y Google solo aceptan respuestas válidas del backend.
Al recargar, una sesión se muestra autenticada después de consultar `/auth/me/`.
La validación del formato de token en React es un control de contrato; la autorización
real sigue siendo la validación del token en Django. Se conserva el almacenamiento de
tokens existente, por lo que la protección frente a XSS sigue siendo relevante.

El cliente deja de enviar cabeceras de identidad no verificadas. El endpoint de
progreso solo identifica cuentas mediante `request.user`; un invitado conserva su
vista vacía y no puede consultar otro usuario mediante cabeceras o parámetros.

## Privacidad de pistas

El fallo anterior reutilizaba explicaciones con ejemplos resueltos cuando se agotaban
las pistas. HintService ahora ofrece estrategias conceptuales según el tipo de
ejercicio, conservando contadores y revisión. Las pistas específicas siguen asociadas
al ejercicio. No se modificaron el NLP, TutorService, evaluadores ni adaptación.

## Preparación del entorno (sin despliegue automático)

1. Instalar las dependencias ya declaradas en `backend/requirements.txt`, incluidas
   `google-auth` y `requests`.
2. Configurar `GOOGLE_CLIENT_ID` en Django y `VITE_GOOGLE_CLIENT_ID` antes de compilar
   React con el mismo identificador público de aplicación web. No son secretos.
   Si falta configuración, Google se rechaza y se conserva el acceso por contraseña.
3. Revisar y aplicar la migración aditiva `accounts/0002_googleidentity` antes de
   habilitar el endpoint actualizado. No modifica ni elimina usuarios existentes.
   En esta ejecución solo se aplicó sobre una base SQLite en memoria para pruebas;
   no se ejecutó sobre la base de la aplicación.
4. Actualizar backend y frontend juntos. Configurar los orígenes autorizados en Google
   para el dominio real y usar HTTPS. No se cambiaron credenciales ni permisos de Google.
5. Probar con una cuenta autorizada: alta nueva, segundo acceso al mismo usuario,
   logout, rechazo de colisión con correo existente y fallo HTTP sin sesión simulada.

## Pruebas reproducibles

Desde la raíz, con el entorno Python del proyecto y `PYTHONPATH=backend;ml/src`:

```text
python -m pytest -q -p no:cacheprovider
```

Desde `frontend/`:

```text
node --test tests/auth-api.test.mjs
node node_modules/typescript/bin/tsc -b
node node_modules/vite/bin/vite.js build
```

Las pruebas OAuth ejecutan la verificación criptográfica real de google-auth con
tokens RSA firmados localmente y certificados HTTP controlados. Incluyen firma falsa,
JWT malformado/sin firma, audiencia/emisor incorrectos, expiración, emisión futura,
correo no verificado, colisiones, roles, cuenta inactiva y caída de verificación.
No demuestran un login real con Google ni el popup en navegador. Esas comprobaciones
y la validación visual siguen pendientes.

Resultado de esta revisión: suite completa de pytest, **312 aprobadas**; subconjunto
de cuentas y pistas, **53 aprobadas**; pruebas de cliente, **12 aprobadas**.
TypeScript y Vite finalizaron correctamente. `makemigrations accounts --check --dry-run`
no detectó diferencias respecto de la migración escrita. No se hicieron commits,
push, despliegues ni migraciones sobre la base de la aplicación. Los cambios previos
de perfil y navegación permanecen en `ivan-dev`.

Fuentes oficiales consultadas:

- https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
- https://developers.google.com/identity/sign-in/web/backend-auth
