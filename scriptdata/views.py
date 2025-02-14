from django.http import JsonResponse
from scriptdata.utils.retriever import retrieve_similar_ads
from scriptdata.utils.gemini_utils import generate_ad_script

def generate_ad(request):
    """
    API endpoint to generate an ad script using Gemini.
    """
    query = request.GET.get("query", "")

    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    # Step 1: Retrieve similar ads from Pinecone embeddings
    retrieved_ads = retrieve_similar_ads(query)

    if not retrieved_ads:
        return JsonResponse({"error": "No similar ads found."}, status=404)

    # Step 2: Generate ad script with Gemini
    generated_script = generate_ad_script(query, retrieved_ads)

    return JsonResponse({"generated_ad_script": generated_script})




