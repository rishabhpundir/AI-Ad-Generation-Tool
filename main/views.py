import re
from django.shortcuts import render
from scriptdata.models import AdScript
from main.models import *
from scriptdata.utils.retriever import retrieve_similar_ads
from scriptdata.utils.gemini_utils import generate_ad_script



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
                generated_script = generate_ad_script(query, retrieved_ads)
            result += f"\nQuery :- {query}\nResult :- \n\n{generated_script}"
    result = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', result)
    return render(request, 'home.html', {'result': result, "total_docs": total_docs})

