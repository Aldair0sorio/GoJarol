
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


from exercises.services.exercise_evaluator import (
    evaluate_exercise_answer,
)


@pytest.mark.parametrize(
    "answer",
    ["B", "b", "B)", "Opción B", "La respuesta es B"],
)
def test_multiple_choice_correct(answer):
    result = evaluate_exercise_answer(
        answer, "B", "multiple_choice"
    )

    assert result["correct"] is True
    assert result["status"] == "correct"


def test_multiple_choice_incorrect():
    result = evaluate_exercise_answer(
        "A", "B", "multiple_choice"
    )

    assert result["correct"] is False
    assert result["status"] == "incorrect"


@pytest.mark.parametrize("answer", ["", "No sé", "A o B"])
def test_multiple_choice_invalid(answer):
    result = evaluate_exercise_answer(
        answer, "B", "multiple_choice"
    )

    assert result["status"] == "invalid"


def test_fraction_still_works():
    result = evaluate_exercise_answer(
        "6/8", "3/4", "fraction"
    )

    assert result["correct"] is True


def test_unknown_exercise_type():
    with pytest.raises(ValueError):
        evaluate_exercise_answer(
            "B", "B", "open_response"
        )


def test_invalid_expected_choice():
    with pytest.raises(ValueError):
        evaluate_exercise_answer(
            "A", "X", "multiple_choice"
        )
