
from pathlib import Path

import pytest

from curriculum.services.knowledge_service import KnowledgeService


ROOT_DIR = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT_DIR / "content" / "topics"


@pytest.fixture
def service():
    return KnowledgeService(CONTENT_DIR)


def test_load_topics(service):
    topics = service.list_topics()

    assert any(t["id"] == "mat_fracciones" for t in topics)


def test_explanation(service):
    explanation = service.get_explanation("mat_fracciones")

    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_exercise_does_not_expose_answer(service):
    exercise = service.get_public_exercise("mat_fracciones")

    assert exercise["id"] == "frac_001"
    assert "expected_answer" not in exercise


def test_diagnostic_does_not_expose_answer(service):
    diagnostic = service.get_public_diagnostic("mat_fracciones")

    assert "correct_index" not in diagnostic


def test_hint(service):
    hint = service.get_hint("mat_fracciones", 0)

    assert isinstance(hint, str)
    assert len(hint) > 0


def test_unknown_topic(service):
    with pytest.raises(KeyError):
        service.get_public_exercise("tema_inexistente")
