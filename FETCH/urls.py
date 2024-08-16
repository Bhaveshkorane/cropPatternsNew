from django.urls import path
from django.views.generic.base import RedirectView

# Imports for creting/inserting the data into database 
from .views import createstate
from .views import createdistrict
from .views import createsubdistrict
from .views import createvillage

# Imports for API's
from .views import VillageGeneric
from .views import StateGeneric
from .views import DistrictGeneric

# Imports from views 
from .views import state
from .views import district
from .views import subdistrict
# from .views import village
# from .views import crops
from .views import savejson
from .views import viewdata
from .views import queue
from .views import showdistricttables
from .views import showhistory
from .views import gen_pdf
from .views import GenerateDataView  

# Downloading the pdf 



# From utils 
from .utils import generatedata



urlpatterns = [

    # For inserting data into database 
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('createstate/',createstate,name='createstate_url'),
    path('createdistrict/',createdistrict,name='createdistrict_url'),
    path('createsubdistrict/',createsubdistrict,name='createsubdistrict_url'),
    path('createvillage/',createvillage,name='createvillage_url'),

    
    # For fetching data from the database through api 
    path('generic-village/',VillageGeneric.as_view()),
    path('generic-state/',StateGeneric.as_view()),
    path('generic-distirct/',DistrictGeneric.as_view()),
    path('generate-data/', GenerateDataView.as_view(), name='generate_data_view'),
    path('gene/',generatedata.as_view()),


    path('home/',state,name='home_url'),
    path('district/',district,name='district_url'),
    path('subdistrict/',subdistrict,name='subdistrict_url'),
    # path('village/',village,name='village_url'),
    path('savejson/<id>/',savejson,name='savejson_url'),
    path('viewdata/',viewdata,name='viewdata_url'),
    path('showdistricttable/<id>/',showdistricttables,name='showdistricttables_url'),
    path('showhistory/',showhistory,name='history_url'),


    path('queue/',queue,name='queue_url'),
    path('genpdf/<id>/',gen_pdf,name="genpdf_url"),

     
]

