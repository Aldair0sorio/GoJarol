
import json
from pathlib import Path


class KnowledgeService:
    def __init__(self, content_dir: str | Path):
        directory = Path(content_dir)

        if not directory.is_dir():
            raise FileNotFoundError(
                f"Directorio no encontrado: {directory}"
            )

        self._topics = {}

        for file in sorted(directory.glob("*.json")):
            data = json.loads(file.read_text(encoding="utf-8"))

            required = {
                "id",
                "subject",
                "name",
                "competency",
                "diagnostic",
                "explanations",
                "exercise",
            }

            if not isinstance(data, dict):
                raise ValueError(f"Formato invalido: {file.name}")

            missing = required - data.keys()

            if missing:
                raise ValueError(
                    f"{file.name}: faltan campos {missing}"
                )

            if "explanation_menu" in data:
                self._validate_explanation_menu(data["explanation_menu"], file.name)

            topic_id = data["id"]

            if topic_id in self._topics:
                raise ValueError(f"Tema duplicado: {topic_id}")

            self._topics[topic_id] = data

        if not self._topics:
            raise ValueError("No se encontraron temas educativos.")

    @staticmethod
    def _validate_explanation_menu(menu, file_name: str) -> None:
        """El menú de diagnóstico debe tener pregunta, invitación a practicar y opciones con letra única."""
        if not isinstance(menu, dict):
            raise ValueError(f"{file_name}: explanation_menu debe ser un objeto")
        for field in ("question", "practice_prompt"):
            if not isinstance(menu.get(field), str) or not menu[field].strip():
                raise ValueError(f"{file_name}: explanation_menu.{field} vacío")
        options = menu.get("options")
        if not isinstance(options, list) or len(options) < 2:
            raise ValueError(f"{file_name}: explanation_menu necesita al menos 2 opciones")
        labels = set()
        for option in options:
            if not isinstance(option, dict) or any(
                not isinstance(option.get(key), str) or not option[key].strip()
                for key in ("label", "text", "explanation")
            ):
                raise ValueError(f"{file_name}: opción de explanation_menu incompleta")
            label = option["label"].strip().upper()
            if len(label) != 1 or not label.isalpha() or label in labels:
                raise ValueError(f"{file_name}: letra de opción inválida o repetida: {option['label']}")
            labels.add(label)

    def _get_topic(self, topic_id: str) -> dict:
        if topic_id not in self._topics:
            raise KeyError(f"Tema no disponible: {topic_id}")

        return self._topics[topic_id]

    def list_topics(self) -> list[dict]:
        return [
            {
                "id": topic["id"],
                "subject": topic["subject"],
                "name": topic["name"],
            }
            for topic in self._topics.values()
        ]

    def has_explanation(self, topic_id: str) -> bool:
        topic = self._topics.get(topic_id)
        return bool(topic and topic["explanations"].get("basic"))

    def get_explanation(
        self,
        topic_id: str,
        level: str = "basic",
    ) -> str:
        explanations = self._get_topic(topic_id)["explanations"]

        if level not in explanations:
            raise ValueError("Nivel de explicacion no disponible")

        return explanations[level]

    def has_explanation_menu(self, topic_id: str) -> bool:
        topic = self._topics.get(topic_id)
        return bool(topic and topic.get("explanation_menu"))

    def get_explanation_menu(self, topic_id: str) -> dict:
        """Pregunta y opciones (letra y texto) sin las explicaciones."""
        menu = self._get_topic(topic_id)["explanation_menu"]
        return {
            "question": menu["question"],
            "options": [
                {"label": option["label"].strip().upper(), "text": option["text"]}
                for option in menu["options"]
            ],
        }

    def get_menu_explanation(self, topic_id: str, label: str) -> str:
        """Explicación corta de una opción, terminada con la invitación a practicar."""
        menu = self._get_topic(topic_id)["explanation_menu"]
        wanted = label.strip().upper()
        for option in menu["options"]:
            if option["label"].strip().upper() == wanted:
                return (
                    f"{option['explanation']}\n\n"
                    f"Si quieres practicar, escríbeme: «{menu['practice_prompt']}»."
                )
        raise KeyError(f"Opción no disponible: {label}")

    def get_public_diagnostic(self, topic_id: str) -> dict:
        diagnostic = self._get_topic(topic_id)["diagnostic"]

        return {
            "id": diagnostic["id"],
            "question": diagnostic["question"],
            "options": diagnostic["options"].copy(),
        }

    def get_public_exercise(self, topic_id: str) -> dict:
        exercise = self._get_topic(topic_id)["exercise"]

        return {
            "id": exercise["id"],
            "question": exercise["question"],
            "difficulty": exercise["difficulty"],
            "type": exercise["type"],
        }

    def get_hint(self, topic_id: str, index: int) -> str | None:
        if index < 0:
            raise ValueError("Indice invalido")

        hints = self._get_topic(topic_id)["exercise"]["hints"]

        if index >= len(hints):
            return None

        return hints[index]

    def get_expected_answer(self, topic_id: str) -> str:
        return self._get_topic(topic_id)["exercise"][
            "expected_answer"
        ]
