import pytest

from exercises.services.exercise_evaluator import (
    evaluate_exercise_answer,
    parse_integer_answer,
)


@pytest.mark.parametrize("answer, expected", [
    ("7", 7), ("x=7", 7), ("x = 7", 7), (" +7 ", 7),
    ("-3", -3), ("x = -3", -3), ("X = -3", -3),
    ("0", 0), ("x=0", 0), (" x = +007 ", 7),
])
def test_integer_answers(answer, expected):
    assert parse_integer_answer(answer) == expected
    result = evaluate_exercise_answer(answer, str(expected), "numeric")
    assert result["correct"] is True
    assert result["status"] == "correct"


@pytest.mark.parametrize("answer", [
    "", "hola", "7.0", "7,0", "7/1", "x = 3.5", "x == 7", "y=7",
    "x=", "x=--3", "x = 3 + 4", "7 o 8", "7; print(7)",
    "__import__('os').system('echo unsafe')", "9" * 41, "٧", None, 7, True,
])
def test_invalid_numeric_formats(answer):
    assert parse_integer_answer(answer) is None
    result = evaluate_exercise_answer(answer, "7", "numeric")
    assert not result["correct"]
    assert result["status"] == "invalid"


@pytest.mark.parametrize("answer, expected", [("8", "7"), ("x=-2", "-3"), ("0", "7")])
def test_incorrect_numeric_answers_do_not_expose_the_solution(answer, expected):
    result = evaluate_exercise_answer(answer, expected, "numeric")
    assert result["status"] == "incorrect"
    assert result["correct"] is False
    assert set(result) == {"correct", "status", "feedback"}
    assert expected not in result["feedback"]


@pytest.mark.parametrize("expected", ["7.0", "7/1", "unknown", None])
def test_invalid_internal_solution_is_rejected(expected):
    with pytest.raises(ValueError, match="esperada"):
        evaluate_exercise_answer("7", expected, "numeric")
