from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
import requests
from rest_framework.response import Response 

# Importing models 
from .models import State
from .models import Subdistrict
from .models import Village
from .models import District
from .models import Crop
from .models import Cropdatajson
from .models import Cropdetails
from .models import Aggridata   


# uuid for generting the unique id 
import uuid 

# Importing serializers 
from .serializers import VillageSerializer
from .serializers import StateSerializer
from .serializers import DistrictSerializer


from django.views import View

# For messages 
from django.contrib import messages

#for .env file
from decouple import config


# For user creation and login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# Aggrigation functions
from django.db.models import Sum

# For time stamp
import time
from datetime import datetime


# For downloading the pdf file 
from django.http import FileResponse
import io
from io import StringIO
from django.http import FileResponse

# from rest_framework.decorators import api_view
from rest_framework.views import APIView

import random

# Importing loggers 
import logging
error_logger = logging.getLogger('error_logger')
info_logger = logging.getLogger('django')
warning_logger = logging.getLogger('warning_logger')
debug_logger = logging.getLogger('dubug_logger')

# For downloading pdf file 
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from .models import Aggridata



def createstate(request):
    try:
        count=0
        stateData = requests.post(config('state_api')).json()
        for i in stateData:
            state_code=i['stateCode']
            english_name=i['stateNameEnglish']
            local_name=i['stateNameLocal']
            data=State(
                        statecode=state_code,
                        englishname=english_name,
                        localname=local_name
                        )
            data.save()
            count += 1

        return HttpResponse(f"hello bhavesh you have added {count} states into the database")
    except Exception as e:            
        error_logger.error(f"errror occured in createstate --->{e}")
        return HttpResponse(f"The error occured {e}")




# Inserting data into district table

def createdistrict(request):
    try:
        dcount = 0
        state_data=State.objects.all()
        for i in state_data:
            id_=i.statecode


            # Fetching the data from API
            # query='https://lgdirectory.gov.in/webservices/lgdws/districtList?stateCode='+str(id_)
            # query=f'https://lgdirectory.gov.in/webservices/lgdws/districtList?stateCode={id_}'
            query=config('district_api_link')+str(id_)
            district_data = requests.post(query).json()

            #creating the state instance for passing as foreign key
            state_=State()
            state_.statecode=id_
        
            for dist in district_data:
                district_code = dist['districtCode']
                if District.objects.filter(districtcode=district_code).exists():
                    dcount += 1
                    continue
                english_name = dist['districtNameEnglish']
                district_name = dist['districtNameLocal']           
                dData=District(
                                districtcode = district_code,
                                englishname= english_name,
                                localname= district_name,
                                state = state_
                                )
                dData.save()
                dcount += 1

        return HttpResponse(f"hello bhavesh you have added {dcount} data into the districts")
    except Exception as e:
            error_logger.error(f"errror occured in createdistrict--->{e}")
            return HttpResponse(f"The error occured {e}")



# Adding the subdistricts to the data 
""" the data for only 
1.maharashtra 
2.MP
3.Rajastan
4.Uttarpradesh
we are going to add
"""

def createsubdistrict(request):
    try:
        sdcount = 0
        state_ids = [23, 27, 9, 8]

        for id_ in state_ids:
            # Retrieve all districts for the current state id
            districts = District.objects.filter(state=id_)

            for district in districts:
                dist_id = district.districtcode
                #query = f'https://lgdirectory.gov.in/webservices/lgdws/subdistrictList?districtCode={dist_id}'
                query = config('subdistrict_api_link')+str(dist_id)
                response = requests.post(query)
                subdistrict_data = response.json()
        
                for subd in subdistrict_data:
                    sdcount += 1
                    subdistrict_code = subd['subdistrictCode']
                    if Subdistrict.objects.filter(subdistrictcode=subdistrict_code).exists():
                        continue
                    english_name = subd['subdistrictNameEnglish']
                    local_name = subd['subdistrictNameLocal']

                    sd_data = Subdistrict(
                        subdistrictcode=subdistrict_code,
                        englishname=english_name,
                        localname=local_name,
                        district=district,
                    )
                    sd_data.save()
        return HttpResponse(f"You have added a total of {sdcount} subdistricts into the table")
    except Exception as e:
            error_logger.error(f"errror occured in createsubdistrict--->{e}")
            return HttpResponse(f"The error occured {e}")

def createvillage(request):
    try:
        vcount = 0
        subdistrict_data = Subdistrict.objects.all()

        for subdistrict in subdistrict_data:
            subdistrict_id = subdistrict.subdistrictcode

            # Taking village Data from API
            #query = f'https://lgdirectory.gov.in/webservices/lgdws/villageList?subDistrictCode={subdistrict_id}'
            query = config('village_api_link')+str(subdistrict_id)

            response = requests.post(query)
            village_data = response.json()


            for village in village_data:
                vcount += 1
                village_code=village['villageCode']
                if Village.objects.filter(villagecode =  village_code).exists():
                    continue
                english_name = village['villageNameEnglish']
                local_name = village['villageNameLocal']

                v_data = Village(
                    villagecode = village_code,
                    englishname = english_name,
                    localname = local_name,
                    subdistrict = subdistrict
                )

                v_data.save()
        return HttpResponse(f"Total {vcount} number of villages are added into the table")
    except Exception as e:
            error_logger.error(f"errror occured in createvillage--->{e}")
            return HttpResponse(f"The error occured {e}")       




class DistrictGeneric(APIView):
    try:
        def get(self,request):
            id_=request.GET.get('id')
            district_obj = District.objects.filter(state_id=id_)
            serializer = District(district_obj,many=True)
            return Response({"status:":200,"payload":serializer.data})
    except Exception as e:
        error_logger.error(f"error occured in DistrictGeneric--->{e}")
    

class VillageGeneric(APIView):
    try:
        def get(self, request):
            village_obj = Village.objects.filter(subdistrict_id=461)
            serializer = VillageSerializer(village_obj, many=True)
            return Response({"status": 200, "payload": serializer.data})
    except Exception as e:
        error_logger.error(f"error occuredVillageGeneric--->{e}")

class StateGeneric(APIView):
    try:
        def get(self, request):
            state_obj = State.objects.filter()
            serializer = StateSerializer(state_obj, many=True)
            return Response({"status": 200, "payload": serializer.data})
    except Exception as e:
        error_logger.error(f"error occured StateGeneric--->{e}")


# Here we are doing it for drop down menu
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def state(request):
    try:
        states = State.objects.all()
        crops =Crop.objects.all().order_by('cropname')
        jsondata = Cropdatajson.objects.order_by('process_id').distinct('process_id').exclude(added=0)
        data = Aggridata.objects.distinct('district')
        
        context = {'states': states,'crops':crops,'notupdated':jsondata,"data":data}
        return render(request, 'states.html', context)
    except Exception as e:
            error_logger.error(f"errror occured state --->{e}")
            messages.info(request,f" Exception occured {e}")
            return render(request,'states.html')


def district(request):
    try:
        state = request.GET.get('state')
        dist = District.objects.filter(state_id=state)
        context = {'districts': dist}
        return render(request, 'partials/district.html', context)
    except Exception as e:
            error_logger.error(f"errror occured district--->{e}")
            messages.info(request,f" Exception occured {e}")
            return render(request, 'partials/district.html')


def subdistrict(request):
    logger = logging.getLogger('django')
    try:
        dist = request.GET.get('district')
        subdistrict = Subdistrict.objects.filter(district_id=dist)
        context = {'subdistricts': subdistrict}
        return render(request, 'partials/subdistrict.html', context)
    except Exception as e:
            logger.error(f"errror occured in subdistrict --->{e}")
            messages.info(request,f" Exception occured {e}")
            return render(request, 'partials/district.html')

# def village(request):
#     subdistrict = request.GET.get('subdistrict')
#     village = Village.objects.filter(subdistrict_id=subdistrict)
#     context = {'villages': village}
#     return render(request, 'partials/village.html', context)


# Api for generating random data 

class GenerateDataView(View):
    def post(self, request):

        try:
            start_time = time.time() #for testing 
            process_id = uuid.uuid4()
            added_time = str(datetime.now())
            
            district = request.POST.get('district')
            
            crop = request.POST.get('crop') 
        
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
            end_time = time.time()

            total_time=end_time-start_time
                        
            messages.success(request, f"Total time taken for data generation = {total_time:.2f}")

            return redirect('/queue/')
        except Exception as e:
            error_logger.error(f"errror occured in GenerateDataView --->{e}")
            messages.info(request,f" Exception occured {e}")
            return redirect('/queue/')

        

    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def savejson(request,id):
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

        messages.success(request,"Crop Details saved successfully ")  

        # Updtating the state added
        jsondata = Cropdatajson.objects.filter(process_id=id).update(added=0)  

        # Call to function for aggrigating the data
        aggirgatedata()

        return redirect('/queue/')
        return HttpResponse("the data you have fetched successfully ")
    except Exception as e:
        error_logger.error(f"errror occured in savejson --->{e}")
        messages.info(request,f" Exception occured {e}")
        return redirect('/queue/')

        


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



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def viewdata(request):
    logger1 = logging.getLogger('info')
    try:
        data = Aggridata.objects.distinct('district')

        context = {"data":data}
        logger1.info(f"you viewed the data------------------------------------------------------------>")

        return render(request, 'data.html', context)
    except Exception as e:
        error_logger.error(f"errror occured in viewdata--->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'data.html')

        
    

# Queue avaliable for extraction 

@login_required(login_url="/login/")
def queue(request):
    try:
        jsondata = Cropdatajson.objects.order_by('process_id').distinct('process_id').exclude(added=0)
        context = {'notupdated':jsondata,}
        return render(request,'quedjson.html',context)
    except Exception as e:
        error_logger.error(f"errror occured in queue --->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'quedjson.html')
    
#working view 

@login_required(login_url="/login/")
def showdistricttables(request,id):
    try:
        data = Aggridata.objects.filter(district=id)
        # state_name = Aggridata.objects.get(district=id).distinct('state').state
        state_names = Aggridata.objects.filter(district=id).values_list('state', flat=True).distinct().order_by('district')
        context={"data":data,"state":state_names[0],"district":id}
        
        return render(request,'distdata.html',context)
    except Exception as e:
        error_logger.error(f"errror occured in showdistricttables --->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'distdata.html')


@login_required(login_url="/login/")
def showhistory(request):
    try:
        jsondata = Cropdatajson.objects.order_by('process_id').distinct('process_id')
        context = {'history':jsondata}
        return render(request,'history.html',context)
    except Exception as e:
        error_logger.error(f"errror occured in showhistory --->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'history.html')
    


def gen_pdf(request, id):
    response = FileResponse(generate_pdf_file(id),
                            as_attachment=True,
                            filename='Data.pdf',
                            content_type='application/pdf')
    return response

def generate_pdf_file(id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Fetch data
    data = Aggridata.objects.filter(district=id)
  
    # Title and Header
    title = Paragraph(f"State:{data[0].state} district:{data[0].district} ")
    elements.append(title)

    # Table Data
    table_data = [['Sr. No', 'Crop', 'Total Area Under Cultivation (ha)']]
    for i, dt in enumerate(data, start=1):
        table_data.append([i, dt.crop, dt.area_cultivated])

    table = Table(table_data)
    elements.append(table)

    # Build the PDF
    doc.build(elements)

    buffer.seek(0)
    return buffer
