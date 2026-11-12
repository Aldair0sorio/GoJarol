"""Content contract and private/public boundaries for the reviewed pilot bank."""

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from exercises.services.exercise_evaluator import evaluate_exercise_answer
from exercises.services.exercise_selector import ExerciseSelector


CONTENT = Path(__file__).resolve().parents[2] / "content/exercises"
BANK = json.loads((CONTENT / "esp_comprension.json").read_text(encoding="utf-8"))
EXERCISES = BANK["exercises"]
# Review key kept separate from the bank: do not derive it from expected_answer.
REVIEWED_KEY = {
    "esp_comp_001": "B", "esp_comp_004": "A", "esp_comp_005": "C",
    "esp_comp_002": "A", "esp_comp_006": "B", "esp_comp_007": "C",
    "esp_comp_003": "C", "esp_comp_008": "A", "esp_comp_009": "B",
}


def test_bank_has_distinct_readings_and_three_activities_per_level():
    counts = Counter(exercise["difficulty"] for exercise in EXERCISES)
    assert set(counts) == {1, 2, 3}
    assert all(counts[level] >= 3 for level in (1, 2, 3))
    assert len({item["id"] for item in EXERCISES}) == len(EXERCISES)
    assert len({item["reading_text"] for item in EXERCISES}) == len(EXERCISES)
    all_ids = [
        item["id"] for path in CONTENT.glob("*.json")
        for item in json.loads(path.read_text(encoding="utf-8"))["exercises"]
    ]
    assert len(all_ids) == len(set(all_ids))


@pytest.mark.parametrize("exercise", EXERCISES, ids=lambda item: item["id"])
def test_reading_content_and_all_options(exercise):
    expected_competency = {
        1: "identificar_informacion_explicita",
        2: "identificar_idea_principal",
        3: "inferir_con_evidencia",
    }
    assert exercise["competency"] == expected_competency[exercise["difficulty"]]
    assert exercise["reading_text"].strip() and exercise["question"].strip()
    assert exercise["expected_answer"] == REVIEWED_KEY[exercise["id"]]
    assert exercise["answer_explanation"].strip()
    assert len(exercise["hints"]) >= 2
    assert len(set(exercise["hints"])) == len(exercise["hints"])
    for label, text in exercise["options"].items():
        result = evaluate_exercise_answer(label, exercise["expected_answer"], "multiple_choice")
        assert result["correct"] is (label == REVIEWED_KEY[exercise["id"]])
        assert result["status"] == ("correct" if result["correct"] else "incorrect")
        assert all(text.casefold() not in hint.casefold() for hint in exercise["hints"])


@pytest.mark.parametrize("exercise", EXERCISES, ids=lambda item: item["id"])
def test_public_readings_never_include_private_evaluation_data(exercise):
    selector = ExerciseSelector(CONTENT)
    public = selector.get_public_exercise("esp_comprension", exercise["id"])
    assert set(public) == {
        "id", "type", "difficulty", "competency", "reading_text", "question", "options",
    }
    assert public["options"] == exercise["options"]
    assert public["reading_text"] == exercise["reading_text"]
    public["options"]["A"] = "changed"
    assert selector.get_public_exercise("esp_comprension", exercise["id"])["options"] == exercise["options"]


@pytest.mark.parametrize("across_topics", [False, True])
def test_duplicate_ids_are_rejected(tmp_path, across_topics):
    bank = deepcopy(BANK)
    bank["exercises"] = [bank["exercises"][0]]
    if across_topics:
        other = deepcopy(bank)
        other["topic_id"] = "other_topic"
        (tmp_path / "other.json").write_text(json.dumps(other), encoding="utf-8")
    else:
        bank["exercises"].append(deepcopy(bank["exercises"][0]))
    (tmp_path / "reading.json").write_text(json.dumps(bank), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicado"):
        ExerciseSelector(tmp_path)


@pytest.mark.parametrize("options", [
    {"A": "First", "C": "Third"},  # The correct B is missing.
    {"A": "Same", "B": " same "},
    {"A": "First", "B": ""},
])
def test_invalid_options_fail_at_load_time(tmp_path, options):
    bank = deepcopy(BANK)
    bank["exercises"] = [bank["exercises"][0]]
    bank["exercises"][0]["options"] = options
    (tmp_path / "reading.json").write_text(json.dumps(bank), encoding="utf-8")
    with pytest.raises(ValueError, match="Opciones"):
        ExerciseSelector(tmp_path)
