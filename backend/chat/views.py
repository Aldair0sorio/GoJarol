from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.services.operation_guides import match_specific_operation_guide
from chat.services.runtime import get_runtime
from progress.models import StudentProgress


class ChatMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        runtime = get_runtime()

        # Permitir reiniciar el contexto conversacional ("Nueva duda") conservando el progreso acumulado
        if request.data.get("reset"):
            if request.user and request.user.is_authenticated:
                progress_obj, _ = StudentProgress.objects.get_or_create(user=request.user)
                old_state = progress_obj.tutor_state if isinstance(progress_obj.tutor_state, dict) else {}
                fresh_state = runtime.tutor.initial_state()
                fresh_state["completed_exercises"] = old_state.get("completed_exercises", [])
                fresh_state["progress_by_topic"] = old_state.get("progress_by_topic", {})
                progress_obj.tutor_state = fresh_state
                progress_obj.save()
            return Response({"status": "reset_ok"})

        message = str(request.data.get("message", "")).strip()
        if not message:
            return Response(
                {"error": {"code": "empty_message", "message": "El mensaje no puede estar vacío."}},
                status=400,
            )

        progress_obj = None
        if request.user and request.user.is_authenticated:
            progress_obj, _ = StudentProgress.objects.get_or_create(user=request.user)
            state = progress_obj.tutor_state or runtime.tutor.initial_state()
        else:
            state = request.data.get("state") or runtime.tutor.initial_state()

        # Asegurar todas las llaves del estado inicial
        base_state = runtime.tutor.initial_state()
        base_state.update(state if isinstance(state, dict) else {})
        state = base_state

        previous_topic = state.get("current_topic")
        previous_type = state.get("last_response_type")
        hints_before = state.get("hints_used", 0)

        # 1. Revisar si el alumno pregunta por una operación específica (ej. "y cuanto seria 5/2", dividir, multiplicar, restar, sumar)
        specific = match_specific_operation_guide(message, state)
        if specific is not None:
            guide_text, mapped_topic = specific
            if mapped_topic:
                state["current_topic"] = mapped_topic
            state["last_response_type"] = "explanation"
            if progress_obj is not None:
                progress_obj.tutor_state = state
                progress_obj.save()
            return Response(
                {
                    "reply": guide_text,
                    "type": "explanation",
                    "exercise": None,
                    "evaluation": None,
                    "nextAction": None,
                    "xpEarned": 0,
                    "totalXp": progress_obj.xp if progress_obj else 0,
                    "streakDays": progress_obj.streak_days if progress_obj else 1,
                    "currentTopic": state.get("current_topic"),
                }
            )

        # 2. Ejecutar el TutorService de Iván (intent_classifier.joblib + CurriculumRetriever + SymPy)
        result = runtime.tutor.process_message(message, state)
        new_state = result["state"]
        response_type = result["type"]
        reply_text = result["message"]
        raw_exercise = result.get("exercise")
        topic_id = new_state.get("current_topic")

        # Si pide otra explicación del mismo tema que acabamos de explicar, alternar con la explicación "alternative"
        if (
            response_type == "explanation"
            and topic_id
            and previous_topic == topic_id
            and previous_type == "explanation"
        ):
            try:
                alt_text = runtime.knowledge.get_explanation(topic_id, "alternative")
                if alt_text and alt_text != reply_text:
                    reply_text = alt_text
            except Exception:
                pass

        # Si el modelo no detectó tema ("clarification") o clasificó erróneamente como progreso sin que el usuario preguntara su avance
        msg_lower = message.lower()
        asked_progress = any(
            w in msg_lower
            for w in ("progreso", "avance", "nivel", "intento", "como voy", "cómo voy", "racha", "xp", "punto")
        )
        if response_type in {"clarification", "topic_required"} or (
            response_type == "progress" and not asked_progress
        ):
            reply_text = (
                "¿Sobre qué tema te gustaría que trabajemos? Puedo explicarte paso a paso o ponerte retos interactivos de:\n\n"
                "• **Matemáticas**: Fracciones, Ecuaciones de primer grado, Porcentajes, Suma, Resta, Multiplicación, División o Teorema de Pitágoras.\n"
                "• **Español**: Comprensión lectora, Ortografía o Reglas de acentuación.\n\n"
                "Por ejemplo, escríbeme: **«Explícame a dividir»**, **«¿Cuánto sería 5/2?»** o **«Ponme un ejercicio de fracciones»**."
            )

        xp_earned = 0
        evaluation = result.get("evaluation")
        if response_type == "evaluation" and evaluation and evaluation.get("correct"):
            xp_earned = 30 if hints_before == 0 else 20

        if progress_obj is not None:
            if xp_earned > 0:
                progress_obj.xp += xp_earned
            progress_obj.tutor_state = new_state
            progress_obj.save()

        formatted_exercise = runtime.format_exercise_for_frontend(topic_id, raw_exercise)

        return Response(
            {
                "reply": reply_text,
                "type": response_type,
                "exercise": formatted_exercise,
                "evaluation": evaluation,
                "nextAction": result.get("next_action"),
                "xpEarned": xp_earned,
                "totalXp": progress_obj.xp if progress_obj else xp_earned,
                "streakDays": progress_obj.streak_days if progress_obj else 1,
                "currentTopic": topic_id,
            }
        )
