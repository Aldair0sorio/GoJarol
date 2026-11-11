
import json
import re
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text: str) -> str:
    text = text.lower()

    text = "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )

    return re.sub(r"\s+", " ", text).strip()


class TopicRetriever:
    def __init__(self, catalog_path: str | Path):
        path = Path(catalog_path)
        topics = json.loads(path.read_text(encoding="utf-8"))

        if not topics:
            raise ValueError("El catalogo de temas esta vacio.")

        self.topics = {topic["id"]: topic for topic in topics}
        self.entries = []

        for topic in topics:
            expressions = sorted(
                set([topic["name"], *topic["aliases"]])
            )

            for expression in expressions:
                self.entries.append({
                    "topic_id": topic["id"],
                    "text": normalize_text(expression),
                })

        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            strip_accents="unicode",
            sublinear_tf=True,
        )

        self.matrix = self.vectorizer.fit_transform(
            [entry["text"] for entry in self.entries]
        )

    @staticmethod
    def empty_result(method: str = "none") -> dict:
        return {
            "subject": None,
            "topic": None,
            "topic_score": 0.0,
            "needs_clarification": True,
            "match_method": method,
        }

    def find_topic(self, message: str) -> dict:
        query = normalize_text(message)

        if not query:
            return self.empty_result()

        # Primero buscar nombres y sinonimos completos.
        exact_matches = set()

        for entry in self.entries:
            expression = entry["text"]

            pattern = (
                rf"(?<!\w){re.escape(expression)}(?!\w)"
            )

            if re.search(pattern, query):
                exact_matches.add(entry["topic_id"])

        if len(exact_matches) == 1:
            topic_id = next(iter(exact_matches))
            topic = self.topics[topic_id]

            return {
                "subject": topic["subject"],
                "topic": topic_id,
                "topic_score": 1.0,
                "needs_clarification": False,
                "match_method": "exact_alias",
            }

        if len(exact_matches) > 1:
            return self.empty_result("ambiguous")

        # Si no hay coincidencia exacta, usar TF-IDF.
        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector, self.matrix
        )[0]

        scores = {}

        for entry, similarity in zip(
            self.entries, similarities
        ):
            topic_id = entry["topic_id"]

            scores[topic_id] = max(
                scores.get(topic_id, 0.0),
                float(similarity),
            )

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_id, best_score = ranked[0]

        # Umbrales iniciales, sujetos a evaluacion.
        if best_score < 0.48:
            return self.empty_result()

        if len(ranked) > 1:
            second_score = ranked[1][1]

            if best_score - second_score < 0.08:
                return self.empty_result("ambiguous")

        topic = self.topics[best_id]

        return {
            "subject": topic["subject"],
            "topic": best_id,
            "topic_score": round(best_score, 4),
            "needs_clarification": False,
            "match_method": "tfidf",
        }
