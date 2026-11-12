
from curriculum.services.knowledge_service import KnowledgeService


class HintService:
    def __init__(self, knowledge_service: KnowledgeService):
        self.knowledge = knowledge_service

    def get_next_hint(
        self,
        topic_id: str,
        hints_used: int = 0,
    ) -> dict:
        if hints_used < 0:
            raise ValueError("El contador de pistas no puede ser negativo.")

        hint = self.knowledge.get_hint(topic_id, hints_used)

        if hint is not None:
            return {
                "message": hint,
                "strategy": "guided_hint",
                "hints_used": hints_used + 1,
                "requires_review": False,
            }

        # Cuando terminan las pistas, cambia la estrategia.
        strategies = [
            (
                "alternative_explanation",
                self.knowledge.get_explanation(topic_id, "alternative")
                + " ¿Qué parte necesitas comprender mejor?",
            ),
            (
                "concept_review",
                self.knowledge.get_explanation(topic_id, "basic")
                + " ¿Puedes identificar qué concepto necesitas utilizar?",
            ),
            (
                "guided_reflection",
                "Vamos por partes. Dime qué has intentado "
                "y en qué paso tienes dificultades.",
            ),
        ]

        # Alternar estrategias sin revelar la solución.
        cycle_index = (hints_used - self._hint_count(topic_id)) % len(
            strategies
        )
        strategy, message = strategies[cycle_index]

        return {
            "message": message,
            "strategy": strategy,
            "hints_used": hints_used + 1,
            "requires_review": True,
        }

    def _hint_count(self, topic_id: str) -> int:
        count = 0

        while self.knowledge.get_hint(topic_id, count) is not None:
            count += 1

        return count

