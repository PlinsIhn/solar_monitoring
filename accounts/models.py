
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_verified = models.BooleanField(default=False)  # Pour indiquer si l'utilisateur est vérifié
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(
        max_length=150,
        unique=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_ ]+$',
                message="Le nom d'utilisateur ne peut contenir que des lettres, chiffres, underscores (_) et espaces.",
                code='invalid_username'
            ),
        ],
    )
    

from django.conf import settings

class Channel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'user')
        
    def __str__(self):
        return self.name

class ChannelData(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.channel.name} - {self.timestamp}"
    
