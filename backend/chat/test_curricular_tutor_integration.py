from pathlib import Path

import pytest

from chat.services.tutor_service import TutorService
from curriculum.services.curriculum_catalog import CurriculumCatalog
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService
from gojarol_ml.nlp.analyzer import JarolAnalyzer
from gojarol_ml.nlp.curriculum_retriever import CurriculumRetriever


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def analyzer():
    return JarolAnalyzer(ROOT / "ml/artifacts/intent_classifier.joblib", ROOT / "ml/data/knowledge/topics.json",
                         curriculum_retriever=CurriculumRetriever(CurriculumCatalog().entries))


@pytest.fixture
def tutor(analyzer):
    knowledge = KnowledgeService(ROOT / "content/topics")
    return TutorService(analyzer, knowledge, HintService(knowledge))


def test_real_nlp_exposes_competency_and_maintains_intent(analyzer):
    result = analyzer.analyze_message("Ponme un ejercicio de ecuaciones", {"academic_context": {"level": "secundaria", "grade": 1}})
    assert result["intent"] == "solicitar_reto"
    assert result["curriculum"]["competency_id"] == "mx.sep.f6.2024.mat.g1.ecuaciones"
    assert result["topic"] == "mat_ecuaciones"


def test_secondary_curriculum_uses_existing_evaluation_hints_and_adaptation(tutor):
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", academic_context={"level": "secundaria", "grade": 1})
    assert result["exercise"]["id"] == "ecu_001"
    assert result["curriculum"]["content_available"] and not result["curriculum"]["validated"]
    assert "apoyo parcial" in result["message"]
    for answer, expected_id in [("x=7", "ecu_002"), ("x=-3", "ecu_004")]:
        result = tutor.process_message(answer, result["state"])
        assert result["evaluation"]["correct"]
        result = tutor.process_message("Ponme otro ejercicio", result["state"])
        assert result["exercise"]["id"] == expected_id
    result = tutor.process_message("No sé", result["state"])
    assert result["state"]["hints_used"] == 1


def test_bachillerato_reuses_assets_but_does_not_invent_a_semester_mapping(tutor):
    profile = {"level": "bachillerato", "model": "mccems_2025", "semester": 3}
    result = tutor.process_message("Explícame ecuaciones", academic_context=profile)
    assert result["type"] == "explanation_menu"  # Jarol pregunta antes de explicar.
    assert result["curriculum"]["competency_id"] == "mx.mccems.2025.pm.algebra"
    assert tutor.curriculum.get(result["curriculum"]["competency_id"])["semester"] is None
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", result["state"])
    assert result["exercise"]["id"] == "ecu_001"
    result = tutor.process_message("x=7", result["state"])
    assert result["evaluation"]["correct"]
    reading = tutor.process_message("Ponme un ejercicio de comprensión lectora", result["state"])
    assert reading["exercise"]["id"] == "esp_comp_001"
    assert reading["state"]["progress_by_topic"]["mat_ecuaciones"]["total_attempts"] == 1


@pytest.mark.parametrize("profile,message,expected", [
    ({"level": "secundaria", "grade": 3}, "Explícame ecuaciones cuadráticas", "mx.sep.f6.2024.mat.g3.cuadraticas"),
    ({"level": "secundaria", "grade": 2}, "Ponme un ejercicio de sistemas de ecuaciones", "mx.sep.f6.2024.mat.g2.sistemas"),
    ({"level": "bachillerato", "model": "mccems_2026"}, "Explícame porcentajes", None),
    ({"level": "bachillerato", "program_id": "cosac_2025", "semester": 1}, "Explícame vínculos entre lectura y escritura", "mx.cosac.2025.lyc.s1.pf1"),
])
def test_cataloged_or_unverified_topics_do_not_fabricate_instruction(tutor, profile, message, expected):
    result = tutor.process_message(message, academic_context=profile)
    assert result["type"] == "curriculum_unavailable"
    assert result["state"]["current_competency_id"] == expected
    assert "exercise" not in result
    if expected:
        assert not result["curriculum"]["content_available"]


def test_ambiguity_requests_context_and_selection_resolves_it(tutor):
    result = tutor.process_message("Compara fracciones y porcentajes", academic_context={"level": "secundaria", "grade": 1})
    assert result["type"] == "curriculum_clarification"
    assert len(result["candidates"]) == 2
    result = tutor.process_message("Explícame fracciones", result["state"], academic_context={"level": "secundaria", "grade": 1})
    assert result["type"] == "explanation_menu"  # Jarol pregunta antes de explicar.
    assert result["curriculum"]["competency_id"] == "mx.sep.f6.2024.mat.g1.operaciones"


def test_profile_change_clears_active_exercise_but_keeps_topic_progress(tutor):
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", academic_context={"level": "secundaria", "grade": 1})
    result = tutor.process_message("x=7", result["state"])
    result = tutor.process_message("Ponme otro ejercicio", result["state"])
    result = tutor.process_message("No sé", result["state"])
    changed = tutor.process_message("Explícame ecuaciones cuadráticas", result["state"], academic_context={"level": "secundaria", "grade": 3})
    assert changed["type"] == "curriculum_unavailable"
    assert changed["state"]["active_exercise_id"] is None
    assert changed["state"]["hints_used"] == 0
    assert changed["state"]["progress_by_topic"] == result["state"]["progress_by_topic"]
    restored = tutor.process_message("Ponme un ejercicio de ecuaciones", changed["state"], academic_context={"level": "secundaria", "grade": 1})
    assert restored["exercise"]["id"] == "ecu_002"
    assert restored["state"]["hints_used"] == 1


def test_out_of_grade_topic_does_not_retain_previous_exercise_or_hints(tutor):
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", academic_context={"level": "secundaria", "grade": 1})
    result = tutor.process_message("No sé", result["state"])
    result = tutor.process_message("Explícame ecuaciones cuadráticas", result["state"])
    assert result["type"] == "curriculum_unavailable"
    assert result["state"]["current_topic"] == "mat_cuadraticas"
    assert result["state"]["active_exercise_id"] is None
    assert tutor.process_message("Dame una pista", result["state"])["type"] != "hint"


@pytest.mark.parametrize("profile", [{"level": "secundaria", "grade": True}, {"level": "secundaria", "semester": 1}, {"level": "bachillerato", "grade": 2}, {"grade": 4}, {"levle": "secundaria"}, {"level": []}])
def test_invalid_academic_context_is_rejected(tutor, profile):
    with pytest.raises(ValueError):
        tutor.process_message("Explícame ecuaciones", academic_context=profile)


def test_curricular_responses_do_not_expose_private_answers(tutor):
    result = tutor.process_message("Ponme un ejercicio de ecuaciones", academic_context={"level": "secundaria", "grade": 1})
    results = [result]
    for message in ("8", "No sé", "x=7", "Ponme otro ejercicio"):
        result = tutor.process_message(message, result["state"])
        results.append(result)
    def check(value):
        if isinstance(value, dict):
            assert not {"expected_answer", "solution_steps", "hints", "correct_index"} & value.keys()
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(results)
