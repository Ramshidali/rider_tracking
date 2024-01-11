from django.contrib.auth.models import User
from locations.models import Location

from rest_framework import serializers

from rides.models import Ride
from users.models import Driver, Profile

# **************************************************************************************
# ******************************** GET SERIALIZERS *************************************
# **************************************************************************************
class RidesGetSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()
    updater_name = serializers.SerializerMethodField()
    rider_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    pickup_location_name = serializers.SerializerMethodField()
    dropoff_location_name = serializers.SerializerMethodField()
    status_value = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = ['id','creator_name','updater_name','rider_name','driver_name','pickup_location_name','dropoff_location_name','status_value','current_location']
        
    def get_creator_name(self, instance):
        username = Profile.objects.get(user__id=instance.creator.pk).name
        return username
    
    def get_updater_name(self, instance):
        username = Profile.objects.get(user__id=instance.updater.pk).name
        return username
    
    def get_rider_name(self, instance):
        username = Profile.objects.get(id=instance.rider.pk).name
        return username
    
    def get_driver_name(self, instance):
        username = Profile.objects.get(id=instance.rider.pk).name
        return username
    
    def get_pickup_location_name(self, instance):
        location = Location.objects.get(id=instance.pickup_location.pk).location
        return location
    
    def get_dropoff_location_name(self, instance):
        location = Location.objects.get(id=instance.dropoff_location.pk).location
        return location
    
    def get_status_value(self, instance):
        status = instance.get_status_display()
        return status
        
class DriverSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ['id','name','is_available','current_location']
    
    def get_name(self, instance):
        name =  Profile.objects.get(user=instance.user).name
        return name
    
# **************************************************************************************
# ******************************** POST SERIALIZERS *************************************
# **************************************************************************************
class RidesPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ride
        fields = ['rider','driver','pickup_location','dropoff_location','status']
        

class RideStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ride
        fields = ['status']
