import random
from rest_framework.response import Response 
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response 
from django.views import View


# Importing models 
from .models import State
from .models import District
from .models import Cropdetails
from .models import Aggridata   


# uuid for generting the unique id 
import uuid 

# Aggrigation functions
from django.db.models import Sum

# For error logging 
import logging
error_logger = logging.getLogger('error_logger')






# from rest_framework.decorators import api_view
from rest_framework.views import APIView

# For randaom value generation
import random

# Importing loggers 
import logging
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('django')
warning_logger = logging.getLogger('warning_logger')
debug_logger = logging.getLogger('dubug_logger')

# For downloading pdf file 
from io import BytesIO
from .models import Aggridata


# uuid for generting the unique id 
import uuid 

class generatedata(APIView):
    def get(self,request): # Make async-------------------------------------------->
        try:
            unique_id = uuid.uuid4()
            data = request.data
            # params = request.query_params  
            village = data['village']
            # village = params['village']
            

        
            # village_code =  params['village_code']
            village_code =  data['village_code']

            # crop =  params['crop']
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

            return Response({"status:":200,"payload":data})
        except Exception as e:
            error_logger.error(f"there is problem in generatedata---->{e}")
            return Response({"status:":404,"payload":data})
        
def aggirgatedata():
    # Perform the aggregation
    logger = logging.getLogger('django')
    try:
        aggregated_data = Cropdetails.objects.values('state', 'district', 'crop_type').annotate(total_area=Sum('area_cultivated'))

        for data in aggregated_data:
            state_name = State.objects.get(statecode=data['state']).englishname
            district_name = District.objects.get(districtcode=data['district']).englishname
            Aggridata.objects.update_or_create(
                state= state_name,
                district    = district_name,
                crop=data['crop_type'],
                defaults={'area_cultivated': data['total_area']}
            )
        
    except Exception as e:
        logger.error(f"errror occured in aggirgatedata--->{e}")


