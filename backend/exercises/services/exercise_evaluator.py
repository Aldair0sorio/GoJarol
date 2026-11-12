
import re
from fractions import Fraction


FRACTION_PATTERN = re.compile(
    r"^\s*([+-]?\d+)(?:\s*/\s*([+-]?\d+))?\s*$"
)


def parse_fraction(value: str) -> Fraction | None:
    if not isinstance(value, str) or len(value) > 40:
        return None

    match = FRACTION_PATTERN.fullmatch(value)

    if not match:
        return None

    numerator = int(match.group(1))
    denominator = (
        int(match.group(2))
        if match.group(2) is not None
        else 1
    )

    if denominator == 0:
        return None

    return Fraction(numerator, denominator)


def evaluate_fraction_answer(
    student_answer: str,
    expected_answer: str,
) -> dict:

    expected = parse_fraction(expected_answer)

    if expected is None:
        raise ValueError(
            "La respuesta esperada del ejercicio es invalida."
        )

    student = parse_fraction(student_answer)

    if student is None:
        return {
            "correct": False,
            "status": "invalid",
            "feedback": (
                "No pude interpretar tu respuesta. "
                "Escribela como fraccion, por ejemplo 1/2."
            ),
        }

    if student == expected:
        return {
            "correct": True,
            "status": "correct",
            "feedback": (
                "Bien hecho. Tu respuesta es correcta. "
                "¿Puedes explicar como llegaste a ella?"
            ),
        }

    return {
        "correct": False,
        "status": "incorrect",
        "feedback": (
            "Todavia no es correcto. "
            "Revisa tu procedimiento y vuelve a intentarlo."
        ),
    }
