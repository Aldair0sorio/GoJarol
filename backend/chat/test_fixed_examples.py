"""Ningún ejemplo fijo de las explicaciones coincide con un ejercicio del banco ni con su resultado."""
import json
import re
from pathlib import Path

import pytest
from sympy import Rational

from chat.services.operation_guides import SPECIFIC_GUIDES

ROOT = Path(__file__).resolve().parents[2]
NUMBER = r"-?\d+(?:/\d+)?"
OPERATION = re.compile(rf"({NUMBER})\s*([+\-×x*÷])\s*({NUMBER})")
RESULT = re.compile(rf"=\s*\**\s*({NUMBER}(?:\.\d+)?)")


def fixed_texts():
    """(nombre, tema o None, texto) de guías, explicaciones y menús."""
    texts = [(f"guía:{pattern.pattern[:25]}", topic, text) for pattern, topic, text in SPECIFIC_GUIDES]
    for path in sorted((ROOT / "content/topics").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        texts += [(f"{path.stem}:{level}", data["id"], text) for level, text in data["explanations"].items()]
        texts += [(f"{path.stem}:menu {o['label']}", data["id"], o["explanation"])
                  for o in data.get("explanation_menu", {}).get("options", [])]
    return texts


def bank():
    exercises = []
    for path in sorted((ROOT / "content/exercises").glob("*.json")):
        exercises += json.loads(path.read_text(encoding="utf-8"))["exercises"]
    return exercises


def operations(text):
    """Operaciones normalizadas; la suma y la multiplicación no dependen del orden."""
    found = set()
    for left, op, right in OPERATION.findall(text.replace("−", "-")):
        op = "*" if op in "×x*" else op
        values = (Rational(left), Rational(right))
        found.add((op, tuple(sorted(values)) if op in "+*" else values))
    return found


def value(token):
    return Rational(token)


TEXTS = fixed_texts()
BANK = bank()
NUMERIC_BANK = [ex for ex in BANK if ex["type"] in {"fraction", "numeric", "percentage"}]
FRACTION_ANSWERS = {value(ex["expected_answer"]) for ex in NUMERIC_BANK
                     if not value(ex["expected_answer"]).is_integer}


@pytest.mark.parametrize("name,topic,text", TEXTS, ids=[t[0] for t in TEXTS])
def test_fixed_example_does_not_reuse_a_bank_operation(name, topic, text):
    shown = operations(text)
    for exercise in NUMERIC_BANK:
        assert not (operations(exercise["question"]) & shown), f"{name} usa la operación de {exercise['id']}"


@pytest.mark.parametrize("name,topic,text", TEXTS, ids=[t[0] for t in TEXTS])
def test_fixed_example_does_not_show_a_bank_result(name, topic, text):
    results = {value(token) for token in RESULT.findall(text.replace("−", "-"))}
    # Fracciones: ningún texto fijo puede mostrar el resultado fraccionario de un ejercicio.
    leaked = results & FRACTION_ANSWERS
    assert not leaked, f"{name} muestra el resultado {leaked} de un ejercicio del banco"
    # Enteros: se revisan contra los ejercicios del mismo tema.
    same_topic = {value(ex["expected_answer"]) for ex in NUMERIC_BANK
                  if topic and ex["id"].split("_")[0] in topic}
    leaked = {r for r in results if r.is_integer} & same_topic
    assert not leaked, f"{name} muestra el resultado {leaked} de un ejercicio de {topic}"


def test_scan_covers_all_topics_and_guides():
    topics = {topic for _, topic, _ in TEXTS if topic}
    assert topics == {path.stem for path in (ROOT / "content/topics").glob("*.json")}
    assert sum(1 for name, _, _ in TEXTS if name.startswith("guía")) == len(SPECIFIC_GUIDES)
