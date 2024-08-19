from celery import shared_task
import uuid
from .models import Cropdatajson
from .models import District
from .models import Subdistrict
from .models import Village
from .models import Crop
from .models import DataGenerationStatus
from datetime import datetime
import requests
from decouple import config


# Importing loggers 
import logging
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('django')
warning_logger = logging.getLogger('warning_logger')
debug_logger = logging.getLogger('dubug_logger')


@shared_task
def generate_data_task(district, crop):
    print(district,crop,"this is called generation----->")
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
                        print("got the payload")
                        error_logger.error(f"the data is genereatd with 200 code {data}")
                    else:
                        print("didnt got the payload got the payload")
                        error_logger.error(f"the data is genereatd with 200 code {data}")

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
