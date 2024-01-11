from django.db import models
from django.contrib.auth.models import User

from main.models import BaseModel

# Create your models here.
class Location(BaseModel):
    location = models.CharField(max_length=128, null=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.CharField(max_length=128)
    longitude = models.CharField(max_length=128)

    class Meta:
        db_table = 'location'
        verbose_name = ('Location')
        verbose_name_plural = ('Locations')
        ordering = ('location',)

    def __str__(self):
        return str(self.location)