from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField
from django.contrib import messages
from yuapp.models import Order, OrderItem, HarvestRecord
# from .forms import TrendKnowledgeBankForm, TrendKnowledgeDiscussionForm, CashRequestForm, RepaymentForm, HarvestForm
from django.db.models import Sum, F

@login_required
def all_orders(request):
    # Get all orders for the currently logged-in user
    buyer = request.user
    orders = Order.objects.filter(buyer=buyer)

    # Render a template that displays all the orders
    return render(request, 'admin/buyer/orders.html', {'orders': orders})

# Create your views here.
@login_required
def create_order(request, items):
    buyer = request.user
    order = Order.objects.create(buyer=buyer)

    # Loop through each item and create an OrderItem for it
    for item in items:
        harvest_record = HarvestRecord.objects.get(id=item['harvest_record_id'])
        quantity_ordered = item['quantity']
        
        # Create an OrderItem for each harvest record
        order_item = OrderItem.objects.create(
            order=order,
            harvest_record=harvest_record,
            quantity_ordered=quantity_ordered
        )
        order_item.save()

    return HttpResponse(f"Order {order.id} placed successfully with {order.get_total_quantity()} kg in total.")