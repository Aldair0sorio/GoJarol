from django.utils import timezone
from django.utils.timesince import timesince
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.services.runtime import TOPIC_METADATA, get_runtime
from progress.models import ExerciseAttempt, StudentProgress
from progress.ranks import rank_for_xp

User = get_user_model()

TOPIC_PROMPTS = {
    "mat_fracciones": "Ponme un ejercicio de fracciones",
    "mat_ecuaciones": "Ponme un ejercicio de ecuaciones de primer grado",
    "mat_porcentajes": "Ponme un ejercicio de porcentajes",
    "esp_comprension": "Dame un reto de comprensión lectora",
    "esp_ortografia": "Ponme un ejercicio de ortografía",
    "esp_acentuacion": "Ayúdame a practicar reglas de acentuación",
}


def format_relative_activity(dt) -> str:
    if not dt:
        return "Sin actividad"
    local_dt = timezone.localtime(dt) if timezone.is_aware(dt) else dt
    now = timezone.localtime(timezone.now())
    diff = now - local_dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Hace un momento"
    if seconds < 3600:
        mins = max(1, seconds // 60)
        return f"Hace {mins} min"
    if local_dt.date() == now.date():
        return f"Hoy, {local_dt.strftime('%H:%M')}"
    if (now.date() - local_dt.date()).days == 1:
        return f"Ayer, {local_dt.strftime('%H:%M')}"
    return local_dt.strftime("%d/%m %H:%M")


def _extract_selected_label(raw_ex: dict, submitted_answer: str) -> str:
    if not submitted_answer:
        return "Sin respuesta"
    options = raw_ex.get("options") or {}
    clean = submitted_answer.strip().upper()
    if options and clean in options:
        return f"{clean}) {options[clean]}"
    return submitted_answer.strip()


def record_exercise_attempt(
    *,
    user,
    topic_id: str,
    raw_ex: dict,
    submitted_answer: str,
    is_correct: bool,
    hints_used: int,
    feedback: str,
) -> None:
    if not user or not getattr(user, "is_authenticated", False):
        return
    ExerciseAttempt.objects.create(
        user=user,
        topic_id=topic_id or "",
        exercise_id=str(raw_ex.get("id", "")),
        exercise_question=str(raw_ex.get("question", "")),
        exercise_type=str(raw_ex.get("type", "numeric")),
        difficulty=int(raw_ex.get("difficulty", 1) or 1),
        submitted_answer=str(submitted_answer or "")[:255],
        is_correct=bool(is_correct),
        hints_used=max(0, int(hints_used or 0)),
        feedback=str(feedback or "")[:500],
    )


def compute_user_diagnostics(progress_obj: StudentProgress | None, user_obj=None) -> dict:
    runtime = get_runtime()
    state = (progress_obj.tutor_state or {}) if progress_obj else {}
    completed_ids = list(state.get("completed_exercises", []))
    completed_set = set(completed_ids)
    progress_by_topic = state.get("progress_by_topic", {})
    hints_by_exercise = state.get("hints_by_exercise", {})

    resolved_user = user_obj or (progress_obj.user if progress_obj else None)
    attempt_qs = (
        ExerciseAttempt.objects.filter(user=resolved_user).order_by("-created_at")
        if resolved_user is not None
        else ExerciseAttempt.objects.none()
    )
    attempts_list = list(attempt_qs[:40])

    hints_by_topic: dict[str, int] = {}
    if attempts_list:
        for att in attempts_list:
            hints_by_topic[att.topic_id] = hints_by_topic.get(att.topic_id, 0) + int(att.hints_used or 0)
    else:
        for ex_id, h_count in hints_by_exercise.items():
            t_id = runtime.find_topic_for_exercise(ex_id)
            if t_id:
                hints_by_topic[t_id] = hints_by_topic.get(t_id, 0) + int(h_count or 0)

    topics_summary = []
    total_attempts_all = 0
    total_correct_all = 0
    needs_help = []
    mastered_topics = []

    for topic_id, meta in TOPIC_METADATA.items():
        all_topic_ex = runtime.selector._exercises.get(topic_id, {})
        total_ex = max(len(all_topic_ex), 1)
        completed_in_topic = sum(1 for ex_id in all_topic_ex if ex_id in completed_set)

        t_prog = progress_by_topic.get(topic_id, {})
        attempts = int(t_prog.get("total_attempts", 0))
        if "correct_attempts" in t_prog:
            correct = int(t_prog.get("correct_attempts", 0))
        elif completed_in_topic > 0:
            # Compatibilidad con alumnos que resolvieron retos antes de registrar correct_attempts
            correct = completed_in_topic
            attempts = max(attempts, correct)
        else:
            correct = 0
        difficulty = int(t_prog.get("difficulty", 1))
        topic_hints = int(hints_by_topic.get(topic_id, 0))

        total_attempts_all += attempts
        total_correct_all += correct

        mastery = min(100, round((completed_in_topic / total_ex) * 100))
        if mastery == 0 and correct > 0:
            mastery = min(100, round((correct / total_ex) * 100))

        topic_accuracy = (
            round((correct / attempts) * 100)
            if attempts > 0
            else (100 if completed_in_topic > 0 else 0)
        )

        if mastery >= 75 or (completed_in_topic >= 3 and topic_accuracy >= 80):
            status = "Dominado"
            mastered_topics.append(meta["topicName"])
        elif attempts > 0 and (topic_accuracy < 60 or int(t_prog.get("consecutive_errors", 0)) >= 2):
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
                "accuracy": topic_accuracy,
                "completedExercises": completed_in_topic,
                "totalExercises": total_ex,
                "attempts": attempts,
                "correctAttempts": correct,
                "hintsUsed": topic_hints,
                "difficulty": difficulty,
                "status": status,
                "prompt": TOPIC_PROMPTS.get(topic_id, f"Quiero practicar {meta['topicName']}"),
            }
        )

    accuracy = (
        round((total_correct_all / total_attempts_all) * 100)
        if total_attempts_all > 0
        else (100 if len(completed_set) > 0 else 0)
    )

    recent_attempts = []
    for att in attempts_list[:15]:
        raw_ex = runtime.selector._exercises.get(att.topic_id, {}).get(att.exercise_id, {})
        topic_meta = TOPIC_METADATA.get(att.topic_id, {})
        recent_attempts.append(
            {
                "id": str(att.id),
                "topicId": att.topic_id,
                "topicName": topic_meta.get("topicName", att.topic_id),
                "exerciseId": att.exercise_id,
                "exerciseTitle": att.exercise_question or raw_ex.get("question") or att.exercise_id,
                "date": format_relative_activity(att.created_at),
                "isCorrect": att.is_correct,
                "selectedOption": _extract_selected_label(raw_ex, att.submitted_answer),
                "explanationGiven": att.feedback or (
                    "Respuesta verificada con el motor pedagógico Go Jarol."
                    if att.is_correct
                    else "Jarol ofreció pistas paso a paso sin revelar la respuesta directa."
                ),
                "hintUsed": (
                    f"Solicitó {att.hints_used} pista{'s' if att.hints_used != 1 else ''}"
                    if att.hints_used > 0
                    else None
                ),
            }
        )

    # Si había ejercicios completados antes de existir ExerciseAttempt, resumirlos sin inventar errores
    if not recent_attempts and completed_ids:
        for idx, ex_id in enumerate(reversed(completed_ids[-6:])):
            t_id = runtime.find_topic_for_exercise(ex_id) or ""
            raw_ex = runtime.selector._exercises.get(t_id, {}).get(ex_id, {})
            topic_meta = TOPIC_METADATA.get(t_id, {})
            recent_attempts.append(
                {
                    "id": f"hist_{idx}_{ex_id}",
                    "topicId": t_id,
                    "topicName": topic_meta.get("topicName", t_id),
                    "exerciseId": ex_id,
                    "exerciseTitle": raw_ex.get("question", f"Ejercicio {ex_id}"),
                    "date": format_relative_activity(progress_obj.updated_at if progress_obj else None),
                    "isCorrect": True,
                    "selectedOption": "Completado correctamente",
                    "explanationGiven": "Evaluado con el motor determinista SymPy y tutoría Jarol.",
                    "hintUsed": (
                        f"Usó {hints_by_exercise[ex_id]} pista(s)"
                        if hints_by_exercise.get(ex_id, 0) > 0
                        else None
                    ),
                }
            )

    last_dt = attempts_list[0].created_at if attempts_list else (
        progress_obj.updated_at if progress_obj and (total_attempts_all > 0 or len(completed_set) > 0 or progress_obj.xp > 0) else None
    )

    hints_used_total = (
        sum(int(att.hints_used or 0) for att in attempts_list)
        if attempts_list
        else sum(int(v or 0) for v in hints_by_exercise.values())
    )

    xp_value = progress_obj.xp if progress_obj else 0

    return {
        "xp": xp_value,
        "league": rank_for_xp(xp_value),
        "streakDays": progress_obj.streak_days if progress_obj else 1,
        "completedCount": len(completed_set),
        "totalAttempts": total_attempts_all,
        "accuracy": accuracy,
        "hintsUsedTotal": hints_used_total,
        "lastActive": format_relative_activity(last_dt),
        "needsHelpWith": needs_help,
        "masteredTopics": mastered_topics,
        "topics": topics_summary,
        "recentAttempts": recent_attempts,
    }


def resolve_user_for_request(request):
    # Identity comes only from validated authentication, never client headers/body.
    if request.user and request.user.is_authenticated:
        return request.user
    return None


def resolve_progress_for_request(request) -> StudentProgress | None:
    user = resolve_user_for_request(request)
    if user is not None:
        progress, _ = StudentProgress.objects.get_or_create(user=user)
        return progress
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
                    "league": rank_for_xp(prog.xp),
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
