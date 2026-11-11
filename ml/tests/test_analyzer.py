
from pathlib import Path

import pytest

from gojarol_ml.nlp.analyzer import JarolAnalyzer


BASE_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def analyzer():
    return JarolAnalyzer(
        model_path=BASE_DIR / "artifacts" / "intent_classifier.joblib",
        catalog_path=BASE_DIR / "data" / "knowledge" / "topics.json",
    )


@pytest.mark.parametrize(
    "message,expected_intent,expected_topic",
    [
        (
            "Explícame cómo resolver ecuaciones",
            "solicitar_explicacion",
            "mat_ecuaciones",
        ),
        (
            "Ponme un ejercicio de fracciones",
            "solicitar_reto",
            "mat_fracciones",
        ),
        (
            "Quiero cambiar de fracciones a Pitágoras",
            "cambiar_tema",
            "mat_pitagoras",
        ),
    ],
)
def test_analyze_message(
    analyzer, message, expected_intent, expected_topic
):
    result = analyzer.analyze_message(message)

    assert result["intent"] == expected_intent
    assert result["topic"] == expected_topic
    assert result["needs_clarification"] is False


def test_context_recovery(analyzer):
    result = analyzer.analyze_message(
        "Dame una pista",
        {"current_topic": "mat_fracciones"},
    )

    assert result["intent"] == "solicitar_pista"
    assert result["topic"] == "mat_fracciones"
    assert result["match_method"] == "context"


def test_ambiguous_topics(analyzer):
    result = analyzer.analyze_message(
        "Compara fracciones con el teorema de Pitágoras"
    )

    assert result["needs_clarification"] is True
    assert result["topic"] is None
