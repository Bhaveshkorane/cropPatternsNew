from rest_framework import serializers

# Models importing 
from .models import State
from .models import Village
from .models import District
from .models import Subdistrict

from django.contrib.auth.models import User

class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        #fields = '__all__'
        exclude=['created_at','updated_at']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        exclude=['created_at','updated_at']
        #fields='__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        exclude = ['created_at','updated_at']

class SubdistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdistrict 
        exclude = ['created_at','updated_at']
