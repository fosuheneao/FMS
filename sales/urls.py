from django.urls import path
from . import views

urlpatterns = [
    #edo
    path('dashboard/sales/price/', views.sale_price_index, name='sale_price_index'),
     #buyer module
    path('dashboard/sales/buyer/', views.sale_buyer_index, name='sale_buyer_index'),
    path('dashboard/sales/buyer/detail/<int:pk>/', views.sale_buyer_detail, name='aic_buyer_detail'),
    path('dashboard/sales/order/orders/', views.sale_all_orders, name='sale_all_orders'),    
    path('dashboard/sales/order/detail/<int:order_id>/', views.sale_order_detail, name='sale_order_detail'),
    path('dashboard/sales/order/<int:order_id>/fulfill/', views.sale_fulfill_order, name='sale_fulfill_order'),
    path('dashboard/sales/order/<int:order_id>/payment/', views.sale_process_payment, name='sale_process_payment'),
    
    path('dashboard/sales/order/create', views.sale_create_buyer, name='sale_create_buyer'), 
    path('dashboard/sales/order/update/<int:buyer_id>/', views.sale_update_buyer, name='sale_update_buyer'),  
    path('dashboard/sales/stock/', views.sale_agent_stock, name='sales_agent_stock'),
    path('ajax/update-unit-price/', views.sa_update_stock_unit_price, name='sa_update_stock_unit_price'),

    
     path('dashboard/sales/order/<int:order_id>/fulfill/', views.sales_fulfill_order, name='sales_fulfill_order'),
    ########################### POS URLS ##################################
    
    path('dashboard/sales/pos/orders/', views.sa_order_list, name='sa_order_list'),
    path('dashboard/sales/pos/orders/new/', views.sa_create_order, name='sa_create_order'),
    path('dashboard/sales/pos/orders/<int:order_id>/update', views.sa_update_order, name='sa_update_order'),
    path('dashboard/sales/pos/orders/<int:order_id>/', views.sa_order_detail, name='sa_order_detail'),
    
    
    path('dashboard/sales/pos/orders/spoilage/', views.sa_order_spoilages, name='sa_order_spoilages'),
    #path('dashboard/sales/pos/orders/spoilage/<int:order_id>/confirm/', views.sa_confirm_spoilage, name='sa_confirm_spoilage'),
    path('spoilage/confirm/<int:spoilage_id>/', views.sa_confirm_spoilage, name='sa_confirm_spoilage'),

    
    ############################ PRINT INVOICE PDFS
    path('dashboard/sales/pos/orders/invoice/<int:order_id>/', views.generate_order_invoice_pdf, name='generate_invoice_pdf'),
    path('dashboard/sales/pos/orders/print/orders/', views.print_all_orders, name='print_all_orders'),
    path('dashboard/sales/pos/orders/print/orders/', views.preview_invoice, name='preview_invoice'),
    
    path('get-orderitem-details/', views.get_orderitem_details, name='get_orderitem_details'),
    #Inline editting of the order item record: 
    path('order-item/<int:order_item_id>/edit/', views.sa_edit_order_item, name='sa_edit_order_item'),    
    path('dashboard/sales/pos/orders/<int:order_id>/edit/', views.sa_edit_order, name='sa_edit_order'),      
    path('dashboard/sales/pos/orders/<int:order_id>/add-item/', views.sa_add_order_item, name='sa_add_order_item'),
    
    #
    path('get-stock-unit-price/', views.get_stock_unit_price, name='get_stock_unit_price'),
    # urls.py
    path('orders/<int:order_id>/payment-modal/', views.order_payment_modal, name='order_payment_modal'),
    #path('dashboard/sales/pos/<int:order_id>/payment/', views.sa_record_payment, name='sa_record_payment'),
    path('record-order-payment/<int:order_id>/', views.sa_record_order_payment, name='sa_record_order_payment'),
     
    path('dashboard/sales/pos/orders/payment/', views.sa_process_payment, name='sa_process_payment'),
   
   
    path('dashboard/sales/pos/stock/transfer/', views.sa_transfer_stock, name='sa_transfer_stock'),
    path('dashboard/sales/pos/stock/movements/', views.sa_stock_movement_list, name='sa_stock_movement_list'),
    path('dashboard/sales/pos/stock/movement/<int:movement_id>/confirm/', views.sa_confirm_stock_reception, name='sa_confirm_stock_reception'),
    path('load-crop-varieties/', views.load_crop_varieties, name='ajax_load_crop_varieties'),
    path('check-stock-balance/', views.check_stock_balance, name='check_stock_balance'),
    
    
    ################ STOCK MOVEMENT #################################
    path('dashboard/sales/pos/movement/create/', views.create_harvest_movement, name='create_harvest_movement'),
    path('dashboard/sales/pos/movement/list/', views.movement_list, name='movement_list'),
    path('dashboard/sales/pos/movement/confirm/<int:movement_id>/', views.confirm_movement_receipt, name='confirm_movement_receipt'),
    #path('orders/create/', views.create_order, name='create_order'),
    #path('orders/<int:order_id>/items/', views.add_order_items, name='add_order_items'),

    #POS Payment
    path('dashboard/sales/pos/payments/', views.sa_payment_list, name='sa_payment_list'),
    path('dashboard/sales/pos/payments/<int:pk>/', views.sa_payment_detail, name='sa_payment_detail'),
    
    #POS Stock Transfer
    path('dashboard/sales/pos/stock/fulfillments/', views.sa_fulfillment_list, name='sa_fulfillment_list'),
    path('dashboard/sales/pos/stock/fulfillment/<int:pk>/', views.sa_fulfillment_detail, name='sa_fulfillment_detail'),
    
    
    ################################### REPORTING AND DOWNLOADABLE URLS ##################################
    path('dashboard/sales/reports/harvest/', views.sa_harvest_report, name='sa_harvest_report'),
    path('dashboard/sales/reports/harvest/pdf/', views.sa_harvest_report_pdf, name='sa_harvest_report_pdf'),
    path('dashboard/sales/reports/harvest/excel/', views.sa_harvest_report_excel, name='sa_harvest_report_excel'),
    
     #inter market_centre stock movement report
    path('dashboard/sales/reports/stockmovement/', views.sa_stock_movement_report, name='sa_stock_movement_report'),
    path('dashboard/sales/reports/stockmovement/excel/', views.sa_stock_movement_report_excel, name='sa_stock_movement_report_excel'),
    
     #stock aggregate from harvest report
    path('dashboard/sales/reports/stockaggregate/', views.sa_stock_aggregate_report, name='sa_stock_aggregate_report'),
    path('dashboard/sales/reports/stockaggregate/excel/', views.sa_stock_aggregate_report_excel, name='sa_stock_aggregate_report_excel'),
    
    path('dashboard/sales/reports/saleorder/', views.sa_sales_order_report, name='sa_sales_order_report'),
    path('dashboard/sales/reports/saleorder/excel/', views.sales_order_report_excel, name='sales_order_report_excel'),
    
    path('dashboard/sales/reports/pdf/', views.sa_export_pdf_report, name='sa_export_pdf_report'),
    path('dashboard/sales/reports/excel/', views.sa_export_excel_report, name='sa_export_excel_report'),
    
]