from pinecone import Pinecone
from app.core.config import settings

def get_pinecone_index(index_name: str = "vazhithunai-idx"):
    if not settings.PINECONE_API_KEY:
        return None
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return pc.Index(index_name)
