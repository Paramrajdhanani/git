from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('api/recent/', views.get_recent_searches, name='recent'),
    path('api/clear/', views.clear_history, name='clear'),
]
