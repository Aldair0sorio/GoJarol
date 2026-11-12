from pathlib import Path
from unittest.mock import Mock

import pytest

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService
from gojarol_ml.nlp.analyzer import JarolAnalyzer


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def analyzer():
    return JarolAnalyzer(
        ROOT / "ml/artifacts/intent_classifier.joblib",
        ROOT / "ml/data/knowledge/topics.json",
    )


@pytest.fixture
def tutor(analyzer):
    knowledge = KnowledgeService(ROOT / "content/topics")
    return TutorService(analyzer, knowledge, HintService(knowledge))


def start(tutor):
    result = tutor.process_message("Ponme un ejercicio de ecuaciones")
    assert result["type"] == "exercise"
    assert result["exercise"]["id"] == "ecu_001"
    return result


def test_explanation_and_adaptation_through_all_levels_with_real_nlp(tutor):
    explanation = tutor.process_message("Explícame las ecuaciones de primer grado")
    assert explanation["type"] == "explanation_menu"  # Jarol pregunta antes de explicar.
    assert explanation["state"]["current_topic"] == "mat_ecuaciones"
    result = start(tutor)
    for attempt, (exercise_id, level, answer) in enumerate([
        ("ecu_001", 1, "x = 7"), ("ecu_002", 1, "x = -3"),
        ("ecu_004", 2, "6"), ("ecu_005", 2, "x=-8"),
        ("ecu_007", 3, "x=6"), ("ecu_008", 3, "-5"), ("ecu_009", 3, "9"),
    ], 1):
        assert result["exercise"]["id"] == exercise_id
        assert result["exercise"]["difficulty"] == level
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        progress = result["state"]["progress_by_topic"]["mat_ecuaciones"]
        assert progress["difficulty"] == min(1 + attempt // 2, 3)
        assert progress["total_attempts"] == attempt
        if attempt in (2, 4):
            assert result["next_action"] == "increase_difficulty"
        result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["type"] == "exercise_unavailable"


@pytest.mark.parametrize("answer", ["7", "x=7", "x = 7", "8", "x = 7.0", "x=oops", "7/1"])
def test_numeric_attempts_bypass_nlp_and_invalid_formats_do_not_count(tutor, answer):
    result = start(tutor)
    tutor.analyzer = Mock()
    result = tutor.process_message(answer, result["state"])
    expected_status = "correct" if answer in {"7", "x=7", "x = 7"} else (
        "incorrect" if answer == "8" else "invalid"
    )
    assert result["evaluation"]["status"] == expected_status
    assert result["state"]["progress_by_topic"]["mat_ecuaciones"]["total_attempts"] == (expected_status != "invalid")
    tutor.analyzer.analyze_message.assert_not_called()


def test_equation_hints_assisted_progress_and_zero_answer(tutor):
    result = start(tutor)
    result = tutor.process_message("x=7", result["state"])
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["exercise"]["id"] == "ecu_002"
    result = tutor.process_message("No sé", result["state"])
    assert result["message"] == tutor.selector.get_hint("mat_ecuaciones", "ecu_002", 0)
    assert result["message"] != tutor.selector.get_hint("mat_ecuaciones", "ecu_001", 0)
    result = tutor.process_message("Otra", result["state"])
    assert result["message"] == tutor.selector.get_hint("mat_ecuaciones", "ecu_002", 1)
    result = tutor.process_message("x=-3", result["state"])
    assert result["next_action"] == "practice_same_level"
    assert result["state"]["progress_by_topic"]["mat_ecuaciones"]["difficulty"] == 1
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["exercise"]["id"] == "ecu_003"
    result = tutor.process_message("x=0", result["state"])
    assert result["evaluation"]["correct"]
    assert result["state"]["progress_by_topic"]["mat_ecuaciones"]["difficulty"] == 1


def test_three_topics_keep_independent_progress_and_active_hints(tutor):
    result = start(tutor)
    result = tutor.process_message("x=7", result["state"])
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    result = tutor.process_message("No sé", result["state"])
    equation_progress = result["state"]["progress_by_topic"]["mat_ecuaciones"]
    result = tutor.process_message("Ponme un ejercicio de fracciones", result["state"])
    assert result["exercise"]["id"] == "frac_001"
    assert result["state"]["hints_used"] == 0
    result = tutor.process_message("6/8", result["state"])
    assert result["evaluation"]["correct"]
    fraction_progress = result["state"]["progress_by_topic"]["mat_fracciones"]
    result = tutor.process_message("Ponme un ejercicio de comprensión lectora", result["state"])
    assert result["exercise"]["id"] == "esp_comp_001"
    result = tutor.process_message("Opción B", result["state"])
    assert result["evaluation"]["correct"]
    reading_progress = result["state"]["progress_by_topic"]["esp_comprension"]
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", result["state"])
    assert result["exercise"]["id"] == "ecu_002"
    assert result["state"]["hints_used"] == 1
    assert result["state"]["progress_by_topic"]["mat_ecuaciones"] == equation_progress
    result = tutor.process_message("Dame una pista", result["state"])
    assert result["message"] == tutor.selector.get_hint("mat_ecuaciones", "ecu_002", 1)
    result = tutor.process_message("x=-3", result["state"])
    assert result["state"]["progress_by_topic"]["mat_fracciones"] == fraction_progress
    assert result["state"]["progress_by_topic"]["esp_comprension"] == reading_progress


def test_completed_equation_cannot_count_twice(tutor):
    result = start(tutor)
    result = tutor.process_message("x=7", result["state"])
    stale = dict(result["state"], active_exercise_id="ecu_001", active_exercise_type="numeric")
    duplicate = tutor.process_message("x=7", stale)
    assert duplicate["type"] == "exercise_required"
    assert duplicate["state"]["progress_by_topic"] == result["state"]["progress_by_topic"]
    assert duplicate["state"]["completed_exercises"] == ["ecu_001"]


def test_public_equation_responses_never_include_solutions(tutor):
    result = start(tutor)
    responses = [result]
    for message in ("x=oops", "8", "No sé", "Otra", "Otra", "Otra", "x=7"):
        result = tutor.process_message(message, result["state"])
        responses.append(result)
    def check(value):
        if isinstance(value, dict):
            assert not {"expected_answer", "solution_steps", "hints", "correct_index"} & value.keys()
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(responses)
