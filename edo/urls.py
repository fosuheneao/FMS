from django.urls import path
from . import views

urlpatterns = [
    #edo
    
    path('dashboard/edo/profile/', views.edo_profile_index, name='edo_profile_index'),
    
    path('dashboard/edo/price/', views.edo_price_index, name='edo_price_index'),
    path('dashboard/edo/price/create', views.edo_create_price, name='edo_create_price'),
    path('dashboard/edo/price/detail/<int:price_id>/', views.edo_price_detail, name='edo_price_detail'),
    path('dashboard/edo/price/<int:pk>/update', views.edo_price_update, name='edo_price_update'),
    
    #Forum
    #forun
    path('dashboard/edo/forum/index/', views.edo_trend_knowledge_index, name='edo_trend_knowledge_index'),
    path('dashboard/edo/forum/create/', views.edo_create_trend_knowledge, name='edo_create_trend_knowledge'),
    path('dashboard/edo/forum/<int:pk>/', views.edo_trend_knowledge_bank_detail, name='edo_trend_knowledge_bank_detail'),
    path('dashboard/edo/forum/discussion/<int:pk>/', views.edo_trend_knowledge_bank_detail, name='edo_discussion_trend_knowledge'),
    path('dashboard/edo/forum/discussion/', views.edo_trend_knowledge_board, name='edo_trend_knowledge_board'),
    
    #harvest record
    path('dashboard/edo/harvest/history/', views.edo_harvest_history, name='edo_harvest_history'),
    path('dashboard/edo/harvest/<int:beneficiary_id>/', views.edo_beneficiary_harvest, name='edo_beneficiary_harvest'),
    path('dashboard/edo/harvest/create/<int:beneficiary_id>/', views.edo_create_harvest, name='edo_create_harvest'),
    path('dashboard/edo/harvest/update/<int:harvest_id>/', views.edo_update_harvest, name='edo_update_harvest'),
    path('dashboard/edo/harvest/<int:harvest_id>/view/', views.edo_view_harvest, name='edo_view_harvest'),
    path('edo-get-price/', views.edo_get_price_for_grade_and_unit, name='edo_get_price_for_grade_and_unit'),
    path("confirm-harvest/", views.edo_confirm_harvest_ajax, name="edo_confirm_harvest_ajax"),
    # path('confirm-harvest/<int:harvest_id>/', views.confirm_harvest, name='confirm_harvest'),
    
    #path('dashboard/edo/harvest/<int:harvest_id>/view/', views.edo_view_harvest, name='edo_view_harvest'),
    #path('dashboard/edo/harvest/history/', views.edo_harvest_history, name='edo_harvest_history'),
    
    
    #crop
    path('dashboard/edo/crop/', views.edo_crop_index, name='edo_crop_index'),
    
    #Greenhouse
    path('dashboard/edo/tunnel/', views.edo_tunnel_index, name='edo_tunnel_index'),
    path('dashboard/edo/changingroom/', views.edo_changingroom_index, name='edo_changingroom_index'),     
    path('dashboard/edo/changingroom_detail/<int:pk>/', views.edo_changingroom_detail, name='edo_changingroom_detail'),

    
    #edo beneficiary
    path('get_greenhouse_rooms/<int:edo_id>/', views.get_greenhouse_rooms, name='get_greenhouse_rooms'),
    path('dashboard/edo/beneficiary/', views.edo_beneficiary_index, name='edo_beneficiary_index'),
    path('dashboard/edo/beneficiary/create', views.edo_create_beneficiary, name='edo_create_beneficiary'), 
    path('dashboard/edo/beneficiary/<int:beneficiary_id>/', views.edo_beneficiary_detail, name='edo_beneficiary_detail'), 
    path('dashboard/edo/beneficiary/update/<int:beneficiary_id>/', views.edo_update_beneficiary, name='edo_update_beneficiary'),

    
    #Financials
    path('dashboard/edo/finance/', views.edo_pricetale_index, name='edo_pricetale_index'),
    path('dashboard/edo/finance/create', views.edo_create_pricetable, name='edo_create_pricetable'),
    path('dashboard/edo/finance/update/<int:pk>/', views.edo_update_price_table, name='edo_update_price_table'),    
    path('dashboard/edo/finance/cash-requests/', views.edo_beneficiaries_cash_requests, name='edo_beneficiaries_cash_requests'),
    path('dashboard/edo/finance/repayments/', views.edo_beneficiaries_repayments, name='edo_beneficiaries_repayments'),
    path('dashboard/edo/finance/change-cash-status/<int:cash_id>/<str:status>/', views.edo_change_cash_status, name='edo_change_cash_status'),
    path('dashboard/edo/finance/change-repayment-status/<int:repayment_id>/<str:status>/', views.edo_change_repayment_status, name='edo_change_repayment_status'),
    path('dashboard/edo/finance/cashloan/', views.edo_cash_loaned_list, name='edo_cash_loaned_list'),
    path('dashboard/edo/finance/cashloandetail/<int:cashload_id>/', views.edo_cashload_detail, name='edo_cashload_detail'),
   
   
    #FARM INPUT
    path('dashboard/edo/farminput/distribute/', views.edo_create_distribute_input, name='edo_create_distribute_input'),
    path('dashboard/edo/farminput/list/', views.edo_distribution_list, name='edo_distribution_list'),
    path('dashboard/edo/farminput/stock/', views.edo_farm_input_stock, name='edo_farm_input_stock'),    
    path('dashboard/edo/farminput/beneficiary-distribution/<int:beneficiary_id>/', views.edo_beneficiary_distribution, name='edo_beneficiary_distribution'),
    
    path('edo_get_farm_input_details/', views.edo_get_farm_input_details, name='edo_get_farm_input_details'),
   

    #farm input from input dealer
    path('dashboard/edo/farminput/farm-input-list/', views.edo_farm_input_list, name='edo_farm_input_list'),
    path('dashboard/edo/farminput/add-farm-input/', views.edo_add_farm_input, name='edo_add_farm_input'),
    path('dashboard/edo/farminput/edit/<int:input_id>/', views.edo_update_farm_input, name='edo_update_farm_input'),
   
    
    #input dealer
    path('dashboard/edo/farminput/inputdealer/', views.edo_input_dealer_list, name='edo_input_dealer_list'),
    path('dashboard/edo/farminput/create_dealer/', views.edo_create_inputdealer, name='edo_create_inputdealer'),
    path('dashboard/edo/farminput/edit_inputdealer/<int:inputdealer_id>/', views.edo_update_farm_inputdealer, name='edo_update_farm_inputdealer'),
    
    #input category module url
    path('dashboard/edo/farminput/create_inputcategory/', views.edo_create_input_category, name='edo_create_input_category'),
    path('dashboard/edo/farminput/inputcategory/', views.edo_input_category_list, name='edo_input_category_list'),
    path('dashboard/edo/farminput/update_inputcategory/<int:inputcategory_id>/', views.edo_update_input_category, name='edo_update_input_category'),
    
    #buyer module
    path('dashboard/edo/buyer/', views.edo_buyer_index, name='edo_buyer_index'),
    path('dashboard/edo/buyer/create', views.edo_create_buyer, name='edo_create_buyer'), 
    path('dashboard/edo/buyer/update/<int:buyer_id>/', views.edo_update_buyer, name='edo_update_buyer'),    
    path('dashboard/edo/buyer/detail/<int:pk>/', views.edo_buyer_detail, name='edo_buyer_detail'),
    
    #EDO
    path('dashboard/edo/edo/', views.edo_edo_index, name='edo_edo_index'),
    path('dashboard/edo/edo/create', views.edo_create_edo, name='edo_create_edo'), 
    path('dashboard/edo/edo/update/<int:edo_id>/', views.edo_update_edo, name='edo_update_edo'),    
    path('dashboard/edo/edo/detail/<int:pk>/', views.edo_edo_detail, name='edo_edo_detail'),
    #farm input from input dealer
    
    # farm nursery records
    path('dashboard/edo/tunnel/nursery/', views.edo_nursery_data_index, name='edo_nursery_data_index'),
    path('dashboard/edo/tunnel/create_nursery/<int:beneficiary_id>/', views.edo_create_nursery_data, name='edo_create_nursery_data'),
    path('dashboard/edo/tunnel/update_nursery/<int:nursery_id>/', views.edo_update_nursery_data, name='edo_update_nursery_data'),
    path('get-crop-varieties/', views.get_crop_varieties, name='get_crop_varieties'),
   
     # farm plant height records
    path('dashboard/edo/tunnel/plant_height/', views.edo_height_data_index, name='edo_height_data_index'),
    path('dashboard/edo/tunnel/create_height/<int:beneficiary_id>/', views.edo_create_height_data, name='edo_create_height_data'),
    path('dashboard/edo/tunnel/update_height/<int:height_id>/', views.edo_update_height_data, name='edo_update_height_data'),
    
    # farm spraying records
    path('dashboard/edo/tunnel/spraying/', views.edo_spraying_data_index, name='edo_spraying_data_index'),
    path('dashboard/edo/tunnel/create_spraying/<int:beneficiary_id>/', views.edo_create_spraying_data, name='edo_create_spraying_data'),
    path('dashboard/edo/tunnel/update_spraying/<int:spraying_id>/<int:beneficiary_id>/', views.edo_update_spraying_data, name='edo_update_spraying_data'),
    
    
     # farm spraying records
    path('dashboard/edo/tunnel/irrigation/', views.edo_irrigation_data_index, name='edo_irrigation_data_index'),
    path('dashboard/edo/tunnel/create_irrigation/<int:beneficiary_id>/', views.edo_create_irrigation_data, name='edo_create_irrigation_data'),
    path('dashboard/edo/tunnel/update_irrigation/<int:irrigation_id>/', views.edo_update_irrigation_data, name='edo_update_irrigation_data'),
    
    
     # farm trellising records
    path('dashboard/edo/tunnel/trellising/', views.edo_trellising_data_index, name='edo_trellising_data_index'),
    path('dashboard/edo/tunnel/create_trellising/<int:beneficiary_id>/', views.edo_create_trellising_data, name='edo_create_trellising_data'),
    path('dashboard/edo/tunnel/update_trellising/<int:trellising_id>/', views.edo_update_trellising_data, name='edo_update_trellising_data'),
    
    
    
    #coworker
    path('dashboard/edo/worker/<int:pk>', views.edo_coworker_detail, name='edo_coworker_detail'),
    path('dashboard/edo/worker/<int:beneficiary_id>/create', views.edo_coworker_create, name='edo_coworker_create'),
    path('dashboard/edo/worker/<int:pk>/update', views.edo_coworker_update, name='edo_coworker_update'),
    path('dashboard/edo/worker/<int:pk>/delete', views.edo_coworker_delete, name='edo_coworker_delete'), 
    path('dashboard/edo/worker/beneficiary_coworker/<int:beneficiary_id>', views.edo_beneficiary_coworker_index, name='edo_beneficiary_coworker_index'), 
    path('dashboard/edo/worker/coworker', views.edo_coworker_index, name='edo_coworker_index'), 
    
    #Farm Cycle
    path('dashboard/edo/accounting/farmcycle/cycles', views.edo_farm_season_index, name='edo_farm_season_index'),
    path('dashboard/edo/accounting/farmcycle/create', views.edo_create_farm_season, name='edo_create_farm_season'),
    path('dashboard/edo/accounting/farmcycle/update/<int:farmseason_id>/', views.edo_update_farm_season, name='edo_update_farm_season'),
      
    
     #Service Request
    path('dashboard/edo/servicerequest/list', views.edo_service_request_index, name='edo_service_request_index'),
    path('dashboard/edo/servicerequest/request', views.edo_create_service_request, name='edo_create_service_request'),
    path('dashboard/edo/servicerequest/update_request/<int:servicerequest_id>/', views.edo_update_service_request, name='edo_update_service_request'),

    #path('dashboard/edo/servicerequest/create/', views.create_service_request, name='create_service_request'),
    path('dashboard/edo/servicerequest/<int:request_id>/edit/', views.edo_edit_service_request, name='edo_edit_service_request'),
    path('dashboard/edo/servicerequest/<int:request_id>/add-item/', views.add_service_request_item, name='add_service_request_item'),
    path('get-serviceitem-details/', views.get_serviceitem_details, name='get_serviceitem_details'),
    
     #<<<<<<<<<<<<<<=================== ACCOUNTING MODULE===============================>>>>>>>>>>>>>>>>>>>>>>>>
    path('dashboard/edo/accounting/<int:beneficiary_id>/accounting-summary/', views.edo_beneficiary_accounting_summary, name='edo_beneficiary_accounting_summary'),
    path('dashboard/edo/accounting/accounting-details/<str:category>/<int:beneficiary_id>/', views.edo_beneficiary_accounting_detail, name='edo_beneficiary_accounting_detail'),

    #<<<<<<<<<<<<<<=================== BENEFICIARY BALANCE SHEET ===============================>>>>>>>>>>>>>>>>>>>>>>>>
    path('dashboard/edo/accounting/<int:beneficiary_id>/balance-sheet/', views.edo_beneficiary_balance_sheet, name='edo_beneficiary_balance_sheet'),
    #path('dashboard/beneficiary/accounting/<int:beneficiary_id>/balance-sheet/', views.beneficiary_balance_sheet, name='beneficiary_balance_sheet'),
    
    #Equipments and Maintenance Modules
    path('dashboard/edo/equipment/', views.equipment_list, name='equipment_list'),
    path('dashboard/edo/equipment/add/', views.equipment_create, name='equipment_create'),
    path('dashboard/edo/equipment/<int:pk>/edit/', views.equipment_update, name='equipment_update'),
    path('dashboard/edo/equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    
    path('dashboard/edo/maintenance/logs/', views.maintenance_list, name='maintenance_list'),
    path('dashboard/edo/maintenance/logs/add/', views.maintenance_create, name='maintenance_create'),
    path('dashboard/edo/maintenance/logs/<int:pk>/edit/', views.maintenance_update, name='maintenance_update'),
    path('dashboard/edo/maintenance/logs/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),

]