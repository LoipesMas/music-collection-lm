from django.db import models

# Create your models here.
class PublicKeys(models.Model):
    user_id = models.IntegerField(unique=True, primary_key=True)
    public_key = models.CharField(max_length=8, unique=True)
