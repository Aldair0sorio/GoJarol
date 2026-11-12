"""Conservative retrieval over injected curriculum metadata, without training or I/O."""

import re
from copy import deepcopy

from gojarol_ml.nlp.topic_retriever import normalize_text


class CurriculumRetriever:
    def __init__(self, entries: list[dict]):
        self.entries = deepcopy(entries)

    def retrieve(self, message: str, context: dict | None = None, topic_hint: str | None = None) -> dict:
        context = context or {}
        query = normalize_text(message)
        matches = []
        for entry in self.entries:
            for alias in entry["aliases"]:
                for match in re.finditer(rf"(?<!\w){re.escape(normalize_text(alias))}(?!\w)", query):
                    matches.append((entry, match.start(), match.end()))
        # A specific phrase suppresses only shorter matches inside that same phrase.
        explicit = {entry["id"] for entry, start, end in matches if not any(
            other_start <= start and end <= other_end and (other_start < start or end < other_end)
            for _, other_start, other_end in matches
        )}
        pool = [entry for entry in self.entries if entry["id"] in explicit] if explicit else [
            entry for entry in self.entries
            if topic_hint and (entry["topic_id"] == topic_hint or any(binding["topic_id"] == topic_hint for binding in entry["bindings"]))
        ]
        mentioned_topics = {entry["topic_id"] for entry in pool} if explicit else set()
        filters = ("level", "grade", "semester", "model", "version", "program_id", "modality", "subject", "area")
        for field in filters:
            if context.get(field) is not None:
                pool = [entry for entry in pool if entry.get(field) == context[field] or (
                    field == "semester" and entry.get(field) is None
                )]
        if context.get("semester") is not None and any(entry["semester"] is not None for entry in pool):
            pool = [entry for entry in pool if entry["semester"] == context["semester"]]
        requested_id = context.get("competency_id")
        if requested_id:
            pool = [entry for entry in pool if entry["id"] == requested_id]
        candidates = [{key: entry[key] for key in (
            "id", "level", "grade", "semester", "model", "version", "program_id", "subject", "subtopic", "topic_id"
        )} for entry in pool]
        result = {"status": "unmapped", "candidates": candidates, "competency_id": None, "topic_id": topic_hint}
        if not pool:
            result["status"] = "context_unavailable" if context and (explicit or topic_hint) else "unmapped"
            if len(mentioned_topics) == 1:
                result["topic_id"] = next(iter(mentioned_topics))
        elif not context and topic_hint and all(
            topic_hint == entry["topic_id"] or any(b["topic_id"] == topic_hint for b in entry["bindings"]) for entry in pool
        ):
            # Preserve ungraded practice, without silently assigning it to a school program.
            result["status"] = "practice"
        elif len(pool) > 1:
            result["status"] = "ambiguous"
            result["topic_id"] = None
        else:
            entry = pool[0]
            binding_topics = {b["topic_id"] for b in entry["bindings"]}
            if len(binding_topics) > 1 and topic_hint not in binding_topics:
                result.update(status="ambiguous", topic_id=None, topic_options=sorted(binding_topics))
                return result
            result.update(
                status="resolved" if entry["verification"] == "verified" else "pending_verification",
                competency_id=entry["id"],
                topic_id=(topic_hint if topic_hint in binding_topics else (
                    next(iter(binding_topics)) if len(binding_topics) == 1 else entry["topic_id"]
                )),
            )
        return result
