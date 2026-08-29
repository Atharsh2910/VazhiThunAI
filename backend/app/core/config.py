from pydantic_settings import BaseSettings
from supabase import create_client, Client

class Settings(BaseSettings):
    GROQ_API_KEY: str = "mock-groq-key"
    GROQ_MODEL_NAME: str = "openai/gpt-oss-20b"
    PINECONE_API_KEY: str = "mock-pinecone-key"
    SUPABASE_URL: str = "https://mock-project.supabase.co"
    SUPABASE_ANON_KEY: str = "mock-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "mock-service-key"
    PINECONE_ENVIRONMENT: str = "mock-env"
    PINECONE_INDEX_NAME: str = "vazhithunai"
    DATABASE_URL: str = "postgresql://postgres:mock-password@db.mock-project.supabase.co:5432/postgres"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Supabase Client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
