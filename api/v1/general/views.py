# -*- coding: utf-8 -*-
import datetime
import requests
from api.v1.general.serializers import LocationSerializer
from locations.models import Location


from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import status



@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def location_list(request):
    
    try :
        instances = Location.objects.filter(is_deleted=False)
        
        serialized = LocationSerializer(instances, many=True, context={"request": request})
        
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