"""Evalua el modelo con pruebas NO usadas para ajustarlo.

Ejecutar solo despues de finalizar decisiones sobre hiperparametros. No usar
los resultados de test para seguir modificando el clasificador una y otra vez.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "artifacts" / "intent_classifier.joblib"
DATA_DIR = BASE_DIR / "data" / "raw"


def evaluate(model, file_name: str):
    data = pd.read_csv(DATA_DIR / file_name, encoding="utf-8")
    pred = model.predict(data.text.astype(str))
    accuracy = float(accuracy_score(data.intent, pred))
    macro_f1 = float(f1_score(data.intent, pred, average="macro"))
    print(f"\n--- {file_name} | {len(data)} mensajes ---")
    print(f"Accuracy: {accuracy:.4f} | Macro-F1: {macro_f1:.4f}")
    print(classification_report(data.intent, pred, zero_division=0))
    errors = data.loc[data.intent != pred, ["text", "intent"]].copy()
    errors["predicted"] = pred[data.intent.to_numpy() != pred]
    print("Ejemplos de errores (max. 20):")
    print(errors.head(20).to_string(index=False) if len(errors) else "Sin errores en este conjunto")
    return {"rows": len(data), "accuracy": accuracy, "macro_f1": macro_f1,
            "errors": len(errors)}


def main():
    if not MODEL_PATH.exists():
        raise SystemExit("No hay modelo. Ejecuta primero train_intents.py")
    # Los archivos joblib se deben cargar SOLO desde un origen confiable.
    model = joblib.load(MODEL_PATH)
    results = {}
    for name in ("intents_test.csv", "intents_realistic_test.csv"):
        results[name] = evaluate(model, name)
    output = BASE_DIR / "artifacts" / "test_metrics.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReporte guardado: {output}")
    print("IMPORTANTE: Falta una prueba nueva con frases de personas ajenas al dataset.")


if __name__ == "__main__":
    main()
