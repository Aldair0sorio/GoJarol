"""Jarol pregunta antes de explicar: menú de diagnóstico A/B/C por tema."""
import json
import re
from pathlib import Path
from unittest.mock import Mock

import pytest
from sympy import Rational, nsimplify

from chat.services.tutor_service import TutorService
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.hint_service import HintService
from gojarol_ml.nlp.analyzer import JarolAnalyzer


ROOT = Path(__file__).resolve().parents[2]
TOPICS = {
    "mat_fracciones": "no entiendo las fracciones",
    "mat_ecuaciones": "explícame las ecuaciones",
    "mat_porcentajes": "explícame los porcentajes",
    "esp_comprension": "no entiendo la comprensión lectora",
    "esp_acentuacion": "explícame la acentuación",
    "esp_ortografia": "explícame la ortografía",
}


@pytest.fixture(scope="module")
def analyzer():
    return JarolAnalyzer(ROOT / "ml/artifacts/intent_classifier.joblib", ROOT / "ml/data/knowledge/topics.json")


@pytest.fixture
def tutor(analyzer):
    knowledge = KnowledgeService(ROOT / "content/topics")
    return TutorService(analyzer, knowledge, HintService(knowledge))


def ask_menu(tutor, topic):
    result = tutor.process_message(TOPICS[topic])
    assert result["type"] == "explanation_menu"
    return result


def spy_on_classifier(tutor):
    spy = Mock(wraps=tutor.analyzer)
    tutor.analyzer = spy
    return spy


# --- La pregunta aparece primero ---------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_explanation_request_gets_diagnostic_question_first(tutor, topic):
    result = ask_menu(tutor, topic)
    menu = tutor.knowledge.get_explanation_menu(topic)

    assert result["state"]["current_topic"] == topic
    assert result["state"]["pending_explanation_menu"] == {"topic": topic}
    assert result["message"].startswith(menu["question"])
    for option in menu["options"]:
        assert f"{option['label']}) {option['text']}" in result["message"]
    assert [option["label"] for option in result["menu"]] == ["A", "B", "C"]
    # Todavía no explica: ni la explicación completa ni la de alguna opción.
    assert tutor.knowledge.get_explanation(topic, "basic") not in result["message"]
    for option in menu["options"]:
        assert tutor.knowledge.get_menu_explanation(topic, option["label"]) not in result["message"]


def test_repeated_request_without_choosing_gives_full_explanation(tutor):
    first = ask_menu(tutor, "mat_fracciones")
    second = tutor.process_message("no entiendo las fracciones", first["state"])

    assert second["type"] == "explanation"
    assert second["message"] == tutor.knowledge.get_explanation("mat_fracciones", "basic")
    assert second["state"]["pending_explanation_menu"] is None


def test_active_exercise_skips_menu_because_its_options_also_use_letters(tutor):
    exercise = tutor.process_message("Ponme un ejercicio de acentuación")
    result = tutor.process_message("explícame la acentuación", exercise["state"])

    assert result["type"] == "explanation"
    assert result["state"]["pending_explanation_menu"] is None


# --- La letra (o el texto de la opción) se interpreta bien ---------------------

@pytest.mark.parametrize("answer,label", [
    ("a", "A"), ("B", "B"), ("b)", "B"), ("C.", "C"), ("la c", "C"), ("opción A", "A"), ("inciso b", "B"),
])
def test_letter_answer_explains_only_that_part_without_classifier(tutor, answer, label):
    menu = ask_menu(tutor, "mat_porcentajes")
    spy = spy_on_classifier(tutor)

    result = tutor.process_message(answer, menu["state"])

    spy.analyze_message.assert_not_called()
    assert result["type"] == "explanation"
    assert result["menu_choice"] == label
    assert result["message"] == tutor.knowledge.get_menu_explanation("mat_porcentajes", label)
    assert result["state"]["pending_explanation_menu"] is None


@pytest.mark.parametrize("topic", TOPICS)
def test_bare_b_is_no_longer_a_farewell(tutor, topic):
    menu = ask_menu(tutor, topic)
    result = tutor.process_message("b", menu["state"])

    assert result["type"] == "explanation"
    assert "Hasta pronto" not in result["message"]
    assert result["state"]["current_topic"] == topic


@pytest.mark.parametrize("answer,label", [
    ("Sumar o restar fracciones con distinto denominador", "C"),
    ("qué significan el numerador y el denominador", "A"),
    ("distinto denominador", "C"),
    ("con el mismo denominador", "B"),
])
def test_option_text_answer_is_recognized(tutor, answer, label):
    menu = ask_menu(tutor, "mat_fracciones")
    result = tutor.process_message(answer, menu["state"])

    assert result["menu_choice"] == label
    assert result["message"] == tutor.knowledge.get_menu_explanation("mat_fracciones", label)


def test_ambiguous_or_unrelated_message_follows_normal_flow(tutor):
    menu = ask_menu(tutor, "mat_fracciones")
    spy = spy_on_classifier(tutor)

    result = tutor.process_message("Ponme un ejercicio de fracciones", menu["state"])

    spy.analyze_message.assert_called_once()
    assert result["type"] == "exercise"
    assert result["state"]["pending_explanation_menu"] is None
    assert "menu_choice" not in result


def test_letter_outside_listed_options_is_not_taken_as_a_choice(tutor):
    menu = ask_menu(tutor, "mat_fracciones")
    spy = spy_on_classifier(tutor)

    result = tutor.process_message("d", menu["state"])

    spy.analyze_message.assert_called_once()
    assert "menu_choice" not in result
    assert result["state"]["pending_explanation_menu"] is None


@pytest.mark.parametrize("topic", TOPICS)
def test_each_part_is_short_and_ends_with_practice_invitation(tutor, topic):
    menu = tutor.knowledge._get_topic(topic)["explanation_menu"]
    assert len(menu["options"]) == 3
    for option in menu["options"]:
        text = tutor.knowledge.get_menu_explanation(topic, option["label"])
        assert text.endswith(f"«{menu['practice_prompt']}».")
        assert len(option["explanation"]) <= 420
        # Sin preguntas de comprobación que el sistema no pueda evaluar.
        assert "¿" not in text and "?" not in text


# --- No se filtra ningún resultado ---------------------------------------------

NUMBER = re.compile(r"-?\d+(?:/\d+)?")
CONCEPT_WORDS = {"aguda", "grave", "esdrujula", "esdrújula"}


def bank(topic):
    data = json.loads((ROOT / "content/exercises" / f"{topic}.json").read_text(encoding="utf-8"))
    return data["exercises"]


def assert_no_leak(topic, text):
    tokens = set(NUMBER.findall(text))
    folded = text.casefold()
    for exercise in bank(topic):
        assert exercise["question"].casefold() not in folded, exercise["id"]
        if exercise.get("answer_explanation"):
            assert exercise["answer_explanation"].casefold() not in folded, exercise["id"]
        if exercise["type"] in {"fraction", "numeric", "percentage"}:
            assert exercise["expected_answer"] not in tokens, exercise["id"]
        options = exercise.get("options") or {}
        correct = options.get(exercise["expected_answer"])
        if correct and correct.casefold() not in CONCEPT_WORDS:
            assert not re.search(rf"(?<!\w){re.escape(correct.casefold())}(?!\w)", folded), exercise["id"]


@pytest.mark.parametrize("topic", TOPICS)
def test_menu_and_parts_do_not_leak_exercise_answers(tutor, topic):
    menu = ask_menu(tutor, topic)
    assert_no_leak(topic, menu["message"])
    for label in "ABC":
        part = tutor.process_message(label.lower(), menu["state"])
        assert_no_leak(topic, part["message"])


@pytest.mark.parametrize("problem,expected", [
    ("2/7 + 3/7", Rational(5, 7)),
    ("3/8 + 1/4", Rational(5, 8)),
])
def test_student_problem_result_never_appears(tutor, problem, expected):
    menu = tutor.process_message(f"no entiendo las fracciones, ¿cuánto es {problem}?")
    replies = [menu["message"]]
    if menu["type"] == "explanation_menu":
        replies += [tutor.process_message(label, menu["state"])["message"] for label in "abc"]

    for reply in replies:
        values = {nsimplify(token) for token in NUMBER.findall(reply)}
        assert expected not in values, reply


def test_active_exercise_answer_stays_private_through_menu_flow(tutor):
    exercise = tutor.process_message("Ponme un ejercicio de fracciones")
    expected = tutor.selector.get_expected_answer("mat_fracciones", exercise["exercise"]["id"])
    solved = tutor.process_message(expected, exercise["state"])
    menu = tutor.process_message("no entiendo las fracciones", solved["state"])

    assert menu["type"] == "explanation_menu"
    assert "expected_answer" not in json.dumps(menu, ensure_ascii=False, default=str)


# --- Validación de datos ---------------------------------------------------------

def test_invalid_menu_in_topic_json_is_rejected(tmp_path):
    topic = json.loads((ROOT / "content/topics/mat_fracciones.json").read_text(encoding="utf-8"))
    topic["explanation_menu"]["options"][1]["label"] = "A"
    (tmp_path / "mat_fracciones.json").write_text(json.dumps(topic), encoding="utf-8")

    with pytest.raises(ValueError, match="repetida"):
        KnowledgeService(tmp_path)


def test_public_menu_has_no_explanations():
    knowledge = KnowledgeService(ROOT / "content/topics")
    for topic in TOPICS:
        for option in knowledge.get_explanation_menu(topic)["options"]:
            assert set(option) == {"label", "text"}
