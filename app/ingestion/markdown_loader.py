
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class MarkdownDocument:
    id: str
    title: str
    document_type: str
    content: str
    source_file: str


class MarkdownLoader:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

        self.document_sources = {
            "incidents/reports": "incident_report",
            "runbooks": "runbook",
            "architecture": "architecture",
        }

    def _create_document_id(self, path: Path, document_type: str) -> str:
        filename = path.stem.upper()

        if document_type == "incident_report":
            return filename

        slug = re.sub(r"[^A-Z0-9]+", "-", filename).strip("-")

        if document_type == "runbook":
            return f"RB-{slug}"

        return f"ARCH-{slug}"

    def _extract_title(self, content: str, path: Path) -> str:
        for line in content.splitlines():
            line = line.strip()

            if line.startswith("# "):
                return line[2:].strip()

        return path.stem.replace("-", " ").replace("_", " ").title()

    def load_documents(self) -> list[MarkdownDocument]:
        documents = []

        for folder, document_type in self.document_sources.items():
            folder_path = self.data_dir / folder

            if not folder_path.exists():
                print(f"Skipping missing folder: {folder_path}")
                continue

            for path in sorted(folder_path.rglob("*.md")):
                content = path.read_text(encoding="utf-8").strip()

                if not content:
                    print(f"Skipping empty document: {path}")
                    continue

                relative_path = path.relative_to(self.data_dir)

                document = MarkdownDocument(
                    id=self._create_document_id(path, document_type),
                    title=self._extract_title(content, path),
                    document_type=document_type,
                    content=content,
                    source_file=str(relative_path),
                )

                documents.append(document)

        return documents
