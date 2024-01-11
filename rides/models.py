import random

from django.db import models
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models

from locations.models import Location
from main.models import BaseModel
from users.models import Profile

STATUS_CHOICES = (
    ('10', 'Requested'),
    ('20', 'Started'),
    ('30', 'Completed'),
    ('40', 'Cancelled'),
)

class Ride(BaseModel):
    
    rider = models.ForeignKey(Profile, related_name='rider', on_delete=models.CASCADE)
    driver = models.ForeignKey(Profile, related_name='driver', on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, related_name='pickup_location', on_delete=models.CASCADE)
    dropoff_location = models.ForeignKey(Location, related_name='drop_location', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='10')
    
    current_location = gis_models.PointField(blank=True, null=True)

    class Meta:
        db_table = 'rides_ride'
        verbose_name = ('Ride')
        verbose_name_plural = ('Ride')
    
    def __str__(self):
        return str(self.id)
    
    def update_location(self, latitude, longitude):
        try:
            # Update the current_location field
            self.current_location = Point(longitude, latitude)
            self.save()

        except (ValueError, TypeError) as e:
            # Handle the error, such as logging or raising a specific exception
            print(f"Error updating location: {e}")