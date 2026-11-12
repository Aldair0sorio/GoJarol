
class AdaptiveLearningService:
    MIN_DIFFICULTY = 1
    MAX_DIFFICULTY = 3
    REQUIRED_CORRECT = 2
    MAX_CONSECUTIVE_ERRORS = 2

    @staticmethod
    def initial_state() -> dict:
        return {
            "difficulty": 1,
            "consecutive_errors": 0,
            "unassisted_correct_ids": [],
            "total_attempts": 0,
        }

    def update_progress(
        self,
        progress: dict,
        exercise_id: str,
        evaluation: dict,
        hints_used: int = 0,
    ) -> dict:

        if not exercise_id:
            raise ValueError("El ejercicio necesita un ID.")

        if hints_used < 0:
            raise ValueError("El numero de pistas es invalido.")

        status = evaluation.get("status")

        if status not in {"correct", "incorrect", "invalid"}:
            raise ValueError("Estado de evaluacion desconocido.")

        state = {
            **self.initial_state(),
            **progress,
        }

        state["unassisted_correct_ids"] = list(
            state["unassisted_correct_ids"]
        )

        difficulty = state["difficulty"]

        if not self.MIN_DIFFICULTY <= difficulty <= self.MAX_DIFFICULTY:
            raise ValueError("Dificultad fuera del rango permitido.")

        # Una respuesta no interpretable no modifica el progreso.
        if status == "invalid":
            return {
                "progress": state,
                "next_action": "clarify_answer",
                "reason": "El estudiante debe corregir el formato.",
            }

        state["total_attempts"] += 1

        if status == "correct":
            state["consecutive_errors"] = 0

            if hints_used > 0:
                state["unassisted_correct_ids"] = []

                return {
                    "progress": state,
                    "next_action": "practice_same_level",
                    "reason": "Respuesta correcta con ayuda.",
                }

            completed = state["unassisted_correct_ids"]

            if exercise_id not in completed:
                completed.append(exercise_id)

            if len(completed) < self.REQUIRED_CORRECT:
                return {
                    "progress": state,
                    "next_action": "practice_same_level",
                    "reason": "Falta comprobar con otro ejercicio.",
                }

            state["unassisted_correct_ids"] = []

            if difficulty < self.MAX_DIFFICULTY:
                state["difficulty"] += 1

                return {
                    "progress": state,
                    "next_action": "increase_difficulty",
                    "reason": "Dos ejercicios distintos sin ayuda.",
                }

            return {
                "progress": state,
                "next_action": "schedule_review",
                "reason": "Buen desempeño en dificultad maxima.",
            }

        # Respuesta incorrecta
        state["consecutive_errors"] += 1
        state["unassisted_correct_ids"] = []

        if (
            state["consecutive_errors"]
            >= self.MAX_CONSECUTIVE_ERRORS
        ):
            state["difficulty"] = max(
                self.MIN_DIFFICULTY,
                difficulty - 1,
            )
            state["consecutive_errors"] = 0

            return {
                "progress": state,
                "next_action": "reinforce_basics",
                "reason": "Se detectaron dificultades repetidas.",
            }

        return {
            "progress": state,
            "next_action": "offer_hint",
            "reason": "Se necesita ayuda con el ejercicio.",
        }
