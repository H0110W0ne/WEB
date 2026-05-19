from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('contacts/', views.contacts, name='contacts'),
    path('health/', views.healthcheck, name='health'),
    path('api/registration/', views.api_registration, name='api_registration'),
]
