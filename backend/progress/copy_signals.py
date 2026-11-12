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


def copy_signal(requests, own_successes):
    """Devuelve ("ok" | "revisar", motivo en texto)."""
    if requests >= MIN_REQUESTS_WITHOUT_SUCCESS and own_successes == 0:
        return "revisar", f"{requests} pedidos de respuesta directa y ningún acierto propio en {WINDOW_DAYS} días."
    if requests >= MIN_REQUESTS_WITH_RATIO and requests >= RATIO * own_successes:
        return "revisar", (f"{requests} pedidos de respuesta directa y solo {own_successes} "
                           f"acierto{'s' if own_successes != 1 else ''} propio{'s' if own_successes != 1 else ''} "
                           f"en {WINDOW_DAYS} días.")
    return "ok", ""
