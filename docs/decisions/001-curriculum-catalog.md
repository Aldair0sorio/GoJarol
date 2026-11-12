# ADR-001: Catálogo curricular separado del contenido educativo

## Estado

Implementado en `ivan-dev`, 2026-11-11. Sin persistencia, endpoints ni cambios de modelos Django.

## Contexto

Los seis bancos existentes permiten práctica, pero no representan por sí solos un currículo oficial. La dificultad adaptativa 1–3 no es un grado escolar. Un mismo banco puede apoyar distintos aprendizajes sin cubrirlos completamente.

## Decisión

`content/curriculum/registry.json` registra fuentes, programas, modelos, modalidades y verificaciones pendientes. `competencies/` divide la semilla por nivel y asignatura; no contiene soluciones educativas. Cada entrada tiene un ID estable, programa, grado o semestre nullable, resúmenes editoriales del contenido y aprendizaje oficiales, tema interno, subtema, alias, prerrequisitos, referencia, verificación y vínculos con los bancos existentes.

Los resúmenes no sustituyen al documento oficial. Los prerrequisitos son una propuesta interna, no seriación oficial. No se deduce el semestre a partir de numerales romanos del Acuerdo 21/08/25. Los programas COSAC 2025 y 2026 y las modalidades DGB se registran por separado; no se copian contenidos entre ellos.

Los IDs curriculares son identificadores internos estables de Go Jarol, no códigos oficiales de SEP.

`CurriculumCatalog` valida IDs, niveles, referencias, versiones, evidencia de revisión y el grafo de prerrequisitos. `CurriculumRetriever`, dentro de NLP, recibe metadatos por inyección y no lee archivos ni importa Django. Busca frases completas con límites de palabra; la frase específica desplaza a otra más corta solo cuando ocupa el mismo fragmento del mensaje. Dos menciones distintas no se convierten artificialmente en una sola interpretación.

`JarolAnalyzer` conserva el clasificador e incorpora opcionalmente el recuperador. `TutorService` usa el mismo recuperador si recibe un analizador anterior o de prueba. No se ejecutan dos recuperaciones cuando el analizador ya entrega el resultado curricular.

Con contexto académico, el tutor resuelve o pide aclaración, consulta la disponibilidad real y limita la selección al vínculo correspondiente. Los resultados públicos contienen IDs, estado y referencias; los evaluadores y las soluciones permanecen en sus servicios existentes. El progreso sigue siendo temporal por tema, no una certificación de dominio curricular. Un cambio de perfil limpia el ejercicio activo, conserva el progreso y recuerda las pistas usadas por ID.

Sin perfil se mantiene la práctica general anterior para los seis temas. Se devuelve `mode: practice` y ninguna competencia elegida: no se adivina un grado. Una pregunta específica sobre un tema no implementado se reconoce, pero no recibe una explicación de otro tema parecido.

## Disponibilidad y evidencia

- `cataloged`: existe una entrada en esta semilla.
- `content_available`: existe explicación en KnowledgeService y un vínculo curricular verificado.
- `exercises_available`: ExerciseSelector encuentra ejercicios compatibles con ese vínculo.
- `validated`: existe revisión pedagógica con responsable, fecha y evidencia. Las pruebas automatizadas nunca activan este estado.

Los vínculos indican `partial`, `prerequisite` o `complete`. Actualmente todos son parciales o prerrequisitos. Una lista vacía de `exercise_competencies` permite el banco completo del tema; una lista no vacía lo restringe por competencia interna de ejercicio. No se duplican los ejercicios.

La disponibilidad se calcula consultando servicios, no copiando indicadores estáticos. Una competencia pendiente de verificación no habilita contenido aunque exista un banco con un nombre parecido.

## Fuentes y límites

Se consultó el PDF oficial de [Fase 6](https://educacionbasica.sep.gob.mx/wp-content/uploads/2024/06/Programa_Sintetico_Fase_6.pdf), las tablas por grado en las páginas impresas 33–35 y 58–59, y los artículos 12–13 del [Acuerdo 21/08/25](https://sidof.segob.gob.mx/notas/docFuente/5765757).

Los índices oficiales de [COSAC](https://cosac.sems.gob.mx/Materiales/web/) y [DGB](https://dgb.sep.gob.mx/mapas-curriculares) estaban indexados, pero las consultas directas devolvieron 502 o agotaron tiempo. Solo se consultaron extractos indexados de los programas COSAC [Matemáticas 2025](https://cosac.sems.gob.mx/Materiales/web/descargar/29) y [Lengua y Comunicación 2025](https://cosac.sems.gob.mx/Materiales/web/descargar/68). Sus dos entradas se mantienen pendientes. Las [consideraciones DGB de RVOE 2026](https://dgb.sep.gob.mx/storage/recursos/2026/04/tk46gEw825-Consideraciones_academicas_2026_VFinal.pdf) se consultaron como contexto de modalidades, no como programa de contenidos.

La semilla no inventaría todos los contenidos nacionales: son 23 entradas, 21 con referencia verificada y 2 pendientes; los programas 2026 pendientes no se cuentan como competencias. Acentuación y ortografía se vinculan como herramientas previas para la meta de escritura del MCCEMS, no como PDA exclusivos de Fase 6. Los textos de comprensión no cubren aún los contextos interculturales y literarios de esos PDA. El informe no presenta apoyo parcial como cobertura completa.

## Uso

Desde la raíz del repositorio, en PowerShell con el entorno existente:

```powershell
$env:PYTHONPATH = 'backend;ml/src'
& ../.venv/Scripts/python.exe -m curriculum.coverage_report --output docs/COBERTURA_CURRICULAR.md
& ../.venv/Scripts/python.exe -m curriculum.coverage_report --format json --output docs/cobertura_curricular.json
& ../.venv/Scripts/python.exe backend/demo_tutor.py --level secundaria --grade 1
& ../.venv/Scripts/python.exe backend/demo_tutor.py --level bachillerato --model mccems_2025 --semester 3
```

El contrato Python es `process_message(message, state=None, *, academic_context=None)`. Contexto: `level`, `grade`, `semester`, `model`, `version`, `program_id`, `modality`, `subject`, `area`, `competency_id`. `None` conserva el perfil anterior; `{}` vuelve a práctica general. Un `competency_id` permite resolver una aclaración; el consumidor debe retirarlo del perfil para cambiar de competencia. No hay perfil de usuario persistido ni inferencia automática de grado desde texto libre.

## Ampliación

Agregar una fuente y un programa verificados antes de nuevas entradas; conservar IDs al corregir resúmenes. Otra versión curricular recibe otros IDs. Verificar grado/semestre en la tabla correspondiente. Documentar el alcance de cada vínculo y no usar `complete` por disponer solo de ejemplos. Registrar revisión docente por separado, ejecutar la suite y regenerar ambos reportes. Antes de implementar contenido de bachillerato por semestre, descargar y contrastar los programas completos de cada modelo y modalidad.
