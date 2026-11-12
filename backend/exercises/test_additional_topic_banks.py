import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest

from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.exercise_evaluator import evaluate_exercise_answer
from exercises.services.exercise_selector import ExerciseSelector


CONTENT = Path(__file__).resolve().parents[2] / "content"
TOPICS = ("mat_porcentajes", "esp_acentuacion", "esp_ortografia")
BANKS = {topic: json.loads((CONTENT / "exercises" / f"{topic}.json").read_text(encoding="utf-8")) for topic in TOPICS}
ACTIVITIES = [item for bank in BANKS.values() for item in bank["exercises"]]
# Keys kept separate from the JSON; linguistic options reviewed against their rules/context.
LANGUAGE_KEYS = {"acent": "BCABCABCA", "orto": "ABCBCABCA"}
# Exact arithmetic checks the quantity requested, including changing percentage bases.
PERCENTAGE_RESULTS = [
    80 * Fraction(10, 100), Fraction(25, 100) * 100, Fraction(1, 4) * 100,
    240 * Fraction(80, 100), 200 * Fraction(115, 100), Fraction(18, 60) * 100,
    500 * Fraction(80, 100) * Fraction(90, 100),
    400 * Fraction(125, 100) * Fraction(80, 100), 360 / Fraction(90, 100),
]


@pytest.mark.parametrize("topic", TOPICS)
def test_topic_structure_diagnostics_and_three_exercises_per_level(topic):
    bank = BANKS[topic]
    assert bank["topic_id"] == topic
    assert Counter(item["difficulty"] for item in bank["exercises"]) == {1: 3, 2: 3, 3: 3}
    assert len({item["question"] for item in bank["exercises"]}) == 9
    knowledge = KnowledgeService(CONTENT / "topics")
    data = json.loads((CONTENT / "topics" / f"{topic}.json").read_text(encoding="utf-8"))
    assert data["curriculum"]["scope"]
    assert 0 <= data["diagnostic"]["correct_index"] < len(data["diagnostic"]["options"])
    assert data["exercise"] == bank["exercises"][0]
    for level in ("basic", "alternative"):
        assert knowledge.get_explanation(topic, level).strip()
    assert "correct_index" not in knowledge.get_public_diagnostic(topic)


def test_all_bank_ids_are_globally_unique():
    ids = [item["id"] for path in (CONTENT / "exercises").glob("*.json")
           for item in json.loads(path.read_text(encoding="utf-8"))["exercises"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("exercise", ACTIVITIES, ids=lambda item: item["id"])
def test_reviewed_answers_hints_and_public_boundary(exercise):
    assert exercise["competency"].strip()
    assert exercise["answer_explanation"].strip()
    assert len(set(exercise["hints"])) >= 2
    assert all(hint.strip() for hint in exercise["hints"])
    prefix, number = exercise["id"].rsplit("_", 1)
    if prefix == "pct":
        assert Fraction(exercise["expected_answer"]) == PERCENTAGE_RESULTS[int(number) - 1]
        assert exercise["type"] == ("percentage" if int(number) in {2, 3, 6} else "numeric")
        assert evaluate_exercise_answer(exercise["expected_answer"], exercise["expected_answer"], exercise["type"])["correct"]
    else:
        assert exercise["expected_answer"] == LANGUAGE_KEYS[prefix][int(number) - 1]
        for label in exercise["options"]:
            result = evaluate_exercise_answer(label, exercise["expected_answer"], exercise["type"])
            assert result["correct"] is (label == LANGUAGE_KEYS[prefix][int(number) - 1])
        assert sum(evaluate_exercise_answer(label, exercise["expected_answer"], exercise["type"])["correct"] for label in exercise["options"]) == 1
    topic = next(topic for topic, bank in BANKS.items() if exercise in bank["exercises"])
    public = ExerciseSelector(CONTENT / "exercises").get_public_exercise(topic, exercise["id"])
    assert not {"hints", "expected_answer", "answer_explanation"} & public.keys()
    assert set(public) <= {"id", "question", "difficulty", "type", "options", "competency"}


@pytest.mark.parametrize("answer", ["25", "25%", " 25 % ", "25.00%", "25,0", "+25%"])
def test_percentage_representations(answer):
    assert evaluate_exercise_answer(answer, "25", "percentage")["status"] == "correct"


@pytest.mark.parametrize("answer", ["12.5%", "12,5", "12.500"])
def test_decimal_percentage_uses_exact_arithmetic(answer):
    assert evaluate_exercise_answer(answer, "12.5", "percentage")["correct"]


@pytest.mark.parametrize("answer", ["", "25%%", "$25", "25 pesos", "x=25", "1/4", "25+0", "NaN", "Infinity", "1e2", "9" * 41, None])
def test_invalid_percentage_formats(answer):
    assert evaluate_exercise_answer(answer, "25", "percentage")["status"] == "invalid"


def test_percentage_is_not_a_quantity_or_a_ratio():
    assert evaluate_exercise_answer("25%", "25", "numeric")["status"] == "invalid"
    assert evaluate_exercise_answer("0.25", "25", "percentage")["status"] == "incorrect"
    assert evaluate_exercise_answer("12.500000000000000001%", "12.5", "percentage")["status"] == "incorrect"
    assert evaluate_exercise_answer("125%", "125", "percentage")["correct"]
    assert evaluate_exercise_answer("-5%", "-5", "percentage")["correct"]


def test_invalid_percentage_solution_fails_when_loading(tmp_path):
    data = json.loads(json.dumps(BANKS["mat_porcentajes"]))
    data["exercises"][1]["expected_answer"] = "NaN"
    (tmp_path / "bank.json").write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="esperada"):
        ExerciseSelector(tmp_path)
