# Perfil y navegación — fase 1

> Actualización posterior: la corrección de OAuth, sesiones simuladas y privacidad
> de pistas se documenta en [AUTH_SECURITY_FIX.md](AUTH_SECURITY_FIX.md). Sus requisitos
> de configuración y migración aditiva sustituyen las observaciones históricas de
> seguridad pendientes y la indicación de que no hacen falta migraciones de este cierre.

Rama ivan-dev. Se conserva autenticación por token, login/registro en modal para invitados y flujo Google existente. No hay migraciones ni campos nuevos en User.

## Contrato

- GET /api/v1/auth/me/: incluye first_name y last_name además de los campos anteriores.
- PATCH /api/v1/auth/me/: permite first_name, last_name y alias. Los estudiantes pueden editar nivel/grado: secundaria 1–3 y bachillerato 1–6. Datos de rol/permisos/otras cuentas, usuario, correo y contraseña se rechazan. Docentes y administradores solo editan datos personales.
- POST /api/v1/auth/logout/: revoca el token presentado y cierra la sesión Django. El sistema existente comparte un token por usuario; revocarlo puede cerrar otras sesiones que usen el mismo token.

## Interfaz

Mi perfil se abre en #/perfil. El menú de cuenta se reutiliza en la cabecera móvil y sidebar; incluye iniciales o fotografía disponible, nombre, perfil y logout. Se retiraron de la navegación los controles que cambiaban el rol para demostraciones y el enlace de registro para autenticados. Los roles proceden del backend al recuperar /me/. El perfil no contiene un selector de rol.

Las rutas internas previas siguen funcionando. Abrir perfil no desmonta el chat; cambiar de cuenta sí limpia su instancia para no mostrar mensajes de otro usuario. La paleta, tipografía y mascota existentes se conservan. El formulario tiene etiquetas, selección de año/semestre dependiente del nivel, mensajes de carga/error/guardado, foco en el encabezado al navegar y controles de al menos 44 px. La estructura usa una columna en móvil y dos desde sm. El menú cierra con Escape o al tocar fuera.

Usuario y correo son de solo lectura hasta contar con los flujos correspondientes. El modelo no tiene residencia; se indica que no está registrada. Seguridad contiene información sobre la próxima fase sin botón inerte. No se implementaron cambio de contraseña ni verificación de correo.

## Validación

Base inicial: 265 pruebas aprobadas y un fallo existente en test_answer_not_exposed. Las explicaciones de fracciones incorporadas previamente contienen 3/4 y se reutilizan al agotar pistas, lo que provoca ese fallo. No se alteró la prueba para ocultarlo ni se cambió contenido educativo en esta fase.

Se añadieron 15 pruebas de API: login por token, GET/PATCH propio, validación académica, campos protegidos, roles docente/administrador, bloqueo de invitados y revocación de token. Suite tras los cambios: 280 aprobadas y el mismo fallo previo. TypeScript y Vite compilaron. La herramienta de navegador falló con failed to write kernel assets; no hay validación visual ni de Google OAuth real en esta ejecución.

## Revisión manual pendiente

Con Django y su base preparados, abrir React en invitado, cerrar o usar el modal y comprobar el acceso al chat. Iniciar sesión con una cuenta de prueba existente. No deben aparecer controles de login/registro ni cambio de rol. Abrir Mi perfil, comprobar los datos contra /auth/me/, editar nombre y guardar; recargar y verificar persistencia. Probar bachillerato semestre 6 y secundaria año 3; confirmar rechazo de grado fuera de rango por API. Repetir con docente y administrador. Cerrar sesión y comprobar que /auth/me/ rechaza el token anterior.

Comprobar 320, 390, 768, 1024 y 1440 px, tabulación, Escape, menús y ausencia de desbordamiento horizontal. Abrir y cerrar perfil durante una conversación: deben conservarse mensajes. Cambiar de cuenta: no deben mostrarse mensajes de la anterior. Verificar login Google con la configuración autorizada existente antes de desplegar.

El equipo debe actualizar backend y frontend juntos para habilitar PATCH y logout; no se requieren migraciones. No considerar resuelto el fallo previo de pistas por estas modificaciones.

## Revisión de cierre

Se reprodujo el fallo de pistas cargando en memoria el HintService y mat_fracciones.json de HEAD, anteriores a los cambios de fase 1: los índices 4 y 7 ya incluían 3/4. No es una regresión del perfil. El diff de backend/chat, backend/exercises, backend/progress, ml y content está vacío.

Se cerraron los dos servidores de validación que permanecían abiertos: Vite (PID 15024, puerto 5173) y el servidor Python HTTP de pruebas (PID 30908, puerto 8765). Ambos terminaron con ReturnValue=0 y no quedaron listeners en esos puertos. Las tareas de pytest anteriores ya habían finalizado.

Las pruebas de cuentas se ampliaron a 17, incluyendo login por correo, solicitud real al chatbot con NLP, acceso de invitado al chat y relectura del perfil tras guardar. Se instaló en el entorno local sympy==1.14.0, ya declarado en requirements.txt, para cargar el endpoint real. No se cambiaron dependencias del repositorio. La revisión detectó un método antiguo apiService.getProfile que devolvía MOCK_STUDENT ante errores y trataba administradores como estudiantes: ahora delega al mismo cliente y mapeador real de perfil que usan ProfileView y AuthContext.

Google OAuth no se validó con una identidad real. La revisión estática encontró dos defectos previos: GoogleLoginView acepta correo del cliente sin verificar la firma del ID token; apiService.loginWithGoogle puede fabricar jarol_gtoken tras un error de backend. Estos problemas requieren una corrección de seguridad antes de aprobar el flujo Google. No se reescribió OAuth ni se presentó como validado.

El navegador continúa sin iniciar (failed to write kernel assets). Se revisaron etiquetas, mensajes ARIA, foco, Escape, estructura responsive y restricciones leyendo código; no se probaron visualmente tamaños de pantalla, tabulación real, lector de pantalla, contraste renderizado, desbordamientos, consola ni el popup Google. Esas verificaciones siguen pendientes.

Resultados de cierre: pruebas afectadas, 23 aprobadas y el fallo previo de pistas; suite completa, 282 aprobadas y el mismo fallo. Las 17 pruebas de perfil/login/chat pasan. Se eliminó el import MOCK_STUDENT ya sin uso al retirar el fallback. No se modificaron los servicios educativos. La fase queda lista para revisión de código, pero no se aprueba un cierre integral mientras sigan pendientes privacidad de pistas, seguridad OAuth y comprobaciones visuales.
