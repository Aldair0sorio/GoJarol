from django.db.models import Count
from rest_framework import serializers

from accounts.models import User
from chat.services.runtime import TOPIC_METADATA
from curriculum.models import Subject
from progress.models import ExerciseAttempt, StudentProgress
from progress.views import TOPIC_PROMPTS, compute_user_diagnostics, format_relative_activity

from .models import ClassAnnouncement, ClassChallenge, Classroom


def format_student_grade(student) -> str:
    if student.rol == User.Rol.DOCENTE:
        return "Docente Facilitador"
    grado = student.grado or 1
    if student.nivel == User.Nivel.BACHILLERATO:
        return f"{grado}° semestre de Bachillerato"
    return f"{grado}° de Secundaria"


def build_student_recommendations(diag: dict) -> list[str]:
    recs: list[str] = []
    if diag["completedCount"] == 0 and diag["totalAttempts"] == 0:
        recs.append("Aún no registra intentos guiados. Asígnale un reto diagnóstico inicial en su tema prioritario.")
        return recs

    weak_topics = [t for t in diag["topics"] if t["status"] == "Requiere refuerzo"]
    for t in weak_topics[:2]:
        recs.append(
            f"Reforzar {t['name']} ({t['accuracy']}% de precisión en {t['attempts']} intento{'s' if t['attempts'] != 1 else ''})."
        )

    if diag.get("hintsUsedTotal", 0) > max(diag["completedCount"], 1):
        recs.append(
            "Solicita varias pistas por reto. Conviene practicar ejercicios de nivel básico antes de subir dificultad."
        )

    mastered = diag.get("masteredTopics") or []
    if mastered:
        recs.append(
            f"Muestra dominio sólido en {', '.join(mastered[:2])}; listo para retos de nivel intermedio o avanzado."
        )

    if not recs:
        recs.append("Avance constante. Mantén práctica periódica en temas activos para consolidar su dominio.")

    return recs


def classify_student_status(diag: dict) -> str:
    if diag["completedCount"] == 0 and diag["totalAttempts"] == 0:
        return "Sin actividad"
    if diag["accuracy"] < 60 or len(diag.get("needsHelpWith", [])) > 0:
        return "Requiere apoyo"
    if diag["accuracy"] >= 85 and diag["completedCount"] >= 3:
        return "Destacado"
    return "Al corriente"


def _compute_challenge_completion_map(classroom: Classroom, challenges: list[ClassChallenge], student_ids: list[int]) -> dict[int, dict[int, int]]:
    """
    Devuelve {challenge_id: {student_id: distinct_correct_exercises_since_assigned}}.
    Permite saber exactamente cuántos alumnos han cumplido un reto sin exponer respuestas.
    """
    if not challenges or not student_ids:
        return {}

    earliest = min(ch.created_at for ch in challenges)
    attempts = list(
        ExerciseAttempt.objects.filter(
            user_id__in=student_ids,
            is_correct=True,
            created_at__gte=earliest,
        ).values("user_id", "topic_id", "exercise_id", "created_at")
    )

    result: dict[int, dict[int, int]] = {}
    for ch in challenges:
        per_student: dict[int, set[str]] = {}
        target_ids = {ch.student_id} if ch.student_id else set(student_ids)
        for att in attempts:
            uid = att["user_id"]
            if (
                uid in target_ids
                and att["topic_id"] == ch.topic_id
                and att["created_at"] >= ch.created_at
            ):
                per_student.setdefault(uid, set()).add(att["exercise_id"])
        result[ch.id] = {uid: len(ex_set) for uid, ex_set in per_student.items()}
    return result


class ClassroomSerializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Subject.objects.all(),
        required=False,
    )
    subject_nombre = serializers.SerializerMethodField()
    docente = serializers.SerializerMethodField()
    estudiantes = serializers.SerializerMethodField()
    averageMastery = serializers.SerializerMethodField()
    totalCompletedExercises = serializers.SerializerMethodField()
    studentsAtRisk = serializers.SerializerMethodField()
    topic_analytics = serializers.SerializerMethodField()
    students_detail = serializers.SerializerMethodField()
    challenges = serializers.SerializerMethodField()
    announcements = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            "id",
            "nombre",
            "nivel",
            "grado",
            "subject",
            "subject_nombre",
            "codigo",
            "codigo_activo",
            "docente",
            "estudiantes",
            "averageMastery",
            "totalCompletedExercises",
            "studentsAtRisk",
            "topic_analytics",
            "students_detail",
            "challenges",
            "announcements",
            "creada",
        ]
        read_only_fields = ["codigo", "creada"]

    def _is_teacher_viewer(self, obj) -> bool:
        req = self.context.get("request")
        user = getattr(req, "user", None)
        return bool(user and user.is_authenticated and (user.id == obj.docente_id or user.rol == User.Rol.DOCENTE))

    def _get_students_bundle(self, obj) -> list[dict]:
        cache = self.context.setdefault("_bundle_cache", {})
        if obj.id in cache:
            return cache[obj.id]

        enrollments = list(obj.enrollments.select_related("student", "student__progress").all())
        student_ids = [enr.student_id for enr in enrollments]
        progress_map = {
            p.user_id: p
            for p in StudentProgress.objects.filter(user_id__in=student_ids)
        }

        bundle = []
        for enr in enrollments:
            student = enr.student
            prog = progress_map.get(student.id)
            if prog is None:
                prog, _ = StudentProgress.objects.get_or_create(user=student)
            diag = compute_user_diagnostics(prog, user_obj=student)
            bundle.append(
                {
                    "enrollment": enr,
                    "student": student,
                    "progress": prog,
                    "diag": diag,
                    "statusLabel": classify_student_status(diag),
                    "recommendations": build_student_recommendations(diag),
                }
            )
        cache[obj.id] = bundle
        return bundle

    def get_subject_nombre(self, obj):
        slug = (obj.subject.slug if obj.subject else "").lower()
        if slug == "espanol":
            return "Español"
        if slug in {"matematicas", "aritmetica", "algebra"}:
            return "Matemáticas"
        return obj.subject.nombre if obj.subject else "Matemáticas"

    def get_docente(self, obj):
        return obj.docente.alias or obj.docente.username

    def get_estudiantes(self, obj):
        return len(self._get_students_bundle(obj))

    def get_averageMastery(self, obj):
        bundle = self._get_students_bundle(obj)
        active = [b["diag"]["accuracy"] for b in bundle if b["diag"]["totalAttempts"] > 0 or b["diag"]["completedCount"] > 0]
        if not active:
            return 0
        return round(sum(active) / len(active))

    def get_totalCompletedExercises(self, obj):
        bundle = self._get_students_bundle(obj)
        return sum(b["diag"]["completedCount"] for b in bundle)

    def get_studentsAtRisk(self, obj):
        bundle = self._get_students_bundle(obj)
        return sum(1 for b in bundle if b["statusLabel"] == "Requiere apoyo")

    def get_topic_analytics(self, obj):
        bundle = self._get_students_bundle(obj)
        rows = []
        for topic_id, meta in TOPIC_METADATA.items():
            active_students = 0
            mastered_students = 0
            struggling_students = 0
            acc_sum = 0
            mastery_sum = 0
            total_attempts = 0
            total_hints = 0

            for item in bundle:
                t_row = next((t for t in item["diag"]["topics"] if t["topicId"] == topic_id), None)
                if not t_row:
                    continue
                if t_row["attempts"] > 0 or t_row["completedExercises"] > 0:
                    active_students += 1
                    acc_sum += t_row["accuracy"]
                    mastery_sum += t_row["mastery"]
                if t_row["status"] == "Dominado":
                    mastered_students += 1
                elif t_row["status"] == "Requiere refuerzo":
                    struggling_students += 1
                total_attempts += t_row["attempts"]
                total_hints += t_row.get("hintsUsed", 0)

            avg_acc = round(acc_sum / active_students) if active_students > 0 else 0
            avg_mastery = round(mastery_sum / active_students) if active_students > 0 else 0

            if active_students == 0:
                health = "Sin datos"
            elif struggling_students > 0 or avg_acc < 60:
                health = "Requiere refuerzo"
            elif mastered_students > 0 and avg_acc >= 75:
                health = "Fortaleza"
            else:
                health = "En progreso"

            rows.append(
                {
                    "topicId": topic_id,
                    "topicName": meta["topicName"],
                    "subjectName": meta["subjectName"],
                    "activeStudents": active_students,
                    "masteredStudents": mastered_students,
                    "strugglingStudents": struggling_students,
                    "averageAccuracy": avg_acc,
                    "averageMastery": avg_mastery,
                    "totalAttempts": total_attempts,
                    "totalHintsUsed": total_hints,
                    "healthStatus": health,
                }
            )
        return rows

    def get_students_detail(self, obj):
        bundle = self._get_students_bundle(obj)
        is_teacher = self._is_teacher_viewer(obj)
        details = []

        for item in bundle:
            student = item["student"]
            enr = item["enrollment"]
            diag = item["diag"]
            row = {
                "id": str(student.id),
                "name": student.alias or student.username,
                "gradeLabel": format_student_grade(student),
                "joinedAt": format_relative_activity(enr.unido),
                "lastActive": diag["lastActive"],
                "completedExercises": diag["completedCount"],
                "totalAttempts": diag["totalAttempts"],
                "accuracy": diag["accuracy"],
                "xp": diag["xp"],
                "streakDays": diag["streakDays"],
                "hintsUsedTotal": diag.get("hintsUsedTotal", 0),
                "statusLabel": item["statusLabel"],
                "needsHelpWith": diag["needsHelpWith"],
                "masteredTopics": diag["masteredTopics"],
            }
            if is_teacher:
                row["email"] = student.email
                row["topics"] = diag["topics"]
                row["recentAttempts"] = diag["recentAttempts"]
                row["recommendations"] = item["recommendations"]
            details.append(row)

        details.sort(key=lambda s: (-s["xp"], s["name"].lower()))
        return details

    def get_challenges(self, obj):
        req = self.context.get("request")
        viewer = getattr(req, "user", None)
        is_teacher = self._is_teacher_viewer(obj)

        challenges = list(obj.challenges.select_related("student", "assigned_by").all())
        if not is_teacher and viewer and viewer.is_authenticated:
            challenges = [ch for ch in challenges if ch.student_id is None or ch.student_id == viewer.id]

        bundle = self._get_students_bundle(obj)
        student_ids = [b["student"].id for b in bundle]
        comp_map = _compute_challenge_completion_map(obj, challenges, student_ids)

        serialized = []
        for ch in challenges:
            meta = TOPIC_METADATA.get(ch.topic_id, {})
            per_student = comp_map.get(ch.id, {})
            assigned_ids = [ch.student_id] if ch.student_id else student_ids
            completed_by_count = sum(1 for uid in assigned_ids if per_student.get(uid, 0) >= ch.target_exercises)

            viewer_solved = (
                per_student.get(viewer.id, 0)
                if viewer and viewer.is_authenticated
                else 0
            )
            serialized.append(
                {
                    "id": str(ch.id),
                    "topicId": ch.topic_id,
                    "topicName": meta.get("topicName", ch.topic_id),
                    "subjectName": meta.get("subjectName", "Práctica Guiada"),
                    "title": ch.title,
                    "instructions": ch.instructions,
                    "targetExercises": ch.target_exercises,
                    "prompt": TOPIC_PROMPTS.get(ch.topic_id, f"Ponme un ejercicio de {meta.get('topicName', ch.topic_id)}"),
                    "isPersonal": ch.student_id is not None,
                    "studentId": str(ch.student_id) if ch.student_id else None,
                    "studentName": (ch.student.alias or ch.student.username) if ch.student else None,
                    "assignedCount": len(assigned_ids),
                    "completedByCount": completed_by_count,
                    "solvedCount": viewer_solved,
                    "isCompleted": viewer_solved >= ch.target_exercises,
                    "createdAt": format_relative_activity(ch.created_at),
                }
            )
        return serialized

    def get_announcements(self, obj):
        return [
            {
                "id": str(ann.id),
                "title": ann.title,
                "message": ann.message,
                "authorName": ann.author.alias or ann.author.username,
                "createdAt": format_relative_activity(ann.created_at),
            }
            for ann in obj.announcements.select_related("author").all()[:15]
        ]
