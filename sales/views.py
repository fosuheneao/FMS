from django.shortcuts import get_object_or_404, render, redirect
# Create your views here
from datetime import time
from django.utils.timezone import now
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
import traceback
from django.http import JsonResponse, HttpResponse
from weasyprint import HTML
import pandas as pd
from django.contrib import messages
from django.db.models import Case, When, IntegerField, Prefetch
from django.db.models import Sum, F, Count, DecimalField, Value, ExpressionWrapper, Exists, OuterRef
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from buyer.forms import PaymentForm
from yuapp.models import Balance, Buyer, CropVariety, Fulfillment, Harvest, HarvestStockAggregate, PriceTable,GreenhouseRoom, Supervisor, Order, OrderItem, Payment, Delivery, TrendKnowledgeBank, TrendKnowledgeDiscussion
from .forms import *
from aic.forms import BuyerForm
import json

import datetime
import io
import xlsxwriter
from xhtml2pdf import pisa


# Create your views here.
@login_required
def sale_price_index(request):
    if request.user.is_authenticated:        
        prices = PriceTable.objects.filter(created_by = request.user.id)
        return render(request, 'admin/sales/price/index.html', {'prices':prices})
    else:
       return redirect('beneficiary_login')


@login_required
def get_greenhouse_rooms(request, edo_id):
    try:
        supervisor = Supervisor.objects.get(id=edo_id)
        
        # Get all greenhouses associated with the supervisor
        greenhouses = supervisor.greenhouse.all()  
        
        # Get all unassigned rooms associated with these greenhouses
        # unassigned_rooms = GreenhouseRoom.objects.filter(greenhouse__in=greenhouses)
         # Get all unassigned rooms (assign = 0) associated with these greenhouses
        unassigned_rooms = GreenhouseRoom.objects.filter(greenhouse__in=greenhouses, assign=0)


        if not unassigned_rooms.exists():
            return JsonResponse({'rooms': [], 'message': 'All Tunnels For Selected EDO Assigned'})

        room_data = [{'id': room.id, 'name': room.room_name} for room in unassigned_rooms]

        return JsonResponse({'rooms': room_data})

    except Supervisor.DoesNotExist:
        return JsonResponse({'rooms': [], 'message': 'Supervisor not found'})
    
@login_required
def get_exiting_greenhouse_rooms(request, tunnelId):
    try:
        room = GreenhouseRoom.objects.get(id=tunnelId)
        # greenhouses = room.greenhouse.all()  # Get all greenhouses associated with the supervisor

        if room:
        # for greenhouse in greenhouses:
            # rooms.extend(greenhouse.rooms.all())  # Extend with rooms from each greenhouse

            room_data = [{'id': room.id, 'name': room.room_name}]

        return JsonResponse({'rooms': room_data})

    except GreenhouseRoom.DoesNotExist:
        return JsonResponse({'rooms': []})
    

@login_required
def sale_buyer_index(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        # Fetch all ChangingRoom assignments for this specific beneficiary
        buyers = Buyer.objects.all()

        return render(request, 'admin/sales/buyer/buyer.html', {
            'buyers': buyers,
        })
    else:
        return redirect('beneficiary_login')

@login_required
def sale_buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'admin/sales/buyer/detail.html', {'buyer': buyer})


#BUYER MODULE
@login_required
def sale_buyer_index(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        # Fetch all ChangingRoom assignments for this specific beneficiary
        buyers = Buyer.objects.all()

        return render(request, 'admin/sales/buyer/buyer.html', {
            'buyers': buyers,
        })
    else:
        return redirect('beneficiary_login')

#ORDER MODULE
@login_required
def sale_all_orders(request):
    # Get all orders for the currently logged-in user
    if request.user.is_authenticated: 
        saleagent = request.user
        orders = Order.objects.filter(created_by = saleagent)
        # Render a template that displays all the orders
        return render(request, 'admin/sales/order/orders.html', {'orders': orders})
    else:
       return redirect('beneficiary_login')

@login_required
def sale_order_detail(request, order_id):
    # Get the specific order for the logged-in user
    order = get_object_or_404(Order, id=order_id)

    # Get all the order items for this order
    order_items = order.order_items.all()

    # Render a template that displays the order and its items
    return render(request, 'admin/sales/order/detail.html', {
        'order': order,
        'order_items': order_items
    })


@login_required
def sale_fulfill_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='pending')
    
    if request.method == "POST":
        for item in order.order_items.all():
            # Record delivery for each order item
            Delivery.objects.create(
                order_item=item,
                volume_delivered=item.quantity,  # Assuming all quantity is delivered
                date=request.POST.get("delivery_date"),  # Pass delivery date from form
                created_by = request.user
            )
        # Update order status
        order.status = 'in_progress'
        order.fulfilled_by = request.user
        order.fulfilled_at = now()
        order.save()
        return redirect('sale_order_detail', order_id=order.id)

    return render(request, 'admin/sales/order/fulfill_order.html', {'order': order})


@login_required
def sale_process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='complete')
    
    if request.method == "POST":
        payment_amount = Decimal(request.POST.get("amount_paid"))
        payment_date = request.POST.get("payment_date")
        transaction_type = request.POST.get("transaction_type")
        total_amnt = order.total_amount
        amount_bal = total_amnt - payment_amount
        # Record payment
        Payment.objects.create(
            order=order,
            transaction_type = transaction_type,
            total_amount = total_amnt,
            amount_paid = payment_amount,
            amount_bal = amount_bal,
            date=payment_date,
            created_by = request.user
        )

        # Update order status
        order.is_paid =True        
        order.status = 'completed'
        order.save()

        return redirect('sale_order_detail', order_id=order.id)
    
    return render(request, 'admin/sales/order/process_payment.html', {'order': order}) 
#END OF ORDER MODULE

@login_required
def aic_buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'admin/sales/buyer/detail.html', {'buyer': buyer})

@login_required
def sale_create_buyer(request):
    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES)
        if form.is_valid():
            
            buyer = form.save(commit=False)
            buyer.created_by = request.user  # Set the logged-in user as the creator

            # Save the beneficiary instance
            buyer.save()
                      
            #use email as username if valid email exist else use function to create unique username
            email = buyer.email  # Assuming 'email' is a field in the Beneficiary model
            if email and '@' in email:  # Basic validation for a valid email
                username = email
            else:
                first_name = buyer.client_name.split()[0].lower()  # Assuming full_name is a field in Beneficiary model
                unique_id = int(time.time()) % 100000   # Get the current time as a unique ID
                username = f"{first_name}_y{unique_id:05}"  # Construct the username
            
            password = 'freshLoc@2024'  # Default password (should be changed later)
            new_user = User.objects.create(
                username=username,
                password=make_password(password),  # Encrypt the password
                email=buyer.email,
                first_name=buyer.client_name.split()[0].lower(),  # Extract first name from full name
                last_name=" ".join(buyer.client_name.split()[1:])  # Rest of the name as last name
            )

               # Assign the existing 'beneficiary' group
            buyer_group = Group.objects.get(name='buyer')
            new_user.groups.add(buyer_group)

            # Save the user and set any other required fields
            new_user.save()
            
            # farm_input.save()
            return redirect('aic_buyer_index')
    else:
        form = BuyerForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/sales/buyer/create.html', {'form': form})

@login_required
def sale_update_buyer(request, buyer_id):
    # Retrieve the existing FarmInput instance
    buyer = get_object_or_404(Buyer, id=buyer_id)

    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES, instance=buyer)
        if form.is_valid():
            # Save the updated FarmInput instance
            buyer = form.save(commit=False)
            # buyer.created_by = request.user
            # if farm_input.confirmation != 0:
            #     farm_input.confirm_by = request.user
            buyer.save()
            return redirect('sale_buyer_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = BuyerForm(instance=buyer)

    return render(request, 'admin/sales/buyer/create.html', {'form': form, 'buyer': buyer})

#aggregate stock
#+++<<<<<<<<<<<<<<<<<<<<<<<<<<<<<=
@login_required
def sale_agent_stock(request):
    try:
        # Get the sales agent associated with the logged-in user
        agent = SaleAgent.objects.get(user=request.user)        
        # Fetch stocks related to the agent's marketing centre
        stocks = HarvestStockAggregate.objects.filter(
            market_centre=agent.marketingcentre  # Ensure correct field name
        ).order_by('-aggregation_date')  # Show recent records first

    except SaleAgent.DoesNotExist:
        stocks = []  # Return empty list if the agent doesn't exist

    return render(request, 'admin/sales/marketing/sales_agent_stock.html', {'stocks': stocks, 'agent':agent})

@csrf_exempt  # Alternatively, use @login_required + pass CSRF in AJAX
def sa_update_stock_unit_price(request):
    if request.method == "POST":
        stock_id = request.POST.get("stock_id")
        try:
            stock = HarvestStockAggregate.objects.get(id=stock_id)
        except HarvestStockAggregate.DoesNotExist:
            return JsonResponse({"success": False, "message": "Stock not found."})

        # Match PriceTable
        price_entry = PriceTable.objects.filter(
            market_center=stock.market_centre,
            crop=stock.crop,
            cropvariety=stock.cropvariety,
            grade=stock.grade,
            unit=stock.unit,
        ).order_by('-from_date').first()  # Choose the most recent

        if price_entry:
            stock.unit_price = price_entry
            stock.save()
            return JsonResponse({"success": True, "message": "Unit price updated."})
        else:
            return JsonResponse({"success": False, "message": "No matching price found."})
    
    return JsonResponse({"success": False, "message": "Invalid request method."})

@login_required
def sales_fulfill_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='pending')
    
    if request.method == "POST":
        for item in order.order_items.all():
            # Record delivery for each order item
            Delivery.objects.create(
                order_item=item,
                volume_delivered=item.quantity,  # Assuming all quantity is delivered
                date=request.POST.get("delivery_date"),  # Pass delivery date from form
                created_by = request.user
            )
        # Update order status
        order.status = 'in_progress'
        order.fulfilled_by = request.user
        order.fulfilled_at = now()
        order.save()
        return redirect('aic_order_detail', order_id=order.id)

    return render(request, 'admin/sales/order/fulfill_order.html', {'order': order})

#+++<<<<<<<<<<<<<<<<<<<<<<<<<<<<<=

##############################################################################################################################
    ######## POINT OF SALES AND STOCK MOVEMENT MODULE ###############################################
@login_required
def sa_order_list(request):
    saleagent = request.user
    orders = (
        Order.objects.filter(created_by=saleagent)
        .prefetch_related(
            'order_items__harveststock__crop',
            'order_items__harveststock__cropvariety',
            'order_items__harveststock__grade',
            'order_items__harveststock__unit_price',
            'buyer'
        )
    )
    #Don't assign to the property
    return render(request, 'admin/sales/pos/order_list.html', {'orders': orders})

@login_required
def sa_order_detail(request, order_id):
    if request.user.is_authenticated: 
        # Get the specific order for the logged-in user
        order_items = get_object_or_404(Order, id=order_id)
        return render(request, 'admin/sales/pos/order_detail.html', {'order_items': order_items})
    else:
       return redirect('sa_order_list')  
   
@login_required
def sa_create_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order_request = form.save(commit=False)
            order_request.created_by = request.user
            try:
                saleagent = SaleAgent.objects.get(user=request.user)
                order_request.saleagent = saleagent
                order_request.save()
                return redirect('sa_edit_order', order_request.id)
            except SaleAgent.DoesNotExist:
                form.add_error(None, "SaleAgent profile not found for the logged-in user.")
    else:
        form = OrderForm(user=request.user)
    return render(request, 'admin/sales/pos/create_order.html', {'form': form})


@login_required
def sa_update_order(request, order_id):
    order_request = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order_request, user=request.user)  # Pass user
        if form.is_valid():
            form.save(user=request.user)  # Save with user context
            return redirect('sa_order_list')  # Redirect after update
    else:
        form = OrderForm(instance=order_request, user=request.user)  # Pass user

    return render(request, 'admin/sales/pos/create_order.html', {
        'form': form, 
        'order_request': order_request
    }) 

@login_required
def sa_add_order_item(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderItemForm(request.POST, user=request.user)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.order = order
            new_item.save()
            return JsonResponse({"success": True})
        return JsonResponse({
            "success": False,
            "form_html": render_to_string("admin/sales/pos/edit_order_item_form.html", {"form": form}, request=request)
        })
    else:
        form = OrderItemForm(user=request.user)
        return render(request, "admin/sales/pos/edit_order_item_form.html", {"form": form})

@login_required
def get_stock_unit_price(request):
    harveststock_id = request.GET.get('harveststock_id')
    try:
        harveststock = HarvestStockAggregate.objects.get(id=harveststock_id)
        price = harveststock.unit_price.selling_price  # Assuming this relationship
        return JsonResponse({'unit_price': price})
    except HarvestStockAggregate.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    
    
@login_required
def sa_edit_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    if request.method == "POST":
        form = OrderItemForm(request.POST, instance=order_item, user=request.user)
        
        if form.is_valid():
            form.save()            
            return JsonResponse({
                "success": True,
                "quantity": order_item.quantity,
                "total_cost": order_item.get_total_cost(),
                "unit_price": order_item.unit_price,
                "order_total": order_item.order.total_cost_sum
            })
            
        return JsonResponse({
            "success": False,
            "form_html": render_to_string("admin/sales/pos/edit_order_item_form.html", {"form": form, "order_item": order_item}, request=request)
        })
    else:
        #form = OrderItemForm(instance=order_item)
        form = OrderItemForm(instance=order_item, user=request.user)
        return render(request, "admin/sales/pos/edit_order_item_form.html", {"form": form, "order_item": order_item})

@login_required
def sa_edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    items = OrderItem.objects.filter(order=order)
    form = OrderForm(instance=order, user=request.user)
    
    item_form = OrderItemForm(user=request.user)
    #OrderItemFormSetClass = OrderItemFormSet(instance=order)
    return render(request, 'admin/sales/pos/update_order.html', {
        'form': form,
        'item_form': item_form,
        'items': items,
        'order': order
        #'OrderItemFormSetClass':OrderItemFormSetClass
    })



@login_required
def sa_order_spoilages(request):
    try:
        saleagent = request.user.sale_agent  # Uses related_name='sale_agent' from OneToOneField
    except SaleAgent.DoesNotExist:
        # Handle the case where the user is not linked to any SaleAgent
        return render(request, 'admin/sales/pos/order_spoilage_list.html', {'spoilages': [], 'error': 'No SaleAgent profile linked to this user.'})

    spoilages = Spoilage.objects.filter(
        orderitem__order__saleagent=saleagent
    ).select_related(
        'orderitem__order',
        'orderitem__harveststock__crop',
        'orderitem__harveststock__cropvariety',
        'orderitem__harveststock__grade'
    ).prefetch_related(
        'orderitem'
    )

    return render(request, 'admin/sales/pos/order_spoilage_list.html', {'spoilages': spoilages})


@login_required
def sa_record_order_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    #print(order_id)
    if request.method == 'POST':
        #form = OrderPaymentForm(request.POST, request.FILES)
        
        print(">>> About to validate form")
        form = OrderPaymentForm(request.POST, request.FILES)
        print(">>> form created:", form)

        if form.is_valid():
            try:
                payment = form.save(commit=False)
                payment.order = order
                payment.created_by = request.user
                payment.save()
                return JsonResponse({'success': True})
            except Exception as e:
                # Add full traceback to debug further if needed
                import traceback
                traceback.print_exc()
                messages.error(request, f"An error occurred: {str(e)}")
        return JsonResponse({
            'success': False,
            'form_html': render(
                request, 'admin/sales/pos/order_payment_form.html',
                {'form': form, 'order': order}
            ).content.decode()
        })

    else:
        form = OrderPaymentForm()
        return render(request, 'admin/sales/pos/order_payment_form.html', {'form': form, 'order': order})


@login_required
def sa_process_payment(request):
    #order = get_object_or_404(Order, pk=order_id)
    #print(order_id)
    if request.method == 'POST':
        #form = OrderPaymentForm(request.POST, request.FILES)
        
        print(">>> About to validate form")
        form = OrderPaymentForm(request.POST, request.FILES)
        print(">>> form created:", form)

        if form.is_valid():
            #try:
                payment = form.save(commit=False)
                #payment.order = order
                payment.created_by = request.user
                payment.save()
                messages.success(request, 'Payment recorded successfully!')
                redirect('sa_order_list')
                #return JsonResponse({'success': True})
                #messages.success(request, 'Payment recorded successfully!')
                return redirect('sa_order_list')
            #except Exception as e:
                # Add full traceback to debug further if needed
                #import traceback
                ##traceback.print_exc()
                messages.error(request, f"An error occurred: {str(e)}")
        return JsonResponse({
            'success': False,
            'form_html': render(
                request, 'admin/sales/pos/order_payment_form.html',
                {'form': form}
            ).content.decode()
        })

    else:
        form = OrderPaymentForm()
        return render(request, 'admin/sales/pos/order_payment_form.html', {'form': form, 'order': order})
        
        
        
        
@login_required
def order_payment_modal(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    form = PaymentForm()
    return render(request, 'partials/order_payment_modal.html', {
        'order': order,
        'form': form
    })
   
@login_required
@require_POST
@csrf_exempt  # if you're not using CSRF tokens in JS (optional - secure with token if possible)
def sa_confirm_spoilage(request, spoilage_id):
    spoilage = get_object_or_404(Spoilage, id=spoilage_id, status='Pending')  # Only allow if Pending

    if request.user.is_authenticated and hasattr(request.user, 'sale_agent'):
        note = request.POST.get('confirmation_note', '').strip()

        spoilage.status = 'Approved'
        spoilage.confirmed_by = request.user
        spoilage.confirmation_note = note
        spoilage.confirmed_at = timezone.now()
        spoilage.save()

        return JsonResponse({'success': True, 'message': 'Spoilage confirmed successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Permission denied or not a SaleAgent.'})


 ##############-------------------- PRINTNG INVOICE------------------################
@login_required
def generate_order_invoice_pdf(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        html_string = render_to_string('admin/sales/pos/invoice.html', {'order': order})
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=order_{order.id}_invoice.pdf'
        
        html.write_pdf(response)
        return response
    except Exception as e:
        # Print detailed traceback for debugging
        error_message = str(e)
        tb = traceback.format_exc()
        print("WeasyPrint Traceback:", tb)
        return HttpResponse(f"PDF generation failed: {error_message}\n\n{tb}")



@login_required
def preview_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/sales/pos/invoice.html', {'order': order})

@login_required
def print_all_orders(request):
    orders = Order.objects.all()
    return render(request, 'admin/sales/pos/print_orders.html', {'orders': orders})
 ##############-------------------- PRINTNG INVOICE------------------################
@login_required
def get_orderitem_details(request):
    harveststock_id = request.GET.get('harveststock_id')
    try:
        orderitem = HarvestStockAggregate.objects.get(id=harveststock_id)
        return JsonResponse({'unit_price': str(orderitem.unit_price.selling_price)})
    except OrderItem.DoesNotExist:
        return JsonResponse({'unit_price': ''})  # or '0' or None
#<<<<<<<<<<<<<<<=========================== END OF ORDERS ==============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#

@login_required
def sa_payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'admin/sales/pos/payment_list.html', {'payments': payments})

@login_required
def sa_payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'admin/sales/pos/payment_detail.html', {'payment': payment})

#stock transfer fulfilment
@login_required
def sa_fulfillment_list(request):
    fulfillments = Fulfillment.objects.all()
    return render(request, 'admin/sales/pos/fulfillment_list.html', {'fulfillments': fulfillments})

#stock transfer fulfilment
@login_required
def sa_fulfillment_detail(request, pk):
    fulfillment = get_object_or_404(Fulfillment, pk=pk)
    return render(request, 'admin/sales/pos/fulfillment_detail.html', {'fulfillment': fulfillment})
        ######## END OF POINT OF SALES AND STOCK MOVEMENT MODULE ###############################################
##############################################################################################################################


############################################### STOCK MOVEMENT ################################################################
#load crop viriety based on crop selected

@login_required
def load_crop_varieties(request):
    crop_id = request.GET.get('crop_id')
    crop_varieties = CropVariety.objects.filter(crop=crop_id).values('id', 'name')
    return JsonResponse(list(crop_varieties), safe=False)


@login_required
@require_POST
def check_stock_balance(request):
    sale_agent = get_object_or_404(SaleAgent, user=request.user)
    
    try:
        data = json.loads(request.body)
        

        market_centre_id = sale_agent.marketingcentre  # Assuming the user belongs to a market centre
        
        crop_id = data.get('crop')
        cropvariety_id = data.get('cropvariety')
        grade_id = data.get('grade')
        unit_id = data.get('unit')

        stock = HarvestStockAggregate.objects.filter(
            market_centre_id=market_centre_id,
            crop_id=crop_id,
            cropvariety_id=cropvariety_id,
            grade_id=grade_id,
            unit_id=unit_id,
        ).aggregate(total=Sum('total_quantity'))['total'] or 0

        return JsonResponse({'success': True, 'stock': float(stock)})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@login_required
def create_harvest_movement(request):
    sale_agent = get_object_or_404(SaleAgent, user=request.user)

    if request.method == 'POST':
        form = HarvestMovementForm(request.POST, sale_agent=sale_agent)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.from_market_centre = sale_agent.marketingcentre
            movement.created_by = request.user
            movement.save()
            return redirect('movement_list')  # Redirect to list page after creation
    else:
        form = HarvestMovementForm(sale_agent=sale_agent)

    return render(request, 'admin/sales/pos/movement_create.html', {'form': form})

@login_required
def movement_list(request):
    sale_agent = get_object_or_404(SaleAgent, user=request.user)
    
    movements = HarvestMovement.objects.filter(
        Q(from_market_centre=sale_agent.marketingcentre) | 
        Q(to_market_centre=sale_agent.marketingcentre)
    ).order_by('-movement_date')
    
    return render(request, 'admin/sales/pos/movement_list.html', {'movements': movements})

@login_required
def confirm_movement_receipt(request, movement_id):
    try:
        saleagent = request.user.sale_agent  # get the related SaleAgent instance
    except SaleAgent.DoesNotExist:
        return render(request, 'errors/403.html', status=403)

    movement = get_object_or_404(
        HarvestMovement,
        id=movement_id,
        to_market_centre=saleagent.marketingcentre  # compare instances, not nested relations
        #movement_date=saleagent.marketingcentre
    )

    if request.method == 'POST':
        movement.confirm_receipt(user=request.user)
        return redirect('movement_list')

    return render(request, 'admin/sales/pos/movement_confirmation.html', {'movement': movement})


#--------------------------------------------------------------------------
# Harvest Movement (Stock Transfer)
@login_required
def sa_transfer_stock(request):
    if request.method == 'POST':
        form = HarvestMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()
            messages.success(request, 'Stock transfer initiated!')
            return redirect('sa_stock_movement_list')
    else:
        form = HarvestMovementForm()
    return render(request, 'admin/sales/pos/transfer_stock.html', {'form': form})

# Stock Movement List View
@login_required
def sa_stock_movement_list(request):
    movements = HarvestMovement.objects.all()
    return render(request, 'admin/sales/pos/stock_movement_list.html', {'movements': movements})

# Confirm Stock Reception
@login_required
def sa_confirm_stock_reception(request, movement_id):
    movement = get_object_or_404(HarvestMovement, id=movement_id, received=False)
    try:
        movement.confirm_receipt(request.user)
        messages.success(request, 'Stock received successfully!')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('sa_stock_movement_list')
############################################### END OF STOCK MOVEMENT #########################################################




##################################################3 REPORTING AND DOWNLOADABLES ########################################################

@login_required
def sa_harvest_report(request):
    records = Harvest.objects.select_related('crop','cropvariety','grade').order_by('-date')
    return render(request, 'admin/sales/reports/harvest_report.html', {'records': records})


@login_required
def sa_harvest_report_pdf(request):
    records = Harvest.objects.all()
    html = render_to_string('admin/sales/reports/harvest_report.html', {'records': records})
    resp = HttpResponse(content_type='application/pdf')
    HTML(string=html).write_pdf(resp)
    return resp

@login_required
def sa_harvest_report_excel(request):
    records = Harvest.objects.all().values(
        'date', 'crop__name', 'cropvariety__name', 'grade__name', 'quantity', 'confirmation'
    )
    df = pd.DataFrame(records)

    # Convert timezone-aware datetimes to naive
    if 'date' in df.columns and pd.api.types.is_datetime64tz_dtype(df['date']):
        df['date'] = df['date'].dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=harvest_report.xlsx'
    df.to_excel(response, index=False)
    return response

############# Stock Aggregate
def sa_stock_aggregate_report(request):
    records = HarvestMovement.objects.select_related('from_market_centre','to_market_centre','grade','crop','cropvariety','grade','unit').order_by('-movement_date') 
    return render(request, 'admin/sales/reports/stock_movement_report.html', {'records': records})

@login_required
def sa_stock_aggregate_report_excel(request):
    records = HarvestMovement.objects.all().values(
        'movement_date', 'crop__name', 'cropvariety__name', 'grade__name', 'unit__name', 'quantity','from_market_centre__name','to_market_centre__name', 'received'
    )
    df = pd.DataFrame(records)

    # Convert timezone-aware datetimes to naive
    if 'movement_date' in df.columns and pd.api.types.is_datetime64tz_dtype(df['movement_date']):
        df['movement_date'] = df['movement_date'].dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=stock_movement_report.xlsx'
    df.to_excel(response, index=False)
    return response



############# Stock Movement
def sa_stock_movement_report(request):
    records = HarvestMovement.objects.select_related('from_market_centre','to_market_centre','grade','crop','cropvariety','grade','unit').order_by('-movement_date') 
    return render(request, 'admin/sales/reports/stock_movement_report.html', {'records': records})

@login_required
def sa_stock_movement_report_excel(request):
    records = HarvestMovement.objects.all().values(
        'movement_date', 'crop__name', 'cropvariety__name', 'grade__name', 'unit__name', 'quantity','from_market_centre__name','to_market_centre__name', 'received'
    )
    df = pd.DataFrame(records)

    # Convert timezone-aware datetimes to naive
    if 'movement_date' in df.columns and pd.api.types.is_datetime64tz_dtype(df['movement_date']):
        df['movement_date'] = df['movement_date'].dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=stock_movement_report.xlsx'
    df.to_excel(response, index=False)
    return response


def sa_sales_order_report(request):
    orders = Order.objects.prefetch_related('order_items','payments').select_related('buyer','sales_agent')
    return render(request, 'admin/sales/reports/sales_order_report.html', {'orders': orders})

@login_required
def sales_order_report_excel(request):
    #orders = Order.objects.select_related('buyer', 'created_by').prefetch_related('payments').all()
    orders = Order.objects.select_related('buyer', 'sales_agent__marketingcentre', 'created_by').prefetch_related('payments').all()
    
    records = []
    for order in orders:
        sales_agent = order.sales_agent
        marketing_centre_name = sales_agent.marketingcentre.name if sales_agent and sales_agent.marketingcentre else "N/A"
        records.append({
            'Order ID': order.id,
            'Market Centre': marketing_centre_name,
            'Buyer': order.buyer.client_name if order.buyer else '',
            'Sales Agent': order.created_by.username if order.created_by else '',
            'Order Date': order.order_date, 
            'Status': order.status.title(),
            'Sale Order Type': order.get_sale_order_type_display(),
            'Is Paid': 'Yes' if order.is_paid else 'No',
            'Total Items': order.total_items,
            'Total Amount': order.total_amount,
            'Total Paid': order.total_paid,
            'Amount Due': order.amount_due,
            'Delivery Date': order.delivery_date,
            'Created At': order.created_at,
        })
        
    df = pd.DataFrame(records)

    # Remove timezone if any
    for col in ['Order Date', 'Delivery Date', 'Created At']:
        if col in df.columns and pd.api.types.is_datetime64tz_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_order_report.xlsx'
    df.to_excel(response, index=False)
    return response


##################################################3 REPORTING AND DOWNLOADABLES ########################################################



######################################## SALES DASHBOARD AND REPORTS ####################################################################
def sa_export_pdf_report(request, report_type):
    context = sa_get_report_context(report_type)
    html = render_to_string(f'reports/{report_type}.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}.pdf"'

    result = pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response)
    if result.err:
        return HttpResponse('Error generating PDF', status=500)
    return response



def sa_export_excel_report(request, report_type):
    context = sa_get_report_context(report_type)
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    data = context['data']
    if data:
        headers = list(data[0].keys())
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        for row_num, row in enumerate(data, 1):
            for col_num, key in enumerate(headers):
                worksheet.write(row_num, col_num, str(row[key]))
    workbook.close()
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={report_type}.xlsx'
    return response



def sa_get_report_context(report_type):
    if report_type == 'harvest':
        data = Harvest.objects.values(
            'crop__name', 'cropvariety__name', 'beneficiary__full_name', 'quantity', 'total_price', 'confirmation'
        )
    elif report_type == 'stock':
        data = HarvestStockAggregate.objects.values(
            'market_centre__name', 'crop__name', 'grade__name', 'total_quantity', 'total_value'
        )
    elif report_type == 'movement':
        data = HarvestMovement.objects.values(
            'from_market_centre__name', 'to_market_centre__name', 'crop__name', 'quantity', 'movement_date', 'received'
        )
    elif report_type == 'orders':
        data = Order.objects.values(
            'buyer__full_name', 'status', 'total_amount', 'order_date'
        )
    elif report_type == 'payments':
        data = Payment.objects.values(
            'order__id', 'amount_paid', 'payment_method', 'payment_status', 'payment_date'
        )
    elif report_type == 'balances':
        data = Balance.objects.values(
            'order__id', 'total_due', 'amount_paid', 'created_at'
        )
    else:
        data = []
    return {'data': list(data)}
############################################# END OF SALES DASHBOARD##################################################