"""Genera corpus sintetico reproducible de intenciones para Go Jarol.

ATENCION: Las frases sinteticas no reemplazan pruebas con usuarios reales.
Las plantillas de train/validation/test son disjuntas, y el set realista
esta escrito manualmente para reducir la fuga de patrones.
"""
from __future__ import annotations

import csv
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

SEED = 20261111
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Distribucion intencional, orientada a uso educativo. Total = 50,000.
COUNTS = {
    "saludar": 450,
    "solicitar_explicacion": 11000,
    "simplificar_explicacion": 5200,
    "solicitar_ejemplo": 6000,
    "solicitar_pista": 5000,
    "solicitar_reto": 7000,
    "verificar_respuesta": 5500,
    "solicitar_retroalimentacion": 3500,
    "repetir_ejercicio": 1900,
    "cambiar_tema": 2300,
    "consultar_progreso": 1700,
    "despedirse": 450,
}
assert sum(COUNTS.values()) == 50000

TOPICS = [
    "fracciones", "sumas con fracciones", "fracciones equivalentes", "números decimales",
    "divisiones", "multiplicaciones", "porcentajes", "regla de tres", "números negativos",
    "ecuaciones de primer grado", "despejar la x", "propiedades de las potencias",
    "raíz cuadrada", "perímetro", "áreas de figuras", "teorema de Pitágoras",
    "ángulos", "probabilidad", "gráficas", "razonamiento matemático",
    "comprensión lectora", "idea principal de un texto", "acentuación", "uso de la coma",
    "signos de puntuación", "ortografía", "sujeto y predicado", "verbos",
    "tiempos verbales", "sinónimos y antónimos", "tipos de texto", "conectores",
    "resumen de un texto", "metáforas", "texto argumentativo", "inferencias al leer",
]
SCHOOL = [
    "", "voy en primero de secundaria", "soy de segundo de secundaria",
    "voy en tercero de secundaria", "estudio primero de prepa",
    "ando en segundo semestre de bachillerato", "curso cuarto semestre de prepa",
    "voy en sexto semestre de bachillerato", "tengo examen mañana",
    "estoy estudiando para un examen", "es para mi tarea", "lo estamos viendo en clase",
    "apenas estoy aprendiendo", "se me complica mucho", "quiero practicar en el celular",
]
OPENERS = ["", "Jarol, ", "Oye Jarol, ", "oye, ", "una duda: ", "hola Jarol, ",
           "porfa, ", "disculpa, ", "me ayudas? ", "hey Jarol, ", "a ver, ", "bro, "]
CLOSERS = ["", " por favor", " porfa", " plis", " si puedes", " si se puede",
           " porfis", " gracias", " xfa", " cuando puedas", " porfavor", " pls"]
ANSWERS = ["5", "12", "3/4", "0.5", "x = 7", "25", "8 centímetros",
           "la opción B", "la segunda opción", "un sustantivo", "el sujeto"]

# Tres particiones de plantillas escritas por separado (no split aleatorio por filas).
# Formato {topic} y {answer}: la plantilla se rellena con un contenido escolar real.
TEMPLATES = {
"saludar": {
 "train": ["hola", "buenas", "holaaa", "buen día", "buenas tardes", "buenas noches", "qué onda", "qué tal Jarol", "hola tutor", "holi", "buenas Jarol", "hey", "qué hubo", "aquí ando", "ya llegué", "hola de nuevo"],
 "validation": ["saludos profe virtual", "hola qué se cuenta", "buenasss Jarol", "ando por aquí"],
 "test": ["qué ondaaa tutor", "muy buenas Jarol", "qué hay de nuevo", "holis, aquí estoy"],
},
"solicitar_explicacion": {
 "train": ["explícame {topic}", "no entiendo {topic}", "qué es {topic}", "me enseñas {topic}", "tengo dudas con {topic}", "no le agarro a {topic}", "cómo funciona {topic}", "quiero aprender {topic}", "enséñame desde cero {topic}", "ayúdame a comprender {topic}", "de qué trata {topic}", "estoy perdido con {topic}", "no sé nada de {topic}", "necesito que me aclares {topic}", "me cuesta entender {topic}", "cómo se hace lo de {topic}", "puedes contarme sobre {topic}", "ando batallando con {topic}", "me explicas el tema de {topic}", "quiero saber más sobre {topic}"],
 "validation": ["me quedé atorado aprendiendo {topic}", "me podrías enseñar lo básico de {topic}", "qué debería saber de {topic}", "no comprendo bien para qué sirve {topic}"],
 "test": ["ando bien confundido con eso de {topic}", "quiero entender la idea detrás de {topic}", "me pierdo cuando el profe habla de {topic}", "desde dónde empiezo para aprender {topic}"],
},
"simplificar_explicacion": {
 "train": ["explícamelo más fácil", "dilo con palabras sencillas", "no entendí lo anterior", "estuvo muy complicado", "haz la explicación más simple", "dímelo como para principiante", "bájale un poquito la dificultad", "me revolviste con esa explicación", "lo puedes decir más claro", "habla más fácil de {topic}", "me perdí en tu explicación", "repítelo de forma sencilla", "no capto lo que dijiste", "usa palabras que yo entienda", "eso sonó muy técnico", "puedes hacerlo menos complicado", "estoy confundido con lo que explicaste", "una explicación más básica de {topic}"],
 "validation": ["te entendí a medias, dilo diferente", "eso quedó muy enredado", "me lo traduces a lenguaje fácil", "hazlo menos técnico porque me perdí"],
 "test": ["se me hizo bolas la explicación", "¿me lo cuentas como si apenas empezara?", "esa respuesta estuvo pesada, simplifícala", "lo que acabas de decir me confundió más"],
},
"solicitar_ejemplo": {
 "train": ["dame un ejemplo de {topic}", "ponme un ejemplo sobre {topic}", "me muestras un ejemplo de {topic}", "quiero ver un ejemplo de {topic}", "ejemplifícalo con algo sencillo", "puedes ilustrar {topic} con un caso", "enséñame un caso práctico de {topic}", "cómo sería un ejemplo de {topic}", "dame una demostración con un caso", "muéstrame uno resuelto como ejemplo", "quiero verlo aplicado en un ejemplo", "pon un caso de la vida real sobre {topic}", "me das otro ejemplo de {topic}", "necesito un ejemplo para entender", "dame un caso concreto de {topic}", "haz un ejemplo explicado de {topic}"],
 "validation": ["aterriza {topic} en un caso cotidiano", "ponme una situación que use {topic}", "me serviría ver un ejemplo ilustrado", "enséñame cómo se ve en la práctica {topic}"],
 "test": ["¿cómo se aplicaría eso en la vida diaria?", "necesito ver un caso con {topic}", "píntame una situación donde se use {topic}", "muestra cómo se aplica {topic} en un caso real"],
},
"solicitar_pista": {
 "train": ["dame una pista", "ayúdame pero no me digas el resultado", "me puedes orientar tantito", "qué paso hago ahora", "no quiero la respuesta, solo una pista", "me atoré, guíame", "dame una ayudita", "cómo puedo empezar el ejercicio", "pásame una pista chiquita", "no sé cuál es el siguiente paso", "oriéntame con este problema", "dime por dónde seguir", "pista sin resolverlo", "necesito una pista de {topic}", "dame una señal para continuar", "solo ayúdame a pensar el paso siguiente", "me quedé a medias, qué sigue", "hazme una pregunta que me ayude a resolverlo"],
 "validation": ["déjame descubrirlo, solo dame dirección", "avísame qué revisar sin darme la solución", "estoy trabado, oriéntame un poco", "quiero empujoncito para avanzar, no la respuesta"],
 "test": ["no me lo resuelvas, encamíname", "me bloqueé con el problema, ¿una pista?", "nomás indícame por dónde va", "¿qué podría revisar para seguir sin copiarte?"],
},
"solicitar_reto": {
 "train": ["ponme un ejercicio de {topic}", "quiero un reto de {topic}", "hazme preguntas para practicar {topic}", "quiero practicar {topic}", "mándame un problema de {topic}", "dame tarea cortita de {topic}", "puedes ponerme a prueba en {topic}", "invéntame un ejercicio de {topic}", "quiero un examen rápido de {topic}", "necesito practicar con un problema", "vamos a hacer un reto", "pregúntame algo de {topic}", "dame un ejercicio difícil de {topic}", "haz un mini quiz sobre {topic}", "pon un reto fácil sobre {topic}", "quiero contestar preguntas de {topic}", "practiquemos {topic}", "dame ejercicios de opción múltiple sobre {topic}", "me pones a resolver algo de {topic}", "quiero saber si aprendí {topic}"],
 "validation": ["quiero medir qué tanto sé de {topic}", "armemos un desafío de {topic}", "haz que resuelva un problema de {topic}", "ponme a trabajar con preguntas de {topic}"],
 "test": ["échame un problema para resolver yo", "quiero entrenar con una prueba de {topic}", "me puedes retar con {topic}", "vamos a calarme con un cuestionario de {topic}"],
},
"verificar_respuesta": {
 "train": ["está bien mi respuesta", "mi resultado es {answer}, está correcto", "revisa si lo hice bien", "comprueba mi procedimiento", "sí le atiné con {answer}", "lo resolví correctamente", "puedes revisar mi respuesta", "es válido que me diera {answer}", "esa respuesta está correcta", "checa si mi resultado sirve", "así queda bien", "mi solución fue {answer}, está bien", "me salió {answer}, me confirmas", "quiero saber si acerté", "evalúa lo que respondí", "verifica el resultado que te envié", "¿lo hice bien o no?", "checa si acerté en el ejercicio"],
 "validation": ["te paso mi resultado {answer}, lo ves bien", "¿esta solución está aceptable?", "¿me confirmas si acerté al responder {answer}?", "comprueba si mi cuenta dio lo correcto"],
 "test": ["¿mi operación pasó la prueba?", "¿puedes comprobar lo que contesté?", "¿es equivalente mi respuesta {answer}?", "¿coincide mi solución con la esperada?"],
},
"solicitar_retroalimentacion": {
 "train": ["en qué me equivoqué", "por qué salió mal", "dime qué hice incorrecto", "explícame mi error", "qué parte falló", "dónde estuvo el fallo", "quiero entender por qué no acerté", "qué puedo mejorar", "revisa en dónde fallé", "cuál fue mi equivocación", "qué confundí en ese ejercicio", "por qué me marcaste mal", "qué estaba pensando mal", "ayúdame a detectar mi error", "explícame por qué me equivoqué", "dónde me desvié", "qué está mal en mi procedimiento", "no entiendo por qué fallé"],
 "validation": ["señala el paso en que metí la pata", "quiero aprender de mi fallo", "qué concepto confundí en mi respuesta", "¿por qué no me salió bien?"],
 "test": ["¿en qué parte la regué?", "¿qué idea tuve equivocada?", "dime cuál fue la confusión de fondo", "ayúdame a revisar el razonamiento donde fallé"],
},
"repetir_ejercicio": {
 "train": ["quiero repetir este ejercicio", "déjame intentarlo otra vez", "reinicia el reto", "ponme el mismo problema de nuevo", "quiero una segunda oportunidad", "repite la pregunta anterior", "puedo volver a contestar", "vamos a hacer de nuevo ese ejercicio", "quiero reintentar", "borra mi intento y comienzo otra vez", "quiero rehacer el reto", "otra oportunidad con el mismo problema", "repetimos la actividad", "quiero volver a resolverlo", "dame de nuevo esta misma pregunta", "no cambies el problema, quiero repetirlo"],
 "validation": ["deja que haga otro intento del mismo", "¿lo puedo contestar otra vez desde el principio?", "quiero volver a empezar esta pregunta", "me das revancha con ese ejercicio"],
 "test": ["otra vuelta al mismo reto", "quiero regresar a esa pregunta y reintentar", "regrésame al ejercicio que fallé", "¿podemos repetir el problema tal cual?"],
},
"cambiar_tema": {
 "train": ["mejor cambiemos a {topic}", "ahora quiero estudiar {topic}", "dejemos esto y veamos {topic}", "pasemos a {topic}", "quiero hablar de {topic} en lugar de esto", "puedes cambiar la materia a español", "vamos a otro tema", "ya no quiero esto, prefiero {topic}", "cambiemos de matemáticas a español", "terminemos este tema y veamos {topic}", "quiero dejar el ejercicio y estudiar {topic}", "mejor seguimos con {topic}", "otra materia por favor", "olvida este tema, ahora {topic}", "ya acabé aquí, sigamos con {topic}", "vamos a cambiar de tema"],
 "validation": ["quiero moverme a otra materia, {topic}", "cierra este asunto y abre {topic}", "prefiero cambiar el enfoque a {topic}", "salgamos de aquí y estudiemos {topic}"],
 "test": ["hasta aquí con eso, ahora vámonos a {topic}", "me aburrí de este tema, brincamos a {topic}", "¿puedo saltar a {topic} en vez de seguir aquí?", "dejemos pendiente esto, me paso a {topic}"],
},
"consultar_progreso": {
 "train": ["cómo voy en la clase", "muéstrame mi progreso", "cuántos puntos llevo", "qué tanto he aprendido", "quiero ver mis avances", "cómo va mi nivel", "cuál es mi racha", "enséñame mis estadísticas", "cuánto xp tengo", "quiero revisar mis resultados", "en qué voy mejorando", "qué temas ya domino", "cuál es mi liga actual", "muéstrame mi desempeño en {topic}", "cuántos ejercicios he completado", "enséñame mi porcentaje de aciertos", "cómo va mi aprendizaje", "cuántos retos he logrado"],
 "validation": ["cómo está mi rendimiento esta semana", "dónde puedo ver mis logros", "dime qué tal voy comparado con antes", "quiero consultar mi avance en {topic}"],
 "test": ["¿ya subí de nivel o sigo igual?", "¿me puedes dar un resumen de mi progreso académico?", "¿cuántas actividades exitosas llevo hasta hoy?", "¿en qué competencia he avanzado más?"],
},
"despedirse": {
 "train": ["adiós", "nos vemos", "hasta mañana", "bye Jarol", "gracias por hoy", "ya me voy", "chao", "hasta luego", "me despido", "terminamos por hoy", "nos hablamos después", "cierro sesión por ahora", "luego seguimos", "me retiro", "muchas gracias, nos vemos", "me voy a descansar"],
 "validation": ["ahí nos vidrios Jarol", "me desconecto, bye", "por ahora me despido", "nos vemos al rato tutor"],
 "test": ["ya estuvo por hoy, ahí muere", "me salgo, continuamos mañana", "bye bye, ahí te ves", "me tengo que ir, hasta la próxima"],
},
}

# Extras escritos específicamente por clase para que las expresiones tengan sentido.
CLASS_SUFFIX = {
    "saludar": ["", ", ya llegué", ", listo para estudiar", ", qué tal", ", soy nuevo", ", qué gusto", ", aquí estamos", ", ya entré", ", ¿cómo andas?"],
    "despedirse": ["", ", ya me voy", ", gracias", ", seguimos luego", ", Jarol", ", fue todo por hoy", ", toca descansar", ", mañana regreso", ", hasta la próxima"],
    "consultar_progreso": ["", " de esta semana", " de la clase", " en la app", " hasta hoy"],
    "solicitar_pista": ["", " con esto", " en este paso", " sin darme la solución", " con el ejercicio"],
    "repetir_ejercicio": ["", " de ahorita", " el de antes", " en el chat", " por última vez"],
}

# Conjunto de mensajes independientes redactados manualmente. Los alumnos reales
# deben proporcionar una prueba posterior adicional bajo consentimiento adecuado.
REALISTIC = {
"saludar": ["ke onda jarol", "holis ya estoy acá", "ey tutor", "buenas joven", "ola jarol", "hola soy nuevo acá", "qué rollo maestro", "buenas buenas", "hey ¿andamos?", "qué ondaa, ya entré"],
"solicitar_explicacion": ["cómo funcionan las fracciones si tengo pedazos diferentes", "no entiendo por qué la x pasa del otro lado", "profe yo me pierdo con la idea principal de un cuento", "explícame qué es el sujeto en una oración", "me explicas cómo hacer el mínimo común múltiplo", "ando atorado con el tema de los porcentajes", "como es eso de las palabras graves", "se me hace difícil entender qué significa una metáfora", "qué significa que dos fracciones sean equivalentes", "de qué va el teorema de pitagoras"],
"simplificar_explicacion": ["no te caché ni una, háblame normal", "me lo podrías explicar sin tanta palabra rara", "eso que pusiste está muy difícil para mí", "¿me lo dices como para alguien que empieza?", "yo no entendí lo que acabas de escribir", "no entendí tu explicación anterior, inténtalo fácil", "no uses términos tan técnicos", "¿puedes hacerlo más básico que eso?", "se me hizo bolas lo que dijiste", "me revolví con ese párrafo, acláralo"],
"solicitar_ejemplo": ["quiero ver una aplicación de esto en casa", "¿me puedes ilustrar con una cuenta de supermercado?", "¿cómo se vería eso en una oración real?", "pon un caso de un triángulo de la vida real", "dame un ejemplo de texto argumentativo", "¿me muestras un caso de fracciones equivalentes?", "una demostración de cuándo se usa la regla de tres", "quiero un ejemplo concreto con números", "¿puedes usar una historia corta para ilustrarlo?", "pon otro caso diferente para comprender"],
"solicitar_pista": ["me quedé en blanco, dame una ayudita", "no me sueltes la respuesta, nomás oriéntame", "qué debería revisar primero de este problema", "me ayudas con un paso, no con todo", "dame una señal para seguir pensando", "me atasqué, ¿por dónde empiezo?", "una pista chiquita nada más porfa", "no lo hagas por mí, solo guíame", "¿qué tengo que identificar primero?", "necesito una mano para continuar sin copiar"],
"solicitar_reto": ["échame un reto de fracciones para ver si puedo", "hazme cinco preguntas de ortografía", "quiero hacer un mini examen de español", "ponme una ecuación para resolver yo", "quiero competir conmigo con preguntas", "tírame un ejercicio de porcentajes", "¿me dejas una práctica cortita de lectura?", "hazme resolver un problema sin darme el resultado", "ponme un cuestionario para practicar", "¿puedo intentar un problema de pitágoras?"],
"verificar_respuesta": ["oye ¿sí está bien que me diera tres cuartos?", "mi x salió 7, ¿si está correcto?", "¿lo que contesté se acepta?", "¿me confirmas si la opción b es correcta?", "puse que era el predicado, ¿está bien?", "checa mi operación, porfis", "¿mi resultado coincide con el del reto?", "si me dio 42, ¿le atiné?", "¿el procedimiento que hice sirve?", "¿lo que escribí cuenta como respuesta correcta?"],
"solicitar_retroalimentacion": ["¿en cuál paso metí la pata?", "no quiero solo que me digas mal, dime por qué", "qué fue lo que confundí para fallar", "¿por qué se marca incorrecto lo que hice?", "¿me enseñas dónde estuvo mi error?", "qué parte de mi explicación estuvo mal", "explícame por qué no le atiné", "quiero entender el fallo que tuve", "¿qué debería corregir de mi razonamiento?", "¿dónde se rompió mi procedimiento?"],
"repetir_ejercicio": ["deja que lo vuelva a intentar sin cambiar los números", "¿puedo darle otra vuelta a ese mismo?", "quiero repetir la pregunta que acabo de fallar", "reinicia ese mismo reto para mí", "otra oportunidad con el mismo problema porfa", "no me mandes otro, repite este", "regresa el ejercicio al principio", "me gustaría volver a contestarlo", "¿podemos arrancar otra vez ese ejercicio?", "quiero rehacer el problema anterior"],
"cambiar_tema": ["ya no quiero mate, mejor español", "mejor cambiamos de fracciones a gramática", "deja esto tantito y vamos con ecuaciones", "terminé aquí, ahora a comprensión lectora", "salgamos de geometría y pasemos a ortografía", "me cambio de tema, quiero porcentajes", "dejo esto para luego y vemos sujeto y predicado", "mejor abrimos el tema de Pitágoras", "no más fracciones, ahora álgebra", "quiero pasar de español a matemáticas"],
"consultar_progreso": ["¿cuántos xp junté desde ayer?", "¿cómo voy de aciertos en matemáticas?", "¿qué temas ya traigo dominados?", "¿subí a plata esta semana?", "¿cuánto me falta para la siguiente liga?", "¿cuáles son mis puntos actuales?", "enséñame el historial de mis retos", "quiero ver cómo he mejorado con fracciones", "¿en qué fallo más seguido según mis resultados?", "¿cuántos ejercicios hice esta semana?"],
"despedirse": ["ahí te ves jarol, mañana sigo", "listo por hoy, me desconecto", "me tengo que ir a clase, bye", "ya me voy a dormir, adiós", "nos vemos luego profe virtual", "gracias por ayudarme, hasta mañana", "cierro por hoy, saludos", "ya estuvo, luego regreso", "hasta la próxima jarol", "se acabó mi tiempo, nos vemos"],
}


def clean_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^\w\d]+", " ", s).strip()


def maybe_typo(text: str, rng: random.Random) -> str:
    # Variaciones realistas pero controladas, sin cambiar la etiqueta.
    changes = [("por favor", "porfa"), ("porque", "xq"), ("también", "tmb"),
               ("matemáticas", "mates"), ("quiero", "kiero"), ("qué", "q"),
               ("más", "mas"), ("cómo", "como"), ("ejercicio", "ejersicio"),
               ("explicación", "explicacion"), ("pista", "pistita")]
    candidates = [(a,b) for a,b in changes if a in text.lower()]
    if candidates:
        a,b = rng.choice(candidates)
        return re.sub(re.escape(a), b, text, count=1, flags=re.IGNORECASE)
    return text


def sample_line(label: str, template: str, rng: random.Random) -> str:
    topic = rng.choice(TOPICS)
    answer = rng.choice(ANSWERS)
    line = template.format(topic=topic, answer=answer)
    if label in ("saludar", "despedirse"):
        # Evitar saludos llenos de temas o datos de grado ficticios.
        opener = rng.choice((["", "Jarol, ", "oye, ", "hey, ", "holaa, ", "profe, ", "qué tal, ", "saludos, ", "buenas, ", "amigo, "] if label == "saludar" else ["", "Jarol, ", "oye, ", "bueno, ", "ok, ", "listo, ", "sale, ", "entonces, ", "va, ", "perfecto, "]))
        line = opener + line
        line += rng.choice(CLASS_SUFFIX[label])
    else:
        if rng.random() < 0.67:
            line = rng.choice(OPENERS) + line
        if rng.random() < 0.54:
            line += rng.choice(CLOSERS)
        if rng.random() < 0.28:
            context = rng.choice(SCHOOL[1:])
            line = f"{context}, {line}" if rng.random() < 0.6 else f"{line}, {context}"
        if label in CLASS_SUFFIX and rng.random() < 0.35:
            line += rng.choice(CLASS_SUFFIX[label])
    if rng.random() < 0.09:
        line = maybe_typo(line, rng)
    if rng.random() < 0.4 and not line.endswith(("?", "!")):
        line += rng.choice(["", "!", "?", "??"])
    return re.sub(r"\s+", " ", line).strip()


def generate_split(name: str, counts: dict[str,int], seen: set[str], rng: random.Random) -> list[tuple[str,str]]:
    out = []
    for intent, total in counts.items():
        options = TEMPLATES[intent][name]
        made = 0
        tries = 0
        while made < total:
            tries += 1
            if tries > total * 100 + 20000:
                raise RuntimeError(f"Sin combinaciones suficientes para {intent}/{name}: {made}/{total}")
            line = sample_line(intent, rng.choice(options), rng)
            key = clean_key(line)
            if key in seen or len(line) < 3 or len(line) > 240:
                continue
            seen.add(key)
            out.append((line, intent))
            made += 1
    rng.shuffle(out)
    return out


def write_csv(path: Path, rows: list[tuple[str,str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "intent"])
        writer.writerows(rows)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    manual_keys = [clean_key(p) for values in REALISTIC.values() for p in values]
    if len(set(manual_keys)) != len(manual_keys):
        raise ValueError("El conjunto de evaluación manual contiene duplicados")
    seen: set[str] = set(manual_keys)  # Reservar las pruebas manuales ANTES de generar train.
    train = generate_split("train", COUNTS, seen, rng)
    val = generate_split("validation", {key: 100 for key in COUNTS}, seen, rng)
    test = generate_split("test", {key: 100 for key in COUNTS}, seen, rng)
    realistic = []
    for intent, values in REALISTIC.items():
        for phrase in values:
            key = clean_key(phrase)
            realistic.append((phrase, intent))
    rng.shuffle(realistic)
    write_csv(DATA_DIR / "intents_train.csv", train)
    write_csv(DATA_DIR / "intents_validation.csv", val)
    write_csv(DATA_DIR / "intents_test.csv", test)
    write_csv(DATA_DIR / "intents_realistic_test.csv", realistic)
    for label, rows in [("train",train),("validation",val),("test",test),("realistic_test",realistic)]:
        counts = Counter(intent for _,intent in rows)
        print(f"{label:>14}: {len(rows):>6} filas | {len(counts)} clases | minimo={min(counts.values())} maximo={max(counts.values())}")
    print("Duplicados normalizados entre datasets: 0")
    print("AVISO: Un holdout redactado por el mismo equipo NO sustituye una prueba con estudiantes reales.")

if __name__ == "__main__":
    main()
