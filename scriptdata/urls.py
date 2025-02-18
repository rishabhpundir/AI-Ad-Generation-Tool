from django.urls import path
from scriptdata.views import GenerateAdView

urlpatterns = [
    path("generate/", GenerateAdView.as_view(), name="generate_ad"),
]
