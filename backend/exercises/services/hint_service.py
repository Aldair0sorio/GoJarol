
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

        # General explanations contain solved examples and are not safe as hints.
        # Keep teaching strategies, but never reuse worked solutions in an active exercise.
        exercise = (self.selector.get_public_exercise(topic_id, exercise_id)
                    if exercise_id is not None else self.knowledge.get_public_exercise(topic_id))
        approaches = {
            'fraction': ('Representa las fracciones con partes del mismo tamaño antes de operar.',
                         'Revisa qué representan numerador y denominador y cómo obtener fracciones equivalentes.'),
            'numeric': ('Identifica qué operaciones acompañan a la incógnita o cantidad buscada y deshaz una a la vez.',
                        'Revisa las operaciones inversas y comprueba que cada paso conserve las condiciones del problema.'),
            'percentage': ('Distingue la parte y el total que sirve como base de comparación.',
                           'Expresa la relación entre parte y total como una proporción antes de convertirla a porcentaje.'),
            'multiple_choice': ('Compara cada opción con los datos del enunciado sin elegir solo por palabras parecidas.',
                                'Identifica la regla o evidencia que necesitas para descartar opciones que contradicen el enunciado.'),
        }
        alternative, review = approaches[exercise['type']]
        strategies = [
            ('alternative_explanation', alternative),
            ('concept_review', review),
            ('guided_reflection', 'Dime qué has intentado y en qué paso necesitas ayuda.'),
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
