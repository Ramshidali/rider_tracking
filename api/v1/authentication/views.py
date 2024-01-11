# -*- coding: utf-8 -*-
import datetime
import requests

from django.contrib.gis.geos import Point
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User, Group

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from main.functions import encrypt_message, get_auto_id
from api.v1.authentication.functions import generate_serializer_errors, get_user_token
from api.v1.authentication.serializers import ProfileSerializer, SignUpSerializer, LogInSerializer, UserTokenObtainPairSerializer
from users.models import Driver, Profile


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_user(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():

                username = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user_type = serializer.validated_data['type']

                user_data = User.objects.create_user(
                    username=username,
                    password=password,
                    is_staff=False,
                )
            
                if user_type == '10':
                    group_name = 'driver'
                elif user_type == '20':
                    group_name = 'rider'
                
                if Group.objects.filter(name=group_name).exists():
                    group = Group.objects.get(name=group_name)
                else:
                    group = Group.objects.create(name=group_name)
                    user_data.groups.add(group)
                
                encrypted_password = encrypt_message(password)
                serializer.validated_data['password'] = encrypted_password
                serializer.validated_data['user'] = user_data
                serializer.validated_data['auto_id'] = get_auto_id(Profile)
                serializer.validated_data['creator'] = user_data
                serializer.validated_data['updater'] = user_data
                serializer.validated_data['date_updated'] = datetime.datetime.today()
                serializer.save()
                
                clean_longitude = ''.join(c for c in request.POST.get('latitude') if c.isdigit() or c in ['.', '-'])
                clean_latitude = ''.join(c for c in request.POST.get('longitude') if c.isdigit() or c in ['.', '-'])

                # Handle multiple dots in the string
                clean_longitude_parts = clean_longitude.split('.')
                clean_latitude_parts = clean_latitude.split('.')

                # Join the parts, taking only the first part as the integer and the second part as the decimal
                clean_longitude = '.'.join([clean_longitude_parts[0], clean_longitude_parts[1]] if len(clean_longitude_parts) > 1 else clean_longitude_parts) if clean_longitude_parts else clean_longitude
                clean_latitude = '.'.join([clean_latitude_parts[0], clean_latitude_parts[1]] if len(clean_latitude_parts) > 1 else clean_latitude_parts) if clean_latitude_parts else clean_latitude

                # Convert cleaned strings to floats
                try:
                    longitude = float(clean_longitude)
                    latitude = float(clean_latitude)
                    current_location = Point(longitude, latitude)
                except (ValueError, TypeError) as e:
                    # Handle the error, such as logging or raising a specific exception
                    print(f"Error converting coordinates: {e}")
                
                if user_type == "10":
                    Driver.objects.create(
                        user=user_data,
                        current_location=current_location
                    )
                
                status_code = status.HTTP_200_OK
                response_data = {
                    "StatusCode": 6000,
                    "data" : serializer.data
                }
            
        except IntegrityError as e:
                # Handle database integrity error
                status_code = status.HTTP_400_BAD_REQUEST
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": "Integrity error occurred. Please check your data.",
                }

        except Exception as e:
            # Handle other exceptions
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serializer._errors)
        }
    return Response(response_data,status=status_code)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def login(request):
    serialized = LogInSerializer(data=request.data)

    if serialized.is_valid():

        username = serialized.data['username']
        password = serialized.data['password']

        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"username": "' + username + '", "password":"' + password + '"}'
        protocol = "http://"
        if request.is_secure():
            protocol = "https://"

        web_host = request.get_host()
        request_url = protocol + web_host + "/api/v1/auth/token/"

        response = requests.post(request_url, headers=headers, data=data)
        
        if response.status_code == 200:
            response_data = {
                "StatusCode": 6000,
                "data": response.json(),
                "message": "Login successfully",
                
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Validation Error",
            }

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def users_list(request):
    
    try :
        instances = Profile.objects.filter(is_deleted=False)
        
        serialized = ProfileSerializer(instances, many=True, context={"request": request})
        
        status_code = status.HTTP_200_OK  
        response_data = {
            "status": status_code,
            "StatusCode": 6000,
            "data": serialized.data,
        }
    except :
        status_code = status.HTTP_400_BAD_REQUEST 
        response_data = {
            "status": status_code,
            "StatusCode": 6001,
        }

    return Response(response_data, status_code)
    