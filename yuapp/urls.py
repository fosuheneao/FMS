from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import admin
from . import views
from . import admin_views
from . import api_views as apiviews

# Web URLs
urlpatterns = [
    path('', views.index, name='index'), 
    
    # Web Login and Logout
    path('login/', views.user_login, name='user_login'),
    # path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('logout/', views.CustomLogoutView.as_view(), name='user_logout'),

    # Web Dashboard URLs
    path('dashboard/edo/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/beneficiary/', views.beneficiary_dashboard, name='beneficiary_dashboard'),
    path('dashboard/aic/', views.aic_dashboard, name='aic_dashboard'),
    path('dashboard/buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('dashboard/sales/', views.sale_dashboard, name='sale_dashboard'),
    path('dashboard/sale_dashboard/', views.mainsale_dashboard, name='mainsale_dashboard'),
    path('dashboard/finance/', views.finance_dashboard, name='finance_dashboard'),
    
    
    path('ajax/load-crop-varieties/', admin_views.load_crop_varieties, name='ajax_load_crop_varieties'),
    
    #ADMIN PANEL URLS
    path('admin/get-cropvarieties/', admin.get_cropvarieties, name='get_cropvarieties'),
]

# API URLs (prefix with 'api/')
# API URLs (ensure they all have trailing slashes)
api_patterns = [
    # User Login and Logout API
    path('api/login/', apiviews.user_login, name='user_login'), # POST /api/login/
    path('api/logout/', apiviews.custom_logout, name='custom_logout'), # POST /api/logout/

    # Supervisor, Beneficiary, AIC, and Buyer Dashboard APIs
    path('api/supervisor/dashboard/', apiviews.supervisor_dashboard, name='supervisor_dashboard'), # GET /api/supervisor/dashboard/
    path('api/beneficiary/dashboard/', apiviews.beneficiary_dashboard, name='beneficiary_dashboard'),  # GET /api/beneficiary/dashboard/
    path('api/aic/dashboard/', apiviews.aic_dashboard, name='aic_dashboard'),  # GET /api/aic/dashboard/
    path('api/buyer/dashboard/', apiviews.buyer_dashboard, name='buyer_dashboard'),  # GET /api/buyer/dashboard/

    # Trend Knowledge APIs
    path('api/trend-knowledge/', apiviews.trend_knowledge_index, name='trend_knowledge_index'),  # GET, POST /api/trend-knowledge/
    path('api/trend-knowledge/<int:pk>/', apiviews.trend_knowledge_bank_detail, name='trend_knowledge_bank_detail'),  # GET /api/trend-knowledge/<pk>/
    path('api/trend-knowledge/discussion/<int:pk>/', apiviews.discussion_trend_knowledge, name='discussion_trend_knowledge'), # GET, POST /api/trend-knowledge/discussion/<pk>/
    path('api/trend-knowledge/create/', apiviews.create_trend_knowledge, name='create_trend_knowledge'), # POST /api/trend-knowledge/create/
    path('api/trend-knowledge/board/', apiviews.trend_knowledge_board, name='trend_knowledge_board'),  # GET /api/trend-knowledge/board/

    # Crop, Tunnel, Changing Room APIs
    path('api/crop/', apiviews.crop_index, name='crop_index'), # GET /api/crops/
    path('api/tunnel/', apiviews.tunnel_index, name='tunnel_index'), # GET /api/tunels/
    path('api/changing-room/', apiviews.changingroom_index, name='changingroom_index'),  # GET /api/changingrooms/
    path('api/changing-room/<int:pk>/', apiviews.changingroom_detail, name='changingroom_detail'), # GET /api/changingrooms/<pk>/

    # Buyer APIs
    path('api/buyer/', apiviews.buyer_index, name='buyer_index'),  # GET /api/buyers/
    path('api/buyer/<int:pk>/', apiviews.buyer_detail, name='buyer_detail'), # GET /api/buyers/<pk>/

    # Finance APIs
    path('api/finance/', apiviews.finance_index, name='finance_index'), # GET /api/finance/
    path('api/finance/request-cash/', apiviews.request_cash, name='request_cash'), # POST /api/finance/request-cash/
    path('api/finance/submit-repayment/<int:cash_assigned_id>/', apiviews.submit_repayment, name='submit_repayment'),  # POST /api/finance/submit-repayment/<cash_assigned_id>/
    path('api/finance/payment-history/', apiviews.finance_payment_history, name='finance_payment_history'), # GET /api/finance/payment-history/

    # Harvest APIs
    path('api/harvest/', apiviews.harvest_index, name='harvest_index'), # GET /api/harvests/
    path('api/harvest/assigned/<int:beneficiary_id>/<int:crop_id>/', apiviews.assigned_crops_and_harvests, name='assigned_crops_and_harvests'), # GET /api/assigned-crops/<beneficiary_id>/<crop_id>/
    path('api/harvest/create/<int:crop_assigned_id>/', apiviews.create_harvest, name='create_harvest'),  # GET /api/harvest/create/<crop_id>/
 
    # Sales Dashboard API
    path('api/sales/dashboard/', apiviews.sales_dashboard, name='sales_dashboard'), # GET /api/sales-dashboard/

    # EDO APIs
    path('api/edo/', apiviews.edo, name='edo'),  # GET /api/edo/
    path('api/edo/<int:edo_id>/', apiviews.edo_detail, name='edo_detail'),  # GET /api/edo/<edo_id>/
]
# Include this in your main urls.py file

# Combine both web and api patterns
urlpatterns += [
    path('api/', include((api_patterns, 'api'))),  # Include API routes with the 'api/' prefix
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
