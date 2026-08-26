from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('api/toggle/', views.toggle_favorite, name='toggle'),
    path('api/status/<str:username>/', views.check_favorite_status, name='status'),
]
