
from app.database.neo4j_client import Neo4jClient
from app.ingestion.embedding_service import EmbeddingService
from app.retrieval.vector_search import VectorSearch
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.investigation.context_builder import InvestigationContextBuilder


def main():
    client = Neo4jClient()

    try:
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

        retrieval_result = hybrid_retriever.retrieve(
            query="Why are payment requests timing out?",
            top_k=5,
            max_hops=3
        )

        context_builder = InvestigationContextBuilder(client)

        context = context_builder.build(retrieval_result)

        print("\n========== PRIMARY INCIDENT ==========")
        print(context["primary_incident_id"])

        print("\n========== CLASSIFIED GRAPH PATHS ==========")

        for path in context["classified_paths"]:
            names = [
                node.get("name", node.get("id"))
                for node in path["path_nodes"]
            ]

            print(
                path["evidence_type"],
                " -> ".join(names)
            )

        print("\n========== RANKED HISTORICAL EVIDENCE ==========")

        for item in context["ranked_evidence"]:
            print(
                f"{item['incident_id']} | "
                f"{item['title']} | "
                f"Score: {item['total_score']}"
            )

            for reason in item["ranking_reasons"]:
                print(f"  - {reason}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
