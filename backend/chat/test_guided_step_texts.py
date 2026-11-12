"""Cada paso de las guías (fracciones y división) no revela su resultado antes de que el alumno lo dé.

Por paso se juntan TODOS los textos que Jarol muestra mientras el alumno sigue en ese paso:
la presentación del paso, 3 respuestas equivocadas (la 3.ª saca el ejemplo completo) y 5 "no sé"
(todas las ayudas y el ejemplo). Ninguno puede contener la respuesta de ese paso ni la de los
pasos siguientes. Los números que el propio alumno escribió no cuentan como revelados.
"""
import re

import pytest
from sympy import Rational

from chat.services.operation_guides import match_specific_operation_guide

NUMBER = re.compile(r"(?<![\w.,/])(-?\d+)(?:\s*/\s*(\d+)|\.(\d+))?")
WORDS = ["cero", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce"]


def tokens(text):
    """(literal sin espacios, valor exacto, ¿es decimal?) de cada número del texto."""
    found = []
    for match in NUMBER.finditer(text):
        whole, den, dec = match.groups()
        literal = re.sub(r"\s+", "", match.group(0))
        value = Rational(int(whole), int(den)) if den else Rational(literal) if dec else Rational(int(whole))
        found.append((literal, value, dec is not None))
    return found


def step(name, answer, wrong, values=(), literals=(), near=None, words=None):
    """Un paso: lo que el alumno escribe para resolverlo y lo que no puede aparecer antes."""
    return {"name": name, "answer": answer, "wrong": wrong, "values": {Rational(v) for v in values},
            "literals": set(literals), "near": near, "words": words}


CASES = {
    # Distinto denominador: m.c.m. 15, conversiones 10/15 y 9/15, resultado 19/15.
    "2/3 + 3/5": ("¿cuánto es 2/3 + 3/5?", [
        step("common_denominator", "15", ["10", "9", "25"], values=[15]),
        step("convert_first", "10/15", ["2/15", "6/15", "4/6"], literals=["10/15"]),
        step("convert_second", "9/15", ["3/15", "5/15", "6/10"], literals=["9/15"]),
        step("operate", "19", ["13", "12", "17"], values=[19, Rational(19, 15)], literals=["19/15"]),
    ]),
    # Resta: m.c.m. 12, conversiones 10/12 y 3/12, resultado 7/12.
    "5/6 - 1/4": ("¿cuánto es 5/6 - 1/4?", [
        step("common_denominator", "12", ["10", "18", "8"], values=[12]),
        step("convert_first", "10/12", ["5/12", "6/12", "15/18"], literals=["10/12"]),
        step("convert_second", "3/12", ["1/12", "4/12", "2/8"], literals=["3/12"]),
        step("operate", "7/12", ["13/12", "6/12", "9/12"], values=[7, Rational(7, 12)], literals=["7/12"]),
    ]),
    # El denominador común (4) ya está en el problema: no puede ocultarse; sí la conversión y el resultado.
    "1/2 + 3/4": ("¿cuánto es 1/2 + 3/4?", [
        step("common_denominator", "4", ["6", "3", "10"]),
        step("convert_first", "2/4", ["1/4", "3/4", "4/8"], literals=["2/4"]),
        step("operate", "5/4", ["4/4", "6/4", "8/4"], values=[5, Rational(5, 4)], literals=["5/4"]),
    ]),
    # Mismo denominador: un solo paso, resultado 5/8.
    "3/8 + 2/8": ("¿cuánto es 3/8 + 2/8?", [
        step("same_denominator", "5/8", ["5/16", "6/8", "1/8"], values=[5, Rational(5, 8)], literals=["5/8"]),
    ]),
    "7/9 - 4/9": ("¿cuánto es 7/9 - 4/9?", [
        step("same_denominator", "3/9", ["4/18", "11/9", "2/9"], values=[3, Rational(1, 3)], literals=["3/9"]),
    ]),
    # División con residuo: cabe 4, sobran 5, 29 ÷ 6 = 4.8333…
    "29 ÷ 6": ("¿cuánto sería 29/6?", [
        step("integer_part", "4", ["7", "8", "3"], values=[4], words=4),
        step("remainder", "5", ["3", "1", "2"], values=[5]),
        step("decimal", "4.83", ["4.5", "4.2", "3.8"], values=[Rational(29, 6)], near=Rational(29, 6)),
    ]),
    # División con residuo y cociente 1: cabe 1, sobran 3, 7 ÷ 4 = 1.75.
    "7 ÷ 4": ("¿cuánto sería 7/4?", [
        step("integer_part", "1", ["2", "3", "5"], values=[1], words=1),
        step("remainder", "3", ["0", "2", "6"], values=[3]),
        step("decimal", "1.75", ["1.5", "2.75", "1.25"], values=[Rational(7, 4)], near=Rational(7, 4)),
    ]),
    # División exacta: un solo paso (cabe 5 = resultado).
    "45 ÷ 9": ("¿cuánto es 45 entre 9?", [
        step("integer_part", "5", ["4", "6", "3"], values=[5], words=5),
    ]),
}


def visible(text):
    return {value for _, value, _ in tokens(text)}


def check(texts, pending_steps, given, operands, divisor):
    """Ningún texto muestra la respuesta de un paso pendiente (salvo números que ya escribió el alumno)."""
    for text in texts:
        for literal, value, is_decimal in tokens(text):
            for st in pending_steps:
                hidden_values = st["values"] - given - operands
                assert value not in hidden_values, f"[{st['name']}] revela {value}:\n{text}"
                assert literal not in st["literals"] - {g for g in given if isinstance(g, str)}, \
                    f"[{st['name']}] revela {literal}:\n{text}"
                if st["near"] is not None and is_decimal:
                    assert abs(value - st["near"]) >= Rational(1, 10), f"[{st['name']}] aproxima {value}:\n{text}"
        for st in pending_steps:
            if st["words"] is not None:
                # "el 6 cabe cuatro veces" sobre SU división (un ejemplo con otros números sí puede decirlo).
                pattern = rf"el \**{divisor}\** cabe \**{WORDS[st['words']]}\b"
                assert not re.search(pattern, text), f"[{st['name']}] revela cuántas veces cabe:\n{text}"


@pytest.mark.parametrize("leaky_text", [
    "El denominador común es 15.",   # m.c.m. del paso 1
    "Ojo: 2/3 = 10 / 15.",            # conversión del paso 2
    "En total te da 38/30.",         # resultado en otra forma (vale 19/15)
])
def test_control_check_detects_a_revealing_text(leaky_text):
    _, steps = CASES["2/3 + 3/5"]
    with pytest.raises(AssertionError):
        check([leaky_text], steps, set(), visible("2/3 + 3/5"), None)


def test_control_check_detects_division_reveals():
    _, steps = CASES["29 ÷ 6"]
    operands = {Rational(29), Rational(6)}
    for leaky_text in ("Sobran 5.", "Da 4.8 aproximadamente.", "Mira: el **6** cabe **cuatro veces** en el 29."):
        with pytest.raises(AssertionError):
            check([leaky_text], steps, set(), operands, "6")


@pytest.mark.parametrize("name", CASES)
def test_each_guided_step_hides_its_answer_until_the_student_gives_it(name):
    opening, steps = CASES[name]
    state = {}
    intro = match_specific_operation_guide(opening, state)[0]
    operands = visible(opening if "÷" not in name else name.replace("÷", " "))
    divisor = name.split("÷")[1].strip() if "÷" in name else None
    given = set()
    texts = [intro]

    for index, st in enumerate(steps):
        assert state["custom_problem"]["step"] == st["name"], f"Se esperaba {st['name']}"
        for wrong in st["wrong"]:
            given |= visible(wrong) | {wrong}
            texts.append(match_specific_operation_guide(wrong, state)[0])
            assert state["custom_problem"]["step"] == st["name"], f"{wrong!r} no debió resolver {st['name']}"
        for _ in range(5):
            texts.append(match_specific_operation_guide("no sé", state)[0])

        check(texts, steps[index:], given, operands, divisor)

        given |= visible(st["answer"]) | {st["answer"]}
        texts = [match_specific_operation_guide(st["answer"], state)[0]]  # Ya lo dio: puede confirmarse.

    assert "custom_problem" not in state
    assert "🎉" in texts[0]
