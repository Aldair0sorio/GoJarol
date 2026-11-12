# Conectividad en Go Jarol

Requisito del reto: *"funcione bien en celular y con poca conexión"*.

Cada cifra de este documento está rotulada:
- **[medido]**: se midió, y se indica cómo.
- **[estimado]**: estimado sumando el peso de los archivos; no es una medición de red.
- **[sin medir]**: no tenemos el dato.

## 1. Cómo atendemos la poca conexión

> Go Jarol está pensado para celulares con poca señal. Redujimos lo que se descarga: las imágenes pasaron de 4.5 MB a 69 kB (WebP al tamaño en que se muestran), las fuentes se sirven desde nuestro servidor y nginx comprime HTML, JS y CSS con gzip. Cada respuesta del chat pesa en promedio 444 bytes. Si la conexión falla, Jarol no inventa respuestas: avisa «Sin conexión», conserva lo que escribió el alumno y ofrece reintentar; si la red está lenta, deja de esperar a los 30 segundos y lo dice. No es una app offline: la primera carga necesita internet.

## 2. Mediciones antes y después

**Cómo se midió:**
- **Peso de archivos:** `os.stat` sobre `frontend/public` y `frontend/dist` tras `pnpm build`.
- **gzip:** compresión con `gzip.compress(nivel 6)` en Python, para estimar qué transfiere nginx.
- **Píxeles:** leídos de la cabecera de cada imagen.
- **Chat:** cuerpo JSON de `POST /api/v1/chat/messages/` en una conversación real de 9 mensajes, con el cliente de pruebas de Django sobre el código actual y una base SQLite en memoria; no pasó por nginx.

| Medición | Antes | Después | Tipo |
|---|---:|---:|---|
| `frontend/public` total | 4,523,115 B | 189,332 B | [medido] |
| `mascot/jarol-crab` | 1,647,908 B · PNG 1254×1254 | 20,946 B · WebP 320×320 | [medido] |
| `leagues/bronce` | 708,350 B · PNG 575×575 | 9,536 B · WebP 144×144 | [medido] |
| `leagues/plata` | 599,986 B · PNG 575×575 | 8,834 B · WebP 144×144 | [medido] |
| `leagues/oro` | 752,076 B · PNG 616×616 | 9,590 B · WebP 144×144 | [medido] |
| `leagues/diamante` | 800,242 B · PNG 620×620 | 10,626 B · WebP 144×144 | [medido] |
| Favicon | el mismo PNG de 1,647,908 B | `jarol-crab-64.png` 9,507 B · 64×64 | [medido] |
| Fuentes (antes desde Google Fonts) | [sin medir] | 3 woff2: 96,924 B (Atkinson normal 33,996 · itálica 37,644 · Sora 25,284) | [medido] |
| `dist/` total sin comprimir | 5,022,575 B | 690,679 B | [medido] |
| `dist/` total con gzip | 4,530,584 B | 313,576 B | [medido] |
| JS principal sin comprimir / gzip | 443,922 / 128,944 B | 444,717 / 128,959 B | [medido] |
| CSS sin comprimir / gzip | 54,052 / 9,797 B | 55,130 / 10,048 B | [medido] |
| Respuesta del chat, promedio de 9 mensajes | 444 B (gzip 295 B) | 444 B (gzip 295 B) | [medido] |

- Las respuestas del chat pesan menos de 1,024 B, así que nginx no las comprime (`gzip_min_length 1024`). Comprimirlas ahorraría muy poco.
- **gzip en nginx:** se comprobó con `curl -D - -H "Accept-Encoding: gzip"` en un contenedor `nginx:alpine` local que servía `dist/` con este `nginx.conf`. [medido: presencia de `Content-Encoding: gzip` en HTML, JS, CSS y SVG]
  - `index.html` y las rutas de la app conservan `Cache-Control: no-cache, no-store, must-revalidate`.
  - Los archivos con hash, las imágenes y las fuentes conservan la caché de 30 días.

### Presupuesto de la pantalla de login (meta: menos de 500 kB sin caché)

| Recurso | Bytes | Tipo |
|---|---:|---|
| JS principal (gzip) | 128,959 | [estimado] |
| Fuente Atkinson Hyperlegible Next normal | 33,996 | [estimado] |
| Fuente Sora | 25,284 | [estimado] |
| Mascota WebP del encabezado | 20,946 | [estimado] |
| CSS (gzip) | 10,048 | [estimado] |
| Favicon PNG 64 px | 9,507 | [estimado] |
| `index.html` (gzip) | 792 | [estimado] |
| **Total del sitio propio** | **≈ 229,532** | **[estimado por suma de archivos]**, sin encabezados HTTP ni la respuesta de `/auth/config/` |
| Google Sign-In (documento del botón y su script) | — | **[sin medir]** |

El margen para el botón de Google y los encabezados es de unos 270 kB. Solo una medición en DevTools después del despliegue confirma si se cumple la meta.

### Medición en DevTools (3G, caché desactivada)

Se mide con **el mismo navegador, el mismo perfil de red y la misma pantalla (login)** en ambas columnas: Chrome, preset 3G, "Disable cache" activado, ventana de incógnito.

| Métrica | Antes (producción, medido por el equipo) | Después (tras el despliegue) |
|---|---|---|
| Peticiones | 15 | |
| Transferido | 2.3 MB | |
| Tiempo hasta "Finish" | 51 s | |
| `jarol-crab` (transferido · tiempo) | 745 kB · 34 s (`jarol-crab.png`) | |
| Peticiones a terceros | Google Fonts (CSS + 2 fuentes, ~80 kB) y Google Sign-In (~57 kB de documento + script) | |

El archivo `jarol-crab.png` del repositorio pesaba 1,647,908 B. La cifra de 745 kB se deja tal como la registró el equipo en DevTools.

**Verificación de gzip tras el despliegue:**
```
curl -I -H "Accept-Encoding: gzip" https://<dominio>/assets/<archivo-con-hash>.js   # debe incluir Content-Encoding: gzip
curl -I https://<dominio>/                                                         # debe incluir Cache-Control: no-cache, no-store, must-revalidate
```

## 3. Comportamiento sin conexión

| Situación | Qué ve el alumno | ¿Se puede reintentar? |
|---|---|---|
| El chat no puede enviar (falla de red) | «Sin conexión: tu mensaje no se envió. Toca para reintentar.» | Sí: se reenvía el mismo texto, sin repetir la burbuja |
| El servidor responde con error (5xx, 429…) | «El servidor no respondió: tu mensaje no se envió. Toca para reintentar.» | Sí |
| Sin respuesta en 30 s | «La conexión está lenta, reintenta. Tu mensaje pudo haber llegado aunque no veas la respuesta.» | Sí (ver límites) |
| Sesión vencida (401/403) | «Tu sesión ya no es válida: tu mensaje no se envió. Vuelve a iniciar sesión.» | No |
| Falla al enviar la respuesta de un ejercicio | Los mismos mensajes, con «tu respuesta». **No se muestra correcto ni incorrecto, ni se suma XP**, y lo escrito se conserva | Sí, salvo 401/403 |
| Falla al pedir una pista | Los mismos mensajes, con «no pudimos pedir la pista». **No se inventa una pista** | Sí, salvo 401/403 |
| El navegador reporta que no hay red (`navigator.onLine`) | Etiqueta discreta «Sin conexión» arriba del chat | — |
| No cargan el progreso, la liga o las clases | «No pudimos cargar … Revisa tu conexión y toca para reintentar.» En lugar de mostrar 0 XP o "no tienes clases" | Sí |

Antes, si el servidor fallaba, el chat y la tarjeta de ejercicio mostraban **contenido de ejemplo como si fuera real**: un ejercicio falso, la evaluación "incorrecta" de una respuesta que nunca se evaluó, XP local y textos que revelaban resultados. Eso se quitó. `mockData.ts` se conserva, pero ya no se importa.

## 4. Límites honestos

- **No hay modo offline ni PWA.** Sin service worker, la primera carga y cada mensaje necesitan red.
- **Los mensajes no se encolan.** Si no hay red, el alumno tiene que tocar «reintentar» cuando vuelva.
- **El botón de Google Sign-In sigue cargándose en el login.** No se difirió porque cambiarlo toca el flujo de autenticación: hoy el componente espera el script a lo sumo 5 s. Su script es `async defer` y no bloquea el formulario de usuario y contraseña, pero compite por el ancho de banda.
- **Reintentar después de un timeout puede duplicar el procesamiento.** El servidor pudo haber recibido el primer envío, y con el reintento se registran dos veces el intento, el XP o el evento `TutorEvent`. No hay deduplicación; por eso el mensaje avisa que el envío «pudo haber llegado».
- **El panel docente conserva las clases anteriores sin avisar** si una recarga falla después de haberlas cargado. El aviso de error solo aparece cuando no se cargó ninguna clase.
- **`getSubjects` y `getLeaderboard` devuelven una lista vacía sin avisar** cuando fallan.
- **Los mensajes de timeout y de error no se probaron en un navegador.** Se verificó que el proyecto compila (`pnpm build`) y pasa el linter, pero no se ejecutaron en Chrome. Ver PA-10 y PA-11.
- **Las fuentes y las imágenes de `public/` no llevan hash en el nombre.** Si se reemplazan con el mismo nombre, un navegador puede seguir usando la versión anterior hasta 30 días.
- **El JS principal es un solo archivo de 129 kB con gzip** que incluye todas las vistas; no está dividido por pantalla.

## 5. Mejoras futuras

- **Service worker o PWA:** guardar en caché el "cascarón" de la app (HTML, JS, CSS, fuentes e imágenes) para que las visitas siguientes abran sin red.
- **Caché de lecciones:** guardar las explicaciones de los temas ya vistos para consultarlas sin conexión. La evaluación seguiría necesitando al servidor, para no exponer respuestas.
- **Prefetch:** pedir por adelantado el siguiente ejercicio o las vistas probables mientras hay buena señal.
- **Cola de mensajes con identificador único,** para reenviar sin duplicar cuando vuelve la red.
- **Diferir Google Sign-In:** cargar su script desde el componente con un `onload` y un tiempo límite mayor que los 5 s actuales. Lo debe revisar quien mantiene la autenticación.
- **Dividir el JS por pantalla** (`React.lazy`) para que el login descargue menos.

## 6. Pruebas de aceptación

| ID | Prueba | Cómo ejecutar la prueba | Criterio de aceptación | Resultado observado |
|---|---|---|---|---|
| PA-10 | Primera carga en conexión lenta | Chrome en incógnito → DevTools → Network: "Disable cache" + perfil 3G (el mismo de la columna "Antes"). Abrir `/login` y esperar a "Finish". Anotar peticiones, transferido, tiempo y la fila de `jarol-crab`. | Menos de 500 kB transferidos. Ninguna petición a `fonts.googleapis.com` ni a `fonts.gstatic.com`. Las imágenes son `.webp` (el favicon es un PNG de 64 px). El formulario de usuario y contraseña se puede usar sin esperar al botón de Google. | |
| PA-11 | Corte de conexión en pleno ejercicio | Iniciar sesión como alumno → «Ponme un ejercicio de fracciones» → escribir una respuesta. En DevTools poner **Offline** y tocar «Comprobar». Luego enviar un mensaje en el chat. Volver a **Online** y tocar el aviso para reintentar. Para el timeout, repetir con un perfil de red con más de 30 s de latencia. | Offline: aparece «Sin conexión: tu respuesta no se envió…», la respuesta escrita sigue en el campo, **no** se marca correcta ni incorrecta y **no** cambia el XP. Aparece la etiqueta «Sin conexión». En el chat sale el aviso con reintento y no una respuesta inventada. Al volver a Online, el reintento obtiene la respuesta real de Jarol. Con latencia mayor a 30 s aparece «La conexión está lenta, reintenta…». | |
