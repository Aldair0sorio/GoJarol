
import re
from copy import deepcopy
from pathlib import Path

from curriculum.services.curriculum_catalog import CurriculumCatalog
from gojarol_ml.nlp.curriculum_retriever import CurriculumRetriever

from exercises.services.exercise_selector import ExerciseSelector
from exercises.services.hint_service import HintService


from exercises.services.exercise_evaluator import (
    evaluate_exercise_answer,
    normalize_choice,
)

from progress.services.adaptive_learning_service import (
    AdaptiveLearningService,
)

import unicodedata


def normalize_context_text(message: str) -> str:
    text = unicodedata.normalize("NFD", message.casefold())
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


ANSWER_PATTERN = re.compile(
    r"^\s*(?:(?:mi|la)\s+respuesta\s+es\s*|"
    r"respuesta\s*[:=]\s*)?"
    r"([+-]?\d+(?:\s*/\s*[+-]?\d+)?)\s*[.!]?\s*$",
    re.IGNORECASE,
)

# Respuesta a un menú de diagnóstico: "b", "B)", "la b", "opción c", "inciso a"...
MENU_LETTER_PATTERN = re.compile(r"(?:(?:la|el|opcion|inciso|letra)\s+)*([a-z])")


class TutorService:
    def __init__(self, analyzer, knowledge, hints, adaptive=None, selector=None, curriculum=None):
        self.analyzer = analyzer
        self.knowledge = knowledge
        self.selector = selector or hints.selector or ExerciseSelector(
            Path(__file__).resolve().parents[3] / "content" / "exercises"
        )
        self.hints = (
            hints if hints.selector is self.selector
            else HintService(knowledge, self.selector)
        )
        self.adaptive = adaptive or AdaptiveLearningService()
        self.curriculum = curriculum or CurriculumCatalog()
        self.curriculum_retriever = CurriculumRetriever(self.curriculum.entries)

        self.available_topics = {
            topic["id"] for topic in knowledge.list_topics()
        }

    @staticmethod
    def initial_state():
        return {
            "current_topic": None,
            "active_exercise_id": None,
            "hints_used": 0,
            "hints_by_exercise": {},
            "completed_exercises": [],
            "progress_by_topic": {},
            "last_response_type": None,
            "awaiting_reflection": False,
            "active_exercise_type": None,
            "academic_context": {},
            "current_competency_id": None,
            "curriculum": None,
            "pending_explanation_menu": None,
        }

    def _match_menu_choice(self, message, topic_id):
        """Devuelve la letra elegida si el mensaje responde al menú; si no, None."""
        options = self.knowledge.get_explanation_menu(topic_id)["options"]
        normalized = normalize_context_text(message)

        letter = MENU_LETTER_PATTERN.fullmatch(normalized)
        if letter:
            for option in options:
                if option["label"].casefold() == letter.group(1):
                    return option["label"]
            return None

        option_texts = [
            (option["label"], normalize_context_text(option["text"]))
            for option in options
        ]
        for label, text in option_texts:
            if normalized == text:
                return label

        # Un fragmento de al menos dos palabras que aparece en una sola opción.
        if len(normalized.split()) >= 2:
            matches = [label for label, text in option_texts if normalized in text]
            if len(matches) == 1:
                return matches[0]

        return None

    def _explanation_menu(self, topic_id, state):
        menu = self.knowledge.get_explanation_menu(topic_id)
        state["pending_explanation_menu"] = {"topic": topic_id}
        lines = [menu["question"], ""]
        lines.extend(f"{option['label']}) {option['text']}" for option in menu["options"])
        lines.extend(["", "Responde con la letra o escribe la opción con tus palabras."])
        return self._response(
            "\n".join(lines),
            state,
            "explanation_menu",
            menu=menu["options"],
        )

    @staticmethod
    def _response(message, state, response_type, **extra):
        state["last_response_type"] = response_type
        curriculum = state.get("curriculum")
        if curriculum:
            extra["curriculum"] = deepcopy(curriculum)
            if response_type in {"explanation", "exercise"} and curriculum.get("relation") in {"partial", "prerequisite"}:
                message = "Práctica de apoyo parcial; no cubre todo el aprendizaje curricular.\n\n" + message

        return {
            "type": response_type,
            "message": message,
            "state": state,
            **extra,
        }

    def _give_hint(self, state):
        if not state["active_exercise_id"]:
            return self._response(
                "Primero necesitas comenzar un ejercicio.",
                state,
                "exercise_required",
            )

        result = self.hints.get_next_hint(
            state["current_topic"],
            state["hints_used"],
            exercise_id=state["active_exercise_id"],
        )

        state["hints_used"] = result["hints_used"]
        state.setdefault("hints_by_exercise", {})[state["active_exercise_id"]] = result["hints_used"]

        return self._response(
            result["message"],
            state,
            "hint",
            strategy=result["strategy"],
        )

    def process_message(self, message, state=None, *, academic_context=None):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("El mensaje no puede estar vacio.")

        state = deepcopy(
            self.initial_state() if state is None else state
        )

        if academic_context is not None:
            if not isinstance(academic_context, dict):
                raise ValueError("El contexto academico debe ser un objeto.")
            if set(academic_context) - {"level", "grade", "semester", "model", "version", "program_id", "modality", "subject", "area", "competency_id"}:
                raise ValueError("Campo de contexto academico desconocido.")
            if any(value is not None and (not isinstance(value, str) or not value.strip())
                   for key, value in academic_context.items() if key not in {"grade", "semester"}):
                raise ValueError("Los campos del contexto academico deben ser texto.")
            if academic_context.get("level") not in {None, "secundaria", "bachillerato"}:
                raise ValueError("Nivel educativo invalido.")
            if (academic_context.get("grade") is not None and academic_context.get("semester") is not None
                    or academic_context.get("level") == "secundaria" and academic_context.get("semester") is not None
                    or academic_context.get("level") == "bachillerato" and academic_context.get("grade") is not None):
                raise ValueError("No mezcles grados y semestres.")
            for field, allowed in (("grade", {1, 2, 3}), ("semester", set(range(1, 7)))):
                value = academic_context.get(field)
                if value is not None and (type(value) is not int or value not in allowed):
                    raise ValueError("Grado o semestre invalido.")
            if academic_context != state.get("academic_context", {}):
                state["active_exercise_id"] = None
                state["active_exercise_type"] = None
                state["hints_used"] = 0
                state["awaiting_reflection"] = False
                state["current_competency_id"] = None
                state["curriculum"] = None
            state["academic_context"] = deepcopy(academic_context)

        # Si Jarol acaba de preguntar qué parte se le complica, la respuesta
        # (letra u opción) se interpreta aquí, sin pasar por el clasificador.
        # Cualquier otro mensaje descarta el menú y sigue el flujo normal.
        skipped_menu_topic = None
        pending_menu = state.get("pending_explanation_menu")
        if pending_menu:
            state["pending_explanation_menu"] = None
            menu_topic = pending_menu.get("topic") if isinstance(pending_menu, dict) else None
            if menu_topic and self.knowledge.has_explanation_menu(menu_topic):
                choice = self._match_menu_choice(message, menu_topic)
                if choice:
                    return self._response(
                        self.knowledge.get_menu_explanation(menu_topic, choice),
                        state,
                        "explanation",
                        menu_choice=choice,
                    )
            skipped_menu_topic = menu_topic

        # Si hay un ejercicio activo, primero detectamos respuestas.
        active_id = state.get("active_exercise_id")
        exercise_type = (
            self.selector.get_public_exercise(state["current_topic"], active_id)["type"]
            if active_id else None
        )

        if active_id:
            if exercise_type == "fraction":
                answer_match = ANSWER_PATTERN.fullmatch(message)

                if answer_match:
                    return self._evaluate_answer(
                        answer_match.group(1),
                        state,
                    )

            elif exercise_type == "multiple_choice":
                if normalize_choice(message) is not None:
                    return self._evaluate_answer(message, state)

            elif exercise_type in {"numeric", "percentage"}:
                # Also route malformed numeric attempts to format feedback, not NLP.
                if re.match(r"\s*(?:x\s*=|[+-]?[0-9])", message, re.IGNORECASE):
                    return self._evaluate_answer(message, state)


        normalized = normalize_context_text(message)

        if not active_id and state["current_topic"] and normalized in {
            "otra", "otro", "otra por favor", "dame otra", "uno mas",
        }:
            message = "Ponme otro ejercicio"

        # El alumno no sabe resolver el ejercicio activo.
        if state["active_exercise_id"] and normalized in {
            "no se",
            "la verdad no se",
            "no tengo idea",
            "ni idea",
            "no puedo",
            "no entiendo",
        }:
            return self._give_hint(state)

        # El alumno solicita continuar con las pistas.
        if (
                state["active_exercise_id"]
                and state.get("last_response_type") == "hint"
                and normalized in {
            "otra",
            "otra pista",
            "otra por favor",
            "dame otra",
            "una mas",
            "siguiente",
        }
        ):
            return self._give_hint(state)

        # El alumno responde a la reflexión posterior al ejercicio.
        if state.get("awaiting_reflection") and normalized in {
            "solo llegue",
            "no se",
            "no sabria explicar",
            "le atine",
            "fue suerte",
            "al azar",
            "porque si",
        }:
            state["awaiting_reflection"] = False

            return self._response(
                "Está bien. Vamos a revisar tu procedimiento. "
                "¿Qué paso podrías explicar primero?",
                state,
                "reflection",
            )

        analysis = self.analyzer.analyze_message(
            message,
            {"current_topic": state["current_topic"], "academic_context": state.get("academic_context", {})},
        )

        intent = analysis.get("intent")
        detected_topic = analysis.get("topic")

        if intent not in {"saludar", "despedirse", "consultar_progreso"}:
            curricular = analysis.get("curriculum") or self.curriculum_retriever.retrieve(
                message, state.get("academic_context", {}), detected_topic,
            )
            if curricular["status"] == "ambiguous":
                return self._response(
                    "Hay varias competencias posibles. Indica nivel, grado o semestre y modelo; "
                    "también puedes elegir un identificador curricular de las opciones.",
                    state, "curriculum_clarification", candidates=curricular["candidates"],
                )
            if curricular["status"] in {"resolved", "pending_verification", "context_unavailable"}:
                detected_topic = curricular["topic_id"]
                analysis["needs_clarification"] = False
            state["current_competency_id"] = curricular["competency_id"]
            state["curriculum"] = (
                self.curriculum.describe(curricular["competency_id"], detected_topic, self.knowledge, self.selector)
                if curricular["competency_id"] else {"mode": curricular["status"], "competency_id": None}
            )
            if detected_topic and detected_topic != state["current_topic"]:
                state["current_topic"] = detected_topic
                state["active_exercise_id"] = None
                state["active_exercise_type"] = None
                state["hints_used"] = 0
                state["awaiting_reflection"] = False
            if curricular["status"] in {"pending_verification", "context_unavailable"}:
                state["active_exercise_id"] = None
                state["active_exercise_type"] = None
                state["hints_used"] = 0
                state["awaiting_reflection"] = False
                return self._response(
                    "No tengo una vinculación curricular verificada para ese contexto. "
                    "No puedo presentar esta actividad como parte de tu programa. "
                    "Puedes precisar el modelo o solicitar práctica general sin asignación curricular.",
                    state, "curriculum_unavailable",
                )
            if state["current_competency_id"]:
                coverage = state["curriculum"]
                requires_exercise = intent in {"solicitar_reto", "repetir_ejercicio"}
                if not coverage["content_available"] or (requires_exercise and not coverage["exercises_available"]):
                    return self._response(
                        "Esa competencia está catalogada, pero aún no tengo "
                        "contenido o ejercicios implementados para enseñarla. "
                        "El registro curricular no significa cobertura educativa completa.",
                        state, "curriculum_unavailable",
                    )

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
            state["awaiting_reflection"] = False
            state["current_topic"] = detected_topic
            state["active_exercise_id"] = None
            state["active_exercise_type"] = None
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

        # Preguntar antes de explicar: primero qué parte se le complica.
        # Si vuelve a pedir la explicación sin elegir, o tiene un ejercicio
        # activo (sus opciones también usan letras), va la explicación completa.
        if (
            intent == "solicitar_explicacion"
            and not state["active_exercise_id"]
            and topic_id != skipped_menu_topic
            and self.knowledge.has_explanation_menu(topic_id)
        ):
            return self._explanation_menu(topic_id, state)

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
            progress = state["progress_by_topic"].get(
                topic_id,
                self.adaptive.initial_state(),
            )

            try:
                exercise = self.selector.select(
                    topic_id=topic_id,
                    difficulty=progress["difficulty"],
                    excluded_ids=state["completed_exercises"],
                    competencies=(state.get("curriculum") or {}).get("exercise_competencies") or None,
                )
            except KeyError:
                return self._response(
                    "Todavía no tengo ejercicios preparados para este tema.",
                    state,
                    "exercise_unavailable",
                )

            if exercise is None:
                return self._response(
                    "Ya completaste los ejercicios disponibles "
                    "de este nivel. Necesitamos más actividades "
                    "para continuar practicando.",
                    state,
                    "exercise_unavailable",
                )

            state["pending_explanation_menu"] = None
            if state["active_exercise_id"] != exercise["id"]:
                state["active_exercise_id"] = exercise["id"]
                state["active_exercise_type"] = exercise["type"]
                state["hints_used"] = state.get("hints_by_exercise", {}).get(exercise["id"], 0)

            state["awaiting_reflection"] = False

            parts = []
            if exercise.get("reading_text"):
                parts.append(f"Lee: {exercise['reading_text']}")
            parts.append(exercise["question"])
            if exercise.get("options"):
                parts.extend(
                    f"{label}) {text}" for label, text in exercise["options"].items()
                )

            return self._response(
                "\n\n".join(parts),
                state,
                "exercise",
                exercise=exercise,
            )

        if intent == "solicitar_pista":
            return self._give_hint(state)

        if intent in {
            "verificar_respuesta",
            "solicitar_retroalimentacion",
        }:
            answer_format = {
                "numeric": "un número entero o x = entero",
                "percentage": "el porcentaje como número, con o sin %",
                "multiple_choice": "la letra de la opción que elegiste",
            }.get(exercise_type, "tu resultado, por ejemplo: 3/4")
            return self._response(
                f"Si tienes un ejercicio activo, escribe {answer_format}.",
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

        exercise_id = state["active_exercise_id"]
        if not exercise_id or exercise_id in state["completed_exercises"]:
            return self._response(
                "No hay un ejercicio valido para evaluar.",
                state,
                "exercise_required",
            )

        exercise = self.selector.get_public_exercise(topic_id, exercise_id)
        expected = self.selector.get_expected_answer(topic_id, exercise_id)

        evaluation = evaluate_exercise_answer(
            answer,
            expected,
            exercise["type"],
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

        state["awaiting_reflection"] = evaluation["correct"]
        if evaluation["correct"]:
            state["completed_exercises"].append(exercise["id"])
            state["active_exercise_id"] = None
            state["active_exercise_type"] = None
            state["hints_used"] = 0

        return self._response(
            evaluation["feedback"],
            state,
            "evaluation",
            evaluation=evaluation,
            next_action=result["next_action"],
        )
