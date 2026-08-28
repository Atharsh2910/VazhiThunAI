import os
from pinecone import Pinecone
from typing import List, Dict, Any, Optional

class PineconeClient:
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY", "mock_pinecone_key")
        self.environment = environment or os.getenv("PINECONE_ENV", "us-east-1")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "vazhithunai-index")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
        
    def get_index(self):
        return self.pc.Index(self.index_name)

    def upsert_vectors(self, vectors: List[Dict[str, Any]], namespace: str = ""):
        """Upsert vectors into Pinecone."""
        index = self.get_index()
        return index.upsert(vectors=vectors, namespace=namespace)

    def query_vectors(self, vector: List[float], top_k: int = 5, filter_dict: Optional[Dict] = None, namespace: str = "") -> Dict:
        """Query vectors from Pinecone."""
        index = self.get_index()
        return index.query(
            vector=vector,
            top_k=top_k,
            filter=filter_dict,
            include_metadata=True,
            namespace=namespace
        )

pinecone_client = PineconeClient()
