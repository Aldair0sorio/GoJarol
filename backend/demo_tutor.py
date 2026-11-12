
from pathlib import Path
import argparse

from gojarol_ml.nlp.analyzer import JarolAnalyzer

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService
from curriculum.services.curriculum_catalog import CurriculumCatalog
from gojarol_ml.nlp.curriculum_retriever import CurriculumRetriever


ROOT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    ROOT_DIR / "ml" / "artifacts" / "intent_classifier.joblib"
)

CATALOG_PATH = (
    ROOT_DIR / "ml" / "data" / "knowledge" / "topics.json"
)

CONTENT_DIR = ROOT_DIR / "content" / "topics"


def main():
    parser = argparse.ArgumentParser(description="Conversación con NLP real y contexto curricular opcional.")
    parser.add_argument("--level", choices=("secundaria", "bachillerato"))
    parser.add_argument("--grade", type=int)
    parser.add_argument("--semester", type=int)
    parser.add_argument("--model")
    parser.add_argument("--program-id")
    args = parser.parse_args()
    academic_context = {key: value for key, value in vars(args).items() if value is not None}
    curriculum = CurriculumCatalog()
    analyzer = JarolAnalyzer(
        model_path=MODEL_PATH,
        catalog_path=CATALOG_PATH,
        curriculum_retriever=CurriculumRetriever(curriculum.entries),
    )

    knowledge = KnowledgeService(CONTENT_DIR)
    hints = HintService(knowledge)

    tutor = TutorService(
        analyzer=analyzer,
        knowledge=knowledge,
        hints=hints,
        curriculum=curriculum,
    )

    state = tutor.initial_state()

    print("\nGO JAROL - PRUEBA DE CONVERSACION")
    print("Escribe 'salir' para terminar.\n")
    print("Jarol: Hola, ¿qué te gustaria aprender?")

    while True:
        message = input("\nTu: ").strip()

        if message.lower() in {"salir", "exit"}:
            print("Jarol: ¡Hasta pronto!")
            break

        if not message:
            continue

        result = tutor.process_message(message, state, academic_context=academic_context or None)

        state = result["state"]

        print(f"\nJarol: {result['message']}")
        print(f"[Accion: {result['type']}]")
        if result.get("curriculum"):
            print(f"[Competencia: {result['curriculum'].get('competency_id') or 'práctica sin asignación curricular'}]")

        if result["type"] == "evaluation":
            print(
                f"[Siguiente paso: {result['next_action']}]"
            )


if __name__ == "__main__":
    main()
