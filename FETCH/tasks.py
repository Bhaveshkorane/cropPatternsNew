from celery import shared_task
import requests
import uuid
from datetime import datetime
from django.conf import settings
from .models import Cropdatajson, Crop, District, Subdistrict, Village
import logging

error_logger = logging.getLogger(__name__)

@shared_task
def generate_data_task(village_name, crop_name, village_code, district_name, process_id, district, added_time):
    try:
        api_url = settings.DATA_GENERATOR_API  # Assuming you're using Django settings for configuration
        api_response = requests.get(api_url, data={'village': village_name, 'crop': crop_name, 'village_code': village_code})
        
        if api_response.status_code == 200:
            data = api_response.json().get('payload')
        else:
            data = None

        dt = Cropdatajson(cropdata=data,
                          added=district,
                          district=district_name,
                          process_id=process_id,
                          added_time=added_time,
                          crop_type=crop_name
                          )
        dt.save()
    except Exception as e:
        error_logger.error(f"Error occurred in generate_data_task: {e}")
        raise e
