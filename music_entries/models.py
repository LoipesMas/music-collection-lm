from django.db import models

from enum import Enum



# Create your models here.
class MusicEntry(models.Model):
    type_choices = (('album','Album'),('song','Song'),('mix','Playlist/Mix'))
    title = models.CharField(max_length=256)
    artist = models.CharField(max_length=256)
    genre = models.CharField(max_length=256)
    type = models.CharField(max_length=256, choices=type_choices)
    link = models.CharField(max_length=256)
    submitter = models.CharField(max_length=256)
    public_key = models.CharField(max_length=8)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.artist+" - "+self.title

    def get_type(self):
        for c in self.type_choices:
            if c[0] == self.type:
                return c[1]