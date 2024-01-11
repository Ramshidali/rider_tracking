from __future__ import unicode_literals
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type
from django.contrib.auth.models import User

from users.models import Profile


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenObtainPairSerializer, cls).get_token(user)
        return token
    def validate(cls, attrs):
        data = super(UserTokenObtainPairSerializer, cls).validate(attrs)

        refresh = cls.get_token(cls.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)

        if cls.user.is_superuser:
            data['role'] = "superuser"
        else:
            data['role'] = "user"

        return data


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['name','phone','dob','type','email','password']


class LogInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)
    

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id','name','phone','dob','type','email']
