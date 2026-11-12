from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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

        hints_before = state.get("hints_used", 0)

        # Ejecutar directamente el TutorService de Iván sin alterar su flujo
        result = runtime.tutor.process_message(message, state)
        new_state = result["state"]
        response_type = result["type"]
        reply_text = result["message"]
        raw_exercise = result.get("exercise")
        topic_id = new_state.get("current_topic")

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
