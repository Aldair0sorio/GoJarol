# BRIEF DE ML/NLP · GO JAROL
Hackathon Veracruz Tech Week 2026 · Reto 5 "Aprender a la jarocha" · 24 horas

## 1. Situación
- Arrancamos el miércoles 11 a las 13:00. Cierre de código y entrega: jueves 12 a las 10:30.
- Puntos de control con al menos un commit de cada integrante: 17:00 y 20:30. El historial de Git cuenta como evidencia.
- El jueves a las 7:00 los organizadores anuncian un requisito nuevo que debe aparecer en el demo. Diseña todo para poder agregar intenciones o temas rápido.
- Presentamos 4 min de demo en vivo ante el jurado, más 4 min de preguntas. Cualquier integrante debe poder explicar cualquier parte. Si nadie puede explicar el NLP, nos descalifican.

## 2. Qué es Jarol y la regla que manda
Jarol es un tutor educativo conversacional para estudiantes de secundaria y bachillerato, pensado para celular y poca conexión. El reto pide un tutor que pregunte antes de responder, se adapte al nivel y le dé al docente una vista del avance del grupo.

Regla del asesor del evento: el asistente NO resuelve problemas ni da el resultado de una operación. Solo explica el tema y guía. Ejemplo: si el alumno plantea un problema con quebrados, Jarol explica cómo se suman, restan, multiplican y dividen quebrados, pero no resuelve ese problema.

Cómo lo cumplimos: Jarol explica con un ejemplo resuelto con OTROS números y le pregunta al alumno cómo aplicarlo a su caso. SymPy solo verifica lo que el alumno escribe; nunca resuelve para mostrar.
Consecuencia para ti: la intención pedir_solucion es la más importante de detectar bien.

## 3. Tu parte (ML/NLP)
Un módulo independiente en ml/ que el backend (Django) llama así:

    analyze_message(message: str, context: dict) -> dict

- Entrada context (el backend lo arma): {"nivel": "secundaria", "grado": 2, "ejercicio_activo": false, "ultima_intencion": null, "tema_actual": null}
- Salida:

    {
      "intent": "solicitar_explicacion",
      "intent_confidence": 0.0,
      "subject": "aritmetica",
      "topic": "fracciones",
      "topic_score": 0.0,
      "needs_clarification": false
    }

Los números son ilustrativos. Las confianzas reales las calcula el modelo. El contrato exacto se acuerda con backend; no lo cambies sin avisar.

## 4. Alcance de contenido (ya acordado)
Solo 3 temas activos, hechos bien:
- Aritmética → Fracciones (equivalentes, suma, resta, multiplicación, división)
- Álgebra → Ecuaciones lineales
- Matemáticas → Teorema de Pitágoras

Las 9 materias (Matemáticas, Español, Historia, Geografía, Física, Álgebra, Química, Biología, Aritmética) aparecen en el catálogo, pero las otras 6 están "próximamente". Si el mensaje trata de una materia no activa, debes reconocer la materia y devolver topic: null. Propuesta a acordar con backend: agregar topic_available: true/false a la salida.

## 5. Intenciones (empieza con estas 15)
solicitar_explicacion, solicitar_ejemplo, simplificar_explicacion, solicitar_pista, solicitar_reto, responder_ejercicio, verificar_respuesta, solicitar_retroalimentacion, cambiar_tema, repetir_ejercicio, consultar_progreso, saludar, finalizar_conversacion, solicitar_aclaracion, *pedir_solucion* (nueva: "resuélveme esto", "dame el resultado de...", "cuánto da...").

Nota: respuestas como "12", "3/4" o "x=5" dependen del contexto. Si ejercicio_activo es true, detéctalas con reglas (regex) primero y deja el modelo como respaldo.

## 6. Datos
- Intenciones: unas 30-40 frases por intención, en español mexicano, con variantes informales, errores de ortografía, mensajes cortos tipo WhatsApp, sin acentos. Mezcla temas distintos en las frases.
- Catálogo de temas: JSON con materia, tema, subtemas y sinónimos (por ejemplo "quebrados", "fracciones", "fraccionarios"). Datos de intenciones y banco de conocimiento educativo van SEPARADOS.
- Todo es sintético. Cero datos reales de estudiantes.
- Si generas frases con IA, revísalas a mano y anótalo en la Bitácora de IA.

## 7. Modelo y evaluación
- Intenciones: TF-IDF (palabras y n-gramas de caracteres, ayuda con errores de ortografía) + Logistic Regression en scikit-learn.
- Temas: TF-IDF + similitud coseno contra el catálogo. Sentence Transformers solo si sobra tiempo; no es prioridad.
- Separa train/validación/test ANTES de ampliar datos; evita frases duplicadas entre conjuntos.
- Test con mensajes escritos por otra persona del equipo, con un estilo distinto.
- Reporta precision, recall y F1 por intención, y matriz de confusión. Pon las métricas reales, sin redondear a favor. No inventes cifras.
- Define el umbral de needs_clarification con el conjunto de validación, no a ojo.
- Guarda con joblib, versionado: intent_v1.joblib, junto a un JSON con fecha, versión del dataset y métricas.
- Restricciones: sin APIs externas de IA (OpenAI, Gemini, Claude), sin modelos generativos, y todo debe correr en local y rápido.

## 8. Estructura en el repo (tu carpeta es ml/)
    ml/
    ├── README.md
    ├── data/            (intents.csv, catalog.json)
    ├── training/        (scripts de entrenamiento y evaluación)
    ├── models/          (modelos .joblib versionados)
    ├── inference/       (analyze_message)
    └── tests/

Debe poder correrse sola: python -m ml.inference "no entiendo como sumar fracciones".

## 9. Plan de entrega
- Antes de las 16:00: contrato acordado y una VERSIÓN 0 de analyze_message basada en palabras clave, con la misma firma, para que backend y frontend integren sin esperar al modelo real.
- 16:45: primer commit con dataset v1, catálogo y primer modelo entrenado. Haz push.
- 20:15: evaluación completa, matriz de confusión, pruebas y documentación. Haz push.
- Noche: corrige los errores más frecuentes con mensajes nuevos. No inventes más intenciones sin consultar.
- Jueves 7:00: prepárate para el requisito nuevo. Si exige una intención o tema nuevo, que sea cuestión de agregar datos y reentrenar.
- Jueves antes de las 9:30: congela cambios. Deja el README del módulo y prepara qué explicarás al jurado.

## 10. Reglas del hackatón que te afectan
- Declara en el README las librerías usadas (scikit-learn, joblib, pandas, SymPy...).
- Anota en la Bitácora de IA qué herramientas usaste, para qué y qué decidiste.
- No presentes como funcional algo que no lo es. En el demo decimos: "clasificador de intenciones entrenado + motor conversacional por reglas y plantillas", no "IA generativa".
- No subas .env, datos personales ni archivos pesados.

## 11. Git
- Trabaja en la rama ml-nlp y solo dentro de ml/.
- Flujo: git pull antes de empezar, commits pequeños, push seguido, Pull Request a main cuando algo funcione.
- Si tocas algo fuera de ml/, avisa al grupo antes.

## Instrucciones para tu asistente de código
Eres ingeniero de ML sénior. Somos principiantes: explica cada archivo y cada decisión en lenguaje sencillo, haz cambios pequeños que podamos probar y no agregues dependencias innecesarias. Empieza por proponer la estructura de ml/, el contrato y la versión 0 por palabras clave. Después construye el dataset, el entrenamiento y la evaluación paso a paso. Nunca inventes métricas ni contenido académico.