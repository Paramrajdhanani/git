from django.db import models

class RepositoryCache(models.Model):
    username = models.CharField(max_length=150, db_index=True)
    repo_name = models.CharField(max_length=200)
    data_json = models.JSONField()
    cached_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Repository Cache'
        verbose_name_plural = 'Repository Caches'
        unique_together = ('username', 'repo_name')

    def __str__(self):
        return f"{self.username}/{self.repo_name}"
