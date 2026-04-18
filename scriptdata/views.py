from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from scriptdata.utils.retriever import retrieve_similar_ads
from scriptdata.utils.gemini_utils import generate_ad_script

class GenerateAdView(APIView):
    """
    API endpoint to generate an ad script using Gemini.
    """
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("query", openapi.IN_QUERY, description="Search query for generating ads", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: "Success"},
    )
    def get(self, request):
        query = request.GET.get("query", "")
        if not query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        retrieved_ads = retrieve_similar_ads(query=query)

        if not retrieved_ads:
            return Response({"error": "No similar ads found."}, status=status.HTTP_404_NOT_FOUND)
        
        generated_script = generate_ad_script(query, retrieved_ads)
        return Response({"query": query, "generated_ad_script": generated_script}, status=status.HTTP_200_OK)
