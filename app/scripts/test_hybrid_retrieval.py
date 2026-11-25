
from app.database.neo4j_client import Neo4jClient

from app.ingestion.embedding_service import EmbeddingService

from app.retrieval.vector_search import VectorSearch
from app.retrieval.graph_retriever import GraphRetriever
from app.retrieval.hybrid_retriever import HybridRetriever



def main():

    client = Neo4jClient()

    try:
        client.verify_connection()

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

        query = "Why are payment requests timing out?"

        result = hybrid_retriever.retrieve(
            query=query,
            top_k=5,
            max_hops=3
        )

        print("\n========== RELATED HISTORICAL INCIDENTS ==========")

        for incident in result["related_incidents"]:
            print(
                f"{incident['source_incident']} -> "
                f"{incident['shared_service']} -> "
                f"{incident['related_incident']}"
            )

        print("\n========== VECTOR RESULTS ==========")

        for document in result["documents"]:

            print(f"\nChunk: {document['chunk_id']}")
            print(f"Source: {document['source_file']}")
            print(f"Score: {document['score']:.4f}")
            print(f"Content: {document['content'][:300]}")

        print("\n========== GRAPH PATHS ==========")

        for index, path in enumerate(
            result["graph_paths"],
            start=1
        ):

            print(f"\nPath {index}")

            for position, node in enumerate(
                path["path_nodes"]
            ):

                print(
                    f"{node['labels']} : "
                    f"{node['name']}"
                )

                if position < len(path["path_relationships"]):
                    print(
                        f"  -- {path['path_relationships'][position]} -->"
                    )

        print(
            f"\nTotal graph paths: "
            f"{len(result['graph_paths'])}"
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()
