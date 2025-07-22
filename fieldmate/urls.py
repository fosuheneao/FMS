from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/beneficiary/forum/index/', views.trend_knowledge_index, name='trend_knowledge_index'),
    path('dashboard/beneficiary/forum/create/', views.create_trend_knowledge, name='create_trend_knowledge'),
    path('dashboard/beneficiary/forum/<int:pk>/', views.trend_knowledge_bank_detail, name='trend_knowledge_bank_detail'),
    path('dashboard/beneficiary/forum/discussion/<int:pk>/', views.trend_knowledge_bank_detail, name='discussion_trend_knowledge'),
    
    path('dashboard/beneficiary/forum/discussion/', views.trend_knowledge_board, name='trend_knowledge_board'),
    path('dashboard/beneficiary/crop/', views.crop_index, name='crop_index'),
    path('dashboard/beneficiary/tunnel/', views.tunnel_index, name='tunnel_index'),
    path('dashboard/beneficiary/changingroom/', views.changingroom_index, name='changingroom_index'),     
    path('dashboard/beneficiary/changingroom_detail/<int:pk>/', views.changingroom_detail, name='changingroom_detail'),

    path('dashboard/beneficiary/buyer/', views.buyer_index, name='buyer_index'),
    path('dashboard/beneficiary/buyer_detail/<int:pk>/', views.buyer_detail, name='buyer_detail'),
    
    #contract models
    path('dashboard/beneficiary/worker/contracts', views.list_contracts, name='contracts'),
    # path('dashboard/beneficiary/worker/create/', views.create_contract, name='create_contract'),
    path('dashboard/beneficiary/workers/<int:worker_id>/create-contract/', views.create_contract, name='create_contract'),
    path('dashboard/beneficiary/worker/<int:contract_id>/update/', views.update_contract, name='update_contract'),

    
    #Finance Model    
    path('dashboard/beneficiary/finance/', views.finance_index, name='finance_index'),
    #path('beneficiary/finance/payment_history/', views.finance_payment_history, name='finance_payment_history'),
    path('dashboard/beneficiary/finance/request-cash/', views.request_cash, name='request_cash'),
    path('dashboard/beneficiary/finance/repayment/<int:cash_assigned_id>/', views.submit_repayment, name='submit_repayment'),    
    path('dashboard/beneficiary/finance/payment_history/<int:cash_assigned_id>/', views.cash_assigned_detail, name='cash_assigned_detail'),    
    path('dashboard/beneficiary/finance/payment_history/', views.cash_assigned_payment_history, name='cash_assigned_payment_history'),
    path('dashboard/beneficiary/finance/income/', views.beneficiary_income, name='beneficiary_income'),
      
    #<<<<<<<<<<<<<<=================== ACCOUNTING MODULE===============================>>>>>>>>>>>>>>>>>>>>>>>>
    path('dashboard/beneficiary/accounting/<int:beneficiary_id>/accounting-summary/', views.beneficiary_accounting_summary, name='beneficiary_accounting_summary'),
    path('dashboard/beneficiary/accounting/accounting-details/<str:category>/<int:beneficiary_id>/', views.beneficiary_accounting_detail, name='beneficiary_accounting_detail'),

    #<<<<<<<<<<<<<<=================== BENEFICIARY BALANCE SHEET ===============================>>>>>>>>>>>>>>>>>>>>>>>>
    path('dashboard/beneficiary/accounting/balance-sheet/', views.beneficiary_balance_sheet, name='beneficiary_balance_sheet'),
    #path('dashboard/beneficiary/accounting/<int:beneficiary_id>/balance-sheet/', views.beneficiary_balance_sheet, name='beneficiary_balance_sheet'),
    
    
    #Farm Input Costing Model    
    path('dashboard/beneficiary/finance/inputcosting/', views.farm_input_index, name='farm_input_index'),
    # path('dashboard/beneficiary/finance/request-cash/', views.request_cash, name='request_cash'),
    # path('dashboard/beneficiary/finance/repayment/<int:cash_assigned_id>/', views.submit_repayment, name='submit_repayment'),    
    path('dashboard/beneficiary/finance/inputcosting/<int:farm_input_assigned_id>/', views.farm_input_assigned_detail, name='farm_input_assigned_detail'),
    
    #Harvest    
    path('dashboard/beneficiary/harvest/', views.harvest_index, name='harvest_index'), 
    path('dashboard/beneficiary/harvest/record/<int:beneficiary_id>/<int:crop_id>/', views.assigned_crops_and_harvests, name='assigned_crops_and_harvests'),
    path('dashboard/beneficiary/harvest/create/<int:crop_assigned_id>/', views.create_harvest, name='create_harvest'),
    path('dashboard/beneficiary/harvest/<int:harvest_id>/update/', views.update_harvest, name='update_harvest'), 
    path('get-price/', views.get_price_for_grade_and_unit, name='get_price_for_grade_and_unit'),
    path('dashboard/beneficiary/harvest/<int:harvest_id>/view/', views.view_harvest, name='view_harvest'),
    path('dashboard/beneficiary/harvest/history/', views.harvest_history, name='harvest_history'),
    path('harvest/confirm/', views.confirm_harvest_ajax, name='confirm_harvest_ajax'),
    
    #benficiary review and confirmation of harvest record
    path('review_harvest/', views.review_harvest, name='review_harvest'),
    
    
    # path('dashboard/beneficiary/harvest/create_harvest/<int:crop_id>/', views.create_beneficiary_harvest, name='create_beneficiary_harvest'),
    # path('dashboard/beneficiary/harvest/update_harvest/<int:harvest_id>/', views.update_beneficiary_harvest, name='update_beneficiary_harvest'),
    
    #market
    path('dashboard/beneficiary/market/dashboard/', views.sales_dashboard, name='sales_dashboard'),     
    #edo
    path('dashboard/beneficiary/edo/', views.edo, name='edo'),
    path('dashboard/beneficiary/edo/<int:edo_id>/', views.edo_detail, name='edo_detail'),
   
    # farm nursery records
    path('dashboard/beneficiary/tunnel/nursery/', views.nursery_data_index, name='nursery_data_index'),
    path('dashboard/beneficiary/tunnel/create_nursery/', views.create_nursery_data, name='create_nursery_data'),
    path('dashboard/beneficiary/tunnel/update_nursery/<int:nursery_id>/', views.update_nursery_data, name='update_nursery_data'),
    
   
    path('dashboard/beneficiary/tunnel/create_trellising/', views.create_trellising_data, name='create_trellising_data'),
    # path('dashboard/beneficiary/tunnel/create_irrigation/', views.create_irrigation_data, name='create_irrigation_data'),
  
     # farm plant height records
    path('dashboard/beneficiary/tunnel/plant_height/', views.height_data_index, name='height_data_index'),
    path('dashboard/beneficiary/tunnel/create_height/', views.create_height_data, name='create_height_data'),
    path('dashboard/beneficiary/tunnel/update_height/<int:height_id>/', views.update_height_data, name='update_height_data'),
    
    # farm spraying records
    path('dashboard/beneficiary/tunnel/spraying/', views.spraying_data_index, name='spraying_data_index'),
    path('dashboard/beneficiary/tunnel/create_spraying/', views.create_spraying_data, name='create_spraying_data'),
    path('dashboard/beneficiary/tunnel/update_spraying/<int:spraying_id>/', views.update_spraying_data, name='update_spraying_data'),
    
    
     # farm spraying records
    path('dashboard/beneficiary/tunnel/irrigation/', views.irrigation_data_index, name='irrigation_data_index'),
    path('dashboard/beneficiary/tunnel/create_irrigation/', views.create_irrigation_data, name='create_irrigation_data'),
    path('dashboard/beneficiary/tunnel/update_irrigation/<int:irrigation_id>/', views.update_irrigation_data, name='update_irrigation_data'),
    
    
     # farm trellising records
    path('dashboard/beneficiary/tunnel/trellising/', views.trellising_data_index, name='trellising_data_index'),
    path('dashboard/beneficiary/tunnel/create_trellising/', views.create_trellising_data, name='create_trellising_data'),
    path('dashboard/beneficiary/tunnel/update_trellising/<int:trellising_id>/', views.update_trellising_data, name='update_trellising_data'),
    
     #Service Request
    path('dashboard/beneficiary/bills/requests_billing', views.beneficiary_service_request_list, name='beneficiary_service_request_list'),
]