from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analise/<uuid:id>/', views.resultado, name='resultado'),
]