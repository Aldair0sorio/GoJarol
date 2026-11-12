
from curriculum.services.knowledge_service import KnowledgeService



class HintService:
    def __init__(self, knowledge_service, exercise_selector=None):
        self.knowledge = knowledge_service
        self.selector = exercise_selector

    def _get_hint(self, topic_id, index, exercise_id=None):
        if exercise_id is None:
            return self.knowledge.get_hint(topic_id, index)

        if self.selector is None:
            raise ValueError("No hay selector de ejercicios.")

        return self.selector.get_hint(
            topic_id,
            exercise_id,
            index,
        )

    def get_next_hint(
        self,
        topic_id,
        hints_used=0,
        exercise_id=None,
    ):
        if hints_used < 0:
            raise ValueError("Contador de pistas invalido.")

        hint = self._get_hint(
            topic_id,
            hints_used,
            exercise_id,
        )

        if hint is not None:
            return {
                "message": hint,
                "strategy": "guided_hint",
                "hints_used": hints_used + 1,
                "requires_review": False,
            }

        count = 0
        while self._get_hint(topic_id, count, exercise_id) is not None:
            count += 1

        strategies = [
            (
                "alternative_explanation",
                self.knowledge.get_explanation(
                    topic_id, "alternative"
                ),
            ),
            (
                "concept_review",
                self.knowledge.get_explanation(
                    topic_id, "basic"
                ),
            ),
            (
                "guided_reflection",
                "Dime qué has intentado y en qué paso "
                "necesitas ayuda.",
            ),
        ]

        strategy, message = strategies[
            (hints_used - count) % len(strategies)
        ]

        return {
            "message": message,
            "strategy": strategy,
            "hints_used": hints_used + 1,
            "requires_review": True,
        }
