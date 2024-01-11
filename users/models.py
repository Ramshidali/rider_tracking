from django.db import models
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models

from main.models import BaseModel

USER_TYPE = (
    ("10", "driver"),
    ("20", "rider"),
)

# Create your models here.
class Profile(BaseModel):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=10)
    dob = models.DateField()
    type = models.CharField(max_length=2,choices=USER_TYPE)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = ('Profile')
        verbose_name_plural = ('Profile')
    
    def __str__(self):
        return str(self.id)
    
    
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    current_location = gis_models.PointField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_driver'
        verbose_name = ('Driver')
        verbose_name_plural = ('Driver')

    def __str__(self):
        return f'Driver: {self.profile.name}'