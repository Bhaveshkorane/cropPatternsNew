from django.db import models

# # Create your models here.

class State(models.Model):
    state_code = models.IntegerField(primary_key=True)
    english_name = models.CharField(max_length=300,null=True,blank=True)
    local_name = models.CharField(max_length=300,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    
class District(models.Model):
    district_code = models.IntegerField(primary_key=True)
    english_name = models.CharField(max_length=200,blank=True,null=True)
    local_name = models.CharField(max_length=200,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE,null=True,blank=True)



class Subdistrict(models.Model):
    subdistrict_code = models.IntegerField(primary_key=True)
    english_name = models.CharField(max_length=200,null=True,blank=True)
    local_name = models.CharField(max_length=200,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True) 
    updated_at = models.DateTimeField(auto_now=True,blank=True,null=True)     
    district = models.ForeignKey(District,on_delete=models.CASCADE,blank=True,null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE,null=True,blank=True)         
          
                                        


class Village(models.Model):
    village_code = models.IntegerField(primary_key=True)
    english_name = models.CharField(max_length=200, null=True, blank=True)
    local_name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    subdistrict = models.ForeignKey(Subdistrict, on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)






class Crop(models.Model):
    name = models.CharField(max_length=200) 


class CropDataJson(models.Model):
    crop_data = models.JSONField(null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    state_name = models.CharField(max_length=255, null=True, blank=True)
    process_id = models.CharField(max_length=255, null=True, blank=True)
    added_time = models.CharField(max_length=255, null=True, blank=True)
    crop_type = models.CharField(max_length=255, null=True, blank=True)

class CropDetails(models.Model):
    
    # Crop details 
    unique_id = models.CharField(max_length=100,primary_key=True)
    area_cultivated = models.IntegerField(null=True,blank=True)
    crop_type = models.CharField(max_length=100,null=True,blank=True)
    yeild_perhectare = models.IntegerField(null=True,blank=True)
    soil_type = models.CharField(max_length=50,null=True,blank=True)
    irrigation_method = models.CharField(max_length=100,null=True,blank=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True,blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE,null=True,blank=True)
    district = models.ForeignKey(District,on_delete=models.CASCADE,null=True,blank=True)
    subdistrict = models.ForeignKey(Subdistrict,on_delete=models.CASCADE,null=True,blank=True)

    # Weather data 
    temp_min = models.IntegerField(null=True,blank=True)
    temp_max = models.IntegerField(null=True,blank=True)
    temp_avg = models.IntegerField(null=True,blank=True)
    rainfall_total = models.IntegerField(null=True,blank=True)
    rainfall_rainy_days = models.IntegerField(null=True,blank=True)
    humidity = models.IntegerField(null=True,blank=True)

    # Fertilizers 
    fertilizer_NPK_kg = models.IntegerField(null=True,blank=True)
    fertilizer_COMPOST_kg = models.IntegerField(null=True,blank=True)


    # Pesticides 
    pesticide_type = models.CharField(max_length=100,null=True,blank=True)
    pesticide_quantity_l = models.IntegerField(null=True,blank=True)

    process_id = models.CharField(max_length=255, null=True, blank=True)



class AggregationData(models.Model):
    state_name = models.CharField(max_length=200,  null=True, blank=True)
    district_name = models.CharField(max_length=200, null=True, blank=True)
    crop_type = models.CharField(max_length=100,null=True,blank=True)
    area_cultivated = models.IntegerField(null=True,blank=True)



class ProcessStatus(models.Model):
    district_name = models.CharField(max_length=255,null=True,blank=True)
    state_name = models.CharField(max_length=255,null=True,blank=True)
    process_id = models.CharField(max_length=255,null=True, blank=True)
    crop_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    is_generating = models.BooleanField(default=False)
    is_extracting = models.BooleanField(default=False)
    is_aggregating = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
