import os
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from app.retrieval.pinecone_client import pinecone_client
from sentence_transformers import SentenceTransformer

try:
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
except Exception:
    embedding_model = None

class ChatService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY", "mock_groq_key"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192")
        )

    def generate_embedding(self, text: str) -> List[float]:
        if embedding_model:
            # e5 models require "query: " prefix for asymmetric search
            return embedding_model.encode(f"query: {text}").tolist()
        return [0.1] * 1024

    def generate_chat_response(self, user_message: str, history: List[Dict[str, str]] = None) -> str:
        history_str = ""
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_str += f"{role.capitalize()}: {content}\n"
        
        # Retrieval from Pinecone using user message
        vector = self.generate_embedding(user_message)
        
        # Using Pinecone client to retrieve relevant resources/context
        # Namespace might be 'resources' or something similar
        retrieved_docs = pinecone_client.query_vectors(vector=vector, top_k=3, namespace="resources")
        
        context_str = ""
        if "matches" in retrieved_docs:
            for match in retrieved_docs["matches"]:
                metadata = match.get("metadata", {})
                content = metadata.get("content", match.get("id", ""))
                context_str += f"- {content}\n"
                
        prompt_template = PromptTemplate(
            input_variables=["user_message", "context", "history"],
            template=(
                "You are an AI learning assistant for VazhiThunAI.\n"
                "Use the following retrieved context to help answer the user's query.\n"
                "Context:\n{context}\n\n"
                "History:\n{history}\n\n"
                "User Query: {user_message}\n"
                "Answer:"
            )
        )
        
        chain = prompt_template | self.llm
        
        response = chain.invoke({
            "user_message": user_message,
            "context": context_str,
            "history": history_str
        })
        
        return response.content

chat_service = ChatService()
