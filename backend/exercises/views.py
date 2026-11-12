from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.services.runtime import get_runtime
from exercises.services.exercise_evaluator import evaluate_exercise_answer
from progress.models import StudentProgress
from progress.views import resolve_progress_for_request


class ExerciseAnswerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, exercise_id: str):
        raw_answer = request.data.get("answer")
        if raw_answer is None:
            raw_answer = request.data.get("option_id", "")
        answer_str = str(raw_answer).strip()

        runtime = get_runtime()
        topic_id = runtime.find_topic_for_exercise(exercise_id)
        if not topic_id:
            return Response(
                {"error": {"code": "not_found", "message": "Ejercicio no encontrado."}},
                status=404,
            )

        public_ex = runtime.selector.get_public_exercise(topic_id, exercise_id)
        expected = runtime.selector.get_expected_answer(topic_id, exercise_id)
        full_ex = runtime.selector._exercises[topic_id][exercise_id]

        evaluation = evaluate_exercise_answer(answer_str, expected, public_ex["type"])
        is_correct = bool(evaluation["correct"])

        progress_obj = resolve_progress_for_request(request)
        state = runtime.tutor.initial_state()
        if progress_obj is not None and isinstance(progress_obj.tutor_state, dict):
            state.update(progress_obj.tutor_state)

        hints_used = state.get("hints_by_exercise", {}).get(
            exercise_id, state.get("hints_used", 0)
        )

        topic_progress = state.setdefault("progress_by_topic", {}).get(
            topic_id,
            runtime.adaptive.initial_state(),
        )
        adaptive_result = runtime.adaptive.update_progress(
            topic_progress,
            exercise_id,
            evaluation,
            hints_used=hints_used,
        )
        state["progress_by_topic"][topic_id] = adaptive_result["progress"]
        state["current_topic"] = topic_id

        xp_earned = 0
        next_exercise_formatted = None

        if is_correct:
            completed = state.setdefault("completed_exercises", [])
            if exercise_id not in completed:
                completed.append(exercise_id)
                xp_earned = 30 if hints_used == 0 else 20
            if state.get("active_exercise_id") == exercise_id:
                state["active_exercise_id"] = None
                state["active_exercise_type"] = None
                state["hints_used"] = 0

            # Explicación formativa de por qué es correcta
            if full_ex.get("answer_explanation"):
                explanation = f"{evaluation['feedback']} {full_ex['answer_explanation']}"
            elif full_ex.get("solution_steps"):
                steps_str = " ".join(full_ex["solution_steps"])
                explanation = f"{evaluation['feedback']} Procedimiento: {steps_str}"
            else:
                explanation = evaluation["feedback"]

            hint_text = None

            # Seleccionar siguiente reto adaptativo del mismo tema
            next_raw = runtime.selector.select(
                topic_id=topic_id,
                difficulty=adaptive_result["progress"].get("difficulty", 1),
                excluded_ids=completed,
            )
            if next_raw:
                state["active_exercise_id"] = next_raw["id"]
                state["active_exercise_type"] = next_raw["type"]
                state["hints_used"] = 0
                next_exercise_formatted = runtime.format_exercise_for_frontend(topic_id, next_raw)
        else:
            # Respuesta incorrecta: NUNCA revelamos la respuesta correcta, damos pista socrática
            hint_res = runtime.hints.get_next_hint(
                topic_id,
                hints_used,
                exercise_id=exercise_id,
            )
            state.setdefault("hints_by_exercise", {})[exercise_id] = hint_res["hints_used"]
            state["hints_used"] = hint_res["hints_used"]
            explanation = evaluation["feedback"]
            hint_text = hint_res["message"]

        if progress_obj is not None:
            if xp_earned > 0:
                progress_obj.xp += xp_earned
            progress_obj.tutor_state = state
            progress_obj.save()

        return Response(
            {
                "isCorrect": is_correct,
                "status": evaluation["status"],
                "title": (
                    f"¡Excelente razonamiento! (+{xp_earned} XP)"
                    if is_correct and xp_earned > 0
                    else ("¡Respuesta correcta!" if is_correct else "¡Casi! Analicemos este paso...")
                ),
                "explanation": explanation,
                "hint": hint_text,
                "xpEarned": xp_earned,
                "totalXp": progress_obj.xp if progress_obj is not None else None,
                "nextExercise": next_exercise_formatted,
            }
        )


class ExerciseHintView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, exercise_id: str):
        runtime = get_runtime()
        topic_id = runtime.find_topic_for_exercise(exercise_id)
        if not topic_id:
            return Response(
                {"error": {"code": "not_found", "message": "Ejercicio no encontrado."}},
                status=404,
            )

        progress_obj = resolve_progress_for_request(request)
        state = runtime.tutor.initial_state()
        if progress_obj is not None and isinstance(progress_obj.tutor_state, dict):
            state.update(progress_obj.tutor_state)

        hints_used = state.get("hints_by_exercise", {}).get(
            exercise_id,
            int(request.data.get("hints_used", state.get("hints_used", 0))),
        )

        hint_res = runtime.hints.get_next_hint(
            topic_id,
            hints_used,
            exercise_id=exercise_id,
        )
        state.setdefault("hints_by_exercise", {})[exercise_id] = hint_res["hints_used"]
        state["hints_used"] = hint_res["hints_used"]

        if progress_obj is not None:
            progress_obj.tutor_state = state
            progress_obj.save()

        return Response(
            {
                "hint": hint_res["message"],
                "strategy": hint_res["strategy"],
                "hintsUsed": hint_res["hints_used"],
            }
        )
