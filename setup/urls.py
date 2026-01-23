from django.contrib import admin
from django.urls import path
# AQUI ESTAVA O ERRO: Mudamos de 'Tevox_Analisador_IA.core' para apenas 'core'
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home e Resultado
    path('', views.home, name='home'),
    path('analise/<uuid:id>/', views.resultado, name='resultado'),
    
    # Nova URL do Chat (API)
    path('api/chat/<uuid:id>/', views.api_chat_processo, name='api_chat_processo'),
]