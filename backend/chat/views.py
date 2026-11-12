from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.services.runtime import TOPIC_METADATA, get_runtime
from progress.models import StudentProgress


class ChatMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = str(request.data.get("message", "")).strip()
        if not message:
            return Response(
                {"error": {"code": "empty_message", "message": "El mensaje no puede estar vacío."}},
                status=400,
            )

        runtime = get_runtime()
        progress_obj = None

        if request.user and request.user.is_authenticated:
            progress_obj, _ = StudentProgress.objects.get_or_create(user=request.user)
            state = progress_obj.tutor_state or runtime.tutor.initial_state()
        else:
            state = request.data.get("state") or runtime.tutor.initial_state()

        # Asegurar todas las llaves del estado inicial por compatibilidad
        base_state = runtime.tutor.initial_state()
        base_state.update(state if isinstance(state, dict) else {})
        state = base_state

        hints_before = state.get("hints_used", 0)
        result = runtime.tutor.process_message(message, state)
        new_state = result["state"]
        response_type = result["type"]
        reply_text = result["message"]
        raw_exercise = result.get("exercise")
        topic_id = new_state.get("current_topic")

        # Si el tutor dio una explicación de un tema disponible y no hay ejercicio activo,
        # seleccionamos un reto inicial para mostrar la tarjeta interactiva debajo de la explicación.
        if response_type == "explanation" and topic_id and not raw_exercise:
            topic_progress = new_state.get("progress_by_topic", {}).get(
                topic_id,
                runtime.adaptive.initial_state(),
            )
            try:
                candidate = runtime.selector.select(
                    topic_id=topic_id,
                    difficulty=topic_progress.get("difficulty", 1),
                    excluded_ids=new_state.get("completed_exercises", []),
                )
            except KeyError:
                candidate = None

            if candidate:
                raw_exercise = candidate
                new_state["active_exercise_id"] = candidate["id"]
                new_state["active_exercise_type"] = candidate["type"]
                new_state["hints_used"] = new_state.get("hints_by_exercise", {}).get(
                    candidate["id"], 0
                )

        # Cuando la respuesta es directamente un ejercicio, evitamos duplicar todo el texto
        # de opciones en la burbuja porque ya se renderiza en el componente ExerciseCard.
        if response_type == "exercise" and raw_exercise:
            meta = TOPIC_METADATA.get(topic_id, {"topicName": "este tema"})
            reply_text = (
                f"¡Sale y vale! Aquí tienes un reto de **{meta['topicName']}** "
                f"(nivel { {1: 'básico', 2: 'intermedio', 3: 'avanzado'}.get(raw_exercise.get('difficulty', 1), 'básico') }). "
                "Analízalo con calma en la tarjeta interactiva o escríbeme tu respuesta. "
                "Recuerda que si te atoras, puedes pedirme una pista sin que te regale la respuesta."
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
