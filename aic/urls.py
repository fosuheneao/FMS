from django.urls import path
from . import views

urlpatterns = [
    #edo
    path('dashboard/aic/price/', views.aic_price_index, name='aic_price_index'),
    path('dashboard/aic/price/create', views.aic_create_price, name='aic_create_price'),
    path('dashboard/aic/price/detail/<int:price_id>/', views.aic_price_detail, name='aic_price_detail'),
    path('dashboard/aic/price/<int:pk>/update', views.aic_price_update, name='aic_price_update'),
    path('dashboard/aic/edo/attendance/', views.aic_attendance_list, name='aic_attendance_list'),
    
    #Greenhouse
    path('dashboard/aic/greenhouse/', views.aic_greenhouse_index, name='aic_greenhouse_index'),
    path('dashboard/aic/greenhouse/detail/<int:greenhouse_id>', views.aic_greenhouse_map_view, name='aic_greenhouse_map_view'),
    
    path('dashboard/aic/forum/index/', views.aic_trend_knowledge_index, name='aic_trend_knowledge_index'),
    path('dashboard/aic/forum/create/', views.aic_create_trend_knowledge, name='aic_create_trend_knowledge'),
    path('dashboard/aic/forum/<int:pk>/', views.aic_trend_knowledge_bank_detail, name='aic_trend_knowledge_bank_detail'),
    path('dashboard/aic/forum/discussion/<int:pk>/', views.aic_trend_knowledge_bank_detail, name='aic_discussion_trend_knowledge'),
    
    path('dashboard/aic/forum/discussion/', views.aic_trend_knowledge_board, name='aic_trend_knowledge_board'),
    
    #harvest record
    path('dashboard/aic/aic/harvest/<int:beneficiary_id>/', views.aic_beneficiary_harvest, name='aic_beneficiary_harvest'),
    # path('dashboard/aic/harvest/create', views.aic_create_beneficiary, name='aic_create_beneficiary'),
    # path('dashboard/aic/harvest/beneficiary/<int:beneficiary_id>', views.beneficiary_harvest, name='beneficiary_harvest'),
    
    #harvest summary details
    path('dashboard/aic/harvest_summary', views.harvest_summary_view, name='harvest_summary_view'),
    
    
    #aic beneficiary
    path('get_greenhouse_rooms/<int:edo_id>/', views.get_greenhouse_rooms, name='get_greenhouse_rooms'),
    path('dashboard/aic/beneficiary/', views.aic_beneficiary_index, name='aic_beneficiary_index'),
    path('dashboard/aic/beneficiary/create', views.aic_create_beneficiary, name='aic_create_beneficiary'), 
    path('dashboard/aic/beneficiary/<int:beneficiary_id>/', views.aic_beneficiary_detail, name='aic_beneficiary_detail'), 
    path('dashboard/aic/beneficiary/update/<int:beneficiary_id>/', views.aic_update_beneficiary, name='aic_update_beneficiary'),

    
    #Financials
    path('dashboard/aic/finance/', views.aic_pricetale_index, name='aic_pricetale_index'),
    path('dashboard/aic/finance/create', views.aic_create_pricetable, name='aic_create_pricetable'),
    path('dashboard/aic/finance/update/<int:pk>/', views.aic_update_price_table, name='aic_update_price_table'),    
    path('dashboard/aic/finance/cash-requests/', views.aic_beneficiaries_cash_requests, name='aic_beneficiaries_cash_requests'),
    path('dashboard/aic/finance/repayments/', views.aic_beneficiaries_repayments, name='aic_beneficiaries_repayments'),
    path('dashboard/aic/finance/change-cash-status/<int:cash_id>/<str:status>/', views.aic_change_cash_status, name='aic_change_cash_status'),
    path('dashboard/aic/finance/change-repayment-status/<int:repayment_id>/<str:status>/', views.aic_change_repayment_status, name='aic_change_repayment_status'),
    path('dashboard/aic/finance/cashloan/', views.aic_cash_loaned_list, name='aic_cash_loaned_list'),
    path('dashboard/aic/finance/cashloandetail/<int:cashload_id>/', views.aic_cashloan_detail, name='aic_cashloan_detail'),
    
    
    #ACCOUNTING MODULES
    #<<<<<<<<<<<===============================================>>>>>>>>>>>>>>>>>>>>>>>>
    path('dashboard/aic/accounting/accounting-summary/', views.aic_accounting_summary, name='aic_accounting_summary'),
    path('dashboard/aic/accounting/accounting-details/<str:category>/<int:beneficiary_id>/', views.aic_accounting_detail, name='aic_accounting_detail'),
   
   #<<<<<<<<<<<<<==========BILLS & COSTING===================================================
   #<<<<<<<<<<<<<<<======================================>>>>>>>>>>>>>
#    path('dashboard/aic/accounting/billing/create_bill_item/', views.aic_create_billable_item, name='aic_create_billable_item'),
#    path('dashboard/aic/accounting/billing/update_bill_item/<int:billable_item_id>/', views.aic_update_billable_item, name='aic_update_billable_item'),
#    path('dashboard/aic/accounting/billing/list_bill_items/', views.aic_billable_items_list, name='aic_billable_items_list'),

#    path('dashboard/aic/accounting/billing/create_maintenance_cost/', views.aic_create_maintenance_cost, name='aic_create_maintenance_cost'),
#    path('dashboard/aic/accounting/billing/update_maintenance_cost/<int:maintenance_cost_id>/', views.aic_update_maintenance_item, name='aic_update_maintenance_item'),
#    path('dashboard/aic/accounting/billing/list_maintenance_cost/', views.aic_maintenance_costs_list, name='aic_maintenance_costs_list'),

#    path('dashboard/aic/accounting/billing/list_beneficiary_shares/', views.aic_beneficiary_shares_list, name='aic_beneficiary_shares_list'),

# #<<<<<<<<<<<<<==============================>>>>>>>>>>>>>>>>>>>>>>>>
#     path('dashboard/aic/accounting/billing/cost/', views.aic_cost_item_list, name='aic_cost_item_list'),
#     path('dashboard/aic/accounting/billing/cost/create/', views.aic_cost_item_create, name='aic_cost_item_create'),
#     path('dashboard/aic/accounting/billing/cost/update/<int:item_cost_id>/', views.aic_cost_item_update, name='aic_cost_item_update'),

#     path('dashboard/aic/accounting/billing/maintenance-costs/', views.aic_maintenance_cost_list, name='aic_maintenance_cost_list'),
#     path('dashboard/aic/accounting/billing/maintenance-costs/create/', views.aic_maintenance_cost_create, name='aic_maintenance_cost_create'),
#     path('dashboard/aic/accounting/billing/maintenance-costs/update/<int:costing_id>/', views.aic_maintenance_cost_update, name='aic_maintenance_cost_update'),

#     path('dashboard/aic/accounting/billing/billing/', views.aic_billing_list, name='aic_billing_list'),
#     path('dashboard/aic/accounting/billing/billing/create/', views.aic_billing_create, name='aic_billing_create'),
#     path('dashboard/aic/accounting/billing/billing/update/<int:bill_id>/', views.aic_billing_update, name='aic_billing_update'),
    
        #Farm season route
      path('dashboard/aic/accounting/farmcycle/cycles', views.aic_farm_season_index, name='aic_farm_season_index'),
      path('dashboard/aic/accounting/farmcycle/create', views.aic_create_farm_season, name='aic_create_farm_season'),
      path('dashboard/aic/accounting/farmcycle/update/<int:farmseason_id>/', views.aic_update_farm_season, name='aic_update_farm_season'),
      
      #billable items
      path('dashboard/aic/accounting/billable/billables', views.aic_billable_item_index, name='aic_billable_item_index'),
      path('dashboard/aic/accounting/billable/create', views.aic_create_billable_item, name='aic_create_billable_item'),
      path('dashboard/aic/accounting/billable/update/<int:billable_item_id>/', views.aic_update_billable_item, name='aic_update_billable_item'),
      
      #billable item cost
      path('dashboard/aic/accounting/billable/itemcost_list', views.aic_item_cost_index, name='aic_item_cost_index'),
      path('dashboard/aic/accounting/billable/create_itemcost', views.aic_create_item_cost, name='aic_create_item_cost'),
      path('dashboard/aic/accounting/billable/update_itemcost/<int:item_cost_id>/', views.aic_update_item_cost, name='aic_update_item_cost'),
      
      
       #Service Item route
      path('dashboard/aic/accounting/serviceitem/serviceitems', views.aic_service_item_index, name='aic_service_item_index'),
      path('dashboard/aic/accounting/serviceitem/create', views.aic_create_service_item, name='aic_create_service_item'),
      path('dashboard/aic/accounting/serviceitem/update/<int:serviceitem_id>/', views.aic_update_service_item, name='aic_update_service_item'),
      
        #Service Request
      path('dashboard/aic/accounting/requests_billing', views.aic_service_request_list, name='aic_service_request_list'),
      #path('dashboard/aic/edo_service/requests/', views.aic_edo_service_requests, name='aic_edo_service_requests'),
      path("approve-service-request/", views.aic_approve_service_request, name="aic_approve_service_request"),


    
      
      path('dashboard/aic/accounting/invoices/', views.aic_invoice_list, name='aic_invoice_list'),
      path('dashboard/aic/accounting/invoices/<int:invoice_id>/', views.aic_invoice_detail, name='aic_invoice_detail'),
      path('dashboard/aic/accounting/invoices/new/', views.aic_invoice_create, name='aic_invoice_create'),
      path('dashboard/aic/accounting/invoices/new/<int:invoice_id>/', views.aic_invoice_update, name='aic_invoice_update'),


    #<<<<<<<<<<<<<========== end of BILLS & COSTING===================================================
   #<<<<<<<<<<<<<<<======================================>>>>>>>>>>>>>
   
    # Make beneficiary_id optional
    path('dashboard/aic/accounting/accounting-details/<str:category>/', views.aic_accounting_detail, name='aic_accounting_detail_no_id'),
    #   path('dashboard/aic/accounting/accounting-details/<str:category>/<int:beneficiary_id>/', views.aic_accounting_detail, name='aic_accounting_detail'),

    path('dashboard/aic/market/', views.aic_market_dashboard, name='aic_market_dashboard'),
 
    
    
    # path('dashboard/beneficiary/harvest/record/<int:beneficiary_id>/<int:crop_id>/', views.aic_assigned_crops_and_harvests, name='assigned_crops_and_harvests'),
    # path('dashboard/beneficiary/harvest/create/<int:crop_assigned_id>/', views.create_harvest, name='create_harvest'),
    # path('dashboard/beneficiary/harvest/<int:harvest_id>/update/', views.update_harvest, name='update_harvest'), 
    # path('get-price/', views.get_price_for_grade_and_unit, name='get_price_for_grade_and_unit'),
    path('dashboard/aic/beneficiary/harvest/<int:harvest_id>/view/', views.aic_view_harvest, name='aic_view_harvest'),
    path('dashboard/aic/harvest/history/', views.aic_harvest_history, name='aic_harvest_history'),
    
    
    #FARM INPUT
    path('dashboard/aic/farminput/distribute/', views.aic_create_distribute_input, name='aic_create_distribute_input'),
    path('dashboard/aic/farminput/list/', views.aic_distribution_list, name='aic_distribution_list'),
    path('dashboard/aic/farminput/edo-distribution/<int:edo_id>/', views.aic_edo_distribution, name='aic_edo_distribution'),
    
    path('get_farm_input_details/', views.get_farm_input_details, name='get_farm_input_details'),
    # path('aic_get_available_quantity/', views.aic_get_available_quantity, name='aic_get_available_quantity'),
    
    #farm input from input dealer
    path('dashboard/aic/farminput/farm-input-list/', views.aic_farm_input_list, name='aic_farm_input_list'),
    path('dashboard/aic/farminput/add-farm-input/', views.aic_add_farm_input, name='aic_add_farm_input'),
    path('dashboard/aic/farminput/edit/<int:input_id>/', views.aic_update_farm_input, name='aic_update_farm_input'),
   
    
    #input dealer
    path('dashboard/aic/farminput/inputdealer/', views.aic_input_dealer_list, name='aic_input_dealer_list'),
    path('dashboard/aic/farminput/create_dealer/', views.aic_create_inputdealer, name='aic_create_inputdealer'),
    path('dashboard/aic/farminput/edit_inputdealer/<int:inputdealer_id>/', views.aic_update_farm_inputdealer, name='aic_update_farm_inputdealer'),
    
    #input category module url
    path('dashboard/aic/farminput/create_inputcategory/', views.aic_create_input_category, name='aic_create_input_category'),
    path('dashboard/aic/farminput/inputcategory/', views.aic_input_category_list, name='aic_input_category_list'),
    path('dashboard/aic/farminput/update_inputcategory/<int:inputcategory_id>/', views.aic_update_input_category, name='aic_update_input_category'),
    
    #buyer module
    path('dashboard/aic/buyer/', views.aic_buyer_index, name='aic_buyer_index'),
    path('dashboard/aic/buyer/detail/<int:pk>/', views.aic_buyer_detail, name='aic_buyer_detail'),
    path('dashboard/aic/order/orders/', views.aic_all_orders, name='aic_all_orders'),    
    path('dashboard/aic/order/detail/<int:order_id>/', views.aic_order_detail, name='aic_order_detail'),
    path('dashboard/aic/order/<int:order_id>/fulfill/', views.aic_fulfill_order, name='aic_fulfill_order'),
    path('dashboard/aic/order/<int:order_id>/payment/', views.aic_process_payment, name='aic_process_payment'),
    
    
    #create buyer order
    # path('dashboard/aic/order/shop/', views.aic_buyer_shop, name='aic_buyer_shop'),
    path('dashboard/aic/order/buyer/<int:user_id>/shop/', views.aic_buyer_shop, name='aic_buyer_shop'),
    path('dashboard/aic/order/placeorder/', views.aic_place_order, name='aic_place_order'),
    path('dashboard/aic/order/<int:order_id>/confirm/', views.aic_buyer_confirm_order, name='aic_buyer_confirm_order'),       
    path('dashboard/aic/order/buyer/<int:user_id>/cart/', views.aic_view_cart, name='aic_view_cart'),
    path('dashboard/aic/order/buyer/<int:user_id>/checkout/', views.aic_checkout, name='aic_checkout'),  # Add this in the next step for order creation
    
        
    path('dashboard/aic/order/create', views.aic_create_buyer, name='aic_create_buyer'), 
    path('dashboard/aic/order/update/<int:buyer_id>/', views.aic_update_buyer, name='aic_update_buyer'),    
    # path('dashboard/aic/order/detail/<int:pk>/', views.aic_buyer_detail, name='aic_buyer_detail'),
    
    #EDO
    path('dashboard/aic/edo/', views.aic_edo_index, name='aic_edo_index'),
    path('dashboard/aic/edo/create', views.aic_create_edo, name='aic_create_edo'), 
    path('dashboard/aic/edo/update/<int:edo_id>/', views.aic_update_edo, name='aic_update_edo'),    
    path('dashboard/aic/edo/detail/<int:edo_id>/', views.aic_edo_detail, name='aic_edo_detail'),
    
    
      #SALES AGENT
    path('dashboard/aic/saleagent/', views.aic_sale_agent_index, name='aic_sale_agent_index'),
    path('dashboard/aic/saleagent/create', views.aic_create_sale_agent, name='aic_create_sale_agent'), 
    path('dashboard/aic/saleagent/update/<int:sale_agent_id>/', views.aic_update_sale_agent, name='aic_update_sale_agent'),    
    path('dashboard/aic/saleagent/detail/<int:sale_agent_id>/', views.aic_sale_agent_detail, name='aic_sale_agent_detail'),
    #farm input from input dealer
    
    ########## Todo
    path('dashboard/aic/todo/', views.aic_todo_list, name='aic_todo_list'),
    path('dashboard/aic/todo/create/', views.aic_create_todo, name='aic_create_todo'),
    path('dashboard/aic/todo/update/<int:pk>/<str:state>/', views.aic_update_todo_state, name='aic_update_todo_state'),
    
    # farm nursery records
    path('dashboard/aic/tunnel/nursery/', views.aic_nursery_data_index, name='aic_nursery_data_index'),
    #path('dashboard/aic/tunnel/create_nursery/<int:beneficiary_id>/', views.aic_create_nursery_data, name='aic_create_nursery_data'),
    
    path('get-crop-varieties/', views.get_crop_varieties, name='get_crop_varieties'),
   
     # farm plant height records
    path('dashboard/aic/tunnel/plant_height/', views.aic_height_data_index, name='aic_height_data_index'),
    #path('dashboard/aic/tunnel/create_height/<int:beneficiary_id>/', views.aic_create_height_data, name='aic_create_height_data'),
   
    # farm spraying records
    path('dashboard/aic/tunnel/spraying/', views.aic_spraying_data_index, name='aic_spraying_data_index'),
    path('aic_spraying_submit_feedback/', views.aic_spraying_submit_feedback, name='aic_spraying_submit_feedback'),
    #path('dashboard/aic/tunnel/create_spraying/<int:beneficiary_id>/', views.aic_create_spraying_data, name='aic_create_spraying_data'),
        
     # farm spraying records
    path('dashboard/aic/tunnel/irrigation/', views.aic_irrigation_data_index, name='aic_irrigation_data_index'),
    #path('dashboard/aic/tunnel/create_irrigation/<int:beneficiary_id>/', views.aic_create_irrigation_data, name='aic_create_irrigation_data'),
    
    
     # farm trellising records
    path('dashboard/aic/tunnel/trellising/', views.aic_trellising_data_index, name='aic_trellising_data_index'),
    #path('dashboard/aic/tunnel/create_trellising/<int:beneficiary_id>/', views.aic_create_trellising_data, name='aic_create_trellising_data'),
    
    
]