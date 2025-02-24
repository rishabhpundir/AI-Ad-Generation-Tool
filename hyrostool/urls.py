from drf_yasg import openapi
from django.contrib import admin
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from django.urls import path, include, re_path


schema_view = get_schema_view(
    openapi.Info(
        title="Stillbloom Ad Generation API",
        default_version="v1",
        description="API documentation for Stillbloom Ad Generation API project",
        terms_of_service="https://www.python.org/",
        contact=openapi.Contact(email="admin@stillbloom.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)



urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('ad/', include('scriptdata.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

