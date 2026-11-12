
import re
from fractions import Fraction
import unicodedata


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



def normalize_choice(answer: str) -> str | None:
    if not isinstance(answer, str):
        return None

    text = unicodedata.normalize("NFD", answer.casefold())
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = " ".join(text.strip().split())

    pattern = (
        r"(?:mi respuesta es |"
        r"(?:la )?respuesta (?:es )?|"
        r"(?:la )?opcion |la )?"
        r"([a-d])\s*[\).]?"
    )

    match = re.fullmatch(pattern, text)

    if not match:
        return None

    return match.group(1).upper()


def evaluate_multiple_choice_answer(
    student_answer: str,
    expected_answer: str,
) -> dict:
    expected = expected_answer.strip().upper()

    if expected not in {"A", "B", "C", "D"}:
        raise ValueError(
            "La respuesta esperada del ejercicio es invalida."
        )

    answer = normalize_choice(student_answer)

    if answer is None:
        return {
            "correct": False,
            "status": "invalid",
            "feedback": (
                "No pude interpretar tu respuesta. "
                "Escribe la letra de la opcion que elegiste."
            ),
        }

    if answer == expected:
        return {
            "correct": True,
            "status": "correct",
            "feedback": (
                "¡Correcto! Identificaste la respuesta adecuada."
            ),
        }

    return {
        "correct": False,
        "status": "incorrect",
        "feedback": (
            "Todavia no es correcto. "
            "Revisa el texto y vuelve a intentarlo."
        ),
    }


INTEGER_ANSWER_PATTERN = re.compile(r"\s*(?:x\s*=\s*)?([+-]?[0-9]+)\s*", re.IGNORECASE)


def parse_integer_answer(value: str) -> int | None:
    """Read a bounded integer literal, optionally assigned to x; never execute it."""
    if not isinstance(value, str) or len(value) > 40:
        return None
    match = INTEGER_ANSWER_PATTERN.fullmatch(value)
    return int(match.group(1)) if match else None


def evaluate_numeric_answer(student_answer: str, expected_answer: str) -> dict:
    expected = parse_integer_answer(expected_answer)
    if expected is None:
        raise ValueError("La respuesta entera esperada del ejercicio es invalida.")
    student = parse_integer_answer(student_answer)
    if student is None:
        return {
            "correct": False,
            "status": "invalid",
            "feedback": "Escribe un número entero, solo o en la forma x = entero. No incluyas operaciones.",
        }
    if student == expected:
        return {
            "correct": True,
            "status": "correct",
            "feedback": "Bien hecho. Tu respuesta es correcta. ¿Puedes explicar cómo la calculaste?",
        }
    return {
        "correct": False,
        "status": "incorrect",
        "feedback": "Todavía no es correcto. Revisa las operaciones y qué cantidad pide el problema. Puedes pedir una pista.",
    }


PERCENTAGE_PATTERN = re.compile(r"\s*([+-]?[0-9]+(?:[.,][0-9]+)?)\s*%?\s*")


def parse_percentage_answer(value: str) -> Fraction | None:
    """Return percentage points exactly: 25 and 25% both mean twenty-five percent."""
    if not isinstance(value, str) or len(value) > 40:
        return None
    match = PERCENTAGE_PATTERN.fullmatch(value)
    return Fraction(match.group(1).replace(",", ".")) if match else None


def evaluate_percentage_answer(student_answer: str, expected_answer: str) -> dict:
    expected = parse_percentage_answer(expected_answer)
    if expected is None:
        raise ValueError("La respuesta porcentual esperada es invalida.")
    student = parse_percentage_answer(student_answer)
    if student is None:
        return {
            "correct": False, "status": "invalid",
            "feedback": "Escribe el porcentaje como número, con o sin %. Puedes usar punto o coma decimal; no incluyas operaciones ni unidades monetarias.",
        }
    correct = student == expected
    return {
        "correct": correct,
        "status": "correct" if correct else "incorrect",
        "feedback": (
            "Correcto. ¿Cómo relacionaste la parte con el total?" if correct
            else "Todavía no es correcto. Revisa la base del porcentaje y distingue la parte del total."
        ),
    }


def evaluate_exercise_answer(
    student_answer: str,
    expected_answer: str,
    exercise_type: str,
) -> dict:
    if exercise_type == "percentage":
        return evaluate_percentage_answer(student_answer, expected_answer)

    if exercise_type == "numeric":
        return evaluate_numeric_answer(student_answer, expected_answer)

    if exercise_type == "fraction":
        return evaluate_fraction_answer(
            student_answer,
            expected_answer,
        )

    if exercise_type == "multiple_choice":
        return evaluate_multiple_choice_answer(
            student_answer,
            expected_answer,
        )

    raise ValueError(
        f"Tipo de ejercicio no compatible: {exercise_type}"
    )
