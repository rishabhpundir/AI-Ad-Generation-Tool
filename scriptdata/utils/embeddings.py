import os
import sys
import django


# env setup
project_path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()


import os
import openai
import pinecone
from django.conf import settings
from sentence_transformers import SentenceTransformer


# Load environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = settings.PINECONE_API_KEY


# Connect to Pinecone
pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")  # Change to your Pinecone region
index = pinecone.Index("ads-index")

# Load local embedding model (if not using OpenAI)
local_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text, use_openai=False):
    """Generate embeddings using OpenAI or local model."""
    if use_openai:
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response["data"][0]["embedding"]
    else:
        return local_embedding_model.encode(text).tolist()
