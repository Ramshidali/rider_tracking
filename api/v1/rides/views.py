# -*- coding: utf-8 -*-
import time
import datetime
import requests

from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User, Group

from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes

from rides.models import Ride
from users.models import Driver, Profile
from locations.models import Location
from main.functions import encrypt_message, get_auto_id
from api.v1.rides.serializers import DriverSerializer, RidesGetSerializer, RidesPostSerializer
from api.v1.authentication.functions import generate_serializer_errors, get_user_token


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_ride(request):
    serializer = RidesPostSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                rider = Profile.objects.get(pk=serializer.data['rider']) 
                driver = Profile.objects.get(pk=serializer.data['driver']) 
                pickup_location = Location.objects.get(pk=serializer.data['pickup_location']) 
                dropoff_location = Location.objects.get(pk=serializer.data['dropoff_location'])
                
                clean_longitude = ''.join(c for c in pickup_location.longitude if c.isdigit() or c in ['.', '-'])
                clean_latitude = ''.join(c for c in pickup_location.latitude if c.isdigit() or c in ['.', '-'])

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
                    starting_location = Point(longitude, latitude)
                except (ValueError, TypeError) as e:
                    # Handle the error, such as logging or raising a specific exception
                    print(f"Error converting coordinates: {e}")
                
                new_ride_instance = Ride.objects.create(
                    auto_id=get_auto_id(Ride),
                    creator=request.user,
                    updater=request.user,
                    status="10",
                    rider=rider,
                    driver=driver,
                    pickup_location=pickup_location,
                    dropoff_location=dropoff_location,
                    current_location=starting_location
                )
                
                status_code = status.HTTP_200_OK
                response_data = {
                    "StatusCode": 6000,
                    "data" : RidesGetSerializer(new_ride_instance, many=False, context={"request": request}).data
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


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def ride(request,pk):
    
    try :
        instance = Ride.objects.get(pk=pk,is_deleted=False)
        
        serialized = RidesGetSerializer(instance, many=False, context={"request": request})
        
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


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def rides_list(request):
    
    try :
        instances = Ride.objects.filter(is_deleted=False)
        
        serialized = RidesGetSerializer(instances, many=True, context={"request": request})
        
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def update_ride_status(request,pk):
    
    try :
        instance = Ride.objects.get(pk=pk,is_deleted=False)
        instance.status = request.POST.get("status")
        instance.save()
        
        if instance.status != "30" or instance.status != "40":
            driver_status = Driver.objects.get(user=instance.driver.user)
            driver_status.is_available = True
            driver_status.current_location = instance.current_location
            driver_status.save()
        
        serialized = RidesGetSerializer(instance, many=False, context={"request": request})
        
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def ride_tracking(request, pk):
    ride = get_object_or_404(Ride, pk=pk)

    # Get latitude and longitude from the frontend
    clean_longitude = ''.join(c for c in request.data.get('latitude') if c.isdigit() or c in ['.', '-'])
    clean_latitude = ''.join(c for c in request.data.get('longitude') if c.isdigit() or c in ['.', '-'])

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
        starting_location = Point(longitude, latitude)
    except (ValueError, TypeError) as e:
        # Handle the error, such as logging or raising a specific exception
        print(f"Error converting coordinates: {e}")

    if latitude is not None and longitude is not None:
        # Simulate ride tracking
        try:
            with transaction.atomic():
                ride.update_location(latitude, longitude)
                serialized_ride = RidesGetSerializer(ride, many=False, context={"request": request})
                time.sleep(2)

            return JsonResponse({
                'data': serialized_ride.data,
                'message': 'Simulation completed'
                })

        except (ValueError, TypeError) as e:
            # Handle the error, such as logging or returning an error response
            return JsonResponse({'error': f"Error in simulation: {e}"}, status=500)
    else:
        return JsonResponse({'error': 'Latitude and longitude must be provided in the request payload.'}, status=400)
    
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def match_ride_to_driver(request, pk):
    ride = Ride.objects.get(pk=pk)
    available_drivers = Driver.objects.filter(is_available=True)

    closest_driver, min_distance = match_ride_to_driver_algorithm(ride, available_drivers)

    if closest_driver:
        serializer = DriverSerializer(closest_driver, context={"request": request})
        return Response(serializer.data)
    else:
        return Response({'message': 'No available drivers'})

def match_ride_to_driver_algorithm(ride, drivers):
    closest_driver = drivers.first()
    min_distance = 0

    return closest_driver, min_distance


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def accept_ride_request(request, pk):
    driver = Driver.objects.get(user=request.user)
    ride = Ride.objects.get(pk=pk)

    ride.driver = driver
    ride.status = '20'
    ride.save()

    driver.is_available = False
    driver.save()

    serializer = RidesGetSerializer(ride, many=False, context={"request": request})
    return Response({'message': 'Ride request accepted successfully', 'ride': serializer.data})


