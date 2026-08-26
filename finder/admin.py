from django.contrib import admin
from .models import RepositoryCache

@admin.register(RepositoryCache)
class RepositoryCacheAdmin(admin.ModelAdmin):
    list_display = ('username', 'repo_name', 'cached_at')
    search_fields = ('username', 'repo_name')
    list_filter = ('cached_at',)
