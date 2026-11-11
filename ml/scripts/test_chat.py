
from pathlib import Path

import joblib


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "artifacts" / "intent_classifier.joblib"


def main():
    model = joblib.load(MODEL_PATH)

    print("=== Go Jarol NLP ===")
    print("Escribe 'salir' para terminar.\n")

    while True:
        message = input("Alumno: ").strip()

        if message.lower() == "salir":
            print("Prueba finalizada.")
            break

        if not message:
            continue

        probabilities = model.predict_proba([message])[0]
        index = probabilities.argmax()

        intent = model.classes_[index]
        confidence = probabilities[index]

        print(f"Intencion: {intent}")
        print(f"Confianza estimada: {confidence:.2%}\n")


if __name__ == "__main__":
    main()
