from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    THEME_CHOICES = (
        ('dark', 'Dark Mode'),
        ('light', 'Light Mode'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    preferred_language = models.CharField(max_length=10, default='en')
    bio = models.TextField(blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
