from django.db import models

class Accordance(models.Model):
    """
    Модель соответствия полной ссылки - короткой ссылке
    """
    class Meta:
        ordering = ["pk"]
    full_url = models.CharField(blank=False, null=False, max_length=300)  # полная ссылка
    short_url = models.CharField(blank=True, null=True, max_length=150)  # сокращенная ссылка
