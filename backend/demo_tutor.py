
from pathlib import Path

from gojarol_ml.nlp.analyzer import JarolAnalyzer

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService


ROOT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    ROOT_DIR / "ml" / "artifacts" / "intent_classifier.joblib"
)

CATALOG_PATH = (
    ROOT_DIR / "ml" / "data" / "knowledge" / "topics.json"
)

CONTENT_DIR = ROOT_DIR / "content" / "topics"


def main():
    analyzer = JarolAnalyzer(
        model_path=MODEL_PATH,
        catalog_path=CATALOG_PATH,
    )

    knowledge = KnowledgeService(CONTENT_DIR)
    hints = HintService(knowledge)

    tutor = TutorService(
        analyzer=analyzer,
        knowledge=knowledge,
        hints=hints,
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

        result = tutor.process_message(message, state)

        state = result["state"]

        print(f"\nJarol: {result['message']}")
        print(f"[Accion: {result['type']}]")

        if result["type"] == "evaluation":
            print(
                f"[Siguiente paso: {result['next_action']}]"
            )


if __name__ == "__main__":
    main()
