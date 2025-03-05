import re
from main.models import *
from django.shortcuts import render
from scriptdata.models import AdScript
from scriptdata.utils.retriever import retrieve_similar_ads
from scriptdata.utils.gemini_utils import generate_ad_script


def rank_ads_by_performance(retrieved_ads):
    """
    Ranks ads based on performance using Hyros attribution data.
    Args: retrieved_ads (list): List of retrieved ad metadata from Pinecone.
    Returns: list: Top 5 ranked ads.
    """ 
    ranked_ads = []
    for ad_data in retrieved_ads:
        # adscript = AdScript.objects.filter(name=ad_data["file_id"]).first()               # Work on these two
        # ad = Ad.objects.filter()
        if ad and ad.adaccattr:  # Ensure ad has attribution data
            attr = ad.adaccattr
            # Define scoring based on key performance indicators (weights can be adjusted)
            score = (
                (-float(attr.cost_per_unique_sales) if attr.cost_per_unique_sales else 0) * 0.35 +  # Lower is better
                (float(attr.roas) if attr.roas else 0) * 0.35 +  # Higher is better
                (float(attr.profit) if attr.profit else 0) * 0.2 +  # Higher is better
                (-float(attr.cost_per_lead) if attr.cost_per_lead else 0) * 0.1  # Lower is better
            )
            ranked_ads.append((score, ad_data))
    ranked_ads.sort(reverse=True, key=lambda x: x[0]) # Sort by score (highest first)
    return [ad_data for _, ad_data in ranked_ads[:5]] # Select the top 5


def home(request):
    total_docs = AdScript.objects.count()
    result = ""
    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            retrieved_ads = retrieve_similar_ads(query=query)
            if not retrieved_ads:
                result += "No similar ads found."
            else:
                top_5_ads = rank_ads_by_performance(retrieved_ads)  # Rank and select top 5
                print(top_5_ads)
                generated_script = generate_ad_script(query, top_5_ads)
            result += f"\nQuery :- {query}\nResult :- \n\n{generated_script}"
    result = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', result)
    return render(request, 'home.html', {'result': result, "total_docs": total_docs})

