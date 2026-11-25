import json
from pathlib import Path
from typing import Any


class JSONLoader:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_entities(
        self,
        relative_path: str,
        collection_key: str
    ) -> list[dict[str, Any]]:

        file_path = self.data_dir / relative_path

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {file_path}"
            )

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        entities = data.get(collection_key)

        if not isinstance(entities, list):
            raise ValueError(
                f"Expected a list under '{collection_key}' "
                f"in {file_path}"
            )

        return entities