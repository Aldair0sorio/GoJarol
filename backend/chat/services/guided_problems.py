"""Resolución guiada, paso a paso, de un problema que trae el alumno.

Jarol nunca escribe el resultado final ni la respuesta de un paso antes de que
el alumno la dé: pregunta, comprueba con SymPy lo que el alumno escribe y, si
se atora, descompone el paso con ejemplos de OTROS números.

Alcance: suma y resta de dos fracciones, y división entre dos enteros.
El problema vive en state["custom_problem"] (tutor_state, solo en el servidor).
"""
import re
from math import lcm

from sympy import Rational

from gojarol_ml.nlp.topic_retriever import normalize_text


GUIDED_KINDS = {"fraction", "division"}

NUMBER_RE = re.compile(r"(?<![\w.,/])(-?\d+)(?:\s*/\s*(\d+)|\.(\d+))?")
FRACTION_PAIR_RE = re.compile(r"(\d+)\s*/\s*(\d+)\s*([+\-*/÷x×])\s*(\d+)\s*/\s*(\d+)")
HELP_RE = re.compile(
    r"\b(?:no se|no lo se|no entiendo|no le entiendo|no comprendo|no puedo|no me sale|ni idea|"
    r"no tengo idea|no recuerdo|no me acuerdo|como|ayuda\w*|explica\w*|pista\w*|que hago|"
    r"respuesta|resultado|solucion|dime|dame|cual es|que es|otra vez)\b"
)
ANSWER_REQUEST_RE = re.compile(r"\b(?:respuesta|resultado|solucion)\b")
NEW_QUESTION_RE = re.compile(r"\b(?:cuanto (?:es|seria|da|vale)|calcula|resuelve)\b")
LEAVE_RE = re.compile(
    r"\b(?:ejercicio\w*|reto\w*|porcentaj\w*|ecuacion\w*|ortografi\w*|acentu\w*|lectur\w*|"
    r"comprension|pitagoras|hipotenusa|otro tema|cambiar de tema|olvidalo|ya no quiero|otra cosa)\b"
)
ACKNOWLEDGEMENTS = {
    "ok", "okey", "si", "va", "vale", "listo", "entendido", "gracias", "ya", "aja",
    "bueno", "sale", "de acuerdo", "ya entendi", "entiendo", "perfecto",
}

STEP_NAMES = ["Primer", "Segundo", "Tercer", "Cuarto"]
WORDS = ["cero", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce"]
REFUSAL = "No te voy a dar el resultado, pero te acompaño."
NO_ANSWER = f"{REFUSAL}\n\n"


# --- Utilidades -----------------------------------------------------------------

def emit_event(state, kind):
    """Anota un evento para que la vista lo registre (sin texto del alumno)."""
    state.setdefault("pending_events", []).append(kind)


def _word(n):
    return WORDS[n] if 0 <= n < len(WORDS) else str(n)


def _times(n):
    return "una vez" if n == 1 else f"{_word(n)} veces"


def number_tokens(text):
    """Números del texto: enteros, fracciones a/b y decimales, con su valor exacto."""
    text = text.strip()
    if re.fullmatch(r"-?\d+,\d+", text):
        text = text.replace(",", ".")
    tokens = []
    for match in NUMBER_RE.finditer(text):
        whole, den, dec = match.groups()
        literal = re.sub(r"\s+", "", match.group(0))
        if den is not None:
            if int(den) == 0:
                continue
            tokens.append({"literal": literal, "value": Rational(int(whole), int(den)),
                           "kind": "fraction", "num": int(whole), "den": int(den)})
        elif dec is not None:
            tokens.append({"literal": literal, "value": Rational(literal), "kind": "decimal", "digits": len(dec)})
        else:
            tokens.append({"literal": literal, "value": Rational(int(whole)), "kind": "int"})
    return tokens


def _final(p):
    return Rational(p["expected"])


def _verb(p, form="tu"):
    plus = p["op"] == "+"
    return {"tu": "sumas" if plus else "restas", "inf": "sumar" if plus else "restar",
            "title": "Sumar" if plus else "Restar"}[form]


def _secrets(p):
    """Lo que Jarol no debe escribir: (valores secretos, literales secretos, literales permitidos)."""
    given = set(p.get("given", []))
    given_values = {token["value"] for literal in given for token in number_tokens(literal)}
    if p["kind"] == "fraction":
        a, b, c, d = p["a"], p["b"], p["c"], p["d"]
        values, literals = {_final(p)}, {str(_final(p))}
        for common in {lcm(b, d), p.get("common")} - {None}:
            e1, e2 = a * common // b, c * common // d
            total = e1 + e2 if p["op"] == "+" else e1 - e2
            values |= {Rational(common), Rational(total)}
            literals |= {f"{e1}/{common}", f"{e2}/{common}", f"{total}/{common}"}
        visible = {Rational(n) for n in (a, b, c, d)} | {Rational(a, b), Rational(c, d)}
        allowed = {f"{a}/{b}", f"{c}/{d}"}
    else:
        a, b = p["a"], p["b"]
        q, r = divmod(a, b)
        values, literals = {_final(p), Rational(q), Rational(r)}, set()
        visible = {Rational(a), Rational(b)}
        allowed = {f"{a}/{b}"}
    return values - visible - given_values, literals - given - allowed, allowed


def reveals_secret(text, p):
    secret_values, secret_literals, allowed = _secrets(p)
    for token in number_tokens(normalize_text(text)):
        if token["literal"] in allowed:
            continue
        if token["literal"] in secret_literals or token["value"] in secret_values:
            return True
    return False


def _pick_example(candidates, render, p, fallback):
    """Primer ejemplo con otros números: no muestra nada del problema ni reutiliza sus fracciones."""
    _, _, operand_literals = _secrets(p)
    for candidate in candidates:
        text = render(*candidate)
        reuses_operand = any(token["literal"] in operand_literals for token in number_tokens(text))
        if not reuses_operand and not reveals_secret(text, p):
            return text
    return fallback


def _multiples(n, upto):
    return ", ".join(str(n * i) for i in range(1, upto // n + 1))


# --- Inicio de problemas --------------------------------------------------------

def start_fraction_problem(a, b, op, c, d):
    final = Rational(a, b) + Rational(c, d) if op == "+" else Rational(a, b) - Rational(c, d)
    problem = {
        "kind": "fraction", "op": op, "a": a, "b": b, "c": c, "d": d,
        "expr": f"{a}/{b} {op} {c}/{d}", "expected": str(final),
        "step": "same_denominator" if b == d else "common_denominator",
        "common": b if b == d else None, "first": None, "second": None,
        "errors": 0, "help": 0, "given": [],
    }
    intro = (
        f"¡Vamos a resolver **{problem['expr']}** juntos, paso a paso! Yo te guío y tú haces las cuentas: "
        "no te voy a dar el resultado, pero sí te acompaño hasta que llegues a él."
    )
    return problem, f"{intro}\n\n{_prompt(problem)}"


def start_division_problem(a, b):
    problem = {
        "kind": "division", "a": a, "b": b, "expr": f"{a} ÷ {b}", "expected": str(Rational(a, b)),
        "step": "integer_part", "q": None, "r": None, "errors": 0, "help": 0, "given": [],
    }
    intro = (
        f"¡Analicemos **{a} ÷ {b}** paso a paso para que tú mismo encuentres el resultado! "
        "No te lo voy a dar, pero sí te acompaño."
    )
    return problem, f"{intro}\n\n{_prompt(problem)}"


# --- Pasos ----------------------------------------------------------------------

def _steps(p):
    if p["kind"] == "division":
        return ["integer_part", "remainder", "decimal"]
    if p["b"] == p["d"]:
        return ["same_denominator"]
    common = p.get("common")
    steps = ["common_denominator"]
    if common is None or p["b"] != common:
        steps.append("convert_first")
    if common is None or p["d"] != common:
        steps.append("convert_second")
    return steps + ["operate"]


def _label(p):
    return f"**{STEP_NAMES[_steps(p).index(p['step'])]} paso"


def _operands(p):
    """Numeradores ya convertidos (los dio el alumno) y el denominador común."""
    common = p["common"]
    first = p["first"] if p["first"] is not None else p["a"]
    second = p["second"] if p["second"] is not None else p["c"]
    return first, second, common


def _prompt(p):
    a, b = p["a"], p["b"]
    if p["kind"] == "division":
        if p["step"] == "integer_part":
            return (f"{_label(p)} · Parte entera.** ¿Cuántas veces cabe el **{b}** dentro del **{a}** sin pasarse? "
                    f"Recorre la tabla del **{b}** hasta el último resultado que no pase de **{a}**.\n\n¿Cuántas veces cabe?")
        if p["step"] == "remainder":
            return (f"{_label(p)} · Lo que sobra.** Multiplica **{b} × {p['q']}** y réstale ese resultado a **{a}**."
                    "\n\n¿Cuánto sobra?")
        return (f"{_label(p)} · Parte decimal.** Para repartir el **{p['r']}** que sobra, pon un punto después de la "
                f"parte entera y agrégale un cero al {p['r']}: ahora divides **{p['r'] * 10} ÷ {b}** igual que antes."
                f"\n\nEscribe el resultado completo de **{a} ÷ {b}** en decimal.")

    c, d = p["c"], p["d"]
    if p["step"] == "same_denominator":
        return (f"{_label(p)} · {_verb(p, 'title')} numeradores.** Las dos fracciones tienen el mismo denominador "
                f"(**{b}**): ese se queda igual. Solo {_verb(p)} los numeradores **{a}** y **{c}**.\n\n¿Qué fracción obtienes?")
    if p["step"] == "common_denominator":
        return (f"{_label(p)} · Denominador común.** Los denominadores son distintos (**{b}** y **{d}**). Necesitamos "
                f"un número que esté en la tabla del **{b}** y también en la del **{d}**.\n\n"
                "¿Qué número propones como denominador común?")
    if p["step"] in {"convert_first", "convert_second"}:
        num, den = (a, b) if p["step"] == "convert_first" else (c, d)
        return (f"{_label(p)} · Convertir {num}/{den}.** Escribe **{num}/{den}** como una fracción con denominador "
                f"**{p['common']}**: {num}/{den} = ?/{p['common']}\n\n¿Qué fracción obtienes?")
    first, second, common = _operands(p)
    return (f"{_label(p)} · {_verb(p, 'title')}.** Ya tienes las dos fracciones con denominador **{common}**: "
            f"**{first}/{common} {p['op']} {second}/{common}**. Conserva el **{common}** y {_verb(p)} los numeradores."
            "\n\n¿Qué fracción obtienes?")


def _advance(p):
    steps = _steps(p)
    p["step"] = steps[steps.index(p["step"]) + 1]
    p["errors"] = 0
    p["help"] = 0


# --- Ayudas (de menos a más), siempre sin la respuesta ---------------------------

def _practice(p):
    return "Ponme un ejercicio de fracciones" if p["kind"] == "fraction" else "Ponme un ejercicio"


def _full_example(p):
    if p["kind"] == "division":
        def render(x, y):
            q, r = divmod(x, y)
            return (f"Ejemplo completo con otros números: **{x} ÷ {y}**.\n"
                    f"• Parte entera: en la tabla del {y} ({_multiples(y, y * (q + 1))}…) el {y * (q + 1)} ya se pasa "
                    f"de {x}, así que el {y} cabe {_times(q)}.\n"
                    f"• Lo que sobra: el {y} {_times(q)} llega a {y * q}, y de {y * q} a {x} sobran {_word(r)}.\n"
                    f"• Parte decimal: {_word(r)} con un cero es {r * 10}, y {r * 10} ÷ {y} = {r * 10 // y}. "
                    f"Resultado: **{x} ÷ {y} = {q}.{r * 10 // y}**.")
        return _pick_example(
            [(17, 5), (13, 2), (29, 5), (19, 5), (11, 2), (33, 5), (23, 2), (7, 2), (37, 10), (61, 10), (83, 10)],
            render, p,
            "Ejemplo: busca cuántas veces cabe el divisor, calcula lo que sobra y luego reparte lo que sobra "
            "agregando un cero después del punto.",
        )

    if p["b"] == p["d"]:
        return _operate_example(p)

    def render(x1, y1, x2, y2):
        common = lcm(y1, y2)
        n1, n2 = x1 * common // y1, x2 * common // y2
        total = n1 + n2 if p["op"] == "+" else n1 - n2
        conversions = " y ".join(
            f"{x}/{y} = {n}/{common}" for x, y, n in ((x1, y1, n1), (x2, y2, n2)) if y != common
        )
        return (f"Ejemplo completo con otros números: **{x1}/{y1} {p['op']} {x2}/{y2}**.\n"
                f"• Denominador común: en la tabla del {y1} ({_multiples(y1, common)}) y en la del {y2} "
                f"({_multiples(y2, common)}) el primero que se repite es **{common}**.\n"
                f"• Convertir: {conversions}.\n"
                f"• {_verb(p, 'title')}: {n1}/{common} {p['op']} {n2}/{common} = **{total}/{common}**.")
    candidates = (
        [(1, 3, 1, 6), (1, 2, 1, 5), (2, 3, 1, 4), (1, 4, 1, 6), (3, 5, 1, 10), (1, 6, 2, 9), (2, 5, 1, 3)]
        if p["op"] == "+" else
        [(5, 6, 1, 3), (3, 4, 1, 6), (4, 5, 1, 2), (2, 3, 1, 4), (7, 10, 1, 5), (5, 8, 1, 6)]
    )
    return _pick_example(
        candidates, render, p,
        "Ejemplo: busca un denominador común, convierte cada fracción multiplicando arriba y abajo por el mismo "
        f"número y luego {_verb(p)} los numeradores.",
    )


def _operate_example(p):
    def render(x1, x2, y):
        total = x1 + x2 if p["op"] == "+" else x1 - x2
        return (f"Ejemplo con otros números: **{x1}/{y} {p['op']} {x2}/{y} = {total}/{y}**: el {y} se queda igual "
                f"y solo {_verb(p)} los numeradores.")
    candidates = (
        [(2, 3, 7), (1, 4, 9), (3, 5, 11), (2, 6, 13), (4, 7, 15)] if p["op"] == "+"
        else [(5, 2, 7), (7, 4, 9), (8, 3, 11), (9, 4, 13)]
    )
    return _pick_example(candidates, render, p,
                         f"Ejemplo: con el mismo denominador, el de abajo se queda igual y solo {_verb(p)} los de arriba.")


def _helps(p):
    a, b = p["a"], p["b"]
    if p["kind"] == "division":
        q, r = p.get("q"), p.get("r")
        if p["step"] == "integer_part":
            def render(x, y):
                qq = x // y
                return (f"Ejemplo con otros números: para **{x} ÷ {y}**, recorre la tabla del {y}: "
                        f"{_multiples(y, y * (qq + 1))}… El {y * (qq + 1)} ya se pasa de {x}, así que el {y} cabe "
                        f"**{_times(qq)}**.")
            example = _pick_example([(17, 5), (29, 5), (23, 4), (19, 5), (33, 5), (13, 2), (27, 8), (22, 7), (37, 10)],
                                    render, p, "Ejemplo: recorre la tabla del divisor hasta antes de pasarte.")
            return [
                f"{example}\n\nAhora tú con **{a} ÷ {b}**: ¿cuántas veces cabe el **{b}** en el **{a}**?",
                (f"Vamos más despacio: escribe la tabla del **{b}** (el {b} por uno, por dos, por tres…) y detente "
                 f"justo antes de pasarte de **{a}**. ¿Por qué número multiplicaste la última vez?"),
                (f"Otra forma: réstale **{b}** al **{a}** una y otra vez mientras se pueda, sin llegar a números "
                 "negativos. ¿Cuántas veces pudiste restar?"),
            ]
        if p["step"] == "remainder":
            def render(x, y):
                qq, rr = divmod(x, y)
                return (f"Ejemplo con otros números: en **{x} ÷ {y}** el {y} cabe {_times(qq)} y llega a {y * qq}; "
                        f"de {y * qq} a {x} faltan {_word(rr)}, así que sobran **{_word(rr)}**.")
            example = _pick_example([(17, 5), (29, 5), (23, 4), (19, 5), (13, 2), (27, 8), (22, 7), (37, 10)],
                                    render, p, "Ejemplo: multiplica el divisor por lo que cabe y réstalo del dividendo.")
            return [
                f"{example}\n\nAhora tú: calcula **{b} × {q}** y réstaselo a **{a}**.",
                (f"Primero calcula solo **{b} × {q}**. Luego pregúntate: ¿cuánto le falta a ese número para llegar "
                 f"a **{a}**? Eso es lo que sobra."),
            ]

        def render(x, y):
            qq, rr = divmod(x, y)
            return (f"Ejemplo con otros números: en **{x} ÷ {y}** sobraban {_word(rr)}. Pones un punto y agregas un "
                    f"cero: {rr * 10} ÷ {y} = {rr * 10 // y}. Ese número va después del punto: "
                    f"**{x} ÷ {y} = {qq}.{rr * 10 // y}**.")
        example = _pick_example([(17, 5), (13, 2), (29, 5), (19, 5), (11, 2), (33, 5), (37, 10), (61, 10)],
                                render, p, "Ejemplo: agrega un cero a lo que sobra y vuelve a dividir.")
        return [
            f"{example}\n\nAhora tú: divide **{r * 10} ÷ {b}** y ese número va después del punto.",
            (f"Ya tienes la parte entera (**{q}**). Escribe {q} y un punto; después divide **{r * 10} ÷ {b}** "
             "y pon ese número después del punto."),
        ]

    c, d = p["c"], p["d"]
    if p["step"] == "common_denominator":
        def render(x, y):
            common = lcm(x, y)
            return (f"Para encontrar un denominador común, escribe la tabla de cada denominador y busca el primer "
                    f"número que aparezca en las dos. Ejemplo con otros números, **{x}** y **{y}**: tabla del {x}: "
                    f"{_multiples(x, common)}…; tabla del {y}: {_multiples(y, common)}…; el primero que se repite "
                    f"es **{common}**.")
        example = _pick_example([(3, 5), (4, 6), (6, 8), (3, 7), (2, 5), (5, 6), (4, 10), (2, 7), (6, 9)], render, p,
                                "Para encontrar un denominador común, escribe la tabla de cada denominador y busca "
                                "el primer número que aparezca en las dos.")
        big, small = max(b, d), min(b, d)
        return [
            (f"{example}\n\nAhora tú: escribe la tabla del **{b}** y la del **{d}**. ¿Cuál es el primer número "
             "que aparece en las dos?"),
            (f"Vamos más despacio. Recorre la tabla del **{big}** (el denominador más grande): el {big} por uno, "
             f"por dos, por tres… Con cada resultado pregúntate: ¿se puede dividir exacto entre **{small}**? "
             "El primero que sí se pueda es tu denominador común."),
            (f"Otra pista: multiplicar los dos denominadores (**{b} × {d}**) siempre da un denominador común, "
             "aunque a veces no es el más pequeño. ¿Cuánto da?"),
        ]
    if p["step"] in {"convert_first", "convert_second"}:
        num, den = (a, b) if p["step"] == "convert_first" else (c, d)
        common = p["common"]

        def render(x, y, target):
            k = target // y
            return (f"Ejemplo con otros números: para pasar **{x}/{y}** a una fracción con denominador **{target}**, "
                    f"ves que {y} × {k} = {target}; entonces el numerador también se multiplica por {k}: "
                    f"{x} × {k} = {x * k}. Queda **{x}/{y} = {x * k}/{target}**. Multiplicar arriba y abajo por "
                    "el mismo número no cambia el valor.")
        example = _pick_example(
            [(2, 3, 6), (1, 4, 8), (3, 5, 10), (2, 5, 15), (1, 3, 9), (3, 4, 12), (1, 6, 12), (2, 7, 14)],
            render, p, "Para convertir, multiplica el numerador y el denominador por el mismo número.",
        )
        return [
            (f"{example}\n\nAhora tú: ¿por qué número multiplicas **{den}** para obtener **{common}**? "
             f"Multiplica el **{num}** por ese mismo número."),
            (f"Divide **{common} ÷ {den}**: ese es el número por el que debes multiplicar. Luego multiplica el "
             f"**{num}** por ese número y escríbelo arriba del **{common}**."),
            (f"Piénsalo así: si el entero se parte en **{common}** partes en lugar de **{den}**, cada parte de antes "
             f"se convierte en varias partes nuevas. ¿Cuántas partes nuevas son tus **{num}** partes de antes?"),
        ]
    first, second, common = _operands(p)
    return [
        f"{_operate_example(p)}\n\nAhora tú: {_verb(p)} **{first} {p['op']} {second}** arriba y deja el **{common}** abajo.",
        (f"Si te ayuda, imagina rebanadas del mismo tamaño (cada una es una de las **{common}** partes del entero): "
         f"tienes {first} y {'te dan' if p['op'] == '+' else 'quitas'} {second}. ¿Cuántas rebanadas quedan? "
         f"Esa cantidad va arriba y el **{common}** abajo."),
    ]


def _help(p, answer_request=False):
    helps = _helps(p)
    index = p["help"]
    p["help"] += 1
    prefix = NO_ANSWER if answer_request else ""
    if index < len(helps):
        return prefix + helps[index]
    return prefix + _retry_with_example(p)


def next_help(state):
    """Siguiente ayuda del paso actual del problema pendiente (sin el resultado)."""
    return _help(state["custom_problem"])  # Sin prefijo: quien llama pone el rechazo.


def retry_with_example(state):
    """Ejemplo completo con otros números y el paso actual para reintentar."""
    return _retry_with_example(state["custom_problem"])


def _retry_with_example(p):
    return (f"{_full_example(p)}\n\nAhora inténtalo tú con **{p['expr']}**:\n\n{_prompt(p)}\n\n"
            f"Recuerda que también puedes escribir «{_practice(p)}» para practicar con otros.")


# --- Evaluación de respuestas -----------------------------------------------------

def _is_final(p, token):
    final = _final(p)
    if token["value"] == final:
        return True
    if p["kind"] == "division" and token["kind"] == "decimal":
        return abs(token["value"] - final) < Rational(1, 10 ** token["digits"])
    return False


def _finish(p, literal, state):
    state.pop("custom_problem", None)
    state.pop("answer_request_counter", None)  # Problema resuelto: el contador vuelve a cero.
    exact = Rational(literal) == _final(p)
    head = (f"¡Exacto! 🎉 **{p['expr']}** da **{literal}**." if exact
            else f"¡Muy bien! 🎉 **{literal}** es correcto para **{p['expr']}** (el decimal sigue, pero así está bien).")
    extra = ""
    if p["kind"] == "fraction" and "/" in literal:
        num, den = (int(part) for part in literal.split("/"))
        if abs(Rational(num, den).q) != abs(den):
            extra = " Si quieres, todavía puedes simplificarla."
    closing = (f"\n\n¡Lo razonaste paso a paso por tu cuenta! Si quieres ganar XP con retos parecidos, escríbeme: "
               f"«{_practice(p)}».")
    return head + extra + closing


def _wrong(p, feedback):
    p["errors"] += 1
    if p["errors"] % 3 == 0:
        return f"{feedback}\n\n{_retry_with_example(p)}"
    return f"{feedback}\n\n¿Lo intentas otra vez?"


def _evaluate(p, token, state):
    a, b = p["a"], p["b"]
    if p["kind"] == "division" and token["literal"] == f"{a}/{b}":
        return f"Esa es la misma división escrita como fracción. Busquemos cuánto vale:\n\n{_prompt(p)}"
    if _is_final(p, token):
        return _finish(p, token["literal"], state)

    if p["kind"] == "division":
        q, r = divmod(a, b)
        n = token["value"]
        if p["step"] == "integer_part":
            if n == q:
                p["q"] = q
                _advance(p)
                return f"¡Bien! El **{b}** cabe **{_times(q)}** en el **{a}**.\n\n{_prompt(p)}"
            if token["kind"] != "int":
                return _wrong(p, "Aquí solo necesito un número entero: cuántas veces cabe completo.")
            if b * n > a:
                return _wrong(p, f"Te pasaste: si multiplicas **{b} × {token['literal']}**, el resultado ya es mayor que **{a}**.")
            return _wrong(p, "Todavía cabe al menos una vez más: prueba con un número más grande.")
        if p["step"] == "remainder":
            if n == r:
                p["r"] = r
                _advance(p)
                return f"¡Correcto! {'Sobra' if r == 1 else 'Sobran'} **{r}**.\n\n{_prompt(p)}"
            if token["kind"] == "int" and n >= b:
                return _wrong(p, f"Lo que sobra siempre es menor que el **{b}**: si sobra {b} o más, es que cabía otra vez.")
            return _wrong(p, f"Revisa: calcula **{b} × {q}** y luego réstaselo a **{a}**.")
        if token["kind"] == "decimal" and int(token["value"]) != q:
            return _wrong(p, f"Revisa la parte entera: ya encontraste que el **{b}** cabe **{_times(q)}**, "
                             f"así que tu resultado empieza con **{q}** y un punto.")
        return _wrong(p, f"La parte entera (**{q}**) va bien; revisa lo que va después del punto: "
                         f"divide **{r * 10} ÷ {b}**.")

    c, d = p["c"], p["d"]
    if p["step"] == "same_denominator":
        total = a + c if p["op"] == "+" else a - c
        if token["kind"] == "int" and token["value"] == total:
            return _finish(p, f"{total}/{b}", state)
        if token["kind"] == "fraction" and token["den"] != b:
            return _wrong(p, f"Recuerda que el denominador no cambia: debe seguir siendo **{b}**.")
        return _wrong(p, f"Ojo: el **{b}** se queda igual y solo {_verb(p)} los numeradores **{a}** y **{c}**.")

    if p["step"] == "common_denominator":
        n = token["value"]
        if token["kind"] == "int" and n > 0 and n % b == 0 and n % d == 0:
            p["common"] = int(n)
            _advance(p)
            note = ("" if n == lcm(b, d)
                    else " Funciona; hay uno más pequeño que haría las cuentas más cortas, pero con este también llegas.")
            return (f"¡Muy bien! **{n}** está en la tabla del **{b}** y en la del **{d}**.{note}\n\n{_prompt(p)}")
        if token["kind"] != "int" or n <= 0:
            return _wrong(p, f"El denominador común es un número entero que esté en la tabla del **{b}** y en la del **{d}**.")
        if n % b == 0:
            return _wrong(p, f"El **{n}** sí está en la tabla del **{b}**, pero no en la del **{d}**.")
        if n % d == 0:
            return _wrong(p, f"El **{n}** sí está en la tabla del **{d}**, pero no en la del **{b}**.")
        return _wrong(p, f"El **{n}** no está en la tabla del **{b}** ni en la del **{d}**.")

    common = p["common"]
    if p["step"] in {"convert_first", "convert_second"}:
        num, den = (a, b) if p["step"] == "convert_first" else (c, d)
        expected = num * common // den
        ok = (token["kind"] == "fraction" and token["den"] == common and token["num"] == expected) or (
            token["kind"] == "int" and token["value"] == expected)
        if ok:
            p["first" if p["step"] == "convert_first" else "second"] = expected
            p["given"].append(f"{expected}/{common}")
            _advance(p)
            return (f"¡Correcto! **{num}/{den} = {expected}/{common}**: multiplicaste arriba y abajo por el mismo "
                    f"número, así que vale lo mismo.\n\n{_prompt(p)}")
        if token["kind"] == "fraction" and token["den"] == common:
            return _wrong(p, f"El denominador **{common}** está bien. Para que la fracción no cambie de valor, el "
                             f"**{num}** se multiplica por el mismo número que usaste con el **{den}**.")
        if token["value"] == Rational(num, den):
            return _wrong(p, f"Esa fracción vale lo mismo que {num}/{den}, pero necesitamos que el denominador sea **{common}**.")
        return _wrong(p, f"Busca una fracción igual a **{num}/{den}** con denominador **{common}**: piensa por cuánto "
                         f"multiplicas el **{den}** para llegar a **{common}**.")

    first, second, common = _operands(p)
    total = first + second if p["op"] == "+" else first - second
    if token["kind"] == "int" and token["value"] == total:
        return _finish(p, f"{total}/{common}", state)
    if token["kind"] == "fraction" and token["den"] != common:
        return _wrong(p, f"El denominador no cambia: debe seguir siendo **{common}**.")
    return _wrong(p, f"Recuerda: con el mismo denominador solo {_verb(p)} los numeradores **{first}** y "
                     f"**{second}**; el **{common}** se queda igual.")


# --- Punto de entrada -----------------------------------------------------------

def handle_guided_message(message, state):
    """Atiende un mensaje mientras hay un problema guiado pendiente.

    Devuelve el texto de Jarol, o None para que siga el flujo normal (y en ese
    caso el problema se descarta, salvo que el alumno haya planteado uno nuevo).
    """
    p = state["custom_problem"]
    normalized = normalize_text(message)
    tokens = number_tokens(normalized.rsplit("=", 1)[-1] if "=" in normalized else normalized)
    for token in number_tokens(normalized):
        p["given"].append(token["literal"])

    # ¿Plantea otro problema? Lo atiende el constructor de guías.
    pair = FRACTION_PAIR_RE.search(normalized)
    if pair:
        a, b, op, c, d = pair.groups()
        if f"{a}/{b} {op} {c}/{d}" != p.get("expr"):
            return None
    elif NEW_QUESTION_RE.search(normalized) and tokens and not HELP_RE.search(normalized):
        return None

    if LEAVE_RE.search(normalized):
        state.pop("custom_problem", None)
        return None

    if HELP_RE.search(normalized):
        emit_event(state, "hint_used")
        return _help(p, answer_request=bool(ANSWER_REQUEST_RE.search(normalized)))

    if len(tokens) == 1:
        step_before = p["step"]
        reply = _evaluate(p, tokens[0], state)
        if state.get("custom_problem") is not p or p["step"] != step_before:
            emit_event(state, "step_solved")  # Paso (o problema) resuelto por el alumno.
        return reply

    if pair or re.sub(r"[^\w\s]", "", normalized).strip() in ACKNOWLEDGEMENTS:
        return f"¡Sigamos!\n\n{_prompt(p)}"

    if tokens:
        return f"Escríbeme solo tu respuesta a este paso, por ejemplo un solo número o una sola fracción.\n\n{_prompt(p)}"

    state.pop("custom_problem", None)
    return None
