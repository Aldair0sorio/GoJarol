"""Select public activities while keeping solutions and hints server-side."""

import json
from copy import deepcopy
from pathlib import Path

from exercises.services.exercise_evaluator import evaluate_exercise_answer


class ExerciseSelector:
    def __init__(self, content_dir: str | Path):
        directory = Path(content_dir)
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        self._exercises = {}
        ids = set()
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            topic_id = data["topic_id"]
            if topic_id in self._exercises:
                raise ValueError(f"Tema duplicado: {topic_id}")
            exercises = {}
            for exercise in data["exercises"]:
                exercise_id = exercise["id"]
                if not isinstance(exercise_id, str) or not exercise_id or exercise_id in ids:
                    raise ValueError("ID de ejercicio invalido o duplicado.")
                if type(exercise["difficulty"]) is not int or exercise["difficulty"] not in {1, 2, 3}:
                    raise ValueError("Dificultad invalida.")
                if not isinstance(exercise["question"], str) or not exercise["question"].strip():
                    raise ValueError("Pregunta invalida.")
                if not isinstance(exercise["hints"], list) or not all(
                    isinstance(hint, str) and hint.strip() for hint in exercise["hints"]
                ):
                    raise ValueError("Pistas invalidas.")
                evaluate_exercise_answer("", exercise["expected_answer"], exercise["type"])
                if exercise["type"] == "multiple_choice":
                    options = exercise.get("options")
                    if (
                        not isinstance(options, dict)
                        or not 2 <= len(options) <= 4
                        or not set(options) <= {"A", "B", "C", "D"}
                        or not all(isinstance(text, str) and text.strip() for text in options.values())
                        or len({text.strip().casefold() for text in options.values()}) != len(options)
                        or exercise["expected_answer"] not in options
                    ):
                        raise ValueError("Opciones o respuesta del ejercicio invalidas.")
                ids.add(exercise_id)
                exercises[exercise_id] = exercise
            self._exercises[topic_id] = exercises

    def get_public_exercise(self, topic_id: str, exercise_id: str) -> dict:
        exercise = self._exercises[topic_id][exercise_id]
        return deepcopy({key: exercise[key] for key in (
            "id", "question", "difficulty", "type", "options", "reading_text", "competency"
        ) if key in exercise})

    def list_public_exercises(self, topic_id: str, competencies=None) -> list[dict]:
        return [self.get_public_exercise(topic_id, exercise["id"])
                for exercise in self._exercises.get(topic_id, {}).values()
                if competencies is None or exercise.get("competency") in competencies]

    def select(self, topic_id: str, difficulty: int, excluded_ids=(), competencies=None) -> dict | None:
        excluded = set(excluded_ids)
        for exercise in self._exercises.get(topic_id, {}).values():
            if (exercise["difficulty"] == difficulty and exercise["id"] not in excluded
                    and (competencies is None or exercise.get("competency") in competencies)):
                return self.get_public_exercise(topic_id, exercise["id"])
        return None

    def get_expected_answer(self, topic_id: str, exercise_id: str) -> str:
        return self._exercises[topic_id][exercise_id]["expected_answer"]

    def get_hint(self, topic_id: str, exercise_id: str, index: int) -> str | None:
        if index < 0:
            raise ValueError("Indice invalido.")
        hints = self._exercises[topic_id][exercise_id]["hints"]
        return hints[index] if index < len(hints) else None
