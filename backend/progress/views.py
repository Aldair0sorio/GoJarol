from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.services.runtime import TOPIC_METADATA, get_runtime
from progress.models import StudentProgress

User = get_user_model()

TOPIC_PROMPTS = {
    "mat_fracciones": "Ponme un ejercicio de fracciones",
    "mat_ecuaciones": "Ponme un ejercicio de ecuaciones de primer grado",
    "mat_porcentajes": "Ponme un ejercicio de porcentajes",
    "esp_comprension": "Dame un reto de comprensión lectora",
    "esp_ortografia": "Ponme un ejercicio de ortografía",
    "esp_acentuacion": "Ayúdame a practicar reglas de acentuación",
}


def compute_user_diagnostics(progress_obj: StudentProgress | None) -> dict:
    runtime = get_runtime()
    state = (progress_obj.tutor_state or {}) if progress_obj else {}
    completed_ids = set(state.get("completed_exercises", []))
    progress_by_topic = state.get("progress_by_topic", {})

    topics_summary = []
    total_attempts_all = 0
    total_correct_all = 0
    needs_help = []

    for topic_id, meta in TOPIC_METADATA.items():
        all_topic_ex = runtime.selector._exercises.get(topic_id, {})
        total_ex = max(len(all_topic_ex), 1)
        completed_in_topic = sum(1 for ex_id in all_topic_ex if ex_id in completed_ids)

        t_prog = progress_by_topic.get(topic_id, {})
        attempts = int(t_prog.get("total_attempts", 0))
        correct = int(t_prog.get("correct_attempts", 0))
        difficulty = int(t_prog.get("difficulty", 1))

        total_attempts_all += attempts
        total_correct_all += correct

        mastery = min(100, round((completed_in_topic / total_ex) * 100))
        if mastery == 0 and correct > 0:
            mastery = min(100, round((correct / total_ex) * 100))

        if mastery >= 75:
            status = "Dominado"
        elif attempts > 0 and (correct / max(attempts, 1)) < 0.5:
            status = "Requiere refuerzo"
            needs_help.append(meta["topicName"])
        elif completed_in_topic > 0 or attempts > 0:
            status = "En curso"
        else:
            status = "Por iniciar"

        topics_summary.append(
            {
                "topicId": topic_id,
                "name": meta["topicName"],
                "subject": meta["subjectName"],
                "mastery": mastery,
                "completedExercises": completed_in_topic,
                "totalExercises": total_ex,
                "attempts": attempts,
                "correctAttempts": correct,
                "difficulty": difficulty,
                "status": status,
                "prompt": TOPIC_PROMPTS.get(topic_id, f"Quiero practicar {meta['topicName']}"),
            }
        )

    accuracy = (
        round((total_correct_all / total_attempts_all) * 100)
        if total_attempts_all > 0
        else (100 if len(completed_ids) > 0 else 0)
    )

    return {
        "xp": progress_obj.xp if progress_obj else 0,
        "streakDays": progress_obj.streak_days if progress_obj else 1,
        "completedCount": len(completed_ids),
        "totalAttempts": total_attempts_all,
        "accuracy": accuracy,
        "needsHelpWith": needs_help,
        "topics": topics_summary,
    }


def resolve_progress_for_request(request) -> StudentProgress | None:
    if request.user and request.user.is_authenticated:
        prog, _ = StudentProgress.objects.get_or_create(user=request.user)
        return prog

    # Guest diagnostics never resolve another account from client-supplied identity.
    return None


class MyProgressView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        progress_obj = resolve_progress_for_request(request)
        data = compute_user_diagnostics(progress_obj)
        return Response(data)


class LeaderboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        students = User.objects.filter(rol=User.Rol.ESTUDIANTE).select_related("progress")
        rows = []
        for student in students:
            prog, _ = StudentProgress.objects.get_or_create(user=student)
            nivel_label = (
                "Bachillerato"
                if student.nivel == User.Nivel.BACHILLERATO
                else "Secundaria"
            )
            grado_num = student.grado or 1
            unit = "semestre" if student.nivel == User.Nivel.BACHILLERATO else "°"
            grade_str = (
                f"{grado_num}° {nivel_label}"
                if unit == "°"
                else f"{grado_num}° sem. {nivel_label}"
            )
            rows.append(
                {
                    "id": str(student.id),
                    "name": student.alias or student.username,
                    "username": student.username,
                    "grade": grade_str,
                    "xp": prog.xp,
                    "streakDays": prog.streak_days,
                    "isCurrentUser": bool(
                        request.user
                        and request.user.is_authenticated
                        and request.user.id == student.id
                    ),
                }
            )

        rows.sort(key=lambda item: (-item["xp"], item["name"].lower()))
        for idx, row in enumerate(rows):
            row["rank"] = idx + 1

        return Response(rows)
