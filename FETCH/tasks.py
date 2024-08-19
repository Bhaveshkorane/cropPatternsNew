from celery import shared_task
import uuid
from .models import Cropdatajson, Cropdetails, State
from .models import District
from .models import Subdistrict
from .models import Village
from .models import Crop
from .models import DataGenerationStatus
from datetime import datetime
import requests
from decouple import config
from .utils import aggirgatedata


from django.contrib import messages
from django.shortcuts import redirect


# Importing loggers 
import logging
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('django')
warning_logger = logging.getLogger('warning_logger')
debug_logger = logging.getLogger('dubug_logger')


@shared_task
def generate_data_task(district, crop):
    process_id = uuid.uuid4()
    added_time = datetime.now()

    try:
        # Start task and set status to 'in_progress'
        gendata = DataGenerationStatus(
            process_id=process_id,
            district=district,
            crop=crop,
            status='in_progress',
            timestamp=added_time
        )
        gendata.save()

        district_name = District.objects.get(districtcode=district).englishname
        subdistricts = Subdistrict.objects.filter(district_id=district)

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
                        dt = Cropdatajson(cropdata=data,
                                        added=district,
                                        district=district_name,
                                        process_id=process_id,
                                        added_time=added_time,
                                        crop_type=crop
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
                        error_logger.error(f"the data is genereatd with {api_response.status_code} code and the data is:{data}")
                        data = None

                    district = district 
                    dt = Cropdatajson(cropdata=data,
                                    added=district,
                                district=district_name,
                                process_id=process_id,
                                added_time=added_time,
                                crop_type=crop_name
                                )
                dt.save()

        # Update task status to 'completed'
        DataGenerationStatus.objects.filter(process_id=process_id).update(status='completed')
        return True

    except Exception as e:
        # Log the exception details
        logging.error(f"Error in generate_data_task: {e}", exc_info=True)
        
        # Update task status to 'failed'
        DataGenerationStatus.objects.filter(process_id=process_id).update(status='failed')
        return False
    
@shared_task
def save_json_task(id):
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


        # Updtating the state added
        jsondata = Cropdatajson.objects.filter(process_id=id).update(added=0)  

        # Call to function for aggrigating the data
        aggirgatedata()
        return True

    except Exception as e:
        error_logger.error(f"errror occured in savejson --->{e}")    
        return False

