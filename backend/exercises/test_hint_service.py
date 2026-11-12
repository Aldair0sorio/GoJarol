
from pathlib import Path

import pytest

from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService


ROOT_DIR = Path(__file__).resolve().parents[2]
CONTENT_DIR = ROOT_DIR / "content" / "topics"


@pytest.fixture
def service():
    knowledge = KnowledgeService(CONTENT_DIR)
    return HintService(knowledge)


def test_first_hint(service):
    result = service.get_next_hint("mat_fracciones", 0)

    assert result["strategy"] == "guided_hint"
    assert result["hints_used"] == 1
    assert result["requires_review"] is False


def test_second_hint(service):
    result = service.get_next_hint("mat_fracciones", 1)

    assert result["strategy"] == "guided_hint"
    assert result["hints_used"] == 2


def test_third_hint(service):
    result = service.get_next_hint("mat_fracciones", 2)

    assert result["strategy"] == "guided_hint"
    assert result["hints_used"] == 3


def test_unlimited_hints(service):
    for index in range(3, 20):
        result = service.get_next_hint("mat_fracciones", index)

        assert isinstance(result["message"], str)
        assert result["message"]
        assert result["hints_used"] == index + 1
        assert result["requires_review"] is True


def test_answer_not_exposed(service):
    for index in range(10):
        result = service.get_next_hint("mat_fracciones", index)

        assert "expected_answer" not in result
        assert "3/4" not in result["message"]


def test_negative_counter(service):
    with pytest.raises(ValueError):
        service.get_next_hint("mat_fracciones", -1)


def test_unknown_topic(service):
    with pytest.raises(KeyError):
        service.get_next_hint("tema_inexistente", 0)


def test_exhausted_hints_do_not_reuse_worked_examples(service):
    service.knowledge.get_explanation = lambda *args: 'La solución privada es 3/4.'
    for index in range(3,15):
        result=service.get_next_hint('mat_fracciones',index)
        assert '3/4' not in result['message']
        assert result['hints_used']==index+1
        assert result['requires_review']


def test_fraction_bank_fallbacks_do_not_include_solved_operations():
    from exercises.services.exercise_selector import ExerciseSelector
    selector=ExerciseSelector(ROOT_DIR/'content/exercises')
    hints=HintService(KnowledgeService(CONTENT_DIR),selector)
    for exercise in selector.list_public_exercises('mat_fracciones'):
        for index in range(3,12):
            result=hints.get_next_hint('mat_fracciones',index,exercise_id=exercise['id'])
            assert '=' not in result['message']
            assert selector.get_expected_answer('mat_fracciones',exercise['id']) not in result['message']
            assert 'expected_answer' not in result
