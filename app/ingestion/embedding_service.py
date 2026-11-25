
from openai import OpenAI
from app.config.settings import settings


class EmbeddingService:

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is missing. "
                "Please configure it in your .env file."
            )

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = settings.EMBEDDING_MODEL

    def generate_embeddings(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        # Preserve the original input ordering.
        ordered_data = sorted(
            response.data,
            key=lambda item: item.index
        )

        return [
            item.embedding
            for item in ordered_data
        ]
