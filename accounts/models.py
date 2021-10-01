from django.db import models

# Relates user_id to public_key (which is used to access collections)
class PublicKeys(models.Model):
    user_id = models.IntegerField(unique=True, primary_key=True)
    public_key = models.CharField(max_length=8, unique=True)
