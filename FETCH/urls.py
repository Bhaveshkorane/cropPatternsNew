from django.urls import path
from django.views.generic.base import RedirectView

# # Imports for creting/inserting the data into database 
from .views import create_state
from .views import create_district
from .views import create_subdistrict
from .views import create_village

# # Imports for API's
from .views import VillageGeneric
from .views import StateGeneric
from .views import DistrictGeneric
from .views import SubdistrictGeneric

# Imports from views 
from .views import state
from .views import district
from .views import subdistrict
# from .views import village
# from .views import crops
from .views import viewdata
from .views import showdistricttables
from .views import showhistory
from .views import gen_pdf
from .views import GenerateDataView  
# Downloading the pdf 



# From .utils 
from .utils import generatedata



urlpatterns = [

    # For inserting data into database 
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('createstate/',create_state,name='createstate_url'),
    path('createdistrict/',create_district,name='createdistrict_url'),
    path('createsubdistrict/',create_subdistrict,name='createsubdistrict_url'),
    path('createvillage/',create_village,name='createvillage_url'),

    
    # # For fetching data from the database through api 
    path('generic-village/',VillageGeneric.as_view()),
    path('generic-state/',StateGeneric.as_view()),
    path('generic-district/',DistrictGeneric.as_view()),
    path('generic-subdistrict/',SubdistrictGeneric.as_view()),

    
    path('generate-data/', GenerateDataView.as_view(), name='generate_data_view'),
    path('gene/',generatedata.as_view()),


    path('home/',state,name='home_url'),
    path('district/',district,name='district_url'),
    path('subdistrict/',subdistrict,name='subdistrict_url'),
    # path('village/',village,name='village_url'),
    path('viewdata/',viewdata,name='viewdata_url'),
    path('showdistricttable/<district_name>/',showdistricttables,name='showdistricttables_url'),
    path('showhistory/',showhistory,name='history_url'),


    path('genpdf/<district_name>/',gen_pdf,name="genpdf_url"),

   
]

