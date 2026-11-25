
from app.retrieval.vector_search import VectorSearch
from app.retrieval.graph_retriever import GraphRetriever


class HybridRetriever:
    """
    Combines vector search and graph traversal to retrieve
    relevant documents, graph paths, and historical incidents.

    Retrieval flow:
        1. Perform vector similarity search.
        2. Identify the primary incident from vector results.
        3. Use the primary incident as the graph traversal anchor.
        4. Retrieve related graph paths and historical incidents.
        5. Return a combined investigation result.
    """

    def __init__(
        self,
        vector_search: VectorSearch,
        graph_retriever: GraphRetriever
    ):
        self.vector_search = vector_search
        self.graph_retriever = graph_retriever

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        max_hops: int = 3
    ) -> dict:
        """
        Execute hybrid retrieval for an investigation query.

        Args:
            query: Natural language investigation question.
            top_k: Number of document chunks retrieved by vector search.
            max_hops: Maximum graph traversal depth (1 to 4).

        Returns:
            Dictionary containing vector results, primary incident,
            graph paths, and related historical incidents.
        """

        # --------------------------------------------------
        # Step 1: Vector similarity search
        # --------------------------------------------------

        vector_results = self.vector_search.search(
            query_text=query,
            top_k=top_k
        )

        # Handle empty vector search results
        if not vector_results:
            return {
                "query": query,
                "primary_incident_id": None,
                "primary_incident_chunk_id": None,
                "documents": [],
                "graph_paths": [],
                "related_incidents": []
            }

        # --------------------------------------------------
        # Step 2: Identify the primary incident
        # --------------------------------------------------

        # Select the highest-ranked incident report.
        # Incident report IDs follow the INC-xxx convention.

        primary_incident = next(
            (
                document
                for document in vector_results
                if document.get("document_id", "").startswith("INC-")
            ),
            None
        )

        primary_incident_id = (
            primary_incident["document_id"]
            if primary_incident else None
        )

        primary_chunk_id = (
            primary_incident["chunk_id"]
            if primary_incident else None
        )

        # --------------------------------------------------
        # Step 3: Graph retrieval
        # --------------------------------------------------

        graph_paths = []
        related_incidents = []

        # Only traverse the graph when a primary incident
        # has been identified.

        if primary_chunk_id:

            graph_paths = (
                self.graph_retriever.retrieve_related_entities(
                    chunk_ids=[primary_chunk_id],
                    max_hops=max_hops
                )
            )

            related_incidents = (
                self.graph_retriever.retrieve_related_incidents(
                    chunk_ids=[primary_chunk_id],
                    max_hops=max_hops
                )
            )

        # --------------------------------------------------
        # Step 4: Return combined retrieval results
        # --------------------------------------------------

        return {
            "query": query,
            "primary_incident_id": primary_incident_id,
            "primary_incident_chunk_id": primary_chunk_id,
            "documents": vector_results,
            "graph_paths": graph_paths,
            "related_incidents": related_incidents
        }
