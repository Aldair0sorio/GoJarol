"""Regla documentada de copySignal (función pura, sin base de datos)."""
import pytest

from progress.copy_signals import RULE_TEXT, copy_signal


@pytest.mark.parametrize("requests,successes,expected", [
    (0, 0, "ok"),
    (2, 0, "ok"),            # Menos de 3 pedidos.
    (3, 0, "revisar"),       # (a) 3+ pedidos y 0 aciertos.
    (3, 1, "ok"),            # Con un acierto propio ya no aplica (a); (b) pide 5+.
    (4, 1, "ok"),
    (5, 2, "revisar"),       # (b) 5 pedidos >= 2 × 2 aciertos.
    (5, 3, "ok"),            # 5 < 2 × 3.
    (6, 3, "revisar"),       # 6 >= 2 × 3.
    (10, 6, "ok"),
])
def test_copy_signal_rule(requests, successes, expected):
    signal, reason = copy_signal(requests, successes)
    assert signal == expected
    assert bool(reason) == (expected == "revisar")


def test_rule_text_documents_both_conditions():
    assert "3 o más veces" in RULE_TEXT and "no tiene aciertos propios" in RULE_TEXT
    assert "5 o más veces" in RULE_TEXT and "al menos el doble" in RULE_TEXT
    assert "7 días" in RULE_TEXT
