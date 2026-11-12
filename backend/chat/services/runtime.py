import sys
from functools import lru_cache
from pathlib import Path


def _resolve_root_dirs() -> tuple[Path, Path]:
    # En Docker (/app/chat/services/runtime.py -> parents[3] == /),
    # montamos /ml y /content. En entorno local está en repo_root/ml y repo_root/content.
    candidates = [
        Path(__file__).resolve().parents[3],
        Path(__file__).resolve().parents[2],
        Path("/"),
    ]
    for base in candidates:
        ml_dir = base / "ml"
        content_dir = base / "content"
        if ml_dir.is_dir() and content_dir.is_dir():
            return ml_dir, content_dir
    raise FileNotFoundError("No se encontraron los directorios 'ml' y 'content'.")


ML_DIR, CONTENT_DIR = _resolve_root_dirs()
ML_SRC = str(ML_DIR / "src")
if ML_SRC not in sys.path:
    sys.path.insert(0, ML_SRC)

from gojarol_ml.nlp.analyzer import JarolAnalyzer  # noqa: E402
from gojarol_ml.nlp.curriculum_retriever import CurriculumRetriever  # noqa: E402

from chat.services.tutor_service import TutorService  # noqa: E402
from curriculum.services.curriculum_catalog import CurriculumCatalog  # noqa: E402
from curriculum.services.knowledge_service import KnowledgeService  # noqa: E402
from exercises.services.exercise_selector import ExerciseSelector  # noqa: E402
from exercises.services.hint_service import HintService  # noqa: E402
from progress.services.adaptive_learning_service import AdaptiveLearningService  # noqa: E402


TOPIC_METADATA = {
    "mat_fracciones": {
        "subjectName": "Aritmética · Matemáticas",
        "topicName": "Fracciones Equivalentes y Suma",
    },
    "mat_ecuaciones": {
        "subjectName": "Álgebra · Matemáticas",
        "topicName": "Ecuaciones Lineales de Primer Grado",
    },
    "mat_porcentajes": {
        "subjectName": "Aritmética · Matemáticas",
        "topicName": "Porcentajes y Proporcionalidad",
    },
    "esp_comprension": {
        "subjectName": "Español · Lenguajes",
        "topicName": "Comprensión Lectora",
    },
    "esp_ortografia": {
        "subjectName": "Español · Lenguajes",
        "topicName": "Ortografía Puntual y Grafías",
    },
    "esp_acentuacion": {
        "subjectName": "Español · Lenguajes",
        "topicName": "Reglas de Acentuación",
    },
}

DIFFICULTY_LABELS = {
    1: "Básico",
    2: "Intermedio",
    3: "Avanzado",
}

INSTRUCTION_BY_TYPE = {
    "multiple_choice": "Lee con calma y selecciona la opción correcta o pide una pista paso a paso.",
    "fraction": "Calcula y escribe tu resultado como fracción o entero (por ejemplo: 3/4).",
    "numeric": "Resuelve paso a paso y escribe el valor numérico (por ejemplo: 7 o x = 7).",
    "percentage": "Calcula el porcentaje y escribe el valor numérico (por ejemplo: 25 o 25%).",
}


class TutorRuntime:
    def __init__(self):
        model_path = ML_DIR / "artifacts" / "intent_classifier.joblib"
        catalog_path = ML_DIR / "data" / "knowledge" / "topics.json"
        topics_dir = CONTENT_DIR / "topics"
        exercises_dir = CONTENT_DIR / "exercises"
        curriculum_dir = CONTENT_DIR / "curriculum"

        self.curriculum = CurriculumCatalog(curriculum_dir)
        self.analyzer = JarolAnalyzer(
            model_path=model_path,
            catalog_path=catalog_path,
            curriculum_retriever=CurriculumRetriever(self.curriculum.entries),
        )
        self.knowledge = KnowledgeService(topics_dir)
        self.selector = ExerciseSelector(exercises_dir)
        self.hints = HintService(self.knowledge, self.selector)
        self.adaptive = AdaptiveLearningService()
        self.tutor = TutorService(
            analyzer=self.analyzer,
            knowledge=self.knowledge,
            hints=self.hints,
            adaptive=self.adaptive,
            selector=self.selector,
            curriculum=self.curriculum,
        )

    def find_topic_for_exercise(self, exercise_id: str) -> str | None:
        for topic_id, exercises in self.selector._exercises.items():
            if exercise_id in exercises:
                return topic_id
        return None

    def format_exercise_for_frontend(self, topic_id: str | None, raw_exercise: dict | None) -> dict | None:
        if not raw_exercise:
            return None
        resolved_topic = topic_id or self.find_topic_for_exercise(raw_exercise.get("id", "")) or "mat_fracciones"
        meta = TOPIC_METADATA.get(
            resolved_topic,
            {"subjectName": "Práctica Guiada", "topicName": resolved_topic},
        )
        ex_type = raw_exercise.get("type", "multiple_choice")
        options_dict = raw_exercise.get("options") or {}
        options_list = [
            {"id": str(label), "label": str(label), "text": str(text)}
            for label, text in options_dict.items()
        ]
        return {
            "id": raw_exercise["id"],
            "topicId": resolved_topic,
            "subjectName": meta["subjectName"],
            "topicName": meta["topicName"],
            "question": raw_exercise["question"],
            "readingText": raw_exercise.get("reading_text"),
            "instruction": INSTRUCTION_BY_TYPE.get(ex_type, INSTRUCTION_BY_TYPE["multiple_choice"]),
            "exerciseType": ex_type,
            "difficulty": DIFFICULTY_LABELS.get(raw_exercise.get("difficulty", 1), "Básico"),
            "options": options_list,
        }


@lru_cache(maxsize=1)
def get_runtime() -> TutorRuntime:
    return TutorRuntime()
