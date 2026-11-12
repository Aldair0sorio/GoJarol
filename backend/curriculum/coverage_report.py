"""Run with PYTHONPATH=backend;ml/src: python -m curriculum.coverage_report."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from curriculum.services.curriculum_catalog import CurriculumCatalog
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.exercise_selector import ExerciseSelector


def build_report(catalog, knowledge, selector) -> dict:
    groups = defaultdict(lambda: dict(cataloged=0, content_available=0, exercises_available=0,
                                     without_content=0, pending_verification=0, validated=0,
                                     practice_supported=0, fully_implemented=0))
    rows = []
    for entry in catalog.entries:
        descriptions = [catalog.describe(entry["id"], binding["topic_id"], knowledge, selector)
                        for binding in entry["bindings"]]
        content = any(item["content_available"] for item in descriptions)
        exercises = any(item["exercises_available"] for item in descriptions)
        practice = any(item["content_available"] and item["exercises_available"] for item in descriptions)
        complete = any(item["relation"] == "complete" and item["content_available"] and item["exercises_available"] for item in descriptions)
        counts = dict(cataloged=1, content_available=int(content), exercises_available=int(exercises),
                      without_content=int(not content), pending_verification=int(entry["verification"] != "verified"),
                      validated=int(entry["pedagogical_validation"] is not None),
                      practice_supported=int(practice), fully_implemented=int(complete))
        for key, value in counts.items():
            groups[(entry["level"], entry["subject"])][key] += value
        rows.append(dict(competency_id=entry["id"], program_id=entry["program_id"], grade=entry["grade"],
                         semester=entry["semester"], **counts, bindings=descriptions))
    totals = {key: sum(group[key] for group in groups.values()) for key in next(iter(groups.values()), {})}
    denominator = totals.get("cataloged", 0)
    return dict(
        schema_version=1,
        scope="Cobertura del catálogo semilla, no del currículo oficial completo. Apoyo parcial no equivale a competencia completa.",
        totals=totals,
        practice_coverage_percent=round(totals.get("practice_supported", 0) * 100 / denominator, 2) if denominator else 0,
        full_coverage_percent=round(totals.get("fully_implemented", 0) * 100 / denominator, 2) if denominator else 0,
        groups=[dict(level=level, subject=subject, **counts) for (level, subject), counts in sorted(groups.items())],
        competencies=rows, sources=list(catalog.sources.values()), programs=list(catalog.programs.values()),
        pending_verifications=catalog.pending,
    )


def markdown_report(report: dict) -> str:
    lines = ["# Cobertura curricular Go Jarol", "", report["scope"], "",
             "| Nivel | Asignatura | Catalogadas | Explicaciones | Ejercicios | Sin contenido | Por verificar | Validadas |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for group in report["groups"]:
        lines.append("| " + " | ".join(str(group[key]) for key in (
            "level", "subject", "cataloged", "content_available", "exercises_available", "without_content", "pending_verification", "validated"
        )) + " |")
    lines.extend(["", f"Apoyo funcional parcial: {report['totals'].get('practice_supported', 0)} / {report['totals'].get('cataloged', 0)} ({report['practice_coverage_percent']}%).",
                  f"Competencias completamente implementadas: {report['totals'].get('fully_implemented', 0)} ({report['full_coverage_percent']}%).",
                  "", "## Fuentes", ""])
    lines.extend(f"- [{source['title']}]({source['url']}) — {source['verification']}. {source['method']}" for source in report["sources"])
    lines.extend(["", "## Verificaciones pendientes", ""])
    lines.extend(f"- {item['task']}" for item in report["pending_verifications"])
    lines.extend(["", "## Competencias y vinculaciones", ""])
    for row in report["competencies"]:
        links = "; ".join(f"{item['topic_id']} ({item['relation']}; contenido={item['content_available']}, ejercicios={item['exercises_available']})" for item in row["bindings"])
        lines.append(f"- `{row['competency_id']}`: {links or 'sin contenido vinculado'}; pendiente={bool(row['pending_verification'])}.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = Path(__file__).resolve().parents[2] / "content"
    report = build_report(CurriculumCatalog(), KnowledgeService(content / "topics"), ExerciseSelector(content / "exercises"))
    result = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown_report(report)
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result)


if __name__ == "__main__":
    main()
