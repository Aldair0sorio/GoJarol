from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pytest

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService
from gojarol_ml.nlp.analyzer import JarolAnalyzer


ROOT = Path(__file__).resolve().parents[2]
NEW_TOPICS = [
    ("mat_porcentajes", "porcentajes", "pct", ["8", "25%", "192", "230", "360", "400", "400"]),
    ("esp_acentuacion", "acentuación", "acent", ["B", "Opción C", "B", "La respuesta es C", "B", "C", "A"]),
    ("esp_ortografia", "ortografía", "orto", ["A", "Opción B", "B", "La respuesta es C", "B", "C", "A"]),
]


@pytest.fixture(scope="module")
def analyzer():
    return JarolAnalyzer(ROOT / "ml/artifacts/intent_classifier.joblib", ROOT / "ml/data/knowledge/topics.json")


@pytest.fixture
def tutor(analyzer):
    knowledge = KnowledgeService(ROOT / "content/topics")
    return TutorService(analyzer, knowledge, HintService(knowledge))


@pytest.mark.parametrize("topic,name,prefix,answers", NEW_TOPICS)
def test_new_topics_explain_and_adapt_with_real_nlp(tutor, topic, name, prefix, answers):
    explanation = tutor.process_message(f"Explícame {name}")
    assert explanation["type"] == "explanation"
    assert explanation["state"]["current_topic"] == topic
    result = tutor.process_message(f"Ponme un ejercicio de {name}", explanation["state"])
    for attempt, (number, answer) in enumerate(zip([1, 2, 4, 5, 7, 8, 9], answers), 1):
        assert result["exercise"]["id"] == f"{prefix}_{number:03}"
        assert result["exercise"]["difficulty"] == min((attempt + 1) // 2, 3)
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        progress = result["state"]["progress_by_topic"][topic]
        assert progress["difficulty"] == min(1 + attempt // 2, 3)
        assert progress["total_attempts"] == attempt
        if attempt in {2, 4}:
            assert result["next_action"] == "increase_difficulty"
        result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["type"] == "exercise_unavailable"
    assert len(result["state"]["completed_exercises"]) == 7


@pytest.mark.parametrize("topic,name,prefix,answers", NEW_TOPICS)
def test_new_topic_hints_preserve_level_and_completed_ids_do_not_count_twice(tutor, topic, name, prefix, answers):
    result = tutor.process_message(f"Ponme un ejercicio de {name}")
    result = tutor.process_message(answers[0], result["state"])
    first_complete = deepcopy(result["state"])
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    result = tutor.process_message("No sé", result["state"])
    assert result["message"] == tutor.selector.get_hint(topic, f"{prefix}_002", 0)
    result = tutor.process_message("Otra", result["state"])
    assert result["message"] == tutor.selector.get_hint(topic, f"{prefix}_002", 1)
    result = tutor.process_message("Otra", result["state"])
    assert result["strategy"] == "alternative_explanation"
    result = tutor.process_message(answers[1], result["state"])
    assert result["next_action"] == "practice_same_level"
    assert result["state"]["progress_by_topic"][topic]["difficulty"] == 1
    next_exercise = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert next_exercise["exercise"]["id"] == f"{prefix}_003"
    stale = dict(first_complete, active_exercise_id=f"{prefix}_001")
    duplicate = tutor.process_message(answers[0], stale)
    assert duplicate["type"] == "exercise_required"
    assert duplicate["state"]["progress_by_topic"] == first_complete["progress_by_topic"]


def test_percentages_bypass_nlp_and_quantity_rejects_percent_sign(tutor, analyzer):
    start = tutor.process_message("Ponme un ejercicio de porcentajes")
    tutor.analyzer = Mock()
    invalid = tutor.process_message("8%", start["state"])
    assert invalid["evaluation"]["status"] == "invalid"
    assert invalid["state"]["progress_by_topic"]["mat_porcentajes"]["total_attempts"] == 0
    result = tutor.process_message("8", invalid["state"])
    tutor.analyzer.analyze_message.assert_not_called()
    tutor.analyzer = analyzer
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    assert result["exercise"]["id"] == "pct_002"
    tutor.analyzer = Mock()
    result = tutor.process_message("25%", result["state"])
    assert result["evaluation"]["correct"]
    tutor.analyzer.analyze_message.assert_not_called()


def test_six_topics_keep_progress_and_hints_separate(tutor):
    topics = [
        ("mat_fracciones", "fracciones", "frac_001", "6/8"),
        ("mat_ecuaciones", "ecuaciones", "ecu_001", "x=7"),
        ("esp_comprension", "comprensión lectora", "esp_comp_001", "B"),
        ("mat_porcentajes", "porcentajes", "pct_001", "8"),
        ("esp_acentuacion", "acentuación", "acent_001", "B"),
        ("esp_ortografia", "ortografía", "orto_001", "A"),
    ]
    state = None
    progress = {}
    for topic, name, exercise_id, answer in topics:
        result = tutor.process_message(f"Ponme un ejercicio de {name}", state)
        assert result["exercise"]["id"] == exercise_id
        assert result["state"]["hints_used"] == 0
        result = tutor.process_message("Dame una pista", result["state"])
        assert result["message"] == tutor.selector.get_hint(topic, exercise_id, 0)
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        progress[topic] = deepcopy(result["state"]["progress_by_topic"][topic])
        assert result["state"]["progress_by_topic"] == progress
        state = result["state"]
    for topic, name, exercise_id, answer in reversed(topics):
        result = tutor.process_message(f"Ponme un ejercicio de {name}", state)
        assert result["exercise"]["id"] != exercise_id
        assert result["state"]["hints_used"] == 0
        assert result["state"]["progress_by_topic"] == progress
        state = result["state"]


@pytest.mark.parametrize("topic,name,prefix,answers", NEW_TOPICS)
def test_conversations_never_expose_internal_solutions(tutor, topic, name, prefix, answers):
    result = tutor.process_message(f"Ponme un ejercicio de {name}")
    responses = [result]
    wrong = "9" if topic == "mat_porcentajes" else ("A" if answers[0] != "A" else "B")
    for message in [wrong, "No sé", "Otra", "Otra", answers[0], "Ponme otro ejercicio"]:
        result = tutor.process_message(message, result["state"])
        responses.append(result)
    def check(value):
        if isinstance(value, dict):
            assert not {"expected_answer", "answer_explanation", "solution_steps", "correct_index", "hints"} & value.keys()
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(responses)
