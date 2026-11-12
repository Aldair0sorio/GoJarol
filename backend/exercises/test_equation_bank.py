import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest

from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.exercise_evaluator import parse_integer_answer
from exercises.services.exercise_selector import ExerciseSelector


CONTENT = Path(__file__).resolve().parents[2] / "content"
BANK = json.loads((CONTENT / "exercises/mat_ecuaciones.json").read_text(encoding="utf-8"))
# Independent coefficients a, b, c and prompt for each equation ax + b = c.
EQUATIONS = {
    "ecu_001": (1, 5, 12, "x + 5 = 12"),
    "ecu_002": (1, -4, -7, "x - 4 = -7"),
    "ecu_003": (1, 6, 6, "x + 6 = 6"),
    "ecu_004": (3, 0, 18, "3x = 18"),
    "ecu_005": (Fraction(1, 4), 0, -2, "x/4 = -2"),
    "ecu_006": (-5, 0, 20, "-5x = 20"),
    "ecu_007": (2, 5, 17, "2x + 5 = 17"),
    "ecu_008": (4, -3, -23, "4x - 3 = -23"),
    "ecu_009": (Fraction(1, 3), 2, 5, "x/3 + 2 = 5"),
}


def test_nine_equations_three_per_difficulty_and_unique_ids():
    exercises = BANK["exercises"]
    assert Counter(item["difficulty"] for item in exercises) == {1: 3, 2: 3, 3: 3}
    assert {item["id"] for item in exercises} == EQUATIONS.keys()
    assert len({item["question"] for item in exercises}) == 9
    ids = [item["id"] for path in (CONTENT / "exercises").glob("*.json")
           for item in json.loads(path.read_text(encoding="utf-8"))["exercises"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("exercise", BANK["exercises"], ids=lambda item: item["id"])
def test_equation_solutions_by_exact_substitution(exercise):
    a, b, c, equation = EQUATIONS[exercise["id"]]
    solution = parse_integer_answer(exercise["expected_answer"])
    assert solution is not None
    assert a != 0
    assert a * solution + b == c
    assert equation in exercise["question"]
    assert exercise["type"] == "numeric"
    assert exercise["competency"] == {
        1: "despejar_suma_resta", 2: "despejar_producto_cociente", 3: "despejar_dos_operaciones",
    }[exercise["difficulty"]]
    assert len(exercise["solution_steps"]) >= 3
    assert len(set(exercise["hints"])) >= 3
    assert not any("x = " + exercise["expected_answer"] in hint for hint in exercise["hints"])
    public = ExerciseSelector(CONTENT / "exercises").get_public_exercise("mat_ecuaciones", exercise["id"])
    assert set(public) == {"id", "question", "difficulty", "type", "competency"}


def test_equation_topic_is_loadable_and_legacy_exercise_matches_bank():
    service = KnowledgeService(CONTENT / "topics")
    assert any(topic["id"] == "mat_ecuaciones" for topic in service.list_topics())
    for level in ("basic", "intermediate", "alternative"):
        assert service.get_explanation("mat_ecuaciones", level).strip()
    first = BANK["exercises"][0]
    assert service.get_expected_answer("mat_ecuaciones") == first["expected_answer"]
    assert service.get_public_exercise("mat_ecuaciones")["question"] == first["question"]
    for index, hint in enumerate(first["hints"]):
        assert service.get_hint("mat_ecuaciones", index) == hint
    assert "correct_index" not in service.get_public_diagnostic("mat_ecuaciones")
