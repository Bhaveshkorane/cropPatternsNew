from celery import shared_task
import uuid
from .models import CropDataJson, CropDetails, State
from .models import District
from .models import Subdistrict
from .models import Village
from .models import Crop
from .models import ProcessStatus
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
        subdistricts = Subdistrict.objects.filter(district_id=district)

        # Fetch the district object
        district_obj = District.objects.select_related('state').get(district_code=district)

        # Extract the district name and state name
        district_name = district_obj.english_name
        state_name = district_obj.state.english_name

        gendata = ProcessStatus(
            process_id=process_id,
            district_name=district_name,
            crop_type=crop,
            timestamp=added_time,
            state_name=state_name
        )
        gendata.save()
        

        for subd in subdistricts:
            villages = Village.objects.filter(subdistrict_id=subd.subdistrict_code)
            for vil in villages:
                village_name = vil.english_name
                village_code = vil.village_code

                   # Call the API
                if crop == "All":
                    crop_names = Crop.objects.values_list('name', flat=True)
                    for cp in crop_names:
                        api_url = config('data_generator_api')

                        api_response = requests.get(api_url, data={'village': village_name, 'crop':cp,'village_code':village_code})
                        # Check if the request was successful
                        if api_response.status_code == 200:
                            data = api_response.json().get('payload')     
                        else:
                            return False
                        district = district 
                        dt = CropDataJson(
                            crop_data=data,
                            district_name=district_name,
                            state_name=state_name,
                            process_id=str(process_id),
                            added_time=added_time,
                            crop_type=cp
                        )
                        dt.save() 
     
                else:
                    crop_name = Crop.objects.get(id=crop).name
                    api_url = config('data_generator_api')
                    api_response = requests.get(api_url, data={'village': village_name, 'crop':crop_name,'village_code':village_code})
                        # Check if the request was successful
                    if api_response.status_code == 200:
                        data = api_response.json().get('payload')
                        generation_logger.info("data received")
                    else:
                        generation_logger.error(f"the data is genereatd with {api_response.status_code} code and the data is:{data}")
                        return False

                    district = district 
                    dt = CropDataJson(
                        crop_data=data,
                        district_name=district_name,
                        state_name=state_name,
                        process_id=str(process_id),
                        added_time=added_time,
                        crop_type=crop_name                    )
                    ProcessStatus.objects.filter(process_id=process_id).update(crop_type=crop_name)
                    dt.save()
                  
        # Update task status to generation
        ProcessStatus.objects.filter(process_id=process_id).update(is_generating=True)

        return True

    except Exception as e:
        # Log the exception details
        generation_logger.error(f"Error in generate_data_task: {e}", exc_info=True)
        
        # Update task status to 'failed'
        ProcessStatus.objects.filter(process_id=process_id).update(is_failed=True)
        ProcessStatus.objects.filter(process_id=process_id).update(is_complete=True)

        return False
    
@shared_task
def extraction_task(_,process_id):
    try:
        jsondata = CropDataJson.objects.filter(process_id=process_id).values()

        for data in jsondata:
            # For storing the corp data
            unique_id = data['crop_data']['uniqueid']
            crop_type = data['crop_data']['agricultural_data']['crop_type']
            area_cultivated = data['crop_data']['agricultural_data']['area_cultivated']
            yeild_perhectare = data['crop_data']['agricultural_data']['yeild_perhectare']
            soil_type = data['crop_data']['agricultural_data']['soil_type']
            irrigation_method = data['crop_data']['agricultural_data']['irrigation_method']
            village = int(data['crop_data']['village_code'])



            # Resloving Foreign keys 
            # village_=Village()
            # village_.village_code=int(village)


            villlage_instance=Village.objects.get(village_code=int(village))

            state_ =  State()
            state_.state_code = villlage_instance.state_id

            district_ = District()
            district_.district_code = villlage_instance.district_id

            subdistrict_ = Subdistrict()
            subdistrict_.subdistrict_code = villlage_instance.subdistrict_id
            
        
            # For storing the weather data
            temp_min = data['crop_data']['agricultural_data']['weather_data']['temprature']['max']
            temp_max = data['crop_data']['agricultural_data']['weather_data']['temprature']['min']
            temp_avg = data['crop_data']['agricultural_data']['weather_data']['temprature']['average']
            rainfall_total = data['crop_data']['agricultural_data']['weather_data']['Rain_fall']['total_mm']
            rainfall_rainy_days = data['crop_data']['agricultural_data']['weather_data']['Rain_fall']['rainy_days']
            humidity = data['crop_data']['agricultural_data']['weather_data']['humidity']['average_percentage']


            # For fertilizer data
            npk = data['crop_data']['agricultural_data']['pesticide_and_fertilizer_usage']['fertilizers'][0]['quantity_kg']
            compost = data['crop_data']['agricultural_data']['pesticide_and_fertilizer_usage']['fertilizers'][1]['quantity_kg']

            # For Pesticides
            quantity_l = data['crop_data']['agricultural_data']['pesticide_and_fertilizer_usage']['pesticides'][0]['quantity_l']

            
            savecrop = CropDetails(unique_id=unique_id,
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
                            


                            village=villlage_instance,
                            district=district_,
                            subdistrict=subdistrict_,
                            state=state_,
                            process_id = process_id
                            )

            # Adding data into Cropdetails                       
            savecrop.save()
            ProcessStatus.objects.filter(process_id=process_id).update(is_extracting=True)


        # Call to function for aggrigating the data

        aggirgatedata(process_id)
        ProcessStatus.objects.filter(process_id=process_id).update(is_aggregating=True)
        ProcessStatus.objects.filter(process_id=process_id).update(is_complete=True)
        # extraction_logger.info("data has been aggrigated for ")

        return True

    except Exception as e:
        extraction_logger.error(f"errror occured in savejson --->{e}")
        ProcessStatus.objects.filter(process_id=process_id).update(is_complete=True)

        ProcessStatus.objects.filter(process_id=process_id).update(is_failed=True)

        return False

