"""Resolución guiada por pasos: Jarol acompaña sin dar el resultado."""
import re
from math import lcm

import pytest
from sympy import Rational

from chat.services.operation_guides import match_specific_operation_guide


def send(state, message):
    result = match_specific_operation_guide(message, state)
    return result[0] if result else None


# --- Comprobación de fugas (independiente del código) -----------------------------

TOKEN = re.compile(r"(?<![\w.,/])(-?\d+)(?:\s*/\s*(\d+)|\.(\d+))?")


def tokens(text):
    found = []
    for whole, den, dec in TOKEN.findall(text):
        if den:
            found.append((f"{whole}/{den}", Rational(int(whole), int(den))))
        elif dec:
            found.append((f"{whole}.{dec}", Rational(f"{whole}.{dec}")))
        else:
            found.append((whole, Rational(int(whole))))
    return found


def fraction_secrets(a, b, op, c, d):
    """Resultado final y respuesta de cada paso de a/b op c/d."""
    final = Rational(a, b) + Rational(c, d) if op == "+" else Rational(a, b) - Rational(c, d)
    common = lcm(b, d)
    secrets = {"final": ("value", final)}
    if b != d:
        secrets["common"] = ("value", Rational(common))
        secrets["first"] = ("literal", f"{a * common // b}/{common}")
        secrets["second"] = ("literal", f"{c * common // d}/{common}")
    visible = {Rational(n) for n in (a, b, c, d)}
    return secrets, visible, {f"{a}/{b}", f"{c}/{d}"}


def division_secrets(a, b):
    q, r = divmod(a, b)
    secrets = {"final": ("value", Rational(a, b)), "q": ("value", Rational(q)), "r": ("value", Rational(r))}
    return secrets, {Rational(a), Rational(b)}, {f"{a}/{b}"}


def run_flow(secrets, visible, allowed, opening, script):
    """Ejecuta el diálogo y verifica que ningún secreto aparezca antes de que el alumno lo dé."""
    state = {}
    given_values, given_literals = set(), set()
    replies = []
    for message in [opening] + script:
        if message != opening:
            for literal, value in tokens(message):
                given_values.add(value)
                given_literals.add(literal)
        reply = send(state, message)
        assert reply is not None, f"Jarol perdió el contexto en: {message!r}"
        replies.append(reply)
        if "🎉" in reply:
            # El alumno acaba de dar el resultado (por ejemplo, solo el numerador): Jarol lo confirma.
            given_values.add(secrets["final"][1])
        for name, (kind, secret) in secrets.items():
            for literal, value in tokens(reply):
                if literal in allowed:
                    continue
                if kind == "value" and value == secret and secret not in visible and secret not in given_values:
                    pytest.fail(f"Se filtró {name}={secret} en respuesta a {message!r}:\n{reply}")
                if kind == "literal" and literal == secret and secret not in given_literals:
                    pytest.fail(f"Se filtró {name}={secret} en respuesta a {message!r}:\n{reply}")
    return state, replies


HELP_SCRIPT = ["No sé buscar un denominador común", "pista", "dame la respuesta", "dime el resultado", "no entiendo"]


@pytest.mark.parametrize("a,b,op,c,d,script", [
    # El ejemplo del alumno: ayudas, errores, ayudas en cada paso y respuestas parciales.
    (1, 2, "+", 3, 4, HELP_SCRIPT + ["3", "6", "7", "4", "no sé", "pista", "dame la respuesta", "1/2", "3/8", "9/4",
                                    "2/4", "no sé", "pista", "dime el resultado", "6/4", "1", "9", "5/4"]),
    (5, 6, "-", 1, 4, HELP_SCRIPT + ["10", "24", "no sé", "pista", "20/24", "no sé", "6/24", "dame la respuesta",
                                    "13/24", "14/24"]),
    (2, 3, "+", 3, 5, HELP_SCRIPT + ["15", "no se", "10/15", "no se", "pista", "9/15", "como", "19"]),
    (3, 8, "+", 2, 8, ["no sé", "pista", "dame la respuesta", "dime el resultado", "4/8", "6", "7", "5/8"]),
    (7, 9, "-", 4, 9, ["no sé", "pista", "dame el resultado", "2", "3/8", "3"]),
])
def test_fraction_flow_never_leaks_result_or_step_answers(a, b, op, c, d, script):
    secrets, visible, allowed = fraction_secrets(a, b, op, c, d)
    state, replies = run_flow(secrets, visible, allowed, f"¿cuánto es {a}/{b} {op} {c}/{d}?", script)
    assert "¡Exacto!" in replies[-1]
    assert "custom_problem" not in state


@pytest.mark.parametrize("a,b,script", [
    (5, 2, ["dime el resultado", "pista", "no sé", "no sé", "3", "4", "5", "2", "no sé", "pista", "dame la respuesta",
            "2", "3", "4", "1", "no sé", "pista", "dime el resultado", "2.4", "3.5", "2.5"]),
    (7, 4, ["no sé", "2", "1", "no se", "4", "3", "no sé", "1.75"]),
    (29, 6, ["dame la respuesta", "5", "pista", "no sé", "5", "no sé", "4.8"]),
])
def test_division_flow_never_leaks_quotient_remainder_or_result(a, b, script):
    secrets, visible, allowed = division_secrets(a, b)
    state, replies = run_flow(secrets, visible, allowed, f"cuanto seria {a}/{b}", script)
    assert "custom_problem" not in state
    assert "🎉" in replies[-1]


# --- El contexto se conserva y el paso se descompone ------------------------------

def test_student_example_keeps_context_and_breaks_down_common_denominator():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    reply = send(state, "No sé buscar un denominador común")

    assert reply is not None
    assert "¿Sobre qué tema" not in reply
    assert "Ejemplo con otros números" in reply
    assert "tabla del **2** y la del **4**" in reply
    assert state["custom_problem"]["step"] == "common_denominator"


def test_hint_and_answer_requests_give_next_help_never_the_result():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    helps = [send(state, message) for message in ("pista", "dame la respuesta", "dime el resultado")]

    assert len(set(helps)) == 3  # Cada vez, la siguiente ayuda.
    assert helps[1].startswith("No te voy a dar el resultado")
    assert helps[2].startswith("No te voy a dar el resultado")
    assert all("5/4" not in help_text for help_text in helps)


def test_steps_advance_and_check_intermediate_answers():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")

    assert "no en la del **4**" in send(state, "6")
    assert "Convertir 1/2" in send(state, "4")
    assert "denominador sea **4**" in send(state, "4/8")  # Equivalente, pero con otro denominador.
    assert "denominador **4** está bien" in send(state, "3/4")
    step = send(state, "2/4")
    assert "**2/4 + 3/4**" in step and state["custom_problem"]["step"] == "operate"
    assert "¡Exacto!" in send(state, "5")  # El numerador basta: el denominador se conserva.


def test_any_common_multiple_is_accepted():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    reply = send(state, "8")

    assert "hay uno más pequeño" in reply
    assert "?/8" in reply


@pytest.mark.parametrize("step_answers,final", [
    ([], "5/4"),            # En el denominador común.
    (["4"], "1.25"),        # En la conversión, en decimal.
    (["4", "2/4"], "10/8"),  # Equivalente sin simplificar.
])
def test_final_result_is_accepted_at_any_step(step_answers, final):
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    for answer in step_answers:
        send(state, answer)

    assert "¡Exacto!" in send(state, final)
    assert "custom_problem" not in state


def test_division_final_accepted_at_first_step_and_fraction_form_is_not_an_answer():
    state = {}
    send(state, "cuanto seria 5/2")
    assert "misma división escrita como fracción" in send(state, "5/2")
    assert "¡Exacto!" in send(state, "2.5")


def test_three_errors_show_full_example_and_practice_reminder():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    first, second, third = (send(state, n) for n in ("3", "6", "7"))

    assert "Ejemplo completo" not in first + second
    assert "Ejemplo completo con otros números" in third
    assert "Ahora inténtalo tú con **1/2 + 3/4**" in third
    assert "«Ponme un ejercicio de fracciones»" in third
    assert state["custom_problem"]["step"] == "common_denominator"


def test_division_three_errors_show_full_example():
    state = {}
    send(state, "cuanto seria 5/2")
    replies = [send(state, n) for n in ("3", "4", "5")]

    assert "Ejemplo completo con otros números" in replies[2]
    assert "«Ponme un ejercicio»" in replies[2]


def test_division_opening_no_longer_reveals_quotient_or_remainder():
    reply = send({}, "cuanto seria 5/2")

    assert "cabe **2**" not in reply and "sobra **1**" not in reply
    assert "2.5" not in reply


# --- Salir o cambiar de problema -----------------------------------------------------

@pytest.mark.parametrize("message", ["Ponme un ejercicio de fracciones", "explícame los porcentajes", "hola Jarol"])
def test_other_requests_leave_the_problem_and_follow_normal_flow(message):
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    send(state, message)

    assert "custom_problem" not in state


def test_new_problem_replaces_the_pending_one():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    reply = send(state, "¿cuánto es 2/3 + 1/6?")

    assert "**2/3 + 1/6**" in reply
    assert state["custom_problem"]["expr"] == "2/3 + 1/6"


def test_acknowledgement_repeats_current_step():
    state = {}
    send(state, "¿cuánto es 1/2 + 3/4?")
    assert "Denominador común" in send(state, "ok")


def test_multiplication_of_fractions_keeps_previous_behavior():
    state = {}
    reply = send(state, "¿cuánto es 1/2 x 3/4?")

    assert "Multiplica en línea recta" in reply
    assert "kind" not in state["custom_problem"]
