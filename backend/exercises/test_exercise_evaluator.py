
import pytest

from exercises.services.exercise_evaluator import (
    evaluate_fraction_answer,
)


@pytest.mark.parametrize(
    "answer",
    ["3/4", "6/8", "9/12", " 3 / 4 "],
)
def test_equivalent_answers(answer):
    result = evaluate_fraction_answer(answer, "3/4")

    assert result["correct"] is True
    assert result["status"] == "correct"


def test_incorrect_answer():
    result = evaluate_fraction_answer("3/8", "3/4")

    assert result["correct"] is False
    assert result["status"] == "incorrect"


@pytest.mark.parametrize(
    "answer",
    ["hola", "", "1/0", "3//4"],
)
def test_invalid_answer(answer):
    result = evaluate_fraction_answer(answer, "3/4")

    assert result["correct"] is False
    assert result["status"] == "invalid"


def test_invalid_expected_answer():
    with pytest.raises(ValueError):
        evaluate_fraction_answer("1/2", "incorrecto")


def test_answer_is_not_exposed():
    result = evaluate_fraction_answer("1/8", "3/4")

    assert "expected_answer" not in result
    assert "3/4" not in result["feedback"]
