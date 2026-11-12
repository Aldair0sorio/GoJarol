# ml/ · Clasificador de intención de Go Jarol

Módulo de NLP **local** (sin APIs externas de IA). Decide **qué quiere el alumno** (por ejemplo, pedir una explicación o una pista) y **de qué tema habla**. No genera respuestas: las respuestas del tutor salen de reglas y plantillas en `backend/chat/`.

> ⚠️ **Las métricas de abajo vienen de datos sintéticos y de un set pequeño escrito por el propio equipo. No demuestran el rendimiento con estudiantes reales.** Falta probar con frases de personas ajenas al dataset.

## Contenido

| Ruta | Qué es |
|---|---|
| `src/gojarol_ml/nlp/analyzer.py` | `JarolAnalyzer.analyze_message()`: combina intención, tema y currículo; es lo que usa el backend |
| `src/gojarol_ml/nlp/intent_classifier.py` | Carga el modelo entrenado y predice la intención |
| `src/gojarol_ml/nlp/topic_retriever.py` | Detecta el tema del mensaje con el catálogo `data/knowledge/topics.json` |
| `src/gojarol_ml/nlp/curriculum_retriever.py` | Relaciona el mensaje con el catálogo curricular |
| `scripts/generate_intents_dataset.py` | Genera el dataset sintético (semilla fija `20261111`) |
| `scripts/train_intents.py` | Entrena el modelo y guarda `artifacts/intent_classifier.joblib` y su metadata |
| `scripts/evaluate_intents.py` | Evalúa con los sets de prueba y guarda `artifacts/test_metrics.json` |
| `data/raw/` | `intents_train.csv`, `intents_validation.csv`, `intents_test.csv`, `intents_realistic_test.csv` |
| `artifacts/` | Modelo entrenado y métricas |

## Modelo

Un `Pipeline` de scikit-learn ([scripts/train_intents.py](scripts/train_intents.py)) con dos pasos:
- **TF-IDF** de n-gramas de caracteres (`analyzer="char_wb"`, `ngram_range=(3, 5)`, `min_df=2`, `strip_accents="unicode"`, `sublinear_tf=True`).
- **Regresión logística** (`class_weight="balanced"`, `max_iter=1200`, `random_state=42`).

Distingue **12 intenciones**: `cambiar_tema`, `consultar_progreso`, `despedirse`, `repetir_ejercicio`, `saludar`, `simplificar_explicacion`, `solicitar_ejemplo`, `solicitar_explicacion`, `solicitar_pista`, `solicitar_reto`, `solicitar_retroalimentacion` y `verificar_respuesta`.

## Generar, entrenar y evaluar

Desde la carpeta `ml/`, con un entorno que tenga las dependencias de `pyproject.toml` (el `backend/venv` del proyecto las tiene):

```bash
pip install -e .                               # instala el paquete gojarol_ml (el backend lo importa)
python scripts/generate_intents_dataset.py     # reescribe data/raw/*.csv
python scripts/train_intents.py                # reescribe artifacts/intent_classifier.joblib y la metadata
python scripts/evaluate_intents.py             # reescribe artifacts/test_metrics.json
python -m pytest -q                            # pruebas del módulo
```

**Verificado el 12 de noviembre de 2026**, en una copia de `ml/` fuera del repositorio para no reescribir los archivos versionados:
- Los tres pasos corrieron sin errores (15 s en total).
- Las métricas salieron **idénticas** a las de `artifacts/`.
- Los CSV generados tienen el mismo contenido que los del repo y solo cambian los finales de línea: el script escribe CRLF y git guarda LF.
- `python -m pytest -q` en `ml/`: **5 passed**.

## Métricas (leídas de `artifacts/`)

| Conjunto | Filas | Exactitud | F1 macro | Origen |
|---|---:|---:|---:|---|
| Entrenamiento | 50,000 | — | — | Sintético (`intent_classifier_metadata.json`, versión `synthetic-50000-v1`) |
| Validación | 1,200 | 0.77917 | 0.77224 | Sintético, con plantillas distintas a las de entrenamiento |
| Prueba (`intents_test.csv`) | 1,200 | 0.7575 | 0.7591 | Sintético; 291 errores |
| Prueba realista (`intents_realistic_test.csv`) | 120 | 0.8333 | 0.8358 | Frases escritas a mano por el equipo; 20 errores |

**Cómo leerlas:** cerca de 1 de cada 4 frases sintéticas de prueba se clasifica mal. Por eso el tutor no depende solo del clasificador:
- **Las respuestas a ejercicios** y **las letras del menú A/B/C** se interpretan con reglas antes de llegar al modelo.
- **Los pedidos de la respuesta** ("dame la respuesta") los detectan reglas en `backend/chat/services/integrity.py`.
- **Si el tema es ambiguo o no se detecta** (y la intención necesita un tema), el analizador pide aclarar (`needs_clarification`). La confianza de la intención (`intent_confidence`) se calcula y se devuelve, pero hoy **no** decide nada.

## Límites

- **Datos sintéticos:** el set "realista" lo escribió el mismo equipo, así que no sustituye una prueba con estudiantes.
- **Sin validación externa:** no se ha medido con estudiantes reales ni con frases de personas ajenas al equipo.
- **Sin aprendizaje en uso:** el modelo no aprende de las conversaciones y no se guarda el texto de los alumnos. Mejorarlo requiere juntar frases nuevas, etiquetarlas y volver a entrenar.
