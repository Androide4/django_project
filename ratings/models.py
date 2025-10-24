from django.db import models
from django.conf import settings
from django.utils import timezone
from subscriptions.models import Subscription  

class Rating(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    name = models.CharField("Nombre", max_length=120)   
    comment = models.TextField("Comentario", blank=True)
    score = models.PositiveSmallIntegerField("Calificación", help_text="1 a 10")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.subscription} - {self.user} ({self.score})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.score < 1 or self.score > 10:
            raise ValidationError("La calificación debe ser entre 1 y 10.")
