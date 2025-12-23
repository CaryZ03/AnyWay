"""
URL configuration for aiagent project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

# Swagger API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="AI Agent Platform API",
        default_version='v1.0.0',
        description="AI智能体创作平台 RESTful API文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API Endpoints
    path('api/v1/agents/', include('apps.agent.urls')),
    path('api/v1/workflows/', include('apps.workflow.urls')),
    path('api/v1/knowledge/', include('apps.knowledge.urls')),
    path('api/v1/plugins/', include('apps.plugin.urls')),
    path('api/v1/llm/', include('apps.llm.urls')),
    
    # Health Check
    path('health/', lambda request: JsonResponse({'status': 'ok'})),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
