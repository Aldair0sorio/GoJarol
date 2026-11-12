"""Anticopia: detecta pedidos explícitos de la respuesta e intentos de saltarse las reglas.

Jarol responde con un rechazo amable y la siguiente ayuda; nunca con el resultado.
Solo cuentan los pedidos EXPLÍCITOS de la respuesta o el resultado: "no sé",
"dame una pista" o "¿está bien mi respuesta?" no son copia.
No se guarda el texto del mensaje en ningún lado.
"""
import re

from chat.services.guided_problems import GUIDED_KINDS, REFUSAL, next_help, number_tokens, retry_with_example
from chat.services.operation_guides import build_first_step_prompt, build_socratic_math_guide
from chat.services.tutor_service import normalize_context_text


ANSWER_REQUEST = "answer_request"
BYPASS_ATTEMPT = "bypass_attempt"

_TARGET = (
    r"(?:(?:la|las|el|los|tu|una|un)\s+)?(?:respuesta|respuestas|resultado|resultados|solucion|soluciones)"
    r"(?:\s+(?:final|finales|correcta|correctas|directa|completa|exacta))?"
)
_FILLER = r"(?:\s+(?:ya|solo|nada mas|nomas|directo|directamente|de una vez|por favor|porfa|porfavor|rapido|me))*"
_ASK = (
    r"(?:dame|dime|pasame|escribe|escribeme|muestrame|ensename|ponme|quiero|necesito|regalame|sueltame|"
    r"me das|me dices|me pasas|me puedes dar|me puedes decir|puedes darme|puedes decirme|podrias darme|podrias decirme)"
)

ANSWER_REQUEST_PATTERNS = [re.compile(pattern) for pattern in (
    rf"\b{_ASK}\b{_FILLER}\s+(?:cual es\s+)?{_TARGET}\b",
    rf"\bcual es {_TARGET}\b",
    rf"^(?:solo|nomas|nada mas)\s+{_TARGET}\b",
    r"\bhaz(?:me)?\s+(?:la|mi|las|mis)\s+tareas?\b",
    r"\bhazme (?:el|este|mi) (?:ejercicio|problema|trabajo)\b",
    r"\bresuelve(?:lo|la|los|las|me)?\s+(?:tu\s+)?(?:todo\s+)?por mi\b",
    r"\bhaz(?:lo|la)?\s+(?:tu\s+)?por mi\b",
    r"\bresuelvelo tu\b",
)]

BYPASS_PATTERNS = [re.compile(pattern) for pattern in (
    r"\b(?:ignora|ignorar|olvida|olvidate de|saltate|desactiva|rompe)\s+(?:todas\s+)?(?:(?:tus|las|esas|estas)\s+)?"
    r"(?:instrucciones|reglas|restricciones|indicaciones)\b",
    r"\bactua como\b",
    r"\bfinge (?:que|ser)\b",
    r"\bhaz de cuenta que eres\b",
    r"\bahora eres\b",
    r"\b(?:muestra|muestrame|ensename|dime|revela|imprime|escribe)\s+(?:tu|el|tus)\s+"
    r"(?:prompt|system prompt|instrucciones|reglas internas)\b",
    r"\bmodo (?:desarrollador|developer|dios|sin reglas)\b",
    r"\bsin (?:reglas|restricciones|filtros)\b",
    r"\bjailbreak\b",
)]

BYPASS_NOTE = "Mis reglas no cambian: estoy aquí para ayudarte a aprender, no para resolver por ti."
ASK_WHAT_TRIED = (
    "¿Qué intentaste hasta ahora? Cuéntame tu primer paso o en qué parte te atoraste y lo revisamos juntos. "
    "También puedes escribirme tu problema (por ejemplo «¿cuánto es 2/3 + 1/6?») o pedir «Ponme un ejercicio de fracciones»."
)
EXAMPLE_EVERY = 3
CONCEPT_WORDS = {"aguda", "grave", "esdrujula"}


def classify_integrity(message):
    """Devuelve "bypass_attempt", "answer_request" o None (acentos, mayúsculas y signos normalizados)."""
    text = normalize_context_text(message)
    if any(pattern.search(text) for pattern in BYPASS_PATTERNS):
        return BYPASS_ATTEMPT
    if any(pattern.search(text) for pattern in ANSWER_REQUEST_PATTERNS):
        return ANSWER_REQUEST
    return None


def problem_key(state):
    custom = state.get("custom_problem")
    if state.get("active_exercise_id"):
        return f"exercise:{state['active_exercise_id']}"
    if custom:
        return f"problem:{custom.get('expr')}"
    return None


def _count_request(state):
    """Cuenta pedidos sobre el mismo problema; se reinicia al cambiar de problema o resolverlo."""
    key = problem_key(state)
    counter = state.get("answer_request_counter") or {}
    if counter.get("key") != key or "count" not in counter:
        counter = {"key": key, "count": 0}
    counter["count"] += 1
    state["answer_request_counter"] = counter
    return key, counter["count"]


def _exercise_reveals(text, exercise, options):
    """¿El texto muestra la pregunta o la respuesta del ejercicio activo?"""
    folded = normalize_context_text(text)
    if normalize_context_text(exercise["question"]) in folded:
        return True
    expected = str(exercise.get("expected_answer", ""))
    if exercise.get("type") in {"fraction", "numeric", "percentage"}:
        values = {token["value"] for token in number_tokens(text.casefold())}  # Conserva "3/4".
        return any(token["value"] in values for token in number_tokens(expected))
    correct = normalize_context_text(str(options.get(expected, "")))
    return bool(correct) and correct not in CONCEPT_WORDS and re.search(rf"\b{re.escape(correct)}\b", folded) is not None


def _exercise_example(state, tutor):
    """Ejemplo parecido con otros números para el tema del ejercicio activo (del menú del tema)."""
    topic_id = state.get("current_topic")
    exercise = tutor.selector._exercises.get(topic_id, {}).get(state.get("active_exercise_id"), {})
    options = exercise.get("options") or {}
    if topic_id and tutor.knowledge.has_explanation_menu(topic_id):
        menu = tutor.knowledge._get_topic(topic_id)["explanation_menu"]
        # Primero las opciones con una operación resuelta: se parecen más a un ejercicio.
        for option in sorted(menu["options"], key=lambda o: "=" not in o["explanation"]):
            if not _exercise_reveals(option["explanation"], exercise, options):
                return (f"Te dejo un ejemplo parecido, con otros datos:\n\n{option['explanation']}\n\n"
                        "Ahora intenta tu ejercicio con la misma idea.")
    return "Vuelve a leer el ejercicio con calma y dime qué dato crees que es el más importante."


def _menu_reminder(state, tutor):
    topic_id = state["pending_explanation_menu"]["topic"]
    menu = tutor.knowledge.get_explanation_menu(topic_id)
    lines = [f"{option['label']}) {option['text']}" for option in menu["options"]]
    return "Primero dime qué parte se te complica:\n" + "\n".join(lines)


def _start_new_problem(message, state):
    """Si el pedido trae su propio problema (distinto del pendiente), lo arranca sin dar el resultado."""
    first_step = build_first_step_prompt(message)
    if first_step:
        state.pop("custom_problem", None)
        return first_step
    probe = {}
    guide = build_socratic_math_guide(message, probe)
    previous = state.get("custom_problem") or {}
    new_problem = probe.get("custom_problem")
    if guide and new_problem and new_problem.get("expr") != previous.get("expr"):
        state["custom_problem"] = new_problem
        return guide
    return None


def integrity_reply(kind, message, state, tutor):
    """Rechazo amable y explícito + la siguiente ayuda. Nunca incluye el resultado."""
    parts = [REFUSAL]
    if kind == BYPASS_ATTEMPT:
        parts.append(BYPASS_NOTE)

    if state.get("pending_explanation_menu"):
        _count_request(state)
        parts.append(_menu_reminder(state, tutor))
        return "\n\n".join(parts)

    started = None if state.get("active_exercise_id") else _start_new_problem(message, state)
    key, count = _count_request(state)
    if started:
        parts.append(started)
        return "\n\n".join(parts)

    show_example = key is not None and count % EXAMPLE_EVERY == 0
    custom = state.get("custom_problem")
    if state.get("active_exercise_id"):
        if show_example:
            parts.append(_exercise_example(state, tutor))
        else:
            hint = tutor._give_hint(state)
            parts.append(f"Pista: {hint['message']}")
    elif custom and custom.get("kind") in GUIDED_KINDS:
        parts.append(retry_with_example(state) if show_example else next_help(state))
    elif custom:
        parts.append(f"Pista para **{custom['expr']}**: {custom['hint']}")
        if show_example:
            parts.append("Si quieres practicar con otros números, escríbeme «Ponme un ejercicio de fracciones».")
    else:
        parts.append(ASK_WHAT_TRIED)
    return "\n\n".join(parts)
