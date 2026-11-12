from pathlib import Path
from unittest.mock import Mock

import pytest

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.exercise_selector import ExerciseSelector
from exercises.services.hint_service import HintService


ROOT = Path(__file__).resolve().parents[2]


class Analyzer:
    def analyze_message(self, message, context):
        text = message.casefold()
        topic = context.get("current_topic")
        if "fracciones" in text:
            topic = "mat_fracciones"
        elif "lectora" in text:
            topic = "esp_comprension"
        intent = "solicitar_explicacion"
        if "ejercicio" in text:
            intent = "solicitar_reto"
        elif "pista" in text:
            intent = "solicitar_pista"
        return {"intent": intent, "topic": topic}


@pytest.fixture
def tutor():
    knowledge = KnowledgeService(ROOT / "content/topics")
    return TutorService(Analyzer(), knowledge, HintService(knowledge))


def test_progress_through_all_levels_and_exhaustion(tutor):
    result = tutor.process_message("ejercicio de fracciones")
    for number, answer in enumerate(["6/8", "3/5", "12/12", "18/20", "23/12", "23/15"], 1):
        assert result["exercise"]["id"] == f"frac_{number:03}"
        assert result["exercise"]["difficulty"] == (number + 1) // 2
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        assert result["state"]["progress_by_topic"]["mat_fracciones"]["total_attempts"] == number
        result = tutor.process_message("Otra", result["state"])
    assert result["type"] == "exercise_unavailable"
    assert len(result["state"]["completed_exercises"]) == 6


def test_active_exercise_hints_and_assisted_progress(tutor):
    start = tutor.process_message("ejercicio de fracciones")
    correct = tutor.process_message("3/4", start["state"])
    second = tutor.process_message("Otro ejercicio", correct["state"])
    hint = tutor.process_message("No sé", second["state"])
    assert hint["message"] == tutor.selector.get_hint("mat_fracciones", "frac_002", 0)
    assert hint["message"] != tutor.selector.get_hint("mat_fracciones", "frac_001", 0)
    repeat = tutor.process_message("Otro ejercicio", hint["state"])
    assert repeat["state"]["hints_used"] == 1
    correct = tutor.process_message("3/5", repeat["state"])
    assert correct["state"]["progress_by_topic"]["mat_fracciones"]["difficulty"] == 1


def test_choices_bypass_nlp_and_topic_changes_clear_context(tutor):
    start = tutor.process_message("ejercicio de fracciones")
    hint = tutor.process_message("No sé", start["state"])
    spanish = tutor.process_message("ejercicio de comprensión lectora", hint["state"])
    assert spanish["exercise"]["type"] == "multiple_choice"
    assert spanish["state"]["hints_used"] == 0
    spanish_hint = tutor.process_message("Dame una pista", spanish["state"])
    assert spanish_hint["message"] == tutor.selector.get_hint("esp_comprension", "esp_comp_001", 0)
    tutor.analyzer = Mock()
    wrong = tutor.process_message("Opción A", spanish_hint["state"])
    assert wrong["evaluation"]["status"] == "incorrect"
    correct = tutor.process_message("Opción B", wrong["state"])
    assert correct["evaluation"]["correct"]
    tutor.analyzer.analyze_message.assert_not_called()
    tutor.analyzer = Analyzer()
    changed = tutor.process_message("Explícame fracciones", correct["state"])
    assert changed["state"]["active_exercise_id"] is None
    assert changed["state"]["active_exercise_type"] is None
    assert not changed["state"]["awaiting_reflection"]
    assert tutor.process_message("Dame una pista", changed["state"])["type"] == "exercise_required"


def test_invalid_and_duplicate_answers_do_not_inflate_progress(tutor):
    start = tutor.process_message("ejercicio de fracciones")
    invalid = tutor.process_message("1/0", start["state"])
    assert invalid["evaluation"]["status"] == "invalid"
    assert invalid["state"]["progress_by_topic"]["mat_fracciones"]["total_attempts"] == 0
    correct = tutor.process_message("3/4", invalid["state"])
    duplicate = tutor.process_message("3/4", correct["state"])
    assert duplicate["state"]["progress_by_topic"] == correct["state"]["progress_by_topic"]
    stale = dict(correct["state"], active_exercise_id="frac_001", active_exercise_type="fraction")
    duplicate = tutor.process_message("3/4", stale)
    assert duplicate["type"] == "exercise_required"
    assert duplicate["state"]["progress_by_topic"] == correct["state"]["progress_by_topic"]
    assert start["state"]["completed_exercises"] == []


def test_selector_keeps_private_fields_out_and_scopes_ids(tutor):
    selector = tutor.selector
    exercise = selector.select("mat_fracciones", 1)
    assert set(exercise) == {"id", "question", "type", "difficulty"}
    exercise["question"] = "modified"
    assert selector.select("mat_fracciones", 1)["question"] != "modified"
    assert selector.select("mat_fracciones", 1, ["frac_001", "frac_002"]) is None
    with pytest.raises(KeyError):
        selector.get_expected_answer("esp_comprension", "frac_001")
    result = tutor.process_message("ejercicio de fracciones")
    def check_public(value):
        if isinstance(value, dict):
            assert not {"expected_answer", "hints", "correct_index"} & value.keys()
            for item in value.values():
                check_public(item)
        elif isinstance(value, list):
            for item in value:
                check_public(item)
    check_public(result)


def test_selector_rejects_unsupported_evaluation(tmp_path):
    import json
    data = {"topic_id": "x", "exercises": [{
        "id": "x1", "question": "Explain", "type": "open_text",
        "difficulty": 1, "expected_answer": "literal", "hints": [],
    }]}
    (tmp_path / "x.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="compatible"):
        ExerciseSelector(tmp_path)


def test_conversation_with_real_nlp(tutor):
    from gojarol_ml.nlp.analyzer import JarolAnalyzer

    tutor.analyzer = JarolAnalyzer(
        ROOT / "ml/artifacts/intent_classifier.joblib",
        ROOT / "ml/data/knowledge/topics.json",
    )
    result = tutor.process_message("Ponme un ejercicio de fracciones")
    result = tutor.process_message("6/8", result["state"])
    result = tutor.process_message("Otra", result["state"])
    assert result["exercise"]["id"] == "frac_002"
    result = tutor.process_message("3/5", result["state"])
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["exercise"]["id"] == "frac_003"
    result = tutor.process_message("No sé", result["state"])
    assert result["type"] == "hint"
    result = tutor.process_message("Otra", result["state"])
    assert result["state"]["hints_used"] == 2
    result = tutor.process_message("Ponme un ejercicio de comprensión lectora", result["state"])
    assert result["exercise"]["id"] == "esp_comp_001"
    result = tutor.process_message("Opción B", result["state"])
    assert result["evaluation"]["correct"]
    result = tutor.process_message("Solo llegué", result["state"])
    assert result["type"] == "reflection"


def test_spanish_adapts_from_first_level_through_maximum(tutor):
    from gojarol_ml.nlp.analyzer import JarolAnalyzer

    tutor.analyzer = JarolAnalyzer(
        ROOT / "ml/artifacts/intent_classifier.joblib",
        ROOT / "ml/data/knowledge/topics.json",
    )
    result = tutor.process_message("Ponme un ejercicio de comprensión lectora")
    sequence = [
        ("esp_comp_001", 1, "B"),
        ("esp_comp_004", 1, "Opción A"),
        ("esp_comp_002", 2, "La respuesta es A"),
        ("esp_comp_006", 2, "B"),
        ("esp_comp_003", 3, "Opción C"),
        ("esp_comp_008", 3, "La respuesta es A"),
        ("esp_comp_009", 3, "B"),
    ]
    for attempt, (exercise_id, difficulty, answer) in enumerate(sequence, 1):
        assert result["exercise"]["id"] == exercise_id
        assert result["exercise"]["difficulty"] == difficulty
        assert result["exercise"]["reading_text"] in result["message"]
        for label, text in result["exercise"]["options"].items():
            assert f"{label}) {text}" in result["message"]
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        progress = result["state"]["progress_by_topic"]["esp_comprension"]
        assert progress["total_attempts"] == attempt
        assert progress["difficulty"] == min(1 + attempt // 2, 3)
        if attempt in (2, 4):
            assert result["next_action"] == "increase_difficulty"
        if attempt == 6:
            assert result["next_action"] == "schedule_review"
        result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["type"] == "exercise_unavailable"
    assert len(result["state"]["completed_exercises"]) == 7


def test_spanish_assisted_success_keeps_level_then_two_distinct_successes_raise_it(tutor):
    result = tutor.process_message("ejercicio de comprensión lectora")
    first_hint = tutor.process_message("No sé", result["state"])
    assert first_hint["message"] == tutor.selector.get_hint("esp_comprension", "esp_comp_001", 0)
    result = tutor.process_message("Otra", first_hint["state"])
    assert result["message"] == tutor.selector.get_hint("esp_comprension", "esp_comp_001", 1)
    # Exhausting hints offers a strategy, without exposing the private rationale.
    result = tutor.process_message("Otra", result["state"])
    assert result["strategy"] == "alternative_explanation"
    result = tutor.process_message("B", result["state"])
    assert result["state"]["progress_by_topic"]["esp_comprension"]["difficulty"] == 1
    assert result["next_action"] == "practice_same_level"
    for exercise_id, answer in [("esp_comp_004", "A"), ("esp_comp_005", "C")]:
        result = tutor.process_message("Otro ejercicio", result["state"])
        assert result["exercise"]["id"] == exercise_id
        hint = tutor.selector.get_hint("esp_comprension", exercise_id, 0)
        assert hint != first_hint["message"]
        result = tutor.process_message(answer, result["state"])
    assert result["state"]["progress_by_topic"]["esp_comprension"]["difficulty"] == 2


def test_subject_round_trip_keeps_independent_progress_and_hints(tutor):
    result = tutor.process_message("ejercicio de comprensión lectora")
    result = tutor.process_message("B", result["state"])
    spanish_progress = result["state"]["progress_by_topic"]["esp_comprension"]
    result = tutor.process_message("Otro ejercicio", result["state"])
    result = tutor.process_message("Dame una pista", result["state"])
    result = tutor.process_message("ejercicio de fracciones", result["state"])
    assert result["state"]["hints_used"] == 0
    assert result["state"]["progress_by_topic"]["esp_comprension"] == spanish_progress
    result = tutor.process_message("No sé", result["state"])
    assert result["message"] == tutor.selector.get_hint("mat_fracciones", "frac_001", 0)
    result = tutor.process_message("3/4", result["state"])
    math_progress = result["state"]["progress_by_topic"]["mat_fracciones"]
    result = tutor.process_message("ejercicio de comprensión lectora", result["state"])
    assert result["exercise"]["id"] == "esp_comp_004"
    assert result["state"]["hints_used"] == 1
    result = tutor.process_message("No sé", result["state"])
    assert result["message"] == tutor.selector.get_hint("esp_comprension", "esp_comp_004", 1)
    result = tutor.process_message("A", result["state"])
    assert result["state"]["progress_by_topic"]["mat_fracciones"] == math_progress
    assert result["state"]["progress_by_topic"]["esp_comprension"]["total_attempts"] == 2
    assert result["state"]["progress_by_topic"]["esp_comprension"]["difficulty"] == 1


def test_switching_subjects_does_not_turn_assisted_success_into_unassisted(tutor):
    result = tutor.process_message("ejercicio de comprensión lectora")
    result = tutor.process_message("B", result["state"])
    result = tutor.process_message("Otro ejercicio", result["state"])
    result = tutor.process_message("No sé", result["state"])
    result = tutor.process_message("ejercicio de fracciones", result["state"])
    assert result["state"]["hints_used"] == 0
    result = tutor.process_message("ejercicio de comprensión lectora", result["state"])
    assert result["state"]["hints_used"] == 1
    result = tutor.process_message("A", result["state"])
    assert result["next_action"] == "practice_same_level"
    assert result["state"]["progress_by_topic"]["esp_comprension"]["difficulty"] == 1


@pytest.mark.parametrize("answer", ["B", "Opción B", "La respuesta es B"])
def test_spanish_answers_bypass_nlp_and_completed_activity_cannot_count_again(tutor, answer):
    start = tutor.process_message("ejercicio de comprensión lectora")
    tutor.analyzer = Mock()
    correct = tutor.process_message(answer, start["state"])
    assert correct["evaluation"]["correct"]
    stale = dict(correct["state"], active_exercise_id="esp_comp_001", active_exercise_type="multiple_choice")
    duplicate = tutor.process_message(answer, stale)
    assert duplicate["type"] == "exercise_required"
    assert duplicate["state"]["progress_by_topic"] == correct["state"]["progress_by_topic"]
    assert duplicate["state"]["completed_exercises"] == ["esp_comp_001"]
    tutor.analyzer.analyze_message.assert_not_called()


def test_spanish_conversation_responses_keep_evaluation_details_private(tutor):
    result = tutor.process_message("ejercicio de comprensión lectora")
    responses = [result]
    for message in ("No sé", "Otra", "Otra", "A", "La respuesta es B", "Otro ejercicio"):
        result = tutor.process_message(message, result["state"])
        responses.append(result)
    def assert_public(value):
        if isinstance(value, dict):
            assert not {"expected_answer", "answer_explanation", "correct_index", "hints"} & value.keys()
            for item in value.values():
                assert_public(item)
        elif isinstance(value, list):
            for item in value:
                assert_public(item)
    assert_public(responses)
