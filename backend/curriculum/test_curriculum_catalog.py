import json
import shutil
from pathlib import Path

import pytest

from curriculum.coverage_report import build_report, markdown_report
from curriculum.services.curriculum_catalog import CurriculumCatalog, DEFAULT_CATALOG
from curriculum.services.knowledge_service import KnowledgeService
from exercises.services.exercise_selector import ExerciseSelector
from gojarol_ml.nlp.curriculum_retriever import CurriculumRetriever


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def catalog():
    return CurriculumCatalog()


def test_catalog_integrity_levels_grades_sources_and_versions(catalog):
    entries = catalog.entries
    assert len(entries) == len({entry["id"] for entry in entries}) == 23
    for subject in ("Matemáticas", "Español"):
        assert {entry["grade"] for entry in entries if entry["subject"] == subject} == {1, 2, 3}
    for entry in entries:
        assert entry["reference"]["source_id"] in catalog.sources
        assert entry["version"] and entry["model"]
        assert entry["pedagogical_validation"] is None
        assert all(identifier in {item["id"] for item in entries} for identifier in entry["prerequisites"])
        if entry["program_id"] == "mccems_2025":
            assert entry["semester"] is None  # Roman numerals in the agreement are not semester mappings.
    assert catalog.programs["dgb_2025"]["model"] != catalog.programs["dgb_2026_general"]["model"]
    assert catalog.programs["dgb_2026_modular"]["modality"] != catalog.programs["dgb_2026_general"]["modality"]
    catalog.entries[0]["aliases"].clear()
    assert catalog.entries[0]["aliases"]  # Consumers cannot mutate the catalog.


@pytest.mark.parametrize("mutation", ["duplicate", "grade", "semester", "reference", "version", "source", "unverified", "review", "prerequisite", "cycle"])
def test_invalid_catalog_data_is_rejected(tmp_path, mutation):
    target = tmp_path / "curriculum"
    shutil.copytree(DEFAULT_CATALOG, target)
    path = target / "competencies/secundaria/matematicas.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    entry = data["competencies"][0]
    if mutation == "duplicate":
        data["competencies"].append(dict(entry))
    elif mutation == "grade":
        entry["grade"] = 4
    elif mutation == "semester":
        entry["semester"] = 1
    elif mutation == "reference":
        entry["reference"]["source_id"] = "missing"
    elif mutation == "review":
        entry["pedagogical_validation"] = {"tests_passed": True}
    elif mutation == "prerequisite":
        entry["prerequisites"] = ["missing"]
    elif mutation == "cycle":
        entry["prerequisites"] = [entry["id"]]
    else:
        registry_path = target / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if mutation == "version":
            registry["schema_version"] = 2
        elif mutation == "source":
            registry["sources"][0]["url"] = "https://sep.gob.mx.attacker.test/fake.pdf"
        elif mutation == "unverified":
            registry["sources"][0]["verification"] = "indexed_only"
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        CurriculumCatalog(target)


def test_statuses_use_live_content_and_do_not_infer_pedagogical_validation(catalog):
    knowledge = KnowledgeService(ROOT / "content/topics")
    selector = ExerciseSelector(ROOT / "content/exercises")
    coverage = catalog.describe("mx.sep.f6.2024.mat.g1.ecuaciones", "mat_ecuaciones", knowledge, selector)
    assert coverage["cataloged"] and coverage["content_available"] and coverage["exercises_available"]
    assert coverage["relation"] == "partial" and not coverage["validated"]
    missing = catalog.describe("mx.sep.f6.2024.mat.g3.cuadraticas", "mat_cuadraticas", knowledge, selector)
    assert missing["cataloged"] and not missing["content_available"] and not missing["exercises_available"]
    pending = catalog.describe("mx.cosac.2025.pm.pf4", "mat_fracciones", knowledge, selector)
    assert pending["verification"] == "pending" and not pending["content_available"]
    assert not selector.select("mat_ecuaciones", 1, competencies=["despejar_dos_operaciones"])
    assert selector.select("mat_ecuaciones", 1, competencies=["despejar_suma_resta"])["id"] == "ecu_001"


def test_report_is_reproducible_and_denominator_is_only_cataloged_subset(catalog):
    knowledge = KnowledgeService(ROOT / "content/topics")
    selector = ExerciseSelector(ROOT / "content/exercises")
    report = build_report(catalog, knowledge, selector)
    assert report == build_report(catalog, knowledge, selector)
    assert report["totals"] == {
        "cataloged": 23, "content_available": 8, "exercises_available": 8,
        "without_content": 15, "pending_verification": 2, "validated": 0,
        "practice_supported": 8, "fully_implemented": 0,
    }
    assert report["practice_coverage_percent"] == 34.78
    assert report["full_coverage_percent"] == 0
    assert "no del currículo oficial completo" in markdown_report(report)
    assert len(report["sources"]) == 7


@pytest.mark.parametrize("message,context,topic,status,identifier", [
    ("ecuaciones", {"level": "secundaria", "grade": 1}, "mat_ecuaciones", "resolved", "mx.sep.f6.2024.mat.g1.ecuaciones"),
    ("ecuaciones cuadráticas", {"level": "secundaria", "grade": 3}, "mat_ecuaciones", "resolved", "mx.sep.f6.2024.mat.g3.cuadraticas"),
    ("sistemas de ecuaciones", {"level": "secundaria", "grade": 2}, "mat_ecuaciones", "resolved", "mx.sep.f6.2024.mat.g2.sistemas"),
    ("ecuaciones", {"level": "bachillerato", "model": "mccems_2025", "semester": 3}, "mat_ecuaciones", "resolved", "mx.mccems.2025.pm.algebra"),
    ("ecuaciones", {"level": "bachillerato", "model": "mccems_2026"}, "mat_ecuaciones", "context_unavailable", None),
    ("comprensión lectora", {"level": "bachillerato", "program_id": "mccems_2025"}, "esp_comprension", "resolved", "mx.mccems.2025.lyc.lectura_escritura"),
    ("vínculos entre lectura y escritura", {"program_id": "cosac_2025", "semester": 1}, None, "pending_verification", "mx.cosac.2025.lyc.s1.pf1"),
    ("fracciones y porcentajes", {"level": "secundaria", "grade": 1}, None, "ambiguous", None),
    ("una media de algodón", {}, None, "unmapped", None),
    ("mi ensayo de música", {}, None, "unmapped", None),
    ("fracciones", {}, "mat_fracciones", "practice", None),
])
def test_curricular_retrieval_is_specific_and_uses_context(catalog, message, context, topic, status, identifier):
    result = CurriculumRetriever(catalog.entries).retrieve(message, context, topic)
    assert result["status"] == status
    assert result["competency_id"] == identifier


def test_ambiguity_can_be_resolved_without_guessing(catalog):
    retriever = CurriculumRetriever(catalog.entries)
    ambiguous = retriever.retrieve("ecuaciones", {}, None)
    assert ambiguous["status"] == "ambiguous"
    chosen = retriever.retrieve("ecuaciones", {"competency_id": "mx.sep.f6.2024.mat.g1.ecuaciones"}, None)
    assert chosen["status"] == "resolved"
    assert chosen["competency_id"] == "mx.sep.f6.2024.mat.g1.ecuaciones"
