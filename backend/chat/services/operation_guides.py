import re
from sympy import Rational, sympify
from gojarol_ml.nlp.topic_retriever import normalize_text


SPECIFIC_GUIDES = [
    # 1. Operaciones específicas CON fracciones
    (
        re.compile(r"\b(divid\w*|division\w*)\b.*\b(fraccion\w*|quebrad\w*)\b|\b(fraccion\w*|quebrad\w*)\b.*\b(divid\w*|division\w*)\b"),
        "mat_fracciones",
        (
            "Para **dividir fracciones** usamos el método de **productos cruzados** (o multiplicar por el recíproco):\n\n"
            "1. Multiplica el **numerador de la primera** por el **denominador de la segunda** → ese resultado va **arriba** (nuevo numerador).\n"
            "2. Multiplica el **denominador de la primera** por el **numerador de la segunda** → ese resultado va **abajo** (nuevo denominador).\n"
            "3. Simplifica la fracción si ambos números se pueden dividir entre el mismo factor.\n\n"
            "📌 **Ejemplo paso a paso**: (3/4) ÷ (2/5)\n"
            "• Arriba: 3 × 5 = 15\n"
            "• Abajo: 4 × 2 = 8\n"
            "• Resultado: **15/8**.\n\n"
            "Si quieres practicar con retos interactivos de fracciones, escríbeme: **«Ponme un ejercicio de fracciones»**."
        ),
    ),
    (
        re.compile(r"\b(multiplic\w*|producto)\b.*\b(fraccion\w*|quebrad\w*)\b|\b(fraccion\w*|quebrad\w*)\b.*\b(multiplic\w*|producto)\b"),
        "mat_fracciones",
        (
            "Para **multiplicar fracciones** el procedimiento es directo (en línea recta):\n\n"
            "1. Multiplica **numerador por numerador** (los números de arriba).\n"
            "2. Multiplica **denominador por denominador** (los números de abajo).\n"
            "3. Simplifica el resultado dividiendo arriba y abajo entre su máximo común divisor.\n\n"
            "📌 **Ejemplo paso a paso**: (2/3) × (4/5)\n"
            "• Arriba: 2 × 4 = 8\n"
            "• Abajo: 3 × 5 = 15\n"
            "• Resultado: **8/15**."
        ),
    ),
    (
        re.compile(r"\b(rest\w*|sustra\w*)\b.*\b(fraccion\w*|quebrad\w*)\b|\b(fraccion\w*|quebrad\w*)\b.*\b(rest\w*|sustra\w*)\b"),
        "mat_fracciones",
        (
            "Para **restar fracciones** nos fijamos primero en el denominador (el número de abajo):\n\n"
            "1. **Mismo denominador**: Conserva el denominador y resta los numeradores.\n"
            "   • Ejemplo: 5/7 - 2/7 = (5 - 2)/7 = **3/7**.\n"
            "2. **Diferente denominador**: Convierte a fracciones equivalentes con un denominador común y luego resta los numeradores.\n"
            "   • Ejemplo: 3/4 - 1/2 → como 1/2 = 2/4, restamos 3/4 - 2/4 = **1/4**.\n\n"
            "¿Quieres intentarlo? Escríbeme **«Ponme un ejercicio de fracciones»**."
        ),
    ),
    # 2. Operaciones aritméticas generales
    (
        re.compile(r"\b(divid\w*|division\w*|cociente|divisor|dividendo)\b"),
        None,
        (
            "**La división** consiste en repartir una cantidad (**dividendo**) en partes iguales según indica otro número (**divisor**):\n\n"
            "1. **Partes de la división**:\n"
            "   • **Dividendo**: número que vamos a repartir (ej. 24).\n"
            "   • **Divisor**: entre cuántos lo repartimos (ej. 6).\n"
            "   • **Cociente**: cuántas veces cabe el divisor en el dividendo (24 ÷ 6 = 4).\n"
            "   • **Residuo**: lo que sobra cuando la división no es exacta.\n"
            "2. **Cómo resolverla paso a paso**:\n"
            "   • Toma las primeras cifras del dividendo de izquierda a derecha que sean mayores o iguales al divisor.\n"
            "   • Busca qué número multiplicado por el divisor se acerca más sin pasarse.\n"
            "   • Resta ese producto y baja la siguiente cifra.\n"
            "3. **Comprobación**: (Cociente × Divisor) + Residuo = Dividendo.\n\n"
            "💡 También puedo explicarte cómo **dividir fracciones** o despejar divisiones en **ecuaciones de primer grado**."
        ),
    ),
    (
        re.compile(r"\b(multiplic\w*|tablas de multiplicar|factores|producto)\b"),
        None,
        (
            "**La multiplicación** es una suma abreviada donde sumamos un mismo número (**multiplicando**) tantas veces como indica otro (**multiplicador**):\n\n"
            "1. **Con números de varias cifras**:\n"
            "   • Coloca los números alineados a la derecha.\n"
            "   • Multiplica la cifra de las unidades de abajo por cada cifra de arriba (de derecha a izquierda), llevando las decenas.\n"
            "   • Luego multiplica la cifra de las decenas dejando un espacio a la derecha y suma los productos parciales.\n"
            "2. **Ley de los signos (Secundaria y Bachillerato)**:\n"
            "   • Signos iguales dan positivo: (+) × (+) = + y (-) × (-) = +.\n"
            "   • Signos distintos dan negativo: (+) × (-) = -.\n\n"
            "💡 Si quieres practicar cómo despejar multiplicaciones en álgebra, escríbeme: **«Ponme un ejercicio de ecuaciones»**."
        ),
    ),
    (
        re.compile(r"^\s*(?:explicame\s+|ensename\s+|enseña\s+|como\s+|que\s+es\s+)*(?:a\s+|como\s+|la\s+|las\s+)*(?:restar|resta|restas|sustraccion)\s*\??\s*$"),
        None,
        (
            "**La resta o sustracción** permite encontrar la diferencia entre dos cantidades (**minuendo** menos **sustraendo**):\n\n"
            "1. **Resta de números naturales y decimales**:\n"
            "   • Alinea las cifras por su valor posicional (unidades con unidades, decenas con decenas, y el punto decimal alineado).\n"
            "   • Resta columna por columna de derecha a izquierda. Si la cifra de arriba es menor que la de abajo, toma 1 decena prestada de la columna izquierda.\n"
            "2. **Resta con números negativos (Secundaria)**:\n"
            "   • Si restas un número mayor a uno menor (ej. 4 - 7), resta el menor al mayor (7 - 4 = 3) y conserva el signo del número con mayor valor absoluto: **-3**.\n"
            "3. **Resta de fracciones**:\n"
            "   • Si tienen igual denominador, resta solo los numeradores (4/5 - 1/5 = 3/5). Si tienen distinto denominador, conviértelas primero a fracciones equivalentes.\n\n"
            "¿Quieres practicar con **fracciones** o con **ecuaciones con números negativos**?"
        ),
    ),
    (
        re.compile(r"^\s*(?:explicame\s+|ensename\s+|enseña\s+|como\s+|que\s+es\s+)*(?:a\s+|como\s+|la\s+|las\s+)*(?:sumar|suma|sumas|adicion)\s*\??\s*$"),
        None,
        (
            "**La suma o adición** reúne dos o más cantidades (**sumandos**) en un solo total:\n\n"
            "1. **Números enteros y decimales**:\n"
            "   • Alinea unidades con unidades, decenas con decenas (y el punto decimal si hay decimales).\n"
            "   • Suma de derecha a izquierda; si una columna suma 10 o más, escribe la unidad y lleva la decena a la siguiente columna.\n"
            "2. **Suma de números con signo**:\n"
            "   • Si ambos tienen el mismo signo, suma sus valores y conserva el signo (ej. -4 + (-3) = -7).\n"
            "   • Si tienen signos distintos, resta el menor del mayor y deja el signo del mayor (ej. -8 + 5 = -3).\n"
            "3. **Suma de fracciones**:\n"
            "   • Con igual denominador: suma los numeradores y conserva el denominador (1/4 + 2/4 = 3/4).\n\n"
            "Si quieres resolver retos interactivos de suma de fracciones, escríbeme: **«Ponme un ejercicio de fracciones»**."
        ),
    ),
    (
        re.compile(r"\b(pitagoras|hipotenusa|cateto\w*|triangulo rectangulo)\b"),
        None,
        (
            "**El Teorema de Pitágoras** se aplica en todo **triángulo rectángulo** (el que tiene un ángulo de 90°):\n\n"
            "• Los dos lados que forman el ángulo recto se llaman **catetos** (a y b).\n"
            "• El lado más largo, opuesto al ángulo recto, se llama **hipotenusa** (c).\n"
            "• **Fórmula**: a² + b² = c²\n\n"
            "📌 **Ejemplo clásico**: Si los catetos miden a = 3 y b = 4:\n"
            "1. Elevamos al cuadrado: 3² + 4² = 9 + 16 = 25.\n"
            "2. Sacamos raíz cuadrada: c = √25 = **5**."
        ),
    ),
]


# Patrones para detectar cuando el estudiante pregunta una operación numérica directa
# Ej. "y cuanto seria 5/2", "cuanto es 15 entre 3", "cuanto es 1/4 + 2/4", "cuanto es 8 * 7"
FRAC_OP_RE = re.compile(
    r"(\d+)\s*/\s*(\d+)\s*([+\-*/÷x×])\s*(\d+)\s*/\s*(\d+)"
)
DIV_RE = re.compile(
    r"(?:cuanto\s+(?:es|seria|da|vale)|divid\w*|calcula|resuelve|y)?\s*\b(\d+)\s*(?:/|÷|\bentre\b)\s*(\d+)\b"
)
ARITH_RE = re.compile(
    r"(?:cuanto\s+(?:es|seria|da|vale)|calcula|resuelve|y)?\s*\b(\d+)\s*([+\-*x×]|\bmas\b|\bmenos\b|\bpor\b)\s*(\d+)\b"
)
NUMERIC_REPLY_RE = re.compile(
    r"^\s*(?:es\s+|da\s+|seria\s+|resultado\s*[:=]?\s*)?([+-]?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?)\s*$"
)


def evaluate_pending_custom_problem(message: str, state: dict) -> str | None:
    """
    Si el estudiante está respondiendo a la pregunta guiada que le hizo Jarol sobre su propia
    operación (ej. escribió '2.5' después de preguntar 'y cuanto seria 5/2'), verifica con SymPy.
    """
    custom = state.get("custom_problem")
    if not custom or state.get("active_exercise_id"):
        return None

    m = NUMERIC_REPLY_RE.match(message.strip())
    if not m:
        return None

    raw_val = m.group(1).replace(",", ".").replace(" ", "")
    try:
        user_val = sympify(raw_val)
        expected_val = sympify(custom["expected"])
        if user_val == expected_val or abs(float(user_val) - float(expected_val)) < 1e-6:
            state.pop("custom_problem", None)
            return (
                f"¡Exacto! 🎉 El resultado de **{custom['expr']}** es **{raw_val}**.\n\n"
                f"{custom.get('closing', '¡Lo razonaste paso a paso por tu cuenta!')}"
            )
        else:
            return (
                f"¡Casi! Obtuviste **{raw_val}**, pero revisemos de nuevo **{custom['expr']}**:\n"
                f"• {custom['hint']}\n"
                "Inténtalo una vez más, ¿cuánto te da?"
            )
    except Exception:
        return None


def build_socratic_math_guide(message: str, state: dict) -> str | None:
    """
    Detecta cuando el usuario pregunta un cálculo concreto (como 'y cuanto seria 5/2',
    'cuanto es 1/4 + 2/4' o 'cuanto es 8 * 7') y lo guía paso a paso con sus propios números
    sin regalar la respuesta directa.
    """
    if state.get("active_exercise_id"):
        return None

    norm = normalize_text(message)

    # 1. Operación entre dos fracciones: a/b op c/d
    m_frac = FRAC_OP_RE.search(norm)
    if m_frac:
        a, b, op, c, d = (
            int(m_frac.group(1)),
            int(m_frac.group(2)),
            m_frac.group(3),
            int(m_frac.group(4)),
            int(m_frac.group(5)),
        )
        if b == 0 or d == 0:
            return "Recuerda que el denominador de una fracción no puede ser **0**, porque no podemos dividir entre cero."

        f1, f2 = Rational(a, b), Rational(c, d)
        expr_str = f"{a}/{b} {op} {c}/{d}"
        if op == "+":
            ans = f1 + f2
            if b == d:
                hint = f"Como ambas tienen denominador **{b}**, conserva el **{b}** abajo y suma los numeradores: **{a} + {c}**."
            else:
                hint = f"Busca un denominador común entre **{b}** y **{d}**, convierte a fracciones equivalentes y suma los numeradores."
        elif op == "-":
            ans = f1 - f2
            if b == d:
                hint = f"Conserva el denominador **{b}** y resta los numeradores: **{a} - {c}**."
            else:
                hint = f"Convierte **{a}/{b}** y **{c}/{d}** a un denominador común y luego resta los numeradores."
        elif op in {"*", "x", "×"}:
            ans = f1 * f2
            hint = f"Multiplica en línea recta: arriba **{a} × {c}** y abajo **{b} × {d}**."
        else:
            if c == 0:
                return "No podemos dividir entre una fracción con numerador 0."
            ans = f1 / f2
            hint = f"Usa productos cruzados: arriba multiplica **{a} × {d}** y abajo **{b} × {c}**."

        state["custom_problem"] = {
            "expr": expr_str,
            "expected": str(ans),
            "hint": hint,
            "closing": "Si quieres ganar puntos XP resolviendo retos similares, escríbeme: **«Ponme un ejercicio de fracciones»**.",
        }
        return (
            f"¡Vamos a resolver **{expr_str}** juntos paso a paso! (Recuerda que como tu tutor te doy la pista para que tú des el golpe final):\n\n"
            f"1. **Observa las fracciones**: **{a}/{b}** y **{c}/{d}**.\n"
            f"2. **Procedimiento**: {hint}\n\n"
            f"¿Qué resultado obtienes al hacer ese paso? Escríbeme tu respuesta aquí:"
        )

    # 2. División de dos enteros: ej. "y cuanto seria 5/2", "cuanto es 15 entre 3"
    m_div = DIV_RE.search(norm)
    if m_div:
        a, b = int(m_div.group(1)), int(m_div.group(2))
        if b == 0:
            return "No es posible dividir entre **0**. Intenta con un divisor distinto de cero."

        q = a // b
        r = a % b
        exact_val = Rational(a, b)
        expr_str = f"{a} ÷ {b}"

        if r == 0:
            hint = f"Busca qué número multiplicado por **{b}** da exactamente **{a}** ({b} × ? = {a})."
            steps = (
                f"1. **Dividendo**: **{a}** | **Divisor**: **{b}**.\n"
                f"2. Es una división exacta: piensa cuántas veces cabe el **{b}** dentro del **{a}**.\n"
                f"3. Pista: repasa la tabla del **{b}** hasta llegar a **{a}**."
            )
        else:
            near = q * b
            hint = f"El **{b}** cabe **{q}** veces en el **{a}** ({b} × {q} = {near}) y sobra **{r}**. Luego divide ese residuo **{r} ÷ {b}** para obtener la parte decimal."
            steps = (
                f"1. **Dividendo**: **{a}** | **Divisor**: **{b}**.\n"
                f"2. **Parte entera**: ¿Cuántas veces enteras cabe el **{b}** en el **{a}** sin pasarse? Cabe **{q}** {'vez' if q == 1 else 'veces'} porque **{b} × {q} = {near}**.\n"
                f"3. **Residuo**: A **{a}** réstale **{near}** y te sobra **{r}**.\n"
                f"4. **Parte decimal**: Para repartir el **{r}** que sobra, pon un punto decimal, agrégale un cero (**{r * 10}**) y divide **{r * 10} ÷ {b}**."
            )

        state["custom_problem"] = {
            "expr": expr_str,
            "expected": str(exact_val),
            "hint": hint,
            "closing": "¡Excelente dominio de la división!",
        }
        return (
            f"¡Analicemos **{a} ÷ {b}** (**{a}/{b}**) paso a paso para que tú mismo saques el resultado!\n\n"
            f"{steps}\n\n"
            f"¿Cuánto te da entonces **{a} ÷ {b}** (en decimal o fracción)? Escríbelo aquí para comprobarlo:"
        )

    # 3. Suma, resta o multiplicación de dos enteros: ej. "cuanto es 8 * 7", "cuanto es 15 + 28"
    m_arith = ARITH_RE.search(norm)
    if m_arith and any(w in norm for w in ("cuanto", "seria", "calcula", "resuelve", "+", "-", "*", "×", "mas", "menos", "por")):
        a, op_raw, b = int(m_arith.group(1)), m_arith.group(2), int(m_arith.group(3))
        if op_raw in {"+", "mas"}:
            ans = a + b
            expr_str = f"{a} + {b}"
            hint = f"Suma primero las unidades y luego las decenas de **{a}** y **{b}**."
        elif op_raw in {"-", "menos"}:
            ans = a - b
            expr_str = f"{a} - {b}"
            hint = f"Encuentra la diferencia entre **{a}** y **{b}**."
        else:
            ans = a * b
            expr_str = f"{a} × {b}"
            hint = f"Suma el número **{a}** un total de **{b}** veces (o descompón {b} para multiplicar más fácil)."

        state["custom_problem"] = {
            "expr": expr_str,
            "expected": str(ans),
            "hint": hint,
            "closing": "¡Bien calculado!",
        }
        return (
            f"¡Resolvamos **{expr_str}** paso a paso!\n\n"
            f"• **Pista**: {hint}\n\n"
            f"¿Cuál es tu resultado para **{expr_str}**?"
        )

    return None


def match_specific_operation_guide(message: str, state: dict) -> tuple[str, str | None] | None:
    active_exercise_id = state.get("active_exercise_id")
    if active_exercise_id:
        return None

    # 1. ¿Está respondiendo al reto personalizado que acaba de plantear?
    custom_eval = evaluate_pending_custom_problem(message, state)
    if custom_eval is not None:
        return custom_eval, state.get("current_topic")

    # 2. ¿Está preguntando cuánto es una operación numérica concreta (ej. "y cuanto seria 5/2")?
    socratic_math = build_socratic_math_guide(message, state)
    if socratic_math is not None:
        return socratic_math, state.get("current_topic")

    normalized = normalize_text(message)
    if any(word in normalized for word in ("ponme un ejercicio", "dame un reto", "dame un ejercicio", "otro ejercicio", "pista")):
        return None

    # 3. Guías de operaciones generales
    for pattern, topic_id, explanation in SPECIFIC_GUIDES:
        if pattern.search(normalized):
            return explanation, topic_id

    return None
