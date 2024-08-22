from celery import shared_task
import uuid
from .models import Cropdatajson, Cropdetails, State
from .models import District
from .models import Subdistrict
from .models import Village
from .models import Crop
from .models import Process_status
from datetime import datetime
import requests
from decouple import config
from .utils import aggirgatedata


from django.contrib import messages
from django.shortcuts import redirect


# Importing loggers 
import logging
generation_logger = logging.getLogger('generation_logger')
extraction_logger = logging.getLogger('extraction_logger')
aggregation_logger = logging.getLogger('aggregation_logger')


@shared_task
def generate_data_task(district, crop,process_id):
    
    added_time = datetime.now()

    try:
        district_name = District.objects.get(districtcode=district).englishname
        subdistricts = Subdistrict.objects.filter(district_id=district)

        # Fetch the district object
        district_obj = District.objects.select_related('state').get(districtcode=district)

        # Extract the district name and state name
        district_name = district_obj.englishname
        state_name = district_obj.state.englishname

        gendata = Process_status(
            process_id=process_id,
            district=district_name,
            crop=crop,
            timestamp=added_time,
            state=state_name
        )
        gendata.save()
        

        for subd in subdistricts:
            villages = Village.objects.filter(subdistrict_id=subd.subdistrictcode)
            for vil in villages:
                village_name = vil.englishname
                village_code = vil.villagecode

                   # Call the API
                if crop == "All":
                    crop_names = Crop.objects.values_list('cropname', flat=True)
                    for cp in crop_names:
                        api_url = config('data_generator_api')

                        api_response = requests.get(api_url, data={'village': village_name, 'crop':cp,'village_code':village_code})
                        # Check if the request was successful
                        if api_response.status_code == 200:
                            data = api_response.json().get('payload')     
                        else:
                            data = None
                        district = district 
                        dt = Cropdatajson(
                            cropdata=data,
                            district=district_name,
                            state=state_name,
                            process_id=str(process_id),
                            added_time=str(added_time),
                            crop_type=cp
                        )
                        dt.save() 
     
                else:
                    crop_name = Crop.objects.get(id=crop).cropname
                    api_url = config('data_generator_api')
                    api_response = requests.get(api_url, data={'village': village_name, 'crop':crop_name,'village_code':village_code})
                        # Check if the request was successful
                    if api_response.status_code == 200:
                        data = api_response.json().get('payload')
                    else:
                        generation_logger.error(f"the data is genereatd with {api_response.status_code} code and the data is:{data}")
                        data = None

                    district = district 
                    dt = Cropdatajson(
                        cropdata=data,
                        district=district_name,
                        state=state_name,
                        process_id=str(process_id),
                        added_time=str(added_time),
                        crop_type=crop_name                    )
                    Process_status.objects.filter(process_id=process_id).update(crop=crop_name)
                    dt.save()
                  
                

        # Update task status to generation
        Process_status.objects.filter(process_id=process_id).update(is_generation=True)

        return True

    except Exception as e:
        # Log the exception details
        generation_logger.error(f"Error in generate_data_task: {e}", exc_info=True)
        
        # Update task status to 'failed'
        Process_status.objects.filter(process_id=process_id).update(is_failed=True)
        Process_status.objects.filter(process_id=process_id).update(is_completed=True)

        return False
    
@shared_task
def save_json_task(_,id):
    try:
        jsondata = Cropdatajson.objects.filter(process_id=id).values()

        for data in jsondata:
            # For storing the corp data
            unique_id = data['cropdata']['uniqueid']
            crop_type = data['cropdata']['agricultural_data']['crop_type']
            area_cultivated = data['cropdata']['agricultural_data']['area_cultivated']
            yeild_perhectare = data['cropdata']['agricultural_data']['yeild_perhectare']
            soil_type = data['cropdata']['agricultural_data']['soil_type']
            irrigation_method = data['cropdata']['agricultural_data']['irrigation_method']
            village = int(data['cropdata']['village_code'])



            # Resloving Foreign keys 
            village_=Village()
            village_.villagecode=int(village)


            vil=Village.objects.get(villagecode=int(village))

            state_ =  State()
            state_.statecode = vil.state_id

            district_ = District()
            district_.districtcode = vil.district_id

            subdistrict_ = Subdistrict()
            subdistrict_.subdistrictcode = vil.subdistrict_id
            
        
            # For storing the weather data
            temp_min = data['cropdata']['agricultural_data']['weather_data']['temprature']['max']
            temp_max = data['cropdata']['agricultural_data']['weather_data']['temprature']['min']
            temp_avg = data['cropdata']['agricultural_data']['weather_data']['temprature']['average']
            rainfall_total = data['cropdata']['agricultural_data']['weather_data']['Rain_fall']['total_mm']
            rainfall_rainy_days = data['cropdata']['agricultural_data']['weather_data']['Rain_fall']['rainy_days']
            humidity = data['cropdata']['agricultural_data']['weather_data']['humidity']['average_percentage']


            # For fertilizer data
            npk = data['cropdata']['agricultural_data']['pesticide_and_fertilizer_usage']['fertilizers'][0]['quantity_kg']
            compost = data['cropdata']['agricultural_data']['pesticide_and_fertilizer_usage']['fertilizers'][1]['quantity_kg']

            # For Pesticides
            quantity_l = data['cropdata']['agricultural_data']['pesticide_and_fertilizer_usage']['pesticides'][0]['quantity_l']

            
            savecrop = Cropdetails(unique_id=unique_id,
                            crop_type=crop_type,
                            area_cultivated=area_cultivated,
                            yeild_perhectare=yeild_perhectare,
                            soil_type=soil_type,irrigation_method=irrigation_method,
                            temp_avg=temp_avg,
                            temp_max=temp_max,
                            temp_min=temp_min,
                            rainfall_rainy_days=rainfall_rainy_days,
                            rainfall_total=rainfall_total,
                            humidity=humidity,
                            fertilizer_NPK_kg = npk,
                            fertilizer_COMPOST_kg = compost,
                            pesticide_type="Fungicide",
                            pesticide_quantity_l=quantity_l,
                            


                            village=village_,
                            district=district_,
                            subdistrict=subdistrict_,
                            state=state_
                            )

            # Adding data into Cropdetails                       
            savecrop.save()
            Process_status.objects.filter(process_id=id).update(is_extraction=True)


        # Call to function for aggrigating the data

        aggirgatedata()
        Process_status.objects.filter(process_id=id).update(is_aggregation=True)
        Process_status.objects.filter(process_id=id).update(is_completed=True)
        extraction_logger.info("data has been aggrigated for ")

        

        return True

    except Exception as e:
        extraction_logger.error(f"errror occured in savejson --->{e}")
        Process_status.objects.filter(process_id=id).update(is_completed=True)

        Process_status.objects.filter(process_id=id).update(is_failed=True)

        return False

