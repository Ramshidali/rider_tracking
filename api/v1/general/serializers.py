from django.contrib.auth.models import User

from rest_framework import serializers

from locations.models import Location


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['location','short_name','latitude','longitude']
