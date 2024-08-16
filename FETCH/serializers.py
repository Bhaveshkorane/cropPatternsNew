from rest_framework import serializers

# Models importing 
from .models import State
from .models import Village
from .models import District

from django.contrib.auth.models import User

class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        #fields = '__all__'
        exclude=['villagecreated','villageupdated']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        exclude=['statecreated','stateupdated']
        #fields='__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        exclude = ['districtcreated','districtupdated']
