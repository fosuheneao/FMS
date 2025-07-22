from datetime import timezone
from django.utils.timezone import now
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField
from django.contrib import messages
from yuapp.forms import TodoForm
from yuapp.models import AIC, Buyer, Delivery, Order, OrderItem, Harvest, Payment, Spoilage, Todo, Transaction
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Sum, F, Count
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.utils import timezone 
import json
from .forms import OrderForm, OrderItemFormSet, PaymentForm, SpoilageForm
from django.db.models.signals import post_save, post_delete


@receiver([post_save, post_delete], sender=OrderItem)
def update_order_totals(sender, instance, **kwargs):
    order = instance.order
    order.update_totals()
    

@login_required
def all_orders(request):
    buyer = None  # Ensure buyer is always defined
    try:
        # Get the Buyer instance linked to the logged-in user
        buyer = Buyer.objects.get(user=request.user)       
        # Fetch all orders placed by this buyer
        orders = Order.objects.filter(buyer=buyer)
        
    except Buyer.DoesNotExist:
        # No buyer associated with the user
        orders = []

    return render(request, 'admin/buyer/order/index.html', {
        'orders': orders,
        'buyer': buyer
    })


@login_required
def order_detail(request, order_id):
    # Get the Buyer instance linked to the logged-in user
    buyer = get_object_or_404(Buyer, user=request.user)
    
    # Get the specific order for the logged-in buyer
    order = get_object_or_404(Order, id=order_id, buyer=buyer)

    # Get all the order items for this order
    order_items = order.order_items.all()
    
    # Render the template
    return render(request, 'admin/buyer/order/detail.html', {
        'order': order,
        'order_items': order_items
    })

 
# @login_required
# def buyer_confirm_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, status='in_progress')

#     if request.method == "POST":
#         delivery_date = request.POST.get("delivery_date")
#         confirmation_note = request.POST.get("note")
#         quantity_receive = request.POST.get("quantity")

#         for item in order.order_items.all():
#             # Update OrderItem details
#             item.notes = request.POST.get(f"note_{item.id}", "")  # Add specific notes if provided
#             #item.quantity_received = request.POST.get(f"quantity_{item.id}", item.quantity)  # Default to ordered quantity
#             item.is_delivered = True
#             item.save()

#             # Update the existing Delivery record
#             delivery = Delivery.objects.filter(order_item=item).first()
#             if delivery:
#                 #delivery.volume_delivered = item.quantity_received
#                 delivery.delivery_date = delivery_date   
#                 delivery.quantity_receive = quantity_receive
#                 delivery.confirm_by = request.user
#                 delivery.confirm_at = now()        
                
#                 delivery.save()

#         # Update Order details
#         order.status = 'complete'
#         order.confirmation_note = confirmation_note
#         order.confirmed_by = request.user
#         order.confirmed_at = now()
#         order.save()

#         messages.success(request, "Order has been successfully confirmed.")
#         return redirect('order_detail', order_id=order.id)

#     return render(request, 'admin/buyer/order/confirm_order.html', {'order': order})


# @login_required
# def buyer_confirm_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, buyer__user=request.user)

#     if request.method == 'POST':
#         form = ConfirmOrderForm(request.POST, instance=order)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.status = 'completed'
#             order.confirmed_by = request.user
#             order.confirmed_at = timezone.now()
#             order.save()
#             return redirect('all_orders')
#     else:
#         form = ConfirmOrderForm(instance=order)

#     return render(request, 'admin/buyer/order/confirm_order.html', {'form': form, 'order': order})


@login_required
def buyer_make_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer__user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.paidby = request.user
            payment.payment_date = timezone.now()
            payment.save()
            # Optionally update order payment status
            total_paid = sum(p.amount for p in order.payments.all())
            order.is_paid = total_paid >= order.total_amount
            order.save()
            return redirect('all_orders')
    else:
        form = PaymentForm()

    return render(request, 'admin/buyer/order/make_payment.html', {'form': form, 'order': order})


@login_required
def report_spoilage_view(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__buyer__user=request.user)

    if request.method == 'POST':
        form = SpoilageReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.order_item = order_item
            report.reported_by = request.user
            report.status = "Pending"
            report.save()
            return redirect('buyer_orders')
    else:
        form = SpoilageReportForm()

    return render(request, 'admin/buyer/orders/report_spoilage.html', {'form': form, 'order_item': order_item})
    

# @login_required
# def make_payment(request, order_id):
#     order = get_object_or_404(Order, pk=order_id)

#     if request.method == 'POST':
#         payment_amount = Decimal(request.POST['amount_paid'])
#         Payment.objects.create(
#             transaction=order,
#             amount_paid=payment_amount,
#             date=timezone.now(),
#             created_by=request.user
#         )

#         messages.success(request, 'Payment recorded successfully.')
#         return redirect('buyer_orders')

#     return render(request, 'admin/buyer/orders/make_payment.html', {'order': order})


# Calculate the total_amount for a specific order by summing up quantity * price for each item
def calculate_order_total_amount(order_id):
    total_amount = OrderItem.objects.filter(order_id=order_id).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0  # Use 0 as default if total is None
    return total_amount
  
@login_required
def buyer_market_dashboard(request):
    buyer = Buyer.objects.get(user_id=request.user.id)
    todos = Todo.objects.filter(created_by=request.user)
    form = TodoForm()
        #passing the todo form
    # Replace `buyer_id` with the actual ID of the buyer you are interested in
    buyer_orders_count = Order.objects.filter(buyer_id=buyer.user.id).count()
    
    # Replace `buyer_id` with the actual ID of the buyer you are interested in
    buyer_order_items_count = OrderItem.objects.filter(order__buyer_id=buyer.user.id).count()
    
    # First, filter the buyer's orders and check if they are fulfilled
    delivered_orders_count = Order.objects.filter(buyer_id=buyer.user.id).filter(
        order_items__is_delivered=True
    ).distinct().count()
    
        
    total_volume_purchased = Transaction.objects.filter(
        buyer=buyer.user.id, transaction_type=Transaction.CROP_PURCHASE
    ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0

    total_volume_delivered = Delivery.objects.filter(
        order_item__order__buyer=buyer.user.id
    ).aggregate(total_delivered=Sum('volume_delivered'))['total_delivered'] or 0

    # Total payments made by the Buyer
    total_payments_made = Payment.objects.filter(
        order__buyer=buyer.user.id
    ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0

    #count of orders placed
    buyer_orders = Order.objects.filter(buyer = buyer.user.id).count()
    buyer_orders_all = Order.objects.filter(buyer = buyer.user.id)
    # Order and Delivery summary
    total_orders = Order.objects.filter(buyer=buyer.user.id).count()
    total_deliveries = Delivery.objects.filter(order_item__order__buyer=buyer.user.id).count()

    # Convert `order_status_counts` to a JSON-serializable format
    order_status_counts = list(
        Order.objects.filter(buyer=buyer.user.id)
        .values('status')
        .annotate(count=Count('status'))
    )

    #order_total_amount = calculate_order_total_amount(order_id)
    
    # Prepare context with `order_status_counts` as JSON
    context = {
        'buyer':buyer,
        'total_volume_purchased': total_volume_purchased,
        'total_volume_delivered': total_volume_delivered,
        'total_payments_made': total_payments_made,
        'total_orders': total_orders,
        'total_deliveries': total_deliveries,
        'buyer_orders': buyer_orders,
        'buyer_orders_all':buyer_orders_all,
        'buyer_orders_count':buyer_orders_count,
        'buyer_order_items_count':buyer_order_items_count,
        'delivered_orders_count':delivered_orders_count,
        'todos':todos,
        'form':form,
        'order_status_counts_json': json.dumps(order_status_counts),  # Convert to JSON for JavaScript
    }

    return render(request, 'admin/buyer/market/sales_dashboard.html', context)



# Custom function to serialize Decimal to float
def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

@login_required
def buyer_shop(request):
    # Fetch all harvest records where price_record_id is not null
    harvest_records = Harvest.objects.exclude(price_record_id__isnull=True)

    # Calculate total quantity and total price
    total_quantity1 = harvest_records.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
    total_price1 = harvest_records.aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

    total_quantity = float(total_quantity1)  # Convert Decimal to float
    total_price = float(total_price1)  # Convert Decimal to float
    
    # Set a default value for cart_item_count
    cart_item_count = 0
    # Get the cart from the session or initialize a new one
    cart = request.session.get('cart', {})
    # Calculate the total number of items in the cart if the cart is not empty
    if cart:
        #cart_item_count = sum(item['quantity'] for item in cart.values())
        # Count the total number of distinct items in the cart
        cart_item_count = len(cart)
        
    # Handle adding items to cart
    if request.method == 'POST':
        harvest_id = request.POST.get('harvest_id')
        quantity = int(request.POST.get('quantity', 1))
        harvest = get_object_or_404(Harvest, id=harvest_id)

        
        
        
        # Ensure price_record is included and check its existence
        price = harvest.price_record.selling_price if harvest.price_record else 0  # Default to 0 if not available
        
        # Update cart item quantity or add a new item
        if harvest_id in cart:
            # Check if there's enough available stock to add more items
            new_quantity = cart[harvest_id]['quantity'] + quantity
            if new_quantity <= harvest.quantity:
                cart[harvest_id]['quantity'] = new_quantity
            else:
                cart[harvest_id]['quantity'] = harvest.quantity  # Max available stock
        else:
            if quantity <= harvest.quantity:
                # Save the cart item with price record included
                cart[harvest_id] = {
                    'crop_name': harvest.crop.name,
                    'grade_name': harvest.grade.name,
                    'total_price': float(price),  # Convert to float
                    'quantity': quantity,
                    'photo_url': harvest.crop.photo.url,
                    'available_stock': float(harvest.quantity),  # Convert quantity if needed
                    'avlocation': harvest.greenhouse.city.name,
                }
            else:
                # If the requested quantity exceeds the stock, set it to the max available stock
                cart[harvest_id] = {
                    'crop_name': harvest.crop.name,
                    'grade_name': harvest.grade.name,
                    'total_price': float(price),  # Convert to float
                    'quantity': harvest.quantity,
                    'photo_url': harvest.crop.photo.url,
                    'available_stock': float(harvest.quantity),  # Max stock available
                    'avlocation': harvest.greenhouse.city.name,
                }

        # Save the updated cart back into the session
        request.session['cart'] = cart
        request.session.modified = True

        return redirect('buyer_shop')  # Redirect to avoid form re-submission

    return render(request, 'admin/buyer/shop/shop.html', {
        'assigned_harvest_records': harvest_records,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'cart': cart,  # Pass the cart to the template
        'cart_item_count': cart_item_count,
    })
    
@login_required
def view_cart(request):
    # Retrieve cart data from session
    cart = request.session.get('cart', {})

    # Calculate the total cost of the cart by summing price * quantity for each item
    total_cost = sum(item['total_price'] * item['quantity'] for item in cart.values())
    
    # Calculate the total number of items in the cart or set to 0 if empty
    cart_item_count = sum(item['quantity'] for item in cart.values()) if cart else 0
    
    # Add total price for each cart item
    for item in cart.values():
        item['total_item_cost'] = item['total_price'] * item['quantity']

    # Now pass the cart and the total_cost to the template
    return render(request, 'admin/buyer/shop/cart.html', {
        'cart': cart,
        'total_cost': total_cost,
        'cart_item_count': cart_item_count,
    })

@login_required
@login_required
def checkout(request):
    # Retrieve cart from session
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('buyer_shop')

    # Calculate total items for the order, we will calculate `total_amount` after creating items
    total_items = sum(item['quantity'] for item in cart.values())

    # Create the initial Order object
    order = Order.objects.create(
        buyer=request.user,
        created_by=request.user,
        total_items=total_items,
        notes="New Order Created"
    )

    # Initialize total amount to sum up from OrderItems
    total_amount = Decimal('0.00')

    # Loop through the cart items to create OrderItem entries
    for item_id, item_data in cart.items():
        harvest = Harvest.objects.get(id=item_id)
        
        # Calculate cost for this item and update the total_amount
        item_total_cost = Decimal(item_data['total_price']) * item_data['quantity']
        total_amount += item_total_cost

        # Create an OrderItem for each item in the cart
        OrderItem.objects.create(
            order=order,
            harvest=harvest,
            quantity=item_data['quantity'],
            price=Decimal(item_data['total_price'])  # Unit price of the item
        )

        # Optionally, update harvest quantity in stock if items are reserved or purchased
        harvest.quantity -= item_data['quantity']
        harvest.save()

    # Update the order with the calculated total_amount
    order.total_amount = total_amount
    order.save()

    # Clear the cart from session after successful order creation
    request.session['cart'] = {}
    request.session.modified = True

    # Redirect to a success page or order summary
    return render(request, 'admin/buyer/shop/checkout_success.html', {'order': order})



@login_required
def place_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST, prefix='order')
        order_item_formset = OrderItemFormSet(request.POST, prefix='items')
        
        if order_form.is_valid() and order_item_formset.is_valid():
            # Save the order
            order = order_form.save(commit=False)
            order.buyer = request.user
            order.save()

            # Save each item in the order
            order_items = order_item_formset.save(commit=False)
            for item in order_items:
                item.order = order  # Link the item to the order
                item.save()

            # Redirect to a success or order summary page
            return redirect('order_summary', order_id=order.id)

    else:
        # Initial empty form for the order and items
        order_form = OrderForm(prefix='order')
        order_item_formset = OrderItemFormSet(prefix='items')

    return render(request, 'admin/buyer/order/place_order.html', {
        'order_form': order_form,
        'order_item_formset': order_item_formset,
    })
    

@login_required
def create_order(request):
    if request.method == 'POST':
        # Process the form submission
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.buyer = request.user
            order.save()

            # Add selected harvest records as order items
            for harvest_id, quantity in request.POST.getlist('harvest_records'):
                harvest = Harvest.objects.get(id=harvest_id)
                OrderItem.objects.create(
                    order=order,
                    harvest_record=harvest,
                    quantity_ordered=quantity
                )

            messages.success(request, 'Order created successfully.')
            return redirect('order_summary', order_id=order.id)

    else:
        order_form = OrderForm()
        harvest_records = Harvest.objects.filter(confirmation='Open')

    return render(request, 'admin/buyer/order/create.html', {
        'order_form': order_form,
        'harvest_records': harvest_records,
    })

@login_required
def buyer_order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payments = order.payments.all()
    spoilages = Spoilage.objects.filter(orderitem__order=order)

    total_paid = sum(p.amount for p in payments)
    total_spoiled = sum(s.quantity_spoiled for s in spoilages)

    context = {
        'order': order,
        'payments': payments,
        'spoilages': spoilages,
        'total_paid': total_paid,
        'total_spoiled': total_spoiled,
    }
    return render(request, 'admin/buyer/order/order_summary.html', context)


@login_required
def buyer_spoilage(request):
    #buyer = get_object_or_404(Buyer, user=request.user)
    spoilages = Spoilage.objects.filter(reported_by=request.user)
    return render(request, 'admin/buyer/order/spoilage.html', {'spoilages': spoilages})


@login_required
def buyer_spoilage_form(request, spoilage_id=None):
    instance = None
    if spoilage_id:
        instance = get_object_or_404(Spoilage, id=spoilage_id, reported_by=request.user)
        if instance.status != 'Pending':
            return redirect('buyer_spoilage')  # prevent editing non-pending records

    if request.method == 'POST':
        form = SpoilageForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            spoilage = form.save(commit=False)
            if not instance:
                spoilage.reported_by = request.user
                spoilage.reported_at =  timezone.now().replace(microsecond=0)
            spoilage.save()
            return redirect('buyer_spoilage')
    else:
        form = SpoilageForm(instance=instance)

    return render(request, 'admin/buyer/order/create_spoilage.html', {'form': form, 'instance': instance})

# @login_required
# def make_payment(request, order_id):
#     order = get_object_or_404(Order, pk=order_id)

#     if request.method == 'POST':
#         payment_amount = Decimal(request.POST['amount_paid'])
#         Payment.objects.create(
#             transaction=order,
#             amount_paid=payment_amount,
#             date=timezone.now(),
#             created_by=request.user
#         )

#         messages.success(request, 'Payment recorded successfully.')
#         return redirect('buyer_orders')

#     return render(request, 'admin/buyer/orders/make_payment.html', {'order': order})

