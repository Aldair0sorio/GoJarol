from pathlib import Path
import re
import joblib
from gojarol_ml.nlp.topic_retriever import TopicRetriever, normalize_text


class JarolAnalyzer:
    def __init__(self, model_path: str | Path, catalog_path: str | Path):
        self.intent_model = joblib.load(model_path)
        self.topic_retriever = TopicRetriever(catalog_path)

    def analyze_message(self, message: str, context: dict | None = None) -> dict:
        context = context or {}
        message = message.strip()

        if not message:
            return {
                "intent": None,
                "intent_confidence": 0.0,
                "subject": None,
                "topic": None,
                "topic_score": 0.0,
                "match_method": "none",
                "needs_clarification": True,
            }

        probabilities = self.intent_model.predict_proba([message])[0]
        index = int(probabilities.argmax())

        intent = self.intent_model.classes_[index]
        confidence = float(probabilities[index])

        topic_result = self.topic_retriever.find_topic(message)

        subject = topic_result["subject"]
        topic = topic_result["topic"]
        topic_score = topic_result["topic_score"]
        match_method = topic_result["match_method"]

        # Resolver cambios explícitos de un tema a otro.
        if intent == "cambiar_tema" and match_method == "ambiguous":
            normalized = normalize_text(message)

            destination = re.search(
                r"\b(?:de|desde)\b.+?\b(?:a|hacia)\s+(.+)$",
                normalized,
            )

            if destination:
                new_topic = self.topic_retriever.find_topic(
                    destination.group(1)
                )

                if not new_topic["needs_clarification"]:
                    subject = new_topic["subject"]
                    topic = new_topic["topic"]
                    topic_score = new_topic["topic_score"]
                    match_method = "explicit_topic_change"


        # Recuperar el tema anterior cuando el mensaje depende del contexto.
        if topic is None and match_method == "none":
            previous_topic = context.get("current_topic")

            if previous_topic in self.topic_retriever.topics:
                stored_topic = self.topic_retriever.topics[previous_topic]

                topic = previous_topic
                subject = stored_topic["subject"]
                match_method = "context"

        # Algunas intenciones no necesitan un tema académico.
        global_intents = {
            "saludar",
            "despedirse",
            "consultar_progreso",
        }

        needs_clarification = (
                match_method == "ambiguous"
                or (topic is None and intent not in global_intents)
        )

        return {
            "intent": str(intent),
            "intent_confidence": round(confidence, 4),
            "subject": subject,
            "topic": topic,
            "topic_score": topic_score,
            "match_method": match_method,
            "needs_clarification": needs_clarification,
        }
