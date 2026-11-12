from datetime import timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from chat.services.runtime import TOPIC_METADATA
from curriculum.models import Subject
from curriculum.views import _ensure_catalog_seeded
from progress.copy_signals import RECOMMENDATIONS, RULE_TEXT, WINDOW_DAYS, copy_signal
from progress.models import StudentProgress, TutorEvent
from progress.views import compute_user_diagnostics, format_relative_activity

from .models import ClassAnnouncement, ClassChallenge, Classroom, Enrollment
from .serializers import (
    ClassroomSerializer,
    build_student_recommendations,
    classify_student_status,
    format_student_grade,
    _compute_challenge_completion_map,
)


def _ensure_default_subject(slug_or_name: str | None) -> Subject:
    _ensure_catalog_seeded()
    raw = (slug_or_name or "matematicas").strip().lower()
    alias_map = {
        "matemáticas": "matematicas",
        "matematicas": "matematicas",
        "español": "espanol",
        "espanol": "espanol",
        "aritmetica": "aritmetica",
        "aritmética": "aritmetica",
        "algebra": "algebra",
        "álgebra": "algebra",
    }
    slug = alias_map.get(raw, raw)
    subj = Subject.objects.filter(slug=slug).first()
    if subj:
        return subj
    subj = Subject.objects.filter(slug="matematicas").first() or Subject.objects.first()
    if subj:
        return subj
    return Subject.objects.create(
        slug="matematicas",
        nombre="Matemáticas",
        disponible=True,
        orden=1,
    )


def _get_teacher_classroom_or_403(user, class_id: int) -> Classroom:
    classroom = get_object_or_404(Classroom, id=class_id)
    if classroom.docente_id != user.id:
        raise PermissionDenied("Solo el docente dueño de esta clase puede administrarla.")
    return classroom


class ClassroomListCreateView(APIView):
    def get(self, request):
        user = request.user
        if user.rol == User.Rol.DOCENTE:
            clases = Classroom.objects.filter(docente=user).prefetch_related(
                "enrollments__student__progress",
                "challenges__student",
                "announcements__author",
            ).order_by("-creada")
        elif user.rol == User.Rol.ESTUDIANTE:
            clases = Classroom.objects.filter(enrollments__student=user).prefetch_related(
                "enrollments__student__progress",
                "challenges__student",
                "announcements__author",
            ).order_by("-creada")
        else:
            clases = Classroom.objects.none()
        return Response(ClassroomSerializer(clases, many=True, context={"request": request}).data)

    def post(self, request):
        if request.user.rol != User.Rol.DOCENTE:
            raise PermissionDenied("Solo los docentes pueden crear clases.")
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        subj = _ensure_default_subject(data.get("subject"))
        data["subject"] = subj.slug
        if not data.get("nivel"):
            data["nivel"] = User.Nivel.SECUNDARIA
        if not data.get("grado"):
            data["grado"] = 1
        serializer = ClassroomSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(docente=request.user, subject=subj)
        return Response(serializer.data, status=201)


class ClassroomDetailView(APIView):
    def get(self, request, class_id: int):
        classroom = get_object_or_404(Classroom, id=class_id)
        is_owner = classroom.docente_id == request.user.id
        is_enrolled = Enrollment.objects.filter(classroom=classroom, student=request.user).exists()
        if not (is_owner or is_enrolled):
            raise PermissionDenied("No tienes acceso a esta clase.")
        return Response(ClassroomSerializer(classroom, context={"request": request}).data)

    def patch(self, request, class_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        data = request.data

        if "nombre" in data and str(data["nombre"]).strip():
            classroom.nombre = str(data["nombre"]).strip()[:100]
        if "nivel" in data and data["nivel"] in {User.Nivel.SECUNDARIA, User.Nivel.BACHILLERATO}:
            classroom.nivel = data["nivel"]
        if "grado" in data:
            try:
                grado = int(data["grado"])
                if 1 <= grado <= 6:
                    classroom.grado = grado
            except (TypeError, ValueError):
                pass
        if "subject" in data and data["subject"]:
            classroom.subject = _ensure_default_subject(str(data["subject"]))
        if "codigo_activo" in data:
            classroom.codigo_activo = bool(data["codigo_activo"])
        if data.get("regenerate_code"):
            classroom.regenerate_code(save=False)

        classroom.save()
        return Response(ClassroomSerializer(classroom, context={"request": request}).data)

    def delete(self, request, class_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        classroom.delete()
        return Response({"status": "deleted", "id": str(class_id)})


class JoinClassroomView(APIView):
    def post(self, request):
        if request.user.rol != User.Rol.ESTUDIANTE:
            raise PermissionDenied("Solo los estudiantes pueden unirse a una clase.")
        codigo = str(request.data.get("codigo", "")).strip().upper()
        if not codigo:
            return Response(
                {
                    "error": {
                        "code": "missing_code",
                        "message": "Escribe el código de invitación de la clase.",
                    }
                },
                status=400,
            )

        clase = Classroom.objects.filter(codigo=codigo).first()
        if not clase:
            return Response(
                {
                    "error": {
                        "code": "invalid_code",
                        "message": "El código no existe. Verifica con tu docente que esté bien escrito.",
                    }
                },
                status=404,
            )
        if not clase.codigo_activo:
            return Response(
                {
                    "error": {
                        "code": "code_inactive",
                        "message": "El docente pausó temporalmente las inscripciones con este código.",
                    }
                },
                status=403,
            )

        _, created = Enrollment.objects.get_or_create(classroom=clase, student=request.user)
        payload = ClassroomSerializer(clase, context={"request": request}).data
        payload["alreadyEnrolled"] = not created
        return Response(payload)


class LeaveClassroomView(APIView):
    def post(self, request, class_id: int):
        deleted, _ = Enrollment.objects.filter(classroom_id=class_id, student=request.user).delete()
        if not deleted:
            return Response(
                {"error": {"code": "not_enrolled", "message": "No estabas inscrito en esa clase."}},
                status=404,
            )
        return Response({"status": "left", "classId": str(class_id)})


class ClassroomStudentManageView(APIView):
    def delete(self, request, class_id: int, student_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        deleted, _ = Enrollment.objects.filter(classroom=classroom, student_id=student_id).delete()
        if not deleted:
            return Response(
                {"error": {"code": "not_enrolled", "message": "El estudiante no está inscrito en este grupo."}},
                status=404,
            )
        return Response({"status": "removed", "studentId": str(student_id)})


class StudentAnalysisDetailView(APIView):
    def get(self, request, class_id: int, student_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        enrollment = get_object_or_404(Enrollment.objects.select_related("student"), classroom=classroom, student_id=student_id)
        student = enrollment.student
        prog, _ = StudentProgress.objects.get_or_create(user=student)
        diag = compute_user_diagnostics(prog, user_obj=student)

        all_challenges = list(classroom.challenges.order_by("-created_at"))
        applicable = [ch for ch in all_challenges if ch.student_id is None or ch.student_id == student.id]
        comp_map = _compute_challenge_completion_map(classroom, applicable, [student.id])

        assigned_challenges = []
        for ch in applicable:
            solved = comp_map.get(ch.id, {}).get(student.id, 0)
            meta = TOPIC_METADATA.get(ch.topic_id, {})
            assigned_challenges.append(
                {
                    "id": str(ch.id),
                    "topicId": ch.topic_id,
                    "topicName": meta.get("topicName", ch.topic_id),
                    "title": ch.title,
                    "instructions": ch.instructions,
                    "targetExercises": ch.target_exercises,
                    "solvedCount": solved,
                    "isCompleted": solved >= ch.target_exercises,
                    "isPersonal": ch.student_id == student.id,
                    "createdAt": format_relative_activity(ch.created_at),
                }
            )

        return Response(
            {
                "id": str(student.id),
                "name": student.alias or student.username,
                "email": student.email,
                "grade": format_student_grade(student),
                "className": classroom.nombre,
                "joinedAt": format_relative_activity(enrollment.unido),
                "lastActive": diag["lastActive"],
                "totalXP": diag["xp"],
                "streakDays": diag["streakDays"],
                "accuracy": diag["accuracy"],
                "completedExercises": diag["completedCount"],
                "totalAttempts": diag["totalAttempts"],
                "hintsUsedTotal": diag.get("hintsUsedTotal", 0),
                "statusLabel": classify_student_status(diag),
                "weakTopics": diag["needsHelpWith"],
                "masteredTopics": diag["masteredTopics"],
                "topics": diag["topics"],
                "recentAttempts": diag["recentAttempts"],
                "recommendations": build_student_recommendations(diag),
                "assignedChallenges": assigned_challenges,
            }
        )


class ClassroomCopySignalsView(APIView):
    """Señales de copia del grupo (solo el docente dueño). Solo conteos: nunca texto de mensajes."""

    def get(self, request, class_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        since = timezone.now() - timedelta(days=WINDOW_DAYS)
        students = [enr.student for enr in classroom.enrollments.select_related("student").order_by("unido")]
        counts = {
            (row["user_id"], row["kind"]): row["n"]
            for row in TutorEvent.objects.filter(user__in=students, created__gte=since)
            .values("user_id", "kind")
            .annotate(n=Count("id"))
        }

        rows = []
        for student in students:
            answer_requests = counts.get((student.id, TutorEvent.Kind.ANSWER_REQUEST), 0)
            bypass_attempts = counts.get((student.id, TutorEvent.Kind.BYPASS_ATTEMPT), 0)
            steps_solved = counts.get((student.id, TutorEvent.Kind.STEP_SOLVED), 0)
            signal, reason = copy_signal(answer_requests + bypass_attempts, steps_solved)
            rows.append(
                {
                    "id": str(student.id),
                    "name": student.alias or student.username,  # La misma etiqueta del panel; nunca el correo.
                    "answerRequests": answer_requests,
                    "bypassAttempts": bypass_attempts,
                    "stepsSolved": steps_solved,
                    "hintsUsed": counts.get((student.id, TutorEvent.Kind.HINT_USED), 0),
                    "copySignal": signal,
                    "reason": reason,
                }
            )
        rows.sort(key=lambda r: (r["copySignal"] != "revisar", -(r["answerRequests"] + r["bypassAttempts"])))

        def total(field):
            return sum(row[field] for row in rows)

        return Response(
            {
                "classId": str(classroom.id),
                "className": classroom.nombre,
                "windowDays": WINDOW_DAYS,
                "rule": RULE_TEXT,
                "privacyNote": "Solo se cuentan eventos (tipo, tema y fecha). No se guarda el texto de los mensajes.",
                "totals": {
                    "students": len(rows),
                    "studentsToReview": sum(1 for row in rows if row["copySignal"] == "revisar"),
                    "answerRequests": total("answerRequests"),
                    "bypassAttempts": total("bypassAttempts"),
                    "stepsSolved": total("stepsSolved"),
                    "hintsUsed": total("hintsUsed"),
                },
                "students": rows,
                "recommendations": RECOMMENDATIONS,
            }
        )


class ClassroomChallengeListCreateView(APIView):
    def post(self, request, class_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        topic_id = str(request.data.get("topic_id", "")).strip()
        if topic_id not in TOPIC_METADATA:
            return Response(
                {"error": {"code": "invalid_topic", "message": "El tema seleccionado no es válido."}},
                status=400,
            )

        meta = TOPIC_METADATA[topic_id]
        title = str(request.data.get("title", "")).strip() or f"Refuerzo: {meta['topicName']}"
        instructions = str(request.data.get("instructions", "")).strip()
        try:
            target_exercises = max(1, min(10, int(request.data.get("target_exercises", 2))))
        except (TypeError, ValueError):
            target_exercises = 2

        student_obj = None
        raw_student_id = request.data.get("student_id")
        if raw_student_id:
            enr = get_object_or_404(Enrollment.objects.select_related("student"), classroom=classroom, student_id=raw_student_id)
            student_obj = enr.student

        ClassChallenge.objects.create(
            classroom=classroom,
            assigned_by=request.user,
            student=student_obj,
            topic_id=topic_id,
            title=title[:140],
            instructions=instructions,
            target_exercises=target_exercises,
        )
        return Response(ClassroomSerializer(classroom, context={"request": request}).data, status=201)


class ClassroomChallengeDeleteView(APIView):
    def delete(self, request, class_id: int, challenge_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        deleted, _ = ClassChallenge.objects.filter(id=challenge_id, classroom=classroom).delete()
        if not deleted:
            return Response(
                {"error": {"code": "not_found", "message": "Reto no encontrado."}},
                status=404,
            )
        return Response(ClassroomSerializer(classroom, context={"request": request}).data)


class ClassroomAnnouncementListCreateView(APIView):
    def post(self, request, class_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        title = str(request.data.get("title", "")).strip() or "Aviso del docente"
        message = str(request.data.get("message", "")).strip()
        if not message:
            return Response(
                {"error": {"code": "missing_message", "message": "El mensaje del aviso no puede estar vacío."}},
                status=400,
            )

        ClassAnnouncement.objects.create(
            classroom=classroom,
            author=request.user,
            title=title[:140],
            message=message,
        )
        return Response(ClassroomSerializer(classroom, context={"request": request}).data, status=201)


class ClassroomAnnouncementDeleteView(APIView):
    def delete(self, request, class_id: int, announcement_id: int):
        classroom = _get_teacher_classroom_or_403(request.user, class_id)
        deleted, _ = ClassAnnouncement.objects.filter(id=announcement_id, classroom=classroom).delete()
        if not deleted:
            return Response(
                {"error": {"code": "not_found", "message": "Aviso no encontrado."}},
                status=404,
            )
        return Response(ClassroomSerializer(classroom, context={"request": request}).data)
