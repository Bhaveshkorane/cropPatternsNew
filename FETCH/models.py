from django.db import models

# # Create your models here.

class State(models.Model):
    statecode = models.IntegerField(primary_key=True,default=0)
    englishname = models.CharField(max_length=300,null=True,blank=True)
    localname = models.CharField(max_length=300,null=True,blank=True)
    statecreated = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    stateupdated = models.DateTimeField(auto_now=True,null=True,blank=True)
    
class District(models.Model):
    districtcode = models.IntegerField(primary_key=True,default=1)
    englishname = models.CharField(max_length=200,blank=True,null=True)
    localname = models.CharField(max_length=200,blank=True,null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE,default=0,null=True,blank=True)
    districtcreated = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    districtupdated = models.DateTimeField(auto_now=True,null=True,blank=True)


class Subdistrict(models.Model):
    subdistrictcode = models.IntegerField(primary_key=True,default=2)
    englishname = models.CharField(max_length=200,null=True,blank=True)
    localname = models.CharField(max_length=200,null=True,blank=True)
    district = models.ForeignKey(District,on_delete=models.CASCADE,default=1121,blank=True,null=True)          
    subdistrictcreated = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    subdistrictupdated = models.DateTimeField(auto_now=True,blank=True,null=True)
    state = models.IntegerField(null=True,blank=True,default=0)                                                 

from django.db import models

class Village(models.Model):
    villagecode = models.IntegerField(primary_key=True, default=3)
    englishname = models.CharField(max_length=200, null=True, blank=True)
    localname = models.CharField(max_length=200, null=True, blank=True)
    subdistrict = models.ForeignKey(Subdistrict, on_delete=models.CASCADE, default=12342, blank=True, null=True)                 
    villagecreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    villageupdated = models.DateTimeField(auto_now=True, blank=True, null=True)
    state = models.ForeignKey('State', null=True, blank=True, default=None, on_delete=models.CASCADE)
    district = models.ForeignKey('District', null=True, blank=True, default=None, on_delete=models.CASCADE)



class Crop(models.Model):
    cropname = models.CharField(max_length=200) 


class Cropdatajson(models.Model):
    cropdata = models.JSONField(null=True, blank=True, default=None)
    added = models.IntegerField(null=True, blank=True, default=0)
    district = models.CharField(null=True, blank=True, default=None)
    process_id = models.CharField(null=True, blank=True)
    added_time = models.CharField(null=True, blank=True)
    crop_type = models.CharField(null=True, blank=True)


class Cropdetails(models.Model):
    
    # Crop details 
    unique_id = models.CharField(max_length=100,primary_key=True)
    area_cultivated = models.IntegerField(null=True,blank=True)
    crop_type = models.CharField(max_length=100,null=True,blank=True)
    yeild_perhectare = models.IntegerField(null=True,blank=True)
    soil_type = models.CharField(max_length=50,null=True,blank=True)
    irrigation_method = models.CharField(max_length=100,null=True,blank=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True,blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE,null=True,blank=True,default=27)
    district = models.ForeignKey(District,on_delete=models.CASCADE,null=True,blank=True,default=480)
    subdistrict = models.ForeignKey(Subdistrict,on_delete=models.CASCADE,null=True,blank=True,default=3648)

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



class Aggridata(models.Model):
    state = models.CharField(max_length=200,  null=True, blank=True)
    district = models.CharField(max_length=200, null=True, blank=True)
    crop = models.CharField(max_length=100,null=True,blank=True)
    area_cultivated = models.IntegerField(null=True,blank=True)







    



