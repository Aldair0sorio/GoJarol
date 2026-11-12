"""Regla simple y documentada de "señales de copia" para el panel del docente.

Pedidos = answer_request + bypass_attempt. Aciertos propios = step_solved (pasos de un
problema guiado y ejercicios resueltos por el propio alumno, en el chat o en la tarjeta).
Ventana: últimos 7 días. Es un indicio para conversar, no una prueba.
"""

WINDOW_DAYS = 7
MIN_REQUESTS_WITHOUT_SUCCESS = 3
MIN_REQUESTS_WITH_RATIO = 5
RATIO = 2

RULE_TEXT = (
    "«Revisar» si en los últimos 7 días el alumno: (a) pidió la respuesta directa o intentó saltarse "
    "las reglas 3 o más veces y no tiene aciertos propios, o (b) lo hizo 5 o más veces y esos pedidos "
    "son al menos el doble de sus aciertos propios. En cualquier otro caso, «ok». Aciertos propios = "
    "pasos de problemas guiados y ejercicios que el alumno resolvió por su cuenta."
)

RECOMMENDATIONS = [
    "Una señal «revisar» es un indicio, no una prueba: puede reflejar frustración o que el tema aún no se entiende.",
    "Habla en privado con quien aparece en «revisar»: pregúntale qué paso se le complica, sin acusarlo de copiar.",
    "Asigna un reto corto del tema y pide que explique en voz alta su procedimiento, no solo el resultado.",
    "Recuerda al grupo que Jarol no da resultados: guía paso a paso y tú ves cuántas veces se pide la respuesta directa.",
]


def _requests_text(answer_requests, bypass_attempts):
    """Desglosa los pedidos tal como los muestra la tarjeta del docente."""
    bypass = f"{bypass_attempts} intento{'s' if bypass_attempts != 1 else ''} de saltarse las reglas"
    if bypass_attempts == 0:
        return f"{answer_requests} pedido{'s' if answer_requests != 1 else ''} de respuesta directa"
    if answer_requests == 0:
        return bypass
    total = answer_requests + bypass_attempts
    return f"{total} pedidos ({answer_requests} de respuesta directa y {bypass})"


def copy_signal(answer_requests, bypass_attempts, own_successes):
    """Devuelve ("ok" | "revisar", motivo en texto). Pedidos = respuesta directa + saltarse las reglas."""
    requests = answer_requests + bypass_attempts
    detail = _requests_text(answer_requests, bypass_attempts)
    if requests >= MIN_REQUESTS_WITHOUT_SUCCESS and own_successes == 0:
        return "revisar", f"{detail} y ningún acierto propio en {WINDOW_DAYS} días."
    if requests >= MIN_REQUESTS_WITH_RATIO and requests >= RATIO * own_successes:
        successes = f"{own_successes} acierto{'s' if own_successes != 1 else ''} propio{'s' if own_successes != 1 else ''}"
        return "revisar", f"{detail} y solo {successes} en {WINDOW_DAYS} días."
    return "ok", ""
