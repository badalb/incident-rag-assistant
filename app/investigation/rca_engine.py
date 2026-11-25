
from openai import OpenAI

from app.config.settings import settings
from app.investigation.prompt_builder import RCAPromptBuilder
from app.models.rca_report import RCAReport


class RCAEngine:

    def __init__(self, model: str = "gpt-4o-mini"):

        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is missing. Configure it in your .env file."
            )

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = model
        self.prompt_builder = RCAPromptBuilder()

    def generate(self, investigation_context: dict) -> RCAReport:

        prompt = self.prompt_builder.build_prompt(
            investigation_context
        )

        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an experienced SRE performing "
                        "evidence-based root cause analysis. "
                        "Follow the supplied response schema exactly. "
                        "Do not invent evidence."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format=RCAReport,
            temperature=0.2
        )

        message = response.choices[0].message

        if message.refusal:
            raise ValueError(
                f"LLM refused to generate the RCA: {message.refusal}"
            )

        if message.parsed is None:
            raise ValueError(
                "The LLM did not return a parsed RCAReport. "
                f"Finish reason: {response.choices[0].finish_reason}"
            )

        return message.parsed
