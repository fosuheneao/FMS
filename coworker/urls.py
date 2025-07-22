from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import *

urlpatterns = [
    #Beneficiary module route
    path('dashboard/beneficiary/worker', coworker_index, name='beneficiary_coworker'),
     path('dashboard/beneficiary/profile', beneficiary_profile, name='beneficiary_profile'),
     
    #coworker
    path('dashboard/beneficiary/worker/<int:pk>', coworker_detail, name='coworker_detail'),
    path('dashboard/beneficiary/worker/create', coworker_create, name='coworker_create'),
    path('dashboard/beneficiary/worker/<int:pk>/update', coworker_update, name='coworker_update'),
    path('dashboard/beneficiary/worker/<int:pk>/delete', coworker_delete, name='coworker_delete'), 
      
    
    # path('logout', LogoutView.as_view(), name='logout'),
    # path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)