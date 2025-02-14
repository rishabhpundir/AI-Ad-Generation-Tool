import os
import sys
import django

# Django setup
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()

import time
import openai
from django.conf import settings
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
pinecone_api_key = settings.PINECONE_API_KEY

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Index configuration
index_name = "ads-index"

# Check if index exists, otherwise create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Adjust based on embedding model (all-MiniLM-L6-v2 = 384)
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Modify cloud/region if needed
    )

    # Wait for index to be ready
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(2)

# Connect to the index
index = pc.Index(index_name)

# Load local embedding model (if not using OpenAI)
local_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text, use_openai=False):
    """Generate embeddings using OpenAI or local model."""
    if use_openai:
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return response["data"][0]["embedding"]
    else:
        return local_embedding_model.encode(text).tolist()
