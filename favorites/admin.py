from django.contrib import admin
from .models import FavoriteProfile

@admin.register(FavoriteProfile)
class FavoriteProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'user', 'created_at')
    search_fields = ('username', 'name', 'user__username')
    list_filter = ('created_at',)
