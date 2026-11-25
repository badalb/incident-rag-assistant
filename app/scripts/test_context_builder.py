
import json

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
        vector_search = VectorSearch(client, embedding_service)
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

        # print("\n========== GRAPH PATH DETAILS ==========")

        # for path in retrieval_result.get("graph_paths", []):
        #     nodes = path.get("path_nodes", [])
        #     relationships = path.get("path_relationships", [])

        #     node_names = [
        #         node.get("name", node.get("id"))
        #         for node in nodes
        #     ]

        #     path_description = " -> ".join(
        #         f"{node_names[i]} -[{relationships[i]}]"
        #         for i in range(min(len(relationships), len(node_names) - 1))
        #     )

        #     if node_names:
        #         path_description += f" -> {node_names[-1]}"

        #     print(f"Seed: {path.get('seed_chunk_id')}")
        #     print(f"Path: {path_description}")
        #     print("-" * 60)


        print("\n========== RELATED INCIDENT DETAILS ==========")

        for item in retrieval_result.get("related_incidents", []):
            print(
                f"{item.get('source_incident')} "
                f"-> {item.get('shared_service')} "
                f"-> {item.get('related_incident')} "
                f"({item.get('related_incident_title')})"
            )

        # print("\n========== HYBRID RETRIEVAL DEBUG ==========")

        # print("Primary incident:",retrieval_result.get("primary_incident_id"))

        # print("Primary chunk:",retrieval_result.get("primary_incident_chunk_id"))

        # for doc in retrieval_result.get("documents", []):
        #     print(
        #         doc.get("document_id"),
        #         doc.get("chunk_id"),
        #         doc.get("document_type"),
        #         doc.get("score")
        #     )

        context_builder = InvestigationContextBuilder(client)
        context = context_builder.build(retrieval_result)

        # print("\n========== INVESTIGATION CONTEXT ==========")
        # print(json.dumps(context, indent=2, default=str))

        # print("\n========== CONTEXT SUMMARY ==========")
        # print("Incidents:", len(context["incidents"]))
        # print("Deployments:", len(context["deployments"]))
        # print("Graph paths:", len(context["graph_paths"]))
        # print("Related incidents:", len(context["related_incidents"]))
        # print("Timeline events:", len(context["timeline"]))


        # print("\n========== PRIMARY INCIDENT ==========")
        # print(context.get("primary_incident_id"))

        # print("\n========== INCIDENT IDS ==========")
        # print([i["id"] for i in context["incidents"]])

        # print("\n========== DEPLOYMENT IDS ==========")
        # print([d["id"] for d in context["deployments"]])

        # print("\n========== TIMELINE ==========")
        # for event in context["timeline"]:
        #     print(
        #         str(event["timestamp"])[:19],
        #         event["event_type"],
        #         event["event_id"]
        #     )

    finally:
        client.close()


if __name__ == "__main__":
    main()
