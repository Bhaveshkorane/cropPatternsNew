import random
from rest_framework.response import Response 
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response 
from django.views import View


# Importing models 
from .models import State
from .models import District
from .models import CropDetails
from .models import AggregationData  

# For logging 
import logging
generation_logger = logging.getLogger('generation_logger')
extraction_logger = logging.getLogger('extraction_logger')
aggregation_logger = logging.getLogger('aggregation_logger')
error_logger = logging.getLogger('error_logger')


# uuid for generting the unique id 
import uuid 

# Aggrigation functions
from django.db.models import Sum

# from rest_framework.decorators import api_view
from rest_framework.views import APIView

# For randaom value generation
import random


# For downloading pdf file 
from io import BytesIO
from .models import AggregationData


# uuid for generting the unique id 
import uuid 

class generatedata(APIView):
    def get(self,request): # Make async-------------------------------------------->
        try:
            unique_id = uuid.uuid4()
            data = request.data
            village = data['village']
            village_code =  data['village_code']
            crop =  data['crop']

            area = random.randint(1,39)

            soils=['clay', 'sandy', 'silty', 'peaty', 'chalky', 'loamy']
            soil_index=random.randint(0,5)
            soil=soils[soil_index]

            irrigatoins=['flooding','sprinkler','drip']
            irr_index=random.randint(0,2)
            irrigatoin=irrigatoins[irr_index]

            data = {
                        'uniqueid': unique_id,
                        'village': village,  # users input from form
                        'village_code': village_code,
                        "agricultural_data": {
                            "area": area,
                            "crop_type": crop,  # users input from form
                            "area_cultivated": random.randint(1, 500),
                            "yeild_perhectare": random.randint(5, 15),
                            "soil_type": soil,
                            "irrigation_method": irrigatoin,
                            "weather_data": {
                                "temprature": {
                                    "average": random.randint(1, 50),
                                    "max": random.randint(1, 50),
                                    "min": random.randint(1, 50)
                                },
                                "Rain_fall": {
                                    "total_mm": random.randint(1000, 3500),
                                    "rainy_days": random.randint(1000, 3000)
                                },
                                "humidity": {
                                    "average_percentage": random.randint(1, 100)
                                }
                            },
                            "pesticide_and_fertilizer_usage": {
                                "fertilizers": [
                                    {
                                        "type": "NPK",
                                        "quantity_kg": random.randint(500, 1000)
                                    },
                                    {
                                        "type": "Compost",
                                        "quantity_kg": random.randint(600, 2000)
                                    }
                                ],
                                "pesticides": [
                                    {
                                        "type": "Fungicide",
                                        "quantity_l": random.randint(40, 200)
                                    }
                                ]
                            }
                        }
                    }
            generation_logger.info(f" Data generated for {village}")
            return Response({"status:":200,"payload":data})
        
        except Exception as e:
            error_logger.error(f"there is problem in generatedata---->{e}")
            generation_logger.error(f"Problem occured --->{e}")
            return Response({"status:":404,"payload":data})
        
def aggirgatedata(process_id):
    try:
        aggregated_data = CropDetails.objects.filter(process_id=process_id).values('state', 'district', 'crop_type').annotate(total_area=Sum('area_cultivated'))

        for data in aggregated_data:
            state_name = State.objects.get(state_code=data['state']).english_name
            district_name = District.objects.get(district_code=data['district']).english_name
            AggregationData.objects.update_or_create(
                state_name= state_name,
                district_name= district_name,
                crop_type=data['crop_type'],
                defaults={'area_cultivated': data['total_area']}
            )
            aggregation_logger.info(f"Data has been aggregated for {district_name}")
        
    except Exception as e:
        aggregation_logger.error(f"Error occurred in aggirgatedata--->{e}")
        error_logger.error(f"Error in aggregating data: {e}")

        


