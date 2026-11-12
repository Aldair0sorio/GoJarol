
import pytest

from progress.services.adaptive_learning_service import (
    AdaptiveLearningService,
)


@pytest.fixture
def service():
    return AdaptiveLearningService()


def evaluate(status):
    return {"status": status}


def test_initial_state(service):
    state = service.initial_state()

    assert state["difficulty"] == 1
    assert state["total_attempts"] == 0


def test_correct_answer_same_level(service):
    result = service.update_progress(
        service.initial_state(),
        "exercise_1",
        evaluate("correct"),
    )

    assert result["progress"]["difficulty"] == 1
    assert result["next_action"] == "practice_same_level"


def test_increase_difficulty(service):
    first = service.update_progress(
        service.initial_state(),
        "exercise_1",
        evaluate("correct"),
    )

    second = service.update_progress(
        first["progress"],
        "exercise_2",
        evaluate("correct"),
    )

    assert second["progress"]["difficulty"] == 2
    assert second["next_action"] == "increase_difficulty"


def test_same_exercise_does_not_advance(service):
    first = service.update_progress(
        service.initial_state(),
        "exercise_1",
        evaluate("correct"),
    )

    second = service.update_progress(
        first["progress"],
        "exercise_1",
        evaluate("correct"),
    )

    assert second["progress"]["difficulty"] == 1


def test_correct_with_hint(service):
    result = service.update_progress(
        service.initial_state(),
        "exercise_1",
        evaluate("correct"),
        hints_used=2,
    )

    assert result["next_action"] == "practice_same_level"
    assert result["progress"]["unassisted_correct_ids"] == []


def test_repeated_errors(service):
    state = service.initial_state()
    state["difficulty"] = 2

    first = service.update_progress(
        state,
        "exercise_1",
        evaluate("incorrect"),
    )

    second = service.update_progress(
        first["progress"],
        "exercise_1",
        evaluate("incorrect"),
    )

    assert second["progress"]["difficulty"] == 1
    assert second["next_action"] == "reinforce_basics"


def test_invalid_answer_does_not_count(service):
    result = service.update_progress(
        service.initial_state(),
        "exercise_1",
        evaluate("invalid"),
    )

    assert result["progress"]["total_attempts"] == 0
    assert result["next_action"] == "clarify_answer"


def test_maximum_difficulty(service):
    state = service.initial_state()
    state["difficulty"] = 3

    first = service.update_progress(
        state,
        "exercise_1",
        evaluate("correct"),
    )

    second = service.update_progress(
        first["progress"],
        "exercise_2",
        evaluate("correct"),
    )

    assert second["progress"]["difficulty"] == 3
    assert second["next_action"] == "schedule_review"


def test_invalid_hints(service):
    with pytest.raises(ValueError):
        service.update_progress(
            service.initial_state(),
            "exercise_1",
            evaluate("correct"),
            hints_used=-1,
        )
