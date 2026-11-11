
from pathlib import Path

from gojarol_ml.nlp.topic_retriever import TopicRetriever


BASE_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = BASE_DIR / "data" / "knowledge" / "topics.json"


def main():
    retriever = TopicRetriever(CATALOG_PATH)

    messages = [
        "Explicame como resolver ecuaciones",
        "Necesito ayuda con la hipotenusa",
        "No entiendo las fracciones",
        "Como puedo calcular un descuento",
        "Que es la idea principal de un texto",
        "Explicame las palabras graves",
        "Dame una pista",
        "Quiero cambiar de fracciones a Pitagoras",
    ]

    for message in messages:
        result = retriever.find_topic(message)

        print(f"\nMensaje: {message}")
        print(f"Materia: {result['subject']}")
        print(f"Tema: {result['topic']}")
        print(f"Coincidencia: {result['topic_score']:.2f}")
        print(f"Metodo: {result['match_method']}")
        print(
            f"Requiere aclaracion: "
            f"{result['needs_clarification']}"
        )


if __name__ == "__main__":
    main()
