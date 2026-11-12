"""Versioned academic metadata. Educational assets stay in their existing services."""

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_CATALOG = Path(__file__).resolve().parents[3] / "content/curriculum"


class CurriculumCatalog:
    def __init__(self, directory: str | Path = DEFAULT_CATALOG):
        directory = Path(directory)
        metadata = json.loads((directory / "registry.json").read_text(encoding="utf-8"))
        if metadata.get("schema_version") != 1:
            raise ValueError("Version de catalogo no soportada.")
        self.sources = self._index(metadata["sources"])
        self.programs = self._index(metadata["programs"])
        self.pending = deepcopy(metadata["pending_verifications"])
        entries = []
        for path in sorted((directory / "competencies").rglob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("schema_version") != 1:
                raise ValueError(f"Version invalida: {path.name}")
            entries.extend(data["competencies"])
        self._entries = self._index(entries)
        self._validate()

    @staticmethod
    def _index(items: list[dict]) -> dict:
        result = {}
        for item in items:
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier or identifier in result:
                raise ValueError("Identificador curricular invalido o duplicado.")
            result[identifier] = deepcopy(item)
        return result

    def _validate(self):
        for source in self.sources.values():
            url = urlparse(source["url"])
            if url.scheme != "https" or not any(
                (url.hostname or "").endswith(suffix)
                for suffix in (".sep.gob.mx", ".sems.gob.mx", ".segob.gob.mx")
            ):
                raise ValueError("La fuente curricular debe ser oficial y verificable.")
            if source["verification"] not in {"verified", "indexed_only", "unavailable"}:
                raise ValueError("Estado de fuente invalido.")
        for program in self.programs.values():
            if program["source_id"] not in self.sources or not program["model"] or not program["version"]:
                raise ValueError("Programa sin referencia o version.")
            if program["level"] not in {"secundaria", "bachillerato"}:
                raise ValueError("Nivel educativo invalido.")
        for entry in self._entries.values():
            required = {"id", "program_id", "grade", "semester", "area", "subject", "official_content_summary",
                        "learning_outcome_summary", "topic_id", "subtopic", "aliases", "prerequisites",
                        "reference", "verification", "bindings", "pedagogical_validation"}
            if required - entry.keys():
                raise ValueError("Competencia curricular incompleta.")
            program = self.programs.get(entry["program_id"])
            if program is None or entry["reference"]["source_id"] not in self.sources:
                raise ValueError("Programa o referencia desconocidos.")
            for field in ("area", "subject", "official_content_summary", "learning_outcome_summary", "topic_id", "subtopic"):
                if not isinstance(entry[field], str) or not entry[field].strip():
                    raise ValueError(f"Campo curricular invalido: {field}")
            if program["level"] == "secundaria":
                if type(entry["grade"]) is not int or entry["grade"] not in {1, 2, 3} or entry["semester"] is not None:
                    raise ValueError("Grado de secundaria invalido.")
            elif entry["grade"] is not None or (entry["semester"] is not None and (
                type(entry["semester"]) is not int or not 1 <= entry["semester"] <= 6
            )):
                raise ValueError("Semestre de bachillerato invalido.")
            reference = entry["reference"]
            if not reference.get("section") or (reference.get("page") is not None and (
                type(reference["page"]) is not int or reference["page"] < 1
            )):
                raise ValueError("Referencia sin seccion o pagina valida.")
            if entry["verification"] not in {"verified", "pending"}:
                raise ValueError("Estado de verificacion invalido.")
            if entry["verification"] == "verified" and self.sources[reference["source_id"]]["verification"] != "verified":
                raise ValueError("Una fuente pendiente no verifica una competencia.")
            if entry["verification"] == "verified" and program["verification"] != "verified":
                raise ValueError("El programa todavia esta pendiente de verificar.")
            if not isinstance(entry["aliases"], list) or not all(isinstance(alias, str) and len(alias.strip()) >= 5 for alias in entry["aliases"]):
                raise ValueError("Alias curricular demasiado general o invalido.")
            for binding in entry["bindings"]:
                if binding["relation"] not in {"partial", "prerequisite", "complete"} or not binding["note"]:
                    raise ValueError("Vinculo educativo sin alcance explicito.")
                if not isinstance(binding["exercise_competencies"], list):
                    raise ValueError("Competencias de ejercicios invalidas.")
            review = entry["pedagogical_validation"]
            if review is not None and (entry["verification"] != "verified" or not all(review.get(key) for key in ("reviewer", "date", "evidence"))):
                raise ValueError("Validacion pedagogica sin evidencia.")
            if any(item not in self._entries for item in entry["prerequisites"]):
                raise ValueError("Prerrequisito desconocido.")
        def visit(identifier, path):
            if identifier in path:
                raise ValueError("Ciclo de prerrequisitos.")
            for prerequisite in self._entries[identifier]["prerequisites"]:
                visit(prerequisite, path | {identifier})
        for identifier in self._entries:
            visit(identifier, set())

    @property
    def entries(self) -> list[dict]:
        return [self.get(identifier) for identifier in self._entries]

    def get(self, identifier: str) -> dict:
        if identifier not in self._entries:
            raise KeyError(identifier)
        entry = deepcopy(self._entries[identifier])
        program = self.programs[entry["program_id"]]
        return dict(entry, **{key: program[key] for key in ("level", "model", "version", "modality")})

    def describe(self, identifier: str, topic_id: str, knowledge, selector) -> dict:
        entry = self.get(identifier)
        binding = next((item for item in entry["bindings"] if item["topic_id"] == topic_id), None)
        verified = entry["verification"] == "verified"
        content = bool(verified and binding and knowledge.has_explanation(topic_id))
        exercises = selector.list_public_exercises(topic_id, binding["exercise_competencies"] or None) if verified and binding else []
        return {
            "competency_id": identifier, "topic_id": topic_id,
            "cataloged": True, "content_available": content,
            "exercises_available": bool(exercises),
            "validated": entry["pedagogical_validation"] is not None,
            "verification": entry["verification"],
            "relation": binding["relation"] if binding else None,
            "scope_note": binding["note"] if binding else "Sin contenido educativo vinculado.",
            "exercise_competencies": binding["exercise_competencies"] if binding else [],
            "reference": dict(entry["reference"], url=self.sources[entry["reference"]["source_id"]]["url"]),
        }
