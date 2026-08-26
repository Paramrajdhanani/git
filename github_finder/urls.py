from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('finder.urls', namespace='finder')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('history/', include('history.urls', namespace='history')),
    path('favorites/', include('favorites.urls', namespace='favorites')),
]
