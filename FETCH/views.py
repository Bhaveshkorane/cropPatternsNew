import requests
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from rest_framework.response import Response 
from django.views import View


# Importing models 
from .models import State
from .models import Subdistrict
from .models import Village
from .models import District
from .models import Crop
from .models import Aggridata   
from .models import Process_status

# uuid for generting the unique id 
import uuid 

# Importing serializers 
from .serializers import VillageSerializer
from .serializers import StateSerializer
from .serializers import DistrictSerializer
from .serializers import SubdistrictSerializer

# For messages 
from django.contrib import messages

# For .env file
from decouple import config


# For user creation and login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# For downloading the pdf file 
from django.http import FileResponse
import io
from io import StringIO
from django.http import FileResponse

# from rest_framework.decorators import api_view
from rest_framework.views import APIView

# For randaom value generation
import random

# Importing loggers 
import logging
generation_logger = logging.getLogger('generation_logger')
extraction_logger = logging.getLogger('extraction_logger')
aggregation_logger = logging.getLogger('aggregation_logger')
error_logger = logging.getLogger('error_logger')

# For downloading pdf file 
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from .models import Aggridata

# Imports for Tasks 
from .tasks import generate_data_task
from .tasks import save_json_task

# For chaining 
from celery import chain

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
            state= request.GET.get('id')
            district_obj = District.objects.filter(state_id=state)
            serializer = DistrictSerializer(district_obj,many=True)
            return Response({"status:":200,"payload":serializer.data})
    except Exception as e:
        error_logger.error(f"error occured in DistrictGeneric--->{e}")

class SubdistrictGeneric(APIView):
    try:
        def get(self,request):
            district= request.GET.get('id')
            district_obj = Subdistrict.objects.filter(district_id=district)
            serializer = SubdistrictSerializer(district_obj,many=True)
            return Response({"status:":200,"payload":serializer.data})
    except Exception as e:
        error_logger.error(f"error occured in DistrictGeneric--->{e}")

class VillageGeneric(APIView):
    try:
        def get(self, request):
            subdistrict = request.GET.get('id')
            village_obj = Village.objects.filter(subdistrict_id=subdistrict)
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
        process_status = Process_status.objects.all().exclude(is_completed=True) 
        # process_status = Process_status.objects.all()   
           
        context = {'states': states,'crops':crops,"process_status":process_status}
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


# For parallel processing and chaining

class GenerateDataView(View):
    def post(self, request):
        try:
            district = request.POST.get('district')
            crop = request.POST.get('crop')
            process_id = uuid.uuid4()       

            # Chain the tasks for ensuring save_json_task runs after generate_data_task completes
            task_chain = chain(
                generate_data_task.s(district, crop, process_id),
                save_json_task.s(process_id)
            )

            task_chain.apply_async()

            messages.success(request, "Data generation has been started in the background.")
            return redirect('/home/')
        except Exception as e:
            generation_logger.error(f"Error in GenerateDataView: {e}")
            messages.info(request, f"Exception occurred: {e}")
            return redirect('/home/')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def viewdata(request):
    try:
        data = Aggridata.objects.all().distinct('district')

        context = {"data":data}
        return render(request, 'data.html', context)
    except Exception as e:
        error_logger.error(f"errror occured in viewdata--->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'data.html')

        
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/login/")
def showhistory(request):
    try:
        jsondata = Process_status.objects.all().order_by('timestamp')
        context = {'history':jsondata}
        return render(request,'history.html',context)
    except Exception as e:
        error_logger.error(f"errror occured in showhistory --->{e}")
        messages.info(request,f" Exception occured {e}")
        return render(request, 'history.html')
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gen_pdf(request, id):
    try:
        response = FileResponse(generate_pdf_file(id),
                                as_attachment=True,
                                filename='Data.pdf',
                                content_type='application/pdf')
        return response
    except Exception as e:
        error_logger.error(f"error occured in gen_pdf--->{e}")

def generate_pdf_file(id):
    try:

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # For fetchching the data for pdf 
        data = Aggridata.objects.filter(district=id)
    
        # For Title and the header 
        title = Paragraph(f"State:{data[0].state} district:{data[0].district} ")
        elements.append(title)

        # For table data
        table_data = [['Sr. No', 'Crop', 'Total Area Under Cultivation (ha)']]
        for i, dt in enumerate(data, start=1):
            table_data.append([i, dt.crop, dt.area_cultivated])

        table = Table(table_data)
        elements.append(table)

        # For building the pdf 
        doc.build(elements)

        buffer.seek(0)
        return buffer
    
    except Exception as e:
        error_logger.error(f"Error occoured in pdf generate_pdf_file function---->{e}")
