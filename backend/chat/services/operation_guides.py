import re
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
            "📌 **Ejemplo paso a paso**: $(3/4) \\div (2/5)$\n"
            "- Arriba: $3 \\times 5 = 15$\n"
            "- Abajo: $4 \\times 2 = 8$\n"
            "- Resultado: **15/8**.\n\n"
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
            "📌 **Ejemplo paso a paso**: $(2/3) \\times (4/5)$\n"
            "- Arriba: $2 \\times 4 = 8$\n"
            "- Abajo: $3 \\times 5 = 15$\n"
            "- Resultado: **8/15**."
        ),
    ),
    (
        re.compile(r"\b(rest\w*|sustra\w*)\b.*\b(fraccion\w*|quebrad\w*)\b|\b(fraccion\w*|quebrad\w*)\b.*\b(rest\w*|sustra\w*)\b"),
        "mat_fracciones",
        (
            "Para **restar fracciones** nos fijamos primero en el denominador (el número de abajo):\n\n"
            "1. **Mismo denominador**: Conserva el denominador y resta los numeradores.\n"
            "   - Ejemplo: $5/7 - 2/7 = (5 - 2)/7 = 3/7$.\n"
            "2. **Diferente denominador**: Convierte a fracciones equivalentes con un denominador común y luego resta los numeradores.\n"
            "   - Ejemplo: $3/4 - 1/2 \\rightarrow$ como $1/2 = 2/4$, restamos $3/4 - 2/4 = 1/4$.\n\n"
            "¿Quieres intentarlo? Escríbeme **«Ponme un ejercicio de fracciones»**."
        ),
    ),
    # 2. Operaciones aritméticas generales (cuando el alumno pregunta por dividir, multiplicar, restar o sumar en general)
    (
        re.compile(r"\b(divid\w*|division\w*|cociente|divisor|dividendo)\b"),
        None,
        (
            "**La división** consiste en repartir una cantidad (**dividendo**) en partes iguales según indica otro número (**divisor**):\n\n"
            "1. **Partes de la división**:\n"
            "   - **Dividendo**: número que vamos a repartir (ej. 24).\n"
            "   - **Divisor**: entre cuántos lo repartimos (ej. 6).\n"
            "   - **Cociente**: el resultado de cuántas veces cabe el divisor en el dividendo ($24 \\div 6 = 4$).\n"
            "   - **Residuo**: lo que sobra cuando la división no es exacta.\n"
            "2. **Cómo resolverla paso a paso**:\n"
            "   - Toma las primeras cifras del dividendo de izquierda a derecha que sean mayores o iguales al divisor.\n"
            "   - Busca qué número multiplicado por el divisor se acerca más sin pasarse.\n"
            "   - Resta ese producto y baja la siguiente cifra.\n"
            "3. **Comprobación**: $(\\text{Cociente} \\times \\text{Divisor}) + \\text{Residuo} = \\text{Dividendo}$.\n\n"
            "💡 *También puedo explicarte cómo **dividir fracciones** o despejar divisiones en **ecuaciones de primer grado**. ¿Cuál prefieres practicar?*"
        ),
    ),
    (
        re.compile(r"\b(multiplic\w*|tablas de multiplicar|factores|producto)\b"),
        None,
        (
            "**La multiplicación** es una suma abreviada donde sumamos un mismo número (**multiplicando**) tantas veces como indica otro (**multiplicador**):\n\n"
            "1. **Con números de varias cifras**:\n"
            "   - Coloca los números alineados a la derecha.\n"
            "   - Multiplica la cifra de las unidades de abajo por cada cifra de arriba (de derecha a izquierda), llevando las decenas.\n"
            "   - Luego multiplica la cifra de las decenas dejando un espacio a la derecha y suma los productos parciales.\n"
            "2. **Ley de los signos (Secundaria y Bachillerato)**:\n"
            "   - Signos iguales dan positivo: $(+) \\times (+) = +$ y $(-) \\times (-) = +$.\n"
            "   - Signos distintos dan negativo: $(+) \\times (-) = -$.\n\n"
            "💡 *Si quieres practicar cómo despejar multiplicaciones en álgebra, escríbeme: **«Ponme un ejercicio de ecuaciones»**.*"
        ),
    ),
    (
        re.compile(r"^\s*(?:explicame\s+|ensename\s+|enseña\s+|como\s+|que\s+es\s+)*(?:a\s+|como\s+|la\s+|las\s+)*(?:restar|resta|restas|sustraccion)\s*\??\s*$"),
        None,
        (
            "**La resta o sustracción** permite encontrar la diferencia entre dos cantidades (**minuendo** menos **sustraendo**):\n\n"
            "1. **Resta de números naturales y decimales**:\n"
            "   - Alinea las cifras por su valor posicional (unidades con unidades, decenas con decenas, y el punto decimal alineado).\n"
            "   - Resta columna por columna de derecha a izquierda. Si la cifra de arriba es menor que la de abajo, toma 1 decena prestada de la columna izquierda.\n"
            "2. **Resta con números negativos (Secundaria)**:\n"
            "   - Si restas un número mayor a uno menor (ej. $4 - 7$), resta el menor al mayor ($7 - 4 = 3$) y conserva el signo del número con mayor valor absoluto: **$-3$**.\n"
            "3. **Resta de fracciones**:\n"
            "   - Si tienen igual denominador, resta solo los numeradores ($4/5 - 1/5 = 3/5$). Si tienen distinto denominador, conviértelas primero a fracciones equivalentes.\n\n"
            "¿Quieres practicar con **fracciones** o con **ecuaciones con números negativos**?"
        ),
    ),
    (
        re.compile(r"^\s*(?:explicame\s+|ensename\s+|enseña\s+|como\s+|que\s+es\s+)*(?:a\s+|como\s+|la\s+|las\s+)*(?:sumar|suma|sumas|adicion)\s*\??\s*$"),
        None,
        (
            "**La suma o adición** reúne dos o más cantidades (**sumandos**) en un solo total:\n\n"
            "1. **Números enteros y decimales**:\n"
            "   - Alinea unidades con unidades, decenas con decenas (y el punto decimal si hay decimales).\n"
            "   - Suma de derecha a izquierda; si una columna suma 10 o más, escribe la unidad y lleva la decena a la siguiente columna.\n"
            "2. **Suma de números con signo**:\n"
            "   - Si ambos tienen el mismo signo, suma sus valores y conserva el signo (ej. $-4 + (-3) = -7$).\n"
            "   - Si tienen signos distintos, resta el menor del mayor y deja el signo del mayor (ej. $-8 + 5 = -3$).\n"
            "3. **Suma de fracciones**:\n"
            "   - Con igual denominador: suma los numeradores y conserva el denominador ($1/4 + 2/4 = 3/4$).\n\n"
            "Si quieres resolver retos interactivos de suma de fracciones, escríbeme: **«Ponme un ejercicio de fracciones»**."
        ),
    ),
    (
        re.compile(r"\b(pitagoras|hipotenusa|cateto\w*|triangulo rectangulo)\b"),
        None,
        (
            "**El Teorema de Pitágoras** se aplica en todo **triángulo rectángulo** (el que tiene un ángulo de 90°):\n\n"
            "- Los dos lados que forman el ángulo recto se llaman **catetos** ($a$ y $b$).\n"
            "- El lado más largo, opuesto al ángulo recto, se llama **hipotenusa** ($c$).\n"
            "- **Fórmula**: $a^2 + b^2 = c^2$\n\n"
            "📌 **Ejemplo clásico**: Si los catetos miden $a = 3$ y $b = 4$:\n"
            "1. Elevamos al cuadrado: $3^2 + 4^2 = 9 + 16 = 25$.\n"
            "2. Sacamos raíz cuadrada: $c = \\sqrt{25} = 5$."
        ),
    ),
]


def match_specific_operation_guide(message: str, active_exercise_id: str | None = None) -> tuple[str, str | None] | None:
    """
    Si el estudiante no está respondiendo un ejercicio activo y pregunta por una operación
    específica (como dividir, multiplicar, restar, sumar o Pitágoras) que no tiene un banco
    propio en content/topics, devuelve una explicación pedagógica detallada en lugar de
    '¿Sobre qué tema necesitas ayuda?' o de repetir el texto genérico.
    """
    if active_exercise_id:
        return None

    normalized = normalize_text(message)
    # No interceptar si el usuario está pidiendo explícitamente un reto/ejercicio
    if any(word in normalized for word in ("ponme un ejercicio", "dame un reto", "dame un ejercicio", "otro ejercicio", "pista")):
        return None

    for pattern, topic_id, explanation in SPECIFIC_GUIDES:
        if pattern.search(normalized):
            return explanation, topic_id

    return None
