
from app.database.neo4j_client import Neo4jClient
from app.ingestion.embedding_service import EmbeddingService
from app.retrieval.vector_search import VectorSearch
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.hybrid_retriever import HybridRetriever

from app.investigation.context_builder import InvestigationContextBuilder
from app.investigation.rca_engine import RCAEngine
from app.investigation.rca_validator import RCAValidator
from app.investigation.hypothesis_analyzer import HypothesisAnalyzer


class InvestigationService:

    def __init__(self):
        self.client = Neo4jClient()

        try:
            self.client.verify_connection()

            self.embedding_service = EmbeddingService()

            self.vector_search = VectorSearch(
                self.client,
                self.embedding_service
            )

            self.graph_retriever = GraphRetriever(self.client)

            self.hybrid_retriever = HybridRetriever(
                self.vector_search,
                self.graph_retriever
            )

            self.context_builder = InvestigationContextBuilder(
                self.client
            )

            self.rca_engine = RCAEngine()
            self.rca_validator = RCAValidator()
            self.hypothesis_analyzer = HypothesisAnalyzer()

        except Exception:
            self.client.close()
            raise

    def investigate(
        self,
        query: str,
        top_k: int = 5,
        max_hops: int = 3
    ) -> dict:

        # 1. Hybrid retrieval
        retrieval_result = self.hybrid_retriever.retrieve(
            query=query,
            top_k=top_k,
            max_hops=max_hops
        )

        # 2. Build investigation context
        investigation_context = self.context_builder.build(
            retrieval_result
        )

        # 3. Generate RCA hypotheses
        rca_report = self.rca_engine.generate(
            investigation_context
        )

        # 4. Consolidate overlapping hypotheses
        rca_report = self.hypothesis_analyzer.analyze(
            rca_report
        )

        # 5. Validate RCA report
        validated_report = self.rca_validator.validate(
            report=rca_report,
            context=investigation_context
        )

        return {
            "query": query,
            "primary_incident_id": investigation_context.get(
                "primary_incident_id"
            ),
            "context_summary": investigation_context.get(
                "summary", {}
            ),
            "report": validated_report.model_dump(mode="json"),
            "timeline": investigation_context.get("timeline", []),
            "ranked_evidence": investigation_context.get(
                "ranked_evidence", []
            ),
            "related_incidents": investigation_context.get(
                "related_incidents", []
            )
        }

    def close(self):
        self.client.close()
