"""Solo se guarda la respuesta extraída, nunca el resto del mensaje del alumno."""
import pytest

from exercises.services.exercise_evaluator import canonical_answer


@pytest.mark.parametrize("message,exercise_type,expected", [
    ("3/4", "fraction", "3/4"),
    ("mi respuesta es 3 / 4.", "fraction", "3/4"),
    ("x = 7", "numeric", "x = 7"),
    ("  7 ", "numeric", "7"),
    ("25%", "percentage", "25%"),
    ("25", "percentage", "25%"),
    ("La respuesta es B", "multiple_choice", "B"),
    ("opción c", "multiple_choice", "C"),
    ("me lo dijo mi primo, es la B", "multiple_choice", ""),
    ("7 porque así lo vi en internet", "numeric", ""),
    ("x" * 300, "numeric", ""),
    ("", "fraction", ""),
])
def test_canonical_answer(message, exercise_type, expected):
    assert canonical_answer(message, exercise_type) == expected
    assert len(canonical_answer(message, exercise_type)) <= 255
