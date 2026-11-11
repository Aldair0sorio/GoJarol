
from pathlib import Path

from gojarol_ml.nlp.analyzer import JarolAnalyzer


BASE_DIR = Path(__file__).resolve().parents[1]

analyzer = JarolAnalyzer(
    model_path=BASE_DIR / "artifacts" / "intent_classifier.joblib",
    catalog_path=BASE_DIR / "data" / "knowledge" / "topics.json",
)


def main():
    examples = [
        (
            "Explícame cómo resolver ecuaciones",
            {},
        ),
        (
            "Ponme un ejercicio de fracciones",
            {},
        ),
        (
            "Dame una pista",
            {"current_topic": "mat_fracciones"},
        ),
        (
            "No entiendo las palabras graves",
            {},
        ),
        (
            "Quiero cambiar de fracciones a Pitágoras",
            {"current_topic": "mat_fracciones"},
        ),
    ]

    for message, context in examples:
        result = analyzer.analyze_message(message, context)

        print(f"\nAlumno: {message}")
        print(f"Intención: {result['intent']}")
        print(f"Materia: {result['subject']}")
        print(f"Tema: {result['topic']}")
        print(f"Origen: {result['match_method']}")
        print(f"Aclaración: {result['needs_clarification']}")


if __name__ == "__main__":
    main()
