import os
import requests
from typing import List

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/intfloat/multilingual-e5-large"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def get_embedding(text: str) -> List[float]:
    """
    Generates semantic vector embeddings using HuggingFace Inference API.
    This offloads RAM usage, allowing the app to run on Render free tier.
    """
    try:
        payload = {
            "inputs": f"query: {text}",
            "options": {"wait_for_model": True}
        }
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # The API returns a 1D list of floats for a single string input
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    return result[0] # Just in case it wraps it in a 2D array
                return result
                
        print(f"HF API Error: {response.status_code} - {response.text}")
        return [0.1] * 1024
    except Exception as e:
        print(f"Embedding error: {e}")
        return [0.1] * 1024
