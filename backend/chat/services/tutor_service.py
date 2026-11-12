
import re
from copy import deepcopy

from exercises.services.exercise_evaluator import (
    evaluate_fraction_answer,
)
from progress.services.adaptive_learning_service import (
    AdaptiveLearningService,
)


ANSWER_PATTERN = re.compile(
    r"^\s*(?:(?:mi|la)\s+respuesta\s+es\s*|"
    r"respuesta\s*[:=]\s*)?"
    r"([+-]?\d+(?:\s*/\s*[+-]?\d+)?)\s*[.!]?\s*$",
    re.IGNORECASE,
)


class TutorService:
    def __init__(self, analyzer, knowledge, hints, adaptive=None):
        self.analyzer = analyzer
        self.knowledge = knowledge
        self.hints = hints
        self.adaptive = adaptive or AdaptiveLearningService()

        self.available_topics = {
            topic["id"] for topic in knowledge.list_topics()
        }

    @staticmethod
    def initial_state():
        return {
            "current_topic": None,
            "active_exercise_id": None,
            "hints_used": 0,
            "completed_exercises": [],
            "progress_by_topic": {},
        }

    @staticmethod
    def _response(message, state, response_type, **extra):
        return {
            "type": response_type,
            "message": message,
            "state": state,
            **extra,
        }

    def process_message(self, message, state=None):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("El mensaje no puede estar vacio.")

        state = deepcopy(
            self.initial_state() if state is None else state
        )

        # Si hay un ejercicio activo, primero detectamos respuestas.
        answer_match = ANSWER_PATTERN.fullmatch(message)

        if answer_match and state["active_exercise_id"]:
            return self._evaluate_answer(
                answer_match.group(1),
                state,
            )

        analysis = self.analyzer.analyze_message(
            message,
            {"current_topic": state["current_topic"]},
        )

        intent = analysis.get("intent")
        detected_topic = analysis.get("topic")

        if analysis.get("needs_clarification"):
            return self._response(
                "¿Sobre qué tema necesitas ayuda?",
                state,
                "clarification",
            )

        if detected_topic and detected_topic not in self.available_topics:
            return self._response(
                "Reconozco ese tema, pero todavía no tengo "
                "contenido educativo disponible para explicarlo.",
                state,
                "unavailable_topic",
            )

        if detected_topic and detected_topic != state["current_topic"]:
            state["current_topic"] = detected_topic
            state["active_exercise_id"] = None
            state["hints_used"] = 0

        if intent == "saludar":
            return self._response(
                "¡Hola! Soy Jarol. ¿Qué te gustaría aprender?",
                state,
                "greeting",
            )

        if intent == "despedirse":
            return self._response(
                "¡Hasta pronto! Seguiremos aprendiendo.",
                state,
                "farewell",
            )

        topic_id = state["current_topic"]

        if intent == "consultar_progreso":
            progress = state["progress_by_topic"].get(
                topic_id,
                self.adaptive.initial_state(),
            )
            return self._response(
                "Has realizado "
                f"{progress['total_attempts']} intentos "
                f"en este tema. Nivel actual: "
                f"{progress['difficulty']}.",
                state,
                "progress",
            )

        if not topic_id:
            return self._response(
                "¿Qué tema quieres estudiar? "
                "Por ejemplo, puedes preguntarme sobre fracciones.",
                state,
                "topic_required",
            )

        if intent in {
            "solicitar_explicacion",
            "simplificar_explicacion",
            "solicitar_ejemplo",
        }:
            level = (
                "alternative"
                if intent in {
                    "simplificar_explicacion",
                    "solicitar_ejemplo",
                }
                else "basic"
            )

            explanation = self.knowledge.get_explanation(
                topic_id,
                level,
            )

            return self._response(
                explanation,
                state,
                "explanation",
            )

        if intent in {"solicitar_reto", "repetir_ejercicio"}:
            exercise = self.knowledge.get_public_exercise(topic_id)

            if exercise["id"] in state["completed_exercises"]:
                return self._response(
                    "Ya completaste este ejercicio. "
                    "Necesitamos incorporar otro diferente "
                    "para continuar practicando.",
                    state,
                    "exercise_unavailable",
                )

            if state["active_exercise_id"] != exercise["id"]:
                state["active_exercise_id"] = exercise["id"]
                state["hints_used"] = 0

            return self._response(
                exercise["question"],
                state,
                "exercise",
                exercise=exercise,
            )

        if intent == "solicitar_pista":
            if not state["active_exercise_id"]:
                return self._response(
                    "Primero necesitas comenzar un ejercicio.",
                    state,
                    "exercise_required",
                )

            result = self.hints.get_next_hint(
                topic_id,
                state["hints_used"],
            )

            state["hints_used"] = result["hints_used"]

            return self._response(
                result["message"],
                state,
                "hint",
                strategy=result["strategy"],
            )

        if intent in {
            "verificar_respuesta",
            "solicitar_retroalimentacion",
        }:
            return self._response(
                "Si tienes un ejercicio activo, escribe "
                "tu resultado, por ejemplo: 3/4.",
                state,
                "answer_required",
            )

        return self._response(
            "Puedo explicarte el tema, proponerte "
            "un ejercicio o ayudarte con una pista.",
            state,
            "help",
        )

    def _evaluate_answer(self, answer, state):
        topic_id = state["current_topic"]

        exercise = self.knowledge.get_public_exercise(topic_id)

        if exercise["id"] != state["active_exercise_id"]:
            return self._response(
                "No hay un ejercicio valido para evaluar.",
                state,
                "exercise_required",
            )

        expected = self.knowledge.get_expected_answer(topic_id)

        evaluation = evaluate_fraction_answer(
            answer,
            expected,
        )

        progress = state["progress_by_topic"].get(
            topic_id,
            self.adaptive.initial_state(),
        )

        result = self.adaptive.update_progress(
            progress,
            exercise["id"],
            evaluation,
            hints_used=state["hints_used"],
        )

        state["progress_by_topic"][topic_id] = result["progress"]

        if evaluation["correct"]:
            state["completed_exercises"].append(exercise["id"])
            state["active_exercise_id"] = None
            state["hints_used"] = 0

        return self._response(
            evaluation["feedback"],
            state,
            "evaluation",
            evaluation=evaluation,
            next_action=result["next_action"],
        )
