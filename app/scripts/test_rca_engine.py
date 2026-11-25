
from app.database.neo4j_client import Neo4jClient
from app.ingestion.embedding_service import EmbeddingService
from app.retrieval.vector_search import VectorSearch
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.investigation.context_builder import InvestigationContextBuilder
from app.investigation.rca_engine import RCAEngine
from app.investigation.rca_validator import RCAValidator


def main():
    client = Neo4jClient()

    try:
        client.verify_connection()

        # 1. Initialize retrieval components
        embedding_service = EmbeddingService()

        vector_search = VectorSearch(
            client,
            embedding_service
        )

        graph_retriever = GraphRetriever(client)

        hybrid_retriever = HybridRetriever(
            vector_search,
            graph_retriever
        )

        # 2. Retrieve relevant documents and graph evidence
        query = "Why are payment requests timing out?"

        print("\nRunning hybrid retrieval...")

        retrieval_result = hybrid_retriever.retrieve(
            query=query,
            top_k=5,
            max_hops=3
        )

        print(
            "Primary incident:",
            retrieval_result.get("primary_incident_id")
        )

        # 3. Build investigation context
        print("\nBuilding investigation context...")

        context_builder = InvestigationContextBuilder(client)
        investigation_context = context_builder.build(retrieval_result)

        print("\nContext summary:")
        print(investigation_context["summary"])

        # 4. Generate the RCA report using the LLM
        print("\nGenerating RCA report...")

        # Generate the initial LLM report
        rca_engine = RCAEngine()
        report = rca_engine.generate(investigation_context)

        print("\n========== RAW LLM RCA REPORT ==========")
        print(report.model_dump_json(indent=2))

        # Validate and enrich the report
        print("\nValidating RCA report...")

        rca_validator = RCAValidator()

        validated_report = rca_validator.validate(
            report=report,
            context=investigation_context
        )

        print("\n========== VALIDATED RCA REPORT ==========")
        print(validated_report.model_dump_json(indent=2))

    finally:
        client.close()


if __name__ == "__main__":
    main()
