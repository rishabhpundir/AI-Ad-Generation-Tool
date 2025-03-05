import re
from main.models import *
from django.shortcuts import render
from scriptdata.models import AdScript
from scriptdata.utils.retriever import retrieve_similar_ads
from scriptdata.utils.gemini_utils import generate_ad_script


def remove_copy_of(text: str) -> str:
    """
    Repeatedly remove 'Copy of ' substrings from the given text.
    """
    while "Copy of " in text:
        text = text.replace("Copy of ", "")
    return text.strip()

def extract_ids_from_adscript(adscript_str: str, max_ids: int = 3) -> list:
    """
    1. Remove 'Copy of ' substrings.
    2. Split on ' - '.
    3. Take up to `max_ids` segments that look like IDs (or just take the first `max_ids` raw segments).
    4. Return them as a list of separate IDs.
    """
    # 1) Remove "Copy of "
    cleaned_str = remove_copy_of(adscript_str)

    # 2) Split on " - "
    parts = cleaned_str.split(" - ")

    # 3) (Option A) Keep the first `max_ids` segments as-is
    #    If you specifically need them to match an alphanumeric pattern, you can filter.
    #    For example, to require something like "0189T" or "A0182" (letters + digits),
    #    you could do a pattern match. For now, we'll just slice and strip them:
    result = []
    for segment in parts[:max_ids]:
        segment = segment.strip()
        if segment:
            result.append(segment)

    return result

def rank_ads_by_performance(retrieved_ads):
    """
    Ranks ads based on performance using Hyros attribution data.
    """
    file_ids = []
    ranked_ads = []
    
    for ad_data in retrieved_ads:
        adscript = AdScript.objects.filter(filename=ad_data["filename"]).first()
        if not adscript:
            continue

        adscript_str = str(adscript)
        print(f"Raw AdScript: {adscript_str}")

        # Extract up to 3 IDs after removing "Copy of "
        extracted_ids = extract_ids_from_adscript(adscript_str, max_ids=3)
        print(f"Extracted IDs: {extracted_ids}")

        # Extend file_ids by the newly extracted IDs
        file_ids.extend(extracted_ids)

        # Now query for ads whose name is in file_ids
        ads = Ad.objects.filter(name__in=file_ids)
        for ad in ads:
            if hasattr(ad, 'adaccattr') and ad.adaccattr:
                attr = ad.adaccattr
                # Define some scoring logic
                score = (
                    (-float(attr.cost_per_unique_sales) if attr.cost_per_unique_sales else 0) * 0.35 +
                    (float(attr.roas) if attr.roas else 0) * 0.35 +
                    (float(attr.profit) if attr.profit else 0) * 0.2 +
                    (-float(attr.cost_per_lead) if attr.cost_per_lead else 0) * 0.1
                )
                ranked_ads.append((score, ad_data))

    # Sort by descending score (highest first) and pick top 5
    ranked_ads.sort(reverse=True, key=lambda x: x[0])
    print(f"filename>>>>>>>>>>>>>>>>>>>> {file_ids}")
    return [ad_data for _, ad_data in ranked_ads[:5]]


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

