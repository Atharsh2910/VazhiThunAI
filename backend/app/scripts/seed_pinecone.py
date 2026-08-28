import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

def process_resources(df):
    texts = []
    metadata = []
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} ({row.get('resource_type', '')}, {row.get('format', '')}). Provider: {row.get('provider', '')}. Skill: {row.get('primary_skill_name', '')}. Domain: {row.get('domain', '')}."
        texts.append(text)
        meta = {
            "type": "resource",
            "id": str(row.get('resource_id', '')),
            "title": str(row.get('title', '')),
            "skill_name": str(row.get('primary_skill_name', '')),
            "domain": str(row.get('domain', ''))
        }
        metadata.append(meta)
    return texts, metadata

def process_skills(df):
    texts = []
    metadata = []
    for _, row in df.iterrows():
        text = f"{row.get('skill_name', '')}. Domain: {row.get('domain', '')}. Difficulty: {row.get('difficulty_tier', '')}."
        texts.append(text)
        meta = {
            "type": "skill",
            "id": str(row.get('skill_id', '')),
            "title": str(row.get('skill_name', '')),
            "domain": str(row.get('domain', ''))
        }
        metadata.append(meta)
    return texts, metadata

def process_projects(df):
    texts = []
    metadata = []
    for _, row in df.iterrows():
        text = f"{row.get('title', '')} for {row.get('target_role', '')}. Skills: {row.get('primary_skills', '')}. Difficulty: {row.get('difficulty_tier', '')}."
        texts.append(text)
        meta = {
            "type": "project",
            "id": str(row.get('project_id', '')),
            "title": str(row.get('title', '')),
            "skills": str(row.get('primary_skills', ''))
        }
        metadata.append(meta)
    return texts, metadata

def process_assessments(df):
    texts = []
    metadata = []
    for _, row in df.iterrows():
        text = f"{row.get('title', '')}. Type: {row.get('assessment_type', '')}. Skill: {row.get('skill_name', '')}."
        texts.append(text)
        meta = {
            "type": "assessment",
            "id": str(row.get('assessment_id', '')),
            "title": str(row.get('title', '')),
            "skill_name": str(row.get('skill_name', ''))
        }
        metadata.append(meta)
    return texts, metadata

def main():
    # Load env vars
    load_dotenv(dotenv_path='../.env') # Assuming script is run from backend/ or backend/app/scripts/
    # wait, if we run from backend, dotenv_path should just be '.env'
    # we'll find .env dynamically or just let load_dotenv find it
    load_dotenv()
    
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pinecone_api_key or not index_name:
        print("Missing Pinecone credentials in .env")
        return

    # Initialize Pinecone
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)
    
    # Initialize sentence transformer
    print("Loading model: intfloat/multilingual-e5-large...")
    # Add 'query: ' or 'passage: ' prefix for e5 models, typically passage for indexing
    model = SentenceTransformer('intfloat/multilingual-e5-large')
    
    data_dir = os.path.join(os.path.dirname(__file__), '../../data')
    if not os.path.exists(data_dir):
        # fallback
        data_dir = 'data'
        
    print(f"Reading data from {data_dir}...")
    
    # Process files
    files = {
        'resources.csv': process_resources,
        'skills.csv': process_skills,
        'projects.csv': process_projects,
        'assessments.csv': process_assessments
    }
    
    for filename, process_fn in files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        print(f"Processing {filename}...")
        df = pd.read_csv(filepath).fillna('')
        texts, metadata = process_fn(df)
        
        # e5 models usually recommend "passage: " prefix for documents
        prefixed_texts = [f"passage: {t}" for t in texts]
        
        batch_size = 100
        for i in range(0, len(prefixed_texts), batch_size):
            batch_texts = prefixed_texts[i:i+batch_size]
            batch_meta = metadata[i:i+batch_size]
            
            # encode
            embeddings = model.encode(batch_texts, normalize_embeddings=True).tolist()
            
            # create upsert batch
            upserts = []
            for j, (emb, meta) in enumerate(zip(embeddings, batch_meta)):
                # unique id combining type and original id
                doc_id = f"{meta['type']}_{meta['id']}"
                upserts.append((doc_id, emb, meta))
                
            index.upsert(vectors=upserts)
            print(f"Upserted {len(upserts)} items from {filename} ({i} to {i+len(upserts)})")

if __name__ == '__main__':
    main()
