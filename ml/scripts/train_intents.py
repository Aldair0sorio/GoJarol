"""Entrena y valida el clasificador de intenciones de Go Jarol.

IMPORTANTE: NO hace train_test_split de datos sinteticos: los CSV ya estan
separados por familias de plantillas para reducir leakage.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
MODEL_DIR = BASE_DIR / "artifacts"


def read_dataset(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    df = pd.read_csv(path, encoding="utf-8")
    if not {"text", "intent"}.issubset(df.columns):
        raise ValueError(f"Se requieren columnas text,intent: {path}")
    if df[["text", "intent"]].isna().any().any():
        raise ValueError(f"Hay valores vacios en {path}")
    if df["text"].duplicated().any():
        raise ValueError(f"Hay textos duplicados en {path}")
    return df


def main() -> None:
    train = read_dataset("intents_train.csv")
    val = read_dataset("intents_validation.csv")
    if set(train.intent.unique()) != set(val.intent.unique()):
        raise ValueError("Las clases de train y validacion deben coincidir")
    if set(train.text).intersection(val.text):
        raise ValueError("Se detectaron textos compartidos entre train y validacion")

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_features=200000,
            strip_accents="unicode",
            sublinear_tf=True,
        )),
        ("classifier", LogisticRegression(
            max_iter=1200,
            class_weight="balanced",
            random_state=42,
        )),
    ])
    print(f"Entrenamiento: {len(train):,} ejemplos | {train.intent.nunique()} intenciones")
    print(f"Validacion: {len(val):,} ejemplos (plantillas distintas)")
    model.fit(train.text, train.intent)
    pred = model.predict(val.text)
    print(f"Accuracy validacion: {accuracy_score(val.intent, pred):.4f}")
    print(f"F1 macro validacion: {f1_score(val.intent, pred, average='macro'):.4f}")
    print(classification_report(val.intent, pred, zero_division=0))
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / "intent_classifier.joblib"
    joblib.dump(model, path)
    metadata = {
        "version": "synthetic-50000-v1",
        "train_rows": len(train),
        "validation_rows": len(val),
        "intent_labels": sorted(train.intent.unique().tolist()),
        "validation_accuracy": round(float(accuracy_score(val.intent, pred)), 5),
        "validation_macro_f1": round(float(f1_score(val.intent, pred, average="macro")), 5),
        "warning": "Validacion sintetica, no demuestra rendimiento con estudiantes reales",
    }
    (MODEL_DIR / "intent_classifier_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Modelo guardado: {path}")


if __name__ == "__main__":
    main()
