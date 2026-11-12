from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class TeacherStudentClassroomFlowTests(TestCase):
    def setUp(self):
        self.teacher_client = APIClient()
        self.student_client = APIClient()
        self.other_student_client = APIClient()

        res_t = self.teacher_client.post(
            "/api/v1/auth/register/",
            {
                "username": "profe_ana",
                "email": "ana@docentes.sev.gob.mx",
                "password": "PasswordSegura2026!",
                "rol": "docente",
                "alias": "Prof. Ana Ruiz",
            },
            format="json",
        )
        self.assertEqual(res_t.status_code, 201)
        self.teacher_token = res_t.data["token"]
        self.teacher_client.credentials(HTTP_AUTHORIZATION=f"Token {self.teacher_token}")

        res_s = self.student_client.post(
            "/api/v1/auth/register/",
            {
                "username": "luis_est",
                "email": "luis@estudiantes.sev.gob.mx",
                "password": "PasswordSegura2026!",
                "rol": "estudiante",
                "nivel": "secundaria",
                "grado": 3,
                "alias": "Luis Hernández",
            },
            format="json",
        )
        self.assertEqual(res_s.status_code, 201)
        self.student_token = res_s.data["token"]
        self.student_id = res_s.data["user"]["id"]
        self.student_client.credentials(HTTP_AUTHORIZATION=f"Token {self.student_token}")

        res_s2 = self.other_student_client.post(
            "/api/v1/auth/register/",
            {
                "username": "maria_est",
                "email": "maria@estudiantes.sev.gob.mx",
                "password": "PasswordSegura2026!",
                "rol": "estudiante",
                "nivel": "secundaria",
                "grado": 2,
                "alias": "María López",
            },
            format="json",
        )
        self.assertEqual(res_s2.status_code, 201)
        self.other_student_client.credentials(
            HTTP_AUTHORIZATION=f"Token {res_s2.data['token']}"
        )

    def test_full_teacher_class_join_analytics_challenges_and_cleanup(self):
        # 1. Docente crea una clase
        create_res = self.teacher_client.post(
            "/api/v1/classes/",
            {
                "nombre": "3° A Matemáticas",
                "subject": "aritmetica",
                "nivel": "secundaria",
                "grado": 3,
            },
            format="json",
        )
        self.assertEqual(create_res.status_code, 201)
        class_id = create_res.data["id"]
        code = create_res.data["codigo"]
        self.assertTrue(code.startswith("JAROL-"))

        # Estudiante no puede crear clases
        forbidden_create = self.student_client.post(
            "/api/v1/classes/",
            {"nombre": "Hack Class"},
            format="json",
        )
        self.assertEqual(forbidden_create.status_code, 403)

        # 2. Estudiante se une con código (en minúsculas y espacios)
        join_res = self.student_client.post(
            "/api/v1/classes/join/",
            {"codigo": f"  {code.lower()}  "},
            format="json",
        )
        self.assertEqual(join_res.status_code, 200)
        self.assertFalse(join_res.data["alreadyEnrolled"])

        # Reintentar unión no duplica ni falla
        rejoin_res = self.student_client.post(
            "/api/v1/classes/join/",
            {"codigo": code},
            format="json",
        )
        self.assertEqual(rejoin_res.status_code, 200)
        self.assertTrue(rejoin_res.data["alreadyEnrolled"])

        # 3. Docente pausa el código y otro alumno no puede entrar
        patch_pause = self.teacher_client.patch(
            f"/api/v1/classes/{class_id}/",
            {"codigo_activo": False},
            format="json",
        )
        self.assertEqual(patch_pause.status_code, 200)
        self.assertFalse(patch_pause.data["codigo_activo"])

        blocked_join = self.other_student_client.post(
            "/api/v1/classes/join/",
            {"codigo": code},
            format="json",
        )
        self.assertEqual(blocked_join.status_code, 403)
        self.assertEqual(blocked_join.data["error"]["code"], "code_inactive")

        # Reactivar y regenerar código
        regen_res = self.teacher_client.patch(
            f"/api/v1/classes/{class_id}/",
            {"codigo_activo": True, "regenerate_code": True},
            format="json",
        )
        self.assertEqual(regen_res.status_code, 200)
        new_code = regen_res.data["codigo"]
        self.assertNotEqual(new_code, code)

        old_code_res = self.other_student_client.post(
            "/api/v1/classes/join/",
            {"codigo": code},
            format="json",
        )
        self.assertEqual(old_code_res.status_code, 404)

        # 4. Docente asigna un reto personalizado y publica un aviso
        chal_res = self.teacher_client.post(
            f"/api/v1/classes/{class_id}/challenges/",
            {
                "topic_id": "mat_fracciones",
                "student_id": self.student_id,
                "title": "Refuerzo de fracciones",
                "instructions": "Resuelve al menos 1 reto de suma con igual denominador.",
                "target_exercises": 1,
            },
            format="json",
        )
        self.assertEqual(chal_res.status_code, 201)
        self.assertEqual(len(chal_res.data["challenges"]), 1)

        ann_res = self.teacher_client.post(
            f"/api/v1/classes/{class_id}/announcements/",
            {
                "title": "Repaso semanal",
                "message": "Completen sus retos asignados antes del viernes.",
            },
            format="json",
        )
        self.assertEqual(ann_res.status_code, 201)
        self.assertEqual(len(ann_res.data["announcements"]), 1)

        # 5. Estudiante falla primero (frac_001 -> respuesta incorrecta) y luego acierta ("3/4")
        wrong_ans = self.student_client.post(
            "/api/v1/exercises/frac_001/answer/",
            {"answer": "1/4"},
            format="json",
        )
        self.assertEqual(wrong_ans.status_code, 200)
        self.assertFalse(wrong_ans.data["isCorrect"])

        right_ans = self.student_client.post(
            "/api/v1/exercises/frac_001/answer/",
            {"answer": "3/4"},
            format="json",
        )
        self.assertEqual(right_ans.status_code, 200)
        self.assertTrue(right_ans.data["isCorrect"])
        self.assertGreater(right_ans.data["xpEarned"], 0)

        # 6. Docente consulta análisis real de clase y detalle del alumno
        teacher_list = self.teacher_client.get("/api/v1/classes/")
        self.assertEqual(teacher_list.status_code, 200)
        cls_data = teacher_list.data[0]
        self.assertEqual(cls_data["estudiantes"], 1)
        self.assertEqual(cls_data["averageMastery"], 50)
        self.assertEqual(cls_data["totalCompletedExercises"], 1)
        self.assertEqual(cls_data["challenges"][0]["completedByCount"], 1)

        frac_topic = next(t for t in cls_data["topic_analytics"] if t["topicId"] == "mat_fracciones")
        self.assertEqual(frac_topic["activeStudents"], 1)
        self.assertEqual(frac_topic["averageAccuracy"], 50)

        student_detail = self.teacher_client.get(
            f"/api/v1/classes/{class_id}/students/{self.student_id}/analysis/"
        )
        self.assertEqual(student_detail.status_code, 200)
        self.assertEqual(student_detail.data["accuracy"], 50)
        self.assertEqual(student_detail.data["completedExercises"], 1)
        self.assertEqual(len(student_detail.data["recentAttempts"]), 2)
        self.assertTrue(student_detail.data["assignedChallenges"][0]["isCompleted"])
        self.assertNotIn("expected_answer", str(student_detail.data))

        # Estudiante también ve su reto completado en GET /api/v1/classes/
        stu_classes = self.student_client.get("/api/v1/classes/")
        self.assertEqual(stu_classes.status_code, 200)
        self.assertTrue(stu_classes.data[0]["challenges"][0]["isCompleted"])
        self.assertEqual(len(stu_classes.data[0]["announcements"]), 1)

        # 7. Estudiante no puede ver análisis del grupo ni remover alumnos
        self.assertEqual(
            self.other_student_client.get(
                f"/api/v1/classes/{class_id}/students/{self.student_id}/analysis/"
            ).status_code,
            403,
        )

        # Docente da de baja al alumno y elimina la clase
        del_student = self.teacher_client.delete(
            f"/api/v1/classes/{class_id}/students/{self.student_id}/"
        )
        self.assertEqual(del_student.status_code, 200)

        del_class = self.teacher_client.delete(f"/api/v1/classes/{class_id}/")
        self.assertEqual(del_class.status_code, 200)

    def test_demo_login_and_switch_role(self):
        res_demo = self.teacher_client.post(
            "/api/v1/auth/demo/",
            {"profile": "teacher"},
            format="json",
        )
        self.assertEqual(res_demo.status_code, 200)
        self.assertEqual(res_demo.data["user"]["rol"], "docente")
        self.assertIn("token", res_demo.data)

        demo_client = APIClient()
        demo_client.credentials(HTTP_AUTHORIZATION=f"Token {res_demo.data['token']}")
        sw = demo_client.post("/api/v1/auth/switch-role/", {"role": "student"}, format="json")
        self.assertEqual(sw.status_code, 200)
        self.assertEqual(sw.data["user"]["rol"], "estudiante")
