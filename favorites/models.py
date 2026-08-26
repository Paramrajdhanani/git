from django.db import models
from django.contrib.auth.models import User

class FavoriteProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    username = models.CharField(max_length=150)
    name = models.CharField(max_length=150, blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'username')

    def __str__(self):
        return f"{self.username} favorited by {self.user.username}"
