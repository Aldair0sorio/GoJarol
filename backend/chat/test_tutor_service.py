
from pathlib import Path

import pytest

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService


ROOT_DIR = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT_DIR / "content" / "topics"


class FakeAnalyzer:
    def analyze_message(self, message, context=None):
        text = message.lower()

        if "ejercicio" in text:
            intent = "solicitar_reto"
        elif "pista" in text:
            intent = "solicitar_pista"
        else:
            intent = "solicitar_explicacion"

        topic = (
            "mat_fracciones"
            if "fracciones" in text
            else (context or {}).get("current_topic")
        )

        return {
            "intent": intent,
            "topic": topic,
            "needs_clarification": False,
        }


@pytest.fixture
def tutor():
    knowledge = KnowledgeService(CONTENT_DIR)

    return TutorService(
        analyzer=FakeAnalyzer(),
        knowledge=knowledge,
        hints=HintService(knowledge),
    )


def start_exercise(tutor):
    return tutor.process_message(
        "Ponme un ejercicio de fracciones"
    )


def test_explanation(tutor):
    result = tutor.process_message("Explícame las fracciones")

    assert result["type"] == "explanation"
    assert result["state"]["current_topic"] == "mat_fracciones"


def test_exercise(tutor):
    result = start_exercise(tutor)

    assert result["type"] == "exercise"
    assert result["exercise"]["id"] == "frac_001"
    assert "expected_answer" not in result["exercise"]


def test_correct_answer(tutor):
    start = start_exercise(tutor)

    result = tutor.process_message(
        "6/8",
        start["state"],
    )

    assert result["evaluation"]["correct"] is True
    assert result["state"]["active_exercise_id"] is None
    assert (
        result["state"]["progress_by_topic"]
        ["mat_fracciones"]["total_attempts"]
        == 1
    )


def test_hints(tutor):
    start = start_exercise(tutor)

    first = tutor.process_message(
        "Dame una pista",
        start["state"],
    )

    second = tutor.process_message(
        "Dame una pista",
        first["state"],
    )

    assert first["type"] == "hint"
    assert second["state"]["hints_used"] == 2


def test_incorrect_answer(tutor):
    start = start_exercise(tutor)

    result = tutor.process_message(
        "3/8",
        start["state"],
    )

    assert result["evaluation"]["correct"] is False
    assert result["state"]["active_exercise_id"] == "frac_001"


def test_cannot_repeat_completed_exercise(tutor):
    start = start_exercise(tutor)
    correct = tutor.process_message("3/4", start["state"])

    repeat = tutor.process_message(
        "Ponme un ejercicio",
        correct["state"],
    )

    assert repeat["type"] == "exercise"
    assert repeat["exercise"]["id"] == "frac_002"


def test_topic_required(tutor):
    result = tutor.process_message("Explícame algo")

    assert result["type"] == "topic_required"


def test_dont_know_during_exercise(tutor):
    start = start_exercise(tutor)

    result = tutor.process_message(
        "La verdad no sé",
        start["state"],
    )

    assert result["type"] == "hint"
    assert result["state"]["hints_used"] == 1


def test_another_hint_with_short_message(tutor):
    start = start_exercise(tutor)

    first = tutor.process_message(
        "Dame una pista",
        start["state"],
    )

    second = tutor.process_message(
        "¿Otra?",
        first["state"],
    )

    assert second["type"] == "hint"
    assert second["state"]["hints_used"] == 2
    assert first["message"] != second["message"]


def test_reflection_after_correct_answer(tutor):
    start = start_exercise(tutor)

    correct = tutor.process_message(
        "6/8",
        start["state"],
    )

    assert correct["state"]["awaiting_reflection"] is True

    reflection = tutor.process_message(
        "Solo llegué",
        correct["state"],
    )

    assert reflection["type"] == "reflection"
    assert reflection["state"]["awaiting_reflection"] is False


def test_new_request_after_correct_answer(tutor):
    start = start_exercise(tutor)

    correct = tutor.process_message(
        "3/4",
        start["state"],
    )

    result = tutor.process_message(
        "Ponme un ejercicio",
        correct["state"],
    )

    assert result["type"] == "exercise"
    assert result["exercise"]["id"] == "frac_002"
