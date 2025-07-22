from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/buyer/orders/', views.all_orders, name='orders'),   
    path('dashboard/buyer/order/create/<int:order_id>/', views.create_order, name='create_order'),
    path('dashboard/buyer/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('dashboard/buyer/order/<int:order_id>/summary/', views.buyer_order_summary, name='buyer_order_summary'),
    path('dashboard/buyer/order/spoilage/', views.buyer_spoilage, name='buyer_spoilage'),
    
    path('dashboard/buyer/order/spoilage/create/', views.buyer_spoilage_form, name='create_spoilage'),
    path('dashboard/buyer/order/spoilage/<int:spoilage_id>/edit/', views.buyer_spoilage_form, name='edit_spoilage'),

    
    #################
   # path('dashboard/buyer/order/<int:order_id>/confirm/', views.buyer_confirm_order, name='buyer_confirm_order'),
    path('dashboard/buyer/order/<int:order_id>/payment/', views.buyer_make_payment, name='buyer_make_payment'),
    path('dashboard/buyer/order/item/<int:order_item_id>/spoilage/', views.report_spoilage_view, name='report_spoilage'),

    #shop
    path('dashboard/buyer/shop/', views.buyer_shop, name='buyer_shop'),
    path('dashboard/buyer/placeorder/', views.place_order, name='place_order'),
    #path('dashboard/buyer/order/<int:order_id>/confirm/', views.buyer_confirm_order, name='buyer_confirm_order'),
    
    
    path('dashboard/buyer/market/', views.buyer_market_dashboard, name='buyer_market_dashboard'),        
    path('dashboard/buyer/shop/cart/', views.view_cart, name='view_cart'),
    path('dashboard/buyer/shop/checkout/', views.checkout, name='checkout'),  # Add this in the next step for order creation
]