from django.contrib import admin
from .models import SearchHistory

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'user', 'session_key', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('username', 'user__username', 'session_key')
