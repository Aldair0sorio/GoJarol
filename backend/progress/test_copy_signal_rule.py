"""Regla documentada de copySignal (función pura, sin base de datos)."""
import pytest

from progress.copy_signals import RULE_TEXT, copy_signal


@pytest.mark.parametrize("answer_requests,bypass,successes,expected", [
    (0, 0, 0, "ok"),
    (2, 0, 0, "ok"),            # Menos de 3 pedidos.
    (3, 0, 0, "revisar"),       # (a) 3+ pedidos y 0 aciertos.
    (2, 1, 0, "revisar"),       # (a) los intentos de saltarse las reglas también cuentan.
    (3, 0, 1, "ok"),            # Con un acierto propio ya no aplica (a); (b) pide 5+.
    (4, 0, 1, "ok"),
    (5, 0, 2, "revisar"),       # (b) 5 pedidos >= 2 × 2 aciertos.
    (5, 0, 3, "ok"),            # 5 < 2 × 3.
    (5, 1, 3, "revisar"),       # 6 >= 2 × 3.
    (10, 0, 6, "ok"),
])
def test_copy_signal_rule(answer_requests, bypass, successes, expected):
    signal, reason = copy_signal(answer_requests, bypass, successes)
    assert signal == expected
    assert bool(reason) == (expected == "revisar")


@pytest.mark.parametrize("answer_requests,bypass,successes,reason", [
    (6, 1, 1, "7 pedidos (6 de respuesta directa y 1 intento de saltarse las reglas) y solo 1 acierto propio en 7 días."),
    (3, 1, 0, "4 pedidos (3 de respuesta directa y 1 intento de saltarse las reglas) y ningún acierto propio en 7 días."),
    (2, 3, 0, "5 pedidos (2 de respuesta directa y 3 intentos de saltarse las reglas) y ningún acierto propio en 7 días."),
    (3, 0, 0, "3 pedidos de respuesta directa y ningún acierto propio en 7 días."),
    (0, 3, 0, "3 intentos de saltarse las reglas y ningún acierto propio en 7 días."),
    (6, 0, 2, "6 pedidos de respuesta directa y solo 2 aciertos propios en 7 días."),
])
def test_reason_matches_what_the_card_shows(answer_requests, bypass, successes, reason):
    assert copy_signal(answer_requests, bypass, successes) == ("revisar", reason)


def test_rule_text_documents_both_conditions():
    assert "3 o más veces" in RULE_TEXT and "no tiene aciertos propios" in RULE_TEXT
    assert "5 o más veces" in RULE_TEXT and "al menos el doble" in RULE_TEXT
    assert "7 días" in RULE_TEXT
