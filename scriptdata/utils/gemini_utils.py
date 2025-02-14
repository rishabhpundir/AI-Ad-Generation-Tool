import os
import sys
import django

# Django setup
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyrostool.settings')
django.setup()

import grpc
from django.conf import settings
import google.generativeai as genai
from google.generativeai import types


# Gemini API config
GEMINI_API_KEY = settings.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)


def generate_ad_script(user_query, retrieved_ads):
    """
    Generates a new ad script using Gemini by providing retrieved similar ad scripts as context.
    
    Args:
        user_query (str): The user's ad script request (e.g., "Create a skincare ad for anti-aging").
        retrieved_ads (list): A list of retrieved ad scripts (from embeddings search).
    
    Returns:
        str: The generated ad script from Gemini.
    """
    # Step 1: Format the retrieved ads as context for Gemini
    context = "Below are past ad scripts related to your request:\n\n"
    
    for i, ad in enumerate(retrieved_ads, start=1):
        context += f"--- Ad {i} ---\n"
        context += f"Platform: {ad.get('platform', 'Unknown')}\n"
        context += f"Ad Type: {ad.get('ad_type', 'Unknown')}\n"
        context += f"Industry: {ad.get('industry', 'Unknown')}\n"
        context += f"Script:\n{ad.get('content', '')}\n\n"

    # Step 2: Define the prompt for Gemini
    prompt = f"""
    You are an expert in writing high-converting ad scripts. A user has requested a new ad script for the following query:

    "{user_query}"

    {context}

    Based on the above ads, generate a new ad script that follows a similar structure and tone. Ensure the script:
    - Has an engaging **hook** to grab attention.
    - Introduces the **problem** and **solution** clearly.
    - Includes a **call-to-action (CTA)** at the end.

    Return only the ad script, no explanations.
    """

    # Step 3: Send the request to Gemini
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
    )

    # Configuration for model (Tuning)
    generation_config = types.GenerationConfig(
            temperature=0.8,  # Adjust for creativity (0 = factual, 1 = highly creative)
            top_p=0.99,       # Controls randomness in sampling
            top_k=0,          # Used for token selection
            max_output_tokens=1000  # Controls response length
    )

    response = model.generate_content(
        contents=prompt, 
        generation_config=generation_config
    )
    grpc.Channel.close = lambda self: None
    return response.text if response.text else "Failed to generate ad script."


