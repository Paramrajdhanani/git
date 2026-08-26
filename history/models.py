from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='search_histories')
    session_key = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=150)
    avatar_url = models.URLField(blank=True, default='')
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'Search Histories'

    def __str__(self):
        user_str = self.user.username if self.user else f"Session:{self.session_key[:8]}"
        return f"{self.username} searched by {user_str} on {self.searched_at.strftime('%Y-%m-%d %H:%M')}"
