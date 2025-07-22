from datetime import datetime, timedelta
from django.utils.timezone import now
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db.models import Sum, F, Count, DecimalField, Value, ExpressionWrapper, Exists, OuterRef
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from yuapp.models import AIC, Buyer, CashAssigned, CropVariety, HeightData, IrrigationData, NurseryData, PriceTable, SupervisorAttendance, Todo, InputDistribution,  ProductUnit, Grade, Crop, Greenhouse, GreenhouseRoom, Invoice, InvoicePayment, Beneficiary, Repayment, Supervisor, Transaction, Order, OrderItem, Payment, Delivery, Harvest, TrellisingData, TrendKnowledgeBank, TrendKnowledgeDiscussion
from fieldmate.forms import TrendKnowledgeBankForm, TrendKnowledgeDiscussionForm
from .forms import *
from yuapp.forms import TodoForm



# Create your views here.
@login_required
def aic_price_index(request):
    if request.user.is_authenticated:        
        prices = PriceTable.objects.filter(created_by = request.user.id)
        return render(request, 'admin/aic/price/index.html', {'prices':prices})
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
def aic_create_beneficiary(request):
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the beneficiary instance without committing to set additional fields
            beneficiary = form.save(commit=False)
            beneficiary.created_by = request.user  # Set the logged-in user as the creator

            # Save the beneficiary instance
            beneficiary.save()

            # Clear any previous crops, if necessary
            beneficiary.crops.clear()  
            # Add selected crops to the beneficiary
            crops = form.cleaned_data.get('crops')
            if crops:
                beneficiary.crops.set(crops)  # This will automatically create entries in the beneficiary_crops table
           
            assigned_greenhouse_room = form.cleaned_data.get('assigned_tunnel')  # Adjust this field name as necessary
            if assigned_greenhouse_room:
                # Set assign to 0 in the corresponding GreenhouseRoom record
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_greenhouse_room.id)  # Fetch the greenhouse room
                greenhouse_room.assign = 0  # Set assign to 0
                greenhouse_room.save()  # Save the updated greenhouse room
                
                
            # Extract first name and create the username
            #use email as username if valid email exist else use function to create unique username
            email = beneficiary.email  # Assuming 'email' is a field in the Beneficiary model
            if email and '@' in email:  # Basic validation for a valid email
                username = email
            else:
                first_name = beneficiary.full_name.split()[0].lower()   # Assuming full_name is a field in Beneficiary model
                unique_id = int(time.time()) % 100000   # Get the current time as a unique ID
                username = f"{first_name}_y{unique_id:05}"  # Construct the username
            
            password = 'YugepGhana@123'  # Default password (should be changed later)
            new_user = User.objects.create(
                username=username,
                password=make_password(password),  # Encrypt the password
                email=beneficiary.email,
                first_name=beneficiary.full_name.split()[0].lower(),  # Extract first name from full name
                last_name=" ".join(beneficiary.full_name.split()[1:])  # Rest of the name as last name
            )

               # Assign the existing 'beneficiary' group
            beneficiary_group = Group.objects.get(name='Beneficiary')
            new_user.groups.add(beneficiary_group)

            # Save the user and set any other required fields
            new_user.save()

            messages.success(request, 'Beneficiary created successfully! A user account has also been created.')
            return redirect('aic_beneficiary_index')  # Redirect to beneficiary login or desired page
        else:
            print(form.errors)
            messages.error(request, 'Error creating beneficiary. Please check the form.')
    else:
        form = BeneficiaryForm()

    return render(request, 'admin/aic/beneficiary/create_beneficiary.html', {'form': form})

@login_required
def aic_update_beneficiary(request, beneficiary_id):
    # Fetch the existing beneficiary using the ID
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)

    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, request.FILES, instance=beneficiary)
        if form.is_valid():
            # Save the beneficiary instance without committing to set additional fields
            beneficiary = form.save(commit=False)
            beneficiary.modified_by = request.user  # Assuming there is a 'modified_by' field for tracking updates
            
            # Save the updated beneficiary instance
            beneficiary.save()

            # Clear any previous crops, if necessary
            beneficiary.crops.clear()
            # Add selected crops to the beneficiary
            crops = form.cleaned_data.get('crops')
            if crops:
                beneficiary.crops.set(crops)  # This will automatically update entries in the beneficiary_crops table
            
            assigned_greenhouse_room = form.cleaned_data.get('assigned_tunnel')  # Adjust this field name as necessary
            if assigned_greenhouse_room:
                # Set assign to 0 in the corresponding GreenhouseRoom record
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_greenhouse_room.id)  # Fetch the greenhouse room
                greenhouse_room.assign = 0  # Set assign to 0
                greenhouse_room.save()  # Save the updated greenhouse room
            
            messages.success(request, 'Beneficiary updated successfully!')
            return redirect('aic_beneficiary_index')  # Redirect to the desired page after update
        else:
            print(form.errors)
            messages.error(request, 'Error updating beneficiary. Please check the form.')
    else:
        form = BeneficiaryForm(instance=beneficiary)

    return render(request, 'admin/aic/beneficiary/create_beneficiary.html', {'form': form, 'beneficiary': beneficiary})

 
@login_required
def aic_beneficiary_index(request):
    if request.user.is_authenticated:        
        beneficiaries = Beneficiary.objects.all()
        return render(request, 'admin/aic/beneficiary/index.html', {'beneficiaries':beneficiaries})
    else:
       return redirect('aic_beneficiary_index')


@login_required
def aic_beneficiary_detail(request, beneficiary_id):
    # Get the specific beneficiary for the logged-in user
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    
     # Fetch related records
    harvests = beneficiary.beneficiary_harvest.all()  # Assuming `Harvest` has a ForeignKey to `Beneficiary` check related_name from harvest models
    coworkers = beneficiary.workers.all()  # Correctly use `related_name='workers'` check related_name from worker models
    contracts = beneficiary.contracts.all()  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    cashloans = beneficiary.cashloans.all()  # Assuming `CashAssigned` has a ForeignKey to `Beneficiary` check related_name from cash_assigned models
    tunnel = beneficiary.assigned_tunnel  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    edo = beneficiary.assigned_edo  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    
    # Count workers by gender
    workers_by_gender = coworkers.values('gender').annotate(total=Count('id'))
    # Prepare data for the pie chart
    gender_labels = [item['gender'] for item in workers_by_gender]
    gender_totals = [item['total'] for item in workers_by_gender]
        
    #harvest associated quantity and sales amount
     # Safely calculate total_quantity and total_sum
    total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvests)
    total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvests)

    
    # Pass all records to the template
    context = {
        'beneficiary': beneficiary,
        'harvests': harvests,
        'coworkers': coworkers,
        'contracts': contracts,
        'cashloans':cashloans,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'workers_by_gender': workers_by_gender,
        'gender_labels': gender_labels,
        'gender_totals': gender_totals,
        'tunnel':tunnel,
        'edo':edo
    }
    
    return render(request, 'admin/aic/beneficiary/profile.html', context)


@login_required
def aic_cash_loaned_list(request):
    cash_load_records = CashAssigned.objects.prefetch_related('repayment_set').all()
    return render(request, 'admin/aic/finance/cashloan_list.html', {'cash_load_records': cash_load_records})

@login_required
def aic_cashloan_detail(request, cashload_id):
    # Get all cash loan records where the beneficiary is assigned to the logged-in supervisor
    loan = get_object_or_404(CashAssigned, id=cashload_id)
    cash_load_records = CashAssigned.objects.filter(id=cashload_id).prefetch_related('repayment_set')
    #beneficiary = Beneficiary.objects.filter(id = beneficiary_id)
    beneficiary = get_object_or_404(Beneficiary, id=loan.beneficiary.id)
    return render(request, 'admin/aic/finance/cashloan_detail.html', {'cash_load_records': cash_load_records, 'beneficiary':beneficiary})


#Financials
@login_required
def aic_pricetale_index(request):
    if request.user.is_authenticated:        
        prices = PriceTable.objects.all()
        return render(request, 'admin/aic/finance/pricetable.html', {'prices':prices})
    else:
       return redirect('aic_pricetale_index')

@login_required
def aic_create_pricetable(request):
    if request.method == 'POST':
        form = PriceTableForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Pass the user to save method
            return redirect('aic_pricetale_index')
    else:
        form = PriceTableForm()
        return render(request, 'admin/aic/finance/create.html', {'form':form})  

@login_required
def aic_update_price_table(request, pk):
    price_table = get_object_or_404(PriceTable, pk=pk)
    if request.method == 'POST':
        form = PriceTableForm(request.POST, instance=price_table)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('aic_pricetale_index')  # Redirect to the list or any other page
    else:
        form = PriceTableForm(instance=price_table)

    return render(request, 'admin/aic/finance/create.html', {'form':form}) 

@login_required
def aic_price_detail(request, price_id):
    if request.user.is_authenticated: 
        # Get the specific order for the logged-in user
        price = get_object_or_404(PriceTable, id=price_id)
        return render(request, 'admin/aic/price/detail.html', {'price': price})
    else:
       return redirect('beneficiary_login')
     
@login_required
def aic_create_price(request):
    if request.method == 'POST':
        form = PriceTableForm(request.POST)
        if form.is_valid():
            crop = form.cleaned_data['crop']
            grade = form.cleaned_data['grade']
            unit = form.cleaned_data['unit']
            price = form.cleaned_data['price']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            notes = form.cleaned_data['notes']

            # Check if a PriceTable with the same crop, grade, unit, from_date, and to_date already exists
            existing_price_table = PriceTable.objects.filter(
                crop=crop,
                grade=grade,
                unit=unit,
                price=price,
                from_date=from_date,
                to_date=to_date,
                notes=notes
            ).exists()

            if existing_price_table:
                # If an entry already exists, show a message and don't create a new one
                messages.error(request, "A price table with this crop, grade, unit, and date range already exists.")
            else:
                # Create the new PriceTable entry
                price_table = form.save(commit=False)
                price_table.created_by = request.user
                price_table.save()
                messages.success(request, "Price table created successfully.")
                return redirect('price_index')  # Redirect to a list or success page
    else:
        form = PriceTableForm()
    return render(request, 'admin/aic/price/create.html', {'form': form})


#update price record
@login_required
def aic_price_update(request, pk):
    price = get_object_or_404(PriceTable, pk=pk)
    
    if request.method == 'POST':
        # Pass the existing instance to update instead of creating a new one
        form = PriceTableForm(request.POST, instance=price)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Price table updated successfully.')
            return redirect('price_index')  # Redirect to the desired page after update
    else:
        # Pre-populate the form with the existing price table record
        form = PriceTableForm(instance=price)
    
    return render(request, 'admin/aic/price/create.html', {'form': form, 'price':price})


@login_required
def aic_harvest_index(request):
    if request.user.is_authenticated:        
        harvests = Harvest.objects.all()
        return render(request, 'admin/aic/harvest/index.html', {'harvests':harvests})
    else:
       return redirect('beneficiary_login')
   
#Harvest records for AIC
@login_required
def aic_beneficiary_harvest(request, beneficiary_id):
    # Get the beneficiary based on the beneficiary_id
    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_id)    
    # Fetch the harvest records specifically assigned to this beneficiary
    assigned_harvest_records = Harvest.objects.filter(beneficiary=beneficiary)    
    #assigned_harvest_records = Harvest.objects.filter(assigned=True)  # Adjust the queryset as needed
    # Sum the quantity and total_price fields
    total_quantity = assigned_harvest_records.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price = assigned_harvest_records.aggregate(Sum('total_price'))['total_price__sum'] or 0                
  
    return render(request, 'admin/aic/beneficiary/harvest.html', {
        'beneficiary': beneficiary,
        'assigned_harvest_records': assigned_harvest_records,
        'total_quantity':total_quantity,
        'total_price':total_price
    })


@login_required
def aic_harvest_history(request):
    # Fetch all harvest records without filtering by beneficiary
    harvest_records = Harvest.objects.all()
    
    # Calculate total quantity and total price for all records
    total_quantity = harvest_records.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price = harvest_records.aggregate(Sum('total_price'))['total_price__sum'] or 0
                
    return render(request, 'admin/aic/harvest/allrecords.html', {
        'assigned_harvest_records': harvest_records,
        'total_quantity': total_quantity,
        'total_price': total_price
    })

# #sales dashboard
# def aic_sales_dashboard(request):
#     # Total order placed (value)
#     total_orders = Order.objects.aggregate(total_paid=Sum('amount_paid'))
    
#     # Volume of crop purchased
#     total_volume_purchased = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE).aggregate(total_volume=Sum('volume'))['total_volume']
    
#     # Total payments (value)
#     total_payments = Payment.objects.aggregate(total_paid=Sum('amount_paid'))['total_paid']
    
#     # Total deliveries made (volume)
#     total_volume_delivered = Delivery.objects.aggregate(total_delivered=Sum('volume_delivered'))['total_delivered']
    
#     # Overview of debtors (buyers vs arrears)
#     total_due_per_buyer = Transaction.objects.filter(buyer__isnull=False).annotate(
#         total_due=F('total_price') - Sum('payment__amount_paid')
#     ).values('buyer__client_name', 'total_due')  # Changed 'buyer__name' to 'buyer__client_name'

#     # Total cash sales
#     total_cash_sales = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE, buyer__isnull=False).aggregate(total_cash=Sum('total_price'))['total_cash']
    
#     context = {
#         'total_volume_purchased': total_volume_purchased,
#         'total_payments': total_payments,
#         'total_volume_delivered': total_volume_delivered,
#         'total_due_per_buyer': total_due_per_buyer,
#         'total_cash_sales': total_cash_sales,
#     }
    
#     return render(request, 'admin/aic/market/sales_dashboard.html', context)

#ORDER MODULE
@login_required
def aic_all_orders(request):
    # Get all orders for the currently logged-in user
    if request.user.is_authenticated: 
        aic = request.user
        orders = Order.objects.all()
        # Render a template that displays all the orders
        return render(request, 'admin/aic/order/orders.html', {'orders': orders})
    else:
       return redirect('login')

@login_required
def aic_order_detail(request, order_id):
    # Get the specific order for the logged-in user
    order = get_object_or_404(Order, id=order_id)

    # Get all the order items for this order
    order_items = order.order_items.all()

    # Render a template that displays the order and its items
    return render(request, 'admin/aic/order/detail.html', {
        'order': order,
        'order_items': order_items
    })


@login_required
def aic_fulfill_order(request, order_id):
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

    return render(request, 'admin/aic/order/fulfill_order.html', {'order': order})


@login_required
def aic_process_payment(request, order_id):
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

        return redirect('aic_order_detail', order_id=order.id)
    return render(request, 'admin/aic/order/process_payment.html', {'order': order}) 
#END OF ORDER MODULE


@login_required
def aic_market_dashboard(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
    except Buyer.DoesNotExist:
        buyer = None

    todos = Todo.objects.filter(created_by=request.user)
    form = TodoForm()

    # Step 2: Aggregate transaction data related to the Buyer
    total_volume_purchased = Transaction.objects.filter(
        aic__in=AIC.objects.filter(user=request.user), transaction_type=Transaction.CROP_PURCHASE
    ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0

    total_volume_delivered = Delivery.objects.filter(
        order_item__order__buyer=buyer
    ).aggregate(total_delivered=Sum('volume_delivered'))['total_delivered'] or 0

    # ✅ Fixed Query: Get total payments received from buyers
    total_payments_received = Payment.objects.filter(
        order__buyer=buyer  # Corrected
    ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0

    # Step 3: Order and Delivery summary
    total_orders = Order.objects.filter(buyer=buyer).count()
    total_deliveries = Delivery.objects.filter(order_item__order__buyer=buyer).count()

    # Prepare data for charts (example with order statuses)
    order_status_counts = Order.objects.filter(buyer=buyer).values('status').annotate(count=Count('status'))

    # Prepare context
    context = {
        'total_volume_purchased': total_volume_purchased,
        'total_volume_delivered': total_volume_delivered,
        'total_payments_received': total_payments_received,  # Fixed
        'total_orders': total_orders,
        'total_deliveries': total_deliveries,
        'order_status_counts': order_status_counts,
        'todos': todos,
        'form': form
    }

    return render(request, 'admin/aic/market/sales_dashboard.html', context)


@login_required
def aic_edo(request):

    if request.user.is_authenticated:        
        beneficiary = Beneficiary.objects.get(user=request.user)
        #beneficiary = Beneficiary.objects.get(id=some_beneficiary_id)  # Get a specific beneficiary
        supervisor = beneficiary.assigned_edo  # This will give you the assigned supervisor instance

        return render(request, 'admin/aic/edo.html', {'edo':supervisor})
    else:
       return redirect('beneficiary_login')



@login_required
def aic_edo_detail(request, edo_id):
    if request.user.is_authenticated:  
        # Fetch the supervisor object
        edo = get_object_or_404(Supervisor, id=edo_id)
        # Fetch the current logged-in user's beneficiary record (assuming one-to-one relationship)
        beneficiary = Beneficiary.objects.filter(user=request.user).first()
        # Greenhouses assigned to this supervisor
        supervisor_greenhouses = edo.greenhouse.all()
        # Greenhouses that are also assigned to the current beneficiary
        beneficiary_greenhouses = beneficiary.crops.all() if beneficiary else None
        # Cities assigned to this supervisor
        supervisor_cities = edo.city.all()
        context = {
            'beneficiary': beneficiary,
            'edo': edo,
            'supervisor_greenhouses': supervisor_greenhouses,
            'beneficiary_greenhouses': beneficiary_greenhouses,
            'supervisor_cities': supervisor_cities,
        }
       
        
        return render(request, 'admin/aic/edo_detail.html', context)
    
@login_required
def aic_view_harvest(request, harvest_id):
    # Retrieve the specific Harvest record by ID
    harvest = get_object_or_404(Harvest, id=harvest_id)
    #price = harvest.price_record
     # Retrieve the associated PriceTable instance directly
    price_table = harvest.price_record
    # if price_table:
    return render(request, 'admin/aic/harvest/view_harvest.html', {
        'harvest': harvest, 'price_table':price_table
    })

@login_required
def aic_create_distribute_input(request):
    aic = get_object_or_404(AIC, user=request.user)

    if request.method == 'POST':
        form = InputEdoDistributionForm(request.POST, aic=aic)
        if form.is_valid():
            distribution = form.save(commit=False)
            distribution.distributed_by = aic

            # Retrieve the unit cost from the selected farm input
            farm_input = distribution.farm_input
            distribution.unit_cost = farm_input.cost_per_unit  # Set unit cost
            
             # Calculate the total cost
            distribution.total_cost = distribution.quantity * distribution.unit_cost  # Calculate total cost
            distribution.created_by = request.user

            # Save the distribution
            distribution.save()

            return redirect('aic_distribution_list')
    else:
        form = InputEdoDistributionForm()

    return render(request, 'admin/aic/farminput/create_distribute_input.html', {'form': form})


# @login_required
# def aic_distribution_list(request):
#     distributions = InputEdoDistribution.objects.all().order_by('-distribution_date')
#     return render(request, 'admin/aic/farminput/distribution_list.html', {'distributions': distributions})
@login_required
def aic_distribution_list(request):
    distributions = InputEdoDistribution.objects.select_related(
        'supervisor__user',
        'farm_input__inputcategory',
        'distributed_by__user'
    ).prefetch_related(
        'supervisor__greenhouse'
    ).order_by('-distribution_date')
    return render(request, 'admin/aic/farminput/distribution_list.html', {'distributions': distributions})
#end farm input distribution


#farm input distribution to beneficiaries
@login_required
def aic_edo_distribution(request, edo_id):
    edo = get_object_or_404(Supervisor, id=edo_id)
    distributions = InputEdoDistribution.objects.filter(edo=edo).order_by('-distribution_date')
    
    return render(request, 'admin/aic/farminput/edo_distribute.html', 
                  {
                      'distributions': distributions, 
                      'edo': edo
                    }
                  )

#
# @login_required
# def aic_get_available_quantity(request):
#     farm_input_id = request.GET.get('farm_input_id')
#     try:
#         farm_input = FarmInput.objects.get(id=farm_input_id)
#         return JsonResponse({
#             'available_quantity': farm_input.available_quantity,
#             'initial_quantity': farm_input.quantity_received
#         })
#     except FarmInput.DoesNotExist:
#         return JsonResponse({'error': 'Farm input not found'}, status=404)
    
#dynamically show price, available quantity on the form
@login_required
def get_farm_input_details(request):
    farm_input_id = request.GET.get('farm_input_id')
    aic = AIC.objects.get(user=request.user)

    try:
        farm_input = FarmInput.objects.get(pk=farm_input_id)
        distributed_quantity = InputEdoDistribution.objects.filter(
            farm_input=farm_input, distributed_by=aic
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        available_quantity = farm_input.quantity_received - distributed_quantity

        return JsonResponse({
            'price': farm_input.cost_per_unit,
            'available_quantity': available_quantity
        })
    except FarmInput.DoesNotExist:
        return JsonResponse({'error': 'Invalid farm input selected'}, status=400)


# @login_required
# def get_farm_input_details(request):
#     farm_input_id = request.GET.get('farm_input_id')
#     aic = AIC.objects.get(user=request.user)
#     print(farm_input_id)
#     try:
#         farm_input = FarmInput.objects.get(pk=farm_input_id, aic_distributions__distributed_by=aic)
#         #print(farm_input)
#         distributed_quantity = InputEdoDistribution.objects.filter(
#             farm_input=farm_input, distributed_by=aic
#         ).aggregate(Sum('quantity'))['quantity__sum'] or 0
#         available_quantity = farm_input.initial_quantity - distributed_quantity
        
#         return JsonResponse({
#             'price': farm_input.cost_per_unit,
#             'available_quantity': available_quantity
#         })
#     except FarmInput.DoesNotExist:
#         return JsonResponse({'error': 'Invalid farm input selected'}, status=400)

#farm_input = FarmInput.objects.get(pk=farm_input_id, aic_distributions__distributed_by=aic)  # Use the correct related name


#end farm input distribution to beneficiaries

#farm input received from input dealer
#create
@login_required
def aic_add_farm_input(request):
    if request.method == 'POST':
        form = FarmInputForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('aic_farm_input_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        form = FarmInputForm()

    return render(request, 'admin/aic/farminput/create_farminput.html', {'form': form})

#update

@login_required
def aic_update_farm_input(request, input_id):
    # Retrieve the existing FarmInput instance
    farm_input = get_object_or_404(FarmInput, id=input_id)

    if request.method == 'POST':
        form = FarmInputForm(request.POST, request.FILES, instance=farm_input)
        if form.is_valid():
            # Save the updated FarmInput instance
            farm_input = form.save(commit=False)
            # farm_input.created_by = request.user
            if farm_input.confirmation != 0:
                farm_input.confirm_by = request.user
            farm_input.save()
            return redirect('aic_farm_input_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = FarmInputForm(instance=farm_input)

    return render(request, 'admin/aic/farminput/create_farminput.html', {'form': form, 'farm_input': farm_input})

#list
@login_required
def aic_farm_input_list(request):
    farm_inputs = FarmInput.objects.all().order_by('-created_at')
    
    #farm_inputs = FarmInput.objects.all().order_by('-created_at')
    farm_input_data = []

    for farm_input in farm_inputs:
        distributed_quantity = InputEdoDistribution.objects.filter(
            farm_input=farm_input
        ).aggregate(total_distributed=Sum('quantity'))['total_distributed'] or 0
        
        available_quantity = farm_input.quantity_received - distributed_quantity
        totalCost = farm_input.quantity_received * farm_input.cost_per_unit
        
        farm_input_data.append({
            'farm_input': farm_input,
            'distributed_quantity': distributed_quantity,
            'available_quantity': available_quantity,
            'totalcost':totalCost
        })
        
    return render(request, 'admin/aic/farminput/list_farminput.html', {'farm_inputs': farm_inputs, 'farm_input_data': farm_input_data})

#End of farm input received from input dealer


#input dealer module
@login_required
def aic_input_dealer_list(request):
    inputdealers = InputDealer.objects.all().order_by('-created_at')
    return render(request, 'admin/aic/farminput/inputdealer.html', {'inputdealers': inputdealers})

@login_required
def aic_create_inputdealer(request):
    if request.method == 'POST':
        form = InputDealerForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('aic_input_dealer_list')
    else:
        form = InputDealerForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/aic/farminput/create_input_dealer.html', {'form': form})

@login_required
def aic_update_farm_inputdealer(request, inputdealer_id):
    # Retrieve the existing FarmInput instance
    inputdealer = get_object_or_404(InputDealer, id=inputdealer_id)

    if request.method == 'POST':
        form = InputDealerForm(request.POST, request.FILES, instance=inputdealer)
        if form.is_valid():
            # Save the updated FarmInput instance
            inputdealer = form.save(commit=False)
            # inputdealer.created_by = request.user
            # if farm_input.confirmation != 0:
            #     farm_input.confirm_by = request.user
            inputdealer.save()
            return redirect('aic_input_dealer_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = InputDealerForm(instance=inputdealer)

    return render(request, 'admin/aic/farminput/create_input_dealer.html', {'form': form, 'inputdealer': inputdealer})


#farm input category modeule
@login_required
def aic_input_category_list(request):
    inputcats = FarmInputCategory.objects.all().order_by('-created_at')
    return render(request, 'admin/aic/farminput/inputcategory.html', {'inputcats': inputcats})

@login_required
def aic_create_input_category(request):
    if request.method == 'POST':
        form = FarmInputCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('aic_input_category_list')
    else:
        form = FarmInputCategoryForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/aic/farminput/create_input_category.html', {'form': form})

@login_required
def aic_update_input_category(request, inputcategory_id):
    # Retrieve the existing FarmInput instance
    inputcategory = get_object_or_404(FarmInputCategory, id=inputcategory_id)

    if request.method == 'POST':
        form = FarmInputCategoryForm(request.POST, request.FILES, instance=inputcategory)
        if form.is_valid():
            # Save the updated FarmInput instance
            inputcategory = form.save(commit=False)
            # inputcategory.created_by = request.user
            # if farm_input.confirmation != 0:
            #     farm_input.confirm_by = request.user
            inputcategory.save()
            return redirect('aic_input_dealer_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = FarmInputCategoryForm(instance=inputcategory)

    return render(request, 'admin/aic/farminput/create_input_category.html', {'form': form, 'inputcategory': inputcategory})


#BUYER MODULE
@login_required
def aic_buyer_index(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        # Fetch all ChangingRoom assignments for this specific beneficiary
        buyers = Buyer.objects.all()

        return render(request, 'admin/aic/buyer/buyer.html', {
            'buyers': buyers,
        })
    else:
        return redirect('beneficiary_login')

#tracking of supervisor attendance
@login_required
def aic_attendance_list(request):
    attendance_records = SupervisorAttendance.objects.select_related('supervisor', 'greenhouse').all()
    return render(request, 'admin/aic/edo/attendance_list.html', {'attendance_records': attendance_records})

@login_required
def aic_greenhouse_index(request):

    if request.user.is_authenticated:        
        #crops = Crop.objects.all()
        #supervisor = get_object_or_404(Supervisor, user=request.user)# Assuming 'beneficiary' is linked to user  
         # Get all greenhouses assigned to this supervisor
        greenhouses = Greenhouse.objects.all()
    
        # Get all cities assigned to this supervisor
        cities = City.objects.all()
        # Get all greenhouse rooms related to the greenhouses assigned to this supervisor
        all_tunels = GreenhouseRoom.objects.filter(greenhouse__in=greenhouses)

        context = {
            'greenhouses': greenhouses,
            'cities': cities,
            'all_tunels': all_tunels
        }
          
        return render(request, 'admin/aic/greenhouse/greenhouse.html', context)
    else:
       return redirect('user_login')
   
@login_required
def aic_greenhouse_map_view(request, greenhouse_id):
    greenhouse = get_object_or_404(Greenhouse, id=greenhouse_id)
    context = {
        'greenhouse': greenhouse,
    }
    return render(request, 'admin/aic/greenhouse/greenhouse_detail.html', context)
 
@login_required
def aic_buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'admin/aic/buyer/detail.html', {'buyer': buyer})

@login_required
def aic_create_buyer(request):
    if request.method == 'POST':
        form = BuyerForm(request.POST, request.FILES)
        if form.is_valid():
            
            buyer = form.save(commit=False)
            buyer.created_by = request.user  # Set the logged-in user as the creator

            # Save the beneficiary instance
            buyer.save()
            
            # farm_input = form.save(commit=False)
            # farm_input.created_by = request.user            
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
    return render(request, 'admin/aic/buyer/create.html', {'form': form})

@login_required
def aic_update_buyer(request, buyer_id):
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
            return redirect('aic_buyer_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = BuyerForm(instance=buyer)

    return render(request, 'admin/aic/buyer/create.html', {'form': form, 'buyer': buyer})


#ENTERPRISE DEVELOPMENT OFFICER (Edo Module)
@login_required
def aic_edo_index(request):
    if request.user.is_authenticated:        
            edos = Supervisor.objects.all()
            return render(request, 'admin/aic/edo/edo.html', {'edos':edos})
    else:
       return redirect('beneficiary_login')
   
   
@login_required
def aic_edo_detail(request, edo_id):
    if request.user.is_authenticated:  
        # Fetch the supervisor object
        edo = get_object_or_404(Supervisor, id=edo_id)
        # Fetch the current logged-in user's beneficiary record (assuming one-to-one relationship)
        beneficiary = Beneficiary.objects.filter(user=request.user).first()
        # Greenhouses assigned to this supervisor
        supervisor_greenhouses = edo.greenhouse.all()
        # Greenhouses that are also assigned to the current beneficiary
        beneficiary_greenhouses = beneficiary.crops.all() if beneficiary else None
        # Cities assigned to this supervisor
        supervisor_cities = edo.city.all()
        context = {
            'beneficiary': beneficiary,
            'edo': edo,
            'supervisor_greenhouses': supervisor_greenhouses,
            'beneficiary_greenhouses': beneficiary_greenhouses,
            'supervisor_cities': supervisor_cities,
        }
       
        
        return render(request, 'admin/aic/edo/detail.html', context)
    
@login_required
def aic_create_edo(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST, request.FILES)
        if form.is_valid():
            edo = form.save(commit=False)
            edo.created_by = request.user  # Set the logged-in user as the creator

            # Save the edo instance
            edo.save()
            
            # Clear any previous city or greenhouse, if necessary
            edo.city.clear() 
            edo.greenhouse.clear()
            
            # Add selected city and greenhouse to the edo
            city = form.cleaned_data.get('city')
            greenhouse = form.cleaned_data.get('greenhouse')
            if city:
                edo.city.set(city)
            if greenhouse:
                edo.greenhouse.set(greenhouse)
            
            # Use email as username if valid email exists, else create unique username
            email = edo.email  # Assuming 'email' is a field in the edo model
            if email and '@' in email:  # Basic validation for a valid email
                username = email
            else:
                first_name = edo.fullname.split()[0].lower()  # Assuming fullname is a field in edo model
                unique_id = int(time.time()) % 100000  # Generate a unique ID
                username = f"{first_name}_y{unique_id:05}"
            
            password = 'edoLoc@2024'  # Default password
            edo_user = User.objects.create(
                username=username,
                password=make_password(password),  # Encrypt the password
                email=edo.email,
                first_name=edo.fullname.split()[0].lower(),  # Extract first name
                last_name=" ".join(edo.fullname.split()[1:])  # Rest of the name as last name
            )

            # Assign the existing 'EDO' group
            edo_group = Group.objects.get(name='EDO')
            edo_user.groups.add(edo_group)

            # Save the user
            edo_user.save()
            
            return redirect('aic_edo_index')  # Redirect to the appropriate page after successful save
        # If the form is invalid, it will fall through and render the form with errors

    else:
        form = SupervisorForm()
    
    # Render the form template, whether it's a GET request or a failed POST submission
    return render(request, 'admin/aic/edo/create.html', {'form': form})


@login_required
def aic_update_edo(request, edo_id):
    # Retrieve the existing FarmInput instance
    edo = get_object_or_404(Buyer, id=edo_id)

    if request.method == 'POST':
        form = SupervisorForm(request.POST, request.FILES, instance=edo)
        if form.is_valid():
            # Save the updated FarmInput instance
            edo = form.save(commit=False)
            # buyer.created_by = request.user
            # if farm_input.confirmation != 0:
            #     farm_input.confirm_by = request.user
            edo.save()
            
            edo.city.clear() 
            edo.greenhouse.clear() 
            # Add selected crops to the beneficiary
            city = form.cleaned_data.get('city')
            greenhouse = form.cleaned_data.get('greenhouse')
            if city:
                edo.city.set(city)  # This will automatically create entries in the beneficiary_crops table

            if greenhouse:
                edo.greenhouse.set(greenhouse)
                
            return redirect('aic_buyer_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = SupervisorForm(instance=edo)

    return render(request, 'admin/aic/buyer/create.html', {'form': form, 'edo': edo})




#SALE AGENT USER CREATION 
@login_required
def aic_sale_agent_index(request):
    if request.user.is_authenticated:        
            saleagents = SaleAgent.objects.all()
            return render(request, 'admin/aic/saleagent/saleagent.html', {'saleagents':saleagents})
    else:
       return redirect('beneficiary_login')
   
   
# @login_required
# def aic_sale_agent_detail(request, sale_agent_id):
#     if request.user.is_authenticated:  
#         # Fetch the Sales Agent object
#         aics = request.user
#         aic =  AIC.objects.filter(user = aics)
#         saleagent = get_object_or_404(SaleAgent, id=sale_agent_id)
#         # Fetch the current logged-in user's beneficiary record (assuming one-to-one relationship)
#         # Greenhouses assigned to this Sales Agent
#         # saleagent_greenhouses = saleagent.greenhouse.all()
#         saleagent_marketcentres = saleagent.marketingcentre
#         saleagent_cities = saleagent.city.all()
#         context = {
#             'saleagent': saleagent,
#             'aic': aic,
#             'saleagent_marketcentres': saleagent_marketcentres,
#             'saleagent_cities': saleagent_cities,
#         }
       
#         return render(request, 'admin/aic/saleagent/detail.html', context)


# @login_required
# def aic_sale_agent_detail(request, sale_agent_id):
#     if request.user.is_authenticated:  
#         sa = get_object_or_404(SaleAgent, id=sale_agent_id)
#         aic = AIC.objects.filter(user=request.user).first()
#         saleagent_marketcentres = sa.marketingcentre
#         saleagent_cities = sa.city.all()
#         context = {
#             'saleagent': sa,
#             'aic': aic,
#             'saleagent_marketcentres': saleagent_marketcentres,
#             'saleagent_cities': saleagent_cities,
#         }
#         return render(request, 'admin/aic/saleagent/detail.html', context)

@login_required   
def aic_sale_agent_detail(request, sale_agent_id):
    sa = get_object_or_404(SaleAgent, id=sale_agent_id)
    aic = AIC.objects.filter(user=request.user).first()

    context = {
        'saleagent': sa,
        'aic': aic,
        'saleagent_cities': sa.city.all(),
    }

    return render(request, 'admin/aic/saleagent/detail.html', context)   
    
    
        
@login_required
def aic_create_sale_agent(request):
    if request.method == 'POST':
        form = SaleAgentForm(request.POST, request.FILES)
        if form.is_valid():
            sale_agent = form.save(commit=False)
            sale_agent.created_by = request.user  # Set the logged-in user as the creator

            # Save the edo instance
            sale_agent.save()
            
            # Clear any previous city or greenhouse, if necessary
            sale_agent.city.clear() 
            # sale_agent.greenhouse.clear()
            sale_agent.marketingcentre.clear()
            
            # Add selected city and greenhouse to the edo
            city = form.cleaned_data.get('city')
            # greenhouse = form.cleaned_data.get('greenhouse')
            marketingcentre = form.cleaned_data.get('marketingcentre')
            if city:
                sale_agent.city.set(city)
            # if greenhouse:
            #     sale_agent.greenhouse.set(greenhouse)
            if marketingcentre:
                sale_agent.marketingcentre.set(marketingcentre)
                
            # Use email as username if valid email exists, else create unique username
            email = sale_agent.email  # Assuming 'email' is a field in the edo model
            if email and '@' in email:  # Basic validation for a valid email
                username = email
            else:
                first_name = sale_agent.fullname.split()[0].lower()  # Assuming fullname is a field in edo model
                unique_id = int(time.time()) % 100000  # Generate a unique ID
                username = f"{first_name}_y{unique_id:05}"
            
            password = 'SAgent@2024'  # Default password
            sale_agent_user = User.objects.create(
                username=username,
                password=make_password(password),  # Encrypt the password
                email=sale_agent.email,
                first_name=sale_agent.fullname.split()[0].lower(),  # Extract first name
                last_name=" ".join(sale_agent.fullname.split()[1:])  # Rest of the name as last name
            )

            # Assign the existing 'EDO' group
            sales_group = Group.objects.get(name='SALES')
            sale_agent_user.groups.add(sales_group)

            # Save the user
            sale_agent_user.save()
            
            return redirect('aic_sale_agent_index')  # Redirect to the appropriate page after successful save
        # If the form is invalid, it will fall through and render the form with errors

    else:
        form = SaleAgentForm()
    
    # Render the form template, whether it's a GET request or a failed POST submission
    return render(request, 'admin/aic/saleagent/create.html', {'form': form})


#update sales agent details
@login_required
def aic_update_sale_agent(request, sale_agent_id):
    # Retrieve the existing FarmInput instance
    sale_agent = get_object_or_404(SaleAgent, id=sale_agent_id)

    if request.method == 'POST':
        form = SaleAgentForm(request.POST, request.FILES, instance=sale_agent)
        if form.is_valid():
            # Save the updated FarmInput instance
            sale_agent = form.save(commit=False)
            # buyer.created_by = request.user
            # if farm_input.confirmation != 0:
            #     farm_input.confirm_by = request.user
            sale_agent.save()
            
            sale_agent.city.clear() 
            # sale_agent.greenhouse.clear() 
            sale_agent.marketingcentre.clear()
            # Add selected crops to the beneficiary
            city = form.cleaned_data.get('city')
            # greenhouse = form.cleaned_data.get('greenhouse')
            marketingcentre = form.cleaned_data.get('marketingcentre')
            if city:
                sale_agent.city.set(city)  # This will automatically create entries in the beneficiary_crops table

            # if greenhouse:
            #     sale_agent.greenhouse.set(greenhouse)
            if marketingcentre:
                sale_agent.marketingcentre.set(marketingcentre)
                   
            return redirect('aic_sale_agent_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = SaleAgentForm(instance=sale_agent)

    return render(request, 'admin/aic/saleagent/create.html', {'form': form, 'sale_agent': sale_agent})

#FINANCIAL MODULE
#Beneficiary Financials 
# @login_required
# def aic_beneficiaries_cash_requests(request):
#     beneficiaries = Beneficiary.objects.prefetch_related('cashloans').all()
    
#     farm_input_assigned_list = CashAssigned.objects.filter()
#     repayments = Repayment.objects.filter()
#     # Calculate totals
#     total_cash_given = farm_input_assigned_list.aggregate(Sum('amount'))['amount__sum'] or 0
#     total_amount_paid = repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
#     total_amount_bal = repayments.aggregate(Sum('bal_amount'))['bal_amount__sum'] or 0
#     context = {
#         'beneficiaries': beneficiaries,
#          'total_cash_given':total_cash_given,
#          'total_amount_paid':total_amount_paid,
#          'total_amount_bal':total_amount_bal
#     }
#     return render(request, 'admin/aic/finance/cash_request.html', context)

@login_required
def aic_beneficiaries_cash_requests(request):
     # Only get beneficiaries who have at least one CashAssigned entry
    beneficiaries = Beneficiary.objects.annotate(
        has_cash_assigned=Exists(
            CashAssigned.objects.filter(beneficiary=OuterRef('pk'))
        )
    ).filter(has_cash_assigned=True).prefetch_related('cashloans__repayment_set')

    farm_input_assigned_list = CashAssigned.objects.all()
    repayments = Repayment.objects.all()
    
    # Calculate totals
    total_cash_given = farm_input_assigned_list.aggregate(Sum('amount'))['amount__sum'] or 0
    total_amount_paid = repayments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_amount_bal = total_cash_given - total_amount_paid

    context = {
        'beneficiaries': beneficiaries,
        'total_cash_given': total_cash_given,
        'total_amount_paid': total_amount_paid,
        'total_amount_bal': total_amount_bal
    }
    return render(request, 'admin/aic/finance/cash_request.html', context)

@login_required
def aic_beneficiaries_repayments(request):
    repayments = Repayment.objects.select_related('cash_assigned__beneficiary')
    return render(request, 'admin/aic/finance/repayment.html', {'repayments': repayments})
  
@login_required
def aic_change_cash_status(request, cash_id, status):
    cash = get_object_or_404(CashAssigned, id=cash_id)
    if status in ['Approved', 'Denied']:
        cash.status = status
        cash.save()
    return redirect('aic_beneficiaries_cash_requests')

@login_required
def aic_change_repayment_status(request, repayment_id, status):
    repayment = get_object_or_404(Repayment, id=repayment_id)
    if status in ['Approved', 'Denied']:
        repayment.status = status
        repayment.save()
    return redirect('aic_beneficiaries_repayments')

#fulfill order by buyer
@login_required
def fulfill_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        for item_id, volume in request.POST.getlist('order_items'):
            item = OrderItem.objects.get(id=item_id)
            Delivery.objects.create(order_item=item, volume_delivered=volume)
            item.is_delivered = True
            item.save()

        if order.is_fulfilled():
            order.status = 'completed'
            order.save()

        messages.success(request, 'Order fulfilled successfully.')
        return redirect('aic_order_view')

    return render(request, 'admin/aic/orders/fulfill_order.html', {'order': order})


def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value



####################################### AIC CREATE ORDER FOR BUYER #########################################
@login_required
def aic_buyer_shop(request, user_id):
    #buyer = Buyer
    buyer = get_object_or_404(Buyer, user=user_id)
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
        buyer_id = request.POST.get('buyer_id')        
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
                    'buyer_id': buyer_id,
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
                    'buyer_id': buyer_id,
                }

        # Save the updated cart back into the session
        request.session['cart'] = cart
        request.session.modified = True

        return redirect('aic_buyer_shop', buyer.user.id)  # Redirect to avoid form re-submission

    return render(request, 'admin/aic/order/shop.html', {
        'assigned_harvest_records': harvest_records,
        'total_quantity': total_quantity,
        'total_price': total_price,
        'cart': cart,  # Pass the cart to the template
        'buyer':buyer,
        'cart_item_count': cart_item_count,
    })
    
@login_required
def aic_view_cart(request, user_id):
    
    buyer = get_object_or_404(Buyer, user=user_id)
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
    return render(request, 'admin/aic/order/cart.html', {
        'cart': cart,
        'total_cost': total_cost,
        'buyer':buyer,
        'cart_item_count': cart_item_count,
    })


@login_required
def aic_checkout(request, user_id):
    # Retrieve cart from session
    buyer = get_object_or_404(Buyer, user=user_id)
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('buyer_shop')

    # Calculate total items for the order, we will calculate `total_amount` after creating items
    total_items = sum(item['quantity'] for item in cart.values())

    # Create the initial Order object
    order = Order.objects.create(
        buyer=buyer,
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
    return render(request, 'admin/aic/order/checkout_success.html', {'order': order, 'buyer':buyer})



@login_required
def aic_place_order(request):
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

    return render(request, 'admin/aic/order/place_order.html', {
        'order_form': order_form,
        'order_item_formset': order_item_formset,
    })
    

@login_required
def aic_create_order(request):
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

    return render(request, 'admin/aic/order/create.html', {
        'order_form': order_form,
        'harvest_records': harvest_records,
    })


@login_required
def aic_buyer_confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='in_progress')

    if request.method == "POST":
        delivery_date = request.POST.get("delivery_date")
        confirmation_note = request.POST.get("note")
        quantity_receive = request.POST.get("quantity")

        for item in order.order_items.all():
            # Update OrderItem details
            item.notes = request.POST.get(f"note_{item.id}", "")  # Add specific notes if provided
            #item.quantity_received = request.POST.get(f"quantity_{item.id}", item.quantity)  # Default to ordered quantity
            item.is_delivered = True
            item.save()

            # Update the existing Delivery record
            delivery = Delivery.objects.filter(order_item=item).first()
            if delivery:
                #delivery.volume_delivered = item.quantity_received
                delivery.delivery_date = delivery_date   
                delivery.quantity_receive = quantity_receive
                delivery.confirm_by = request.user
                delivery.confirm_at = now()        
                
                delivery.save()

        # Update Order details
        order.status = 'complete'
        order.confirmation_note = confirmation_note
        order.confirmed_by = request.user
        order.confirmed_at = now()
        order.save()

        messages.success(request, "Order has been successfully confirmed.")
        return redirect('order_detail', order_id=order.id)

    return render(request, 'admin/aic/order/confirm_order.html', {'order': order})

# Calculate the total_amount for a specific order by summing up quantity * price for each item
def calculate_order_total_amount(order_id):
    total_amount = OrderItem.objects.filter(order_id=order_id).aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0  # Use 0 as default if total is None
    return total_amount


###############################################
#Discussion Forum
##########################################################3
@login_required
def aic_trend_knowledge_index(request):

    if request.user.is_authenticated:        
        trends = TrendKnowledgeBank.objects.filter(created_by = request.user.id)
        return render(request, 'admin/aic/forum/index.html', {'trends':trends})
    else:
       return redirect('user_login')

# topics for discussion.  
@login_required
def aic_trend_knowledge_board(request):

    if request.user.is_authenticated:        
        trs = TrendKnowledgeBank.objects.all()
        return render(request, 'admin/aic/forum/discussion.html', {'trs':trs})
    else:
       return redirect('user_login')
   
# View to create a new TrendKnowledgeBank
@login_required
def aic_create_trend_knowledge(request):
    if not request.user.groups.filter(name='Beneficiary').exists():
        messages.error(request, 'You do not have permission to create a Trend Knowledge Topic.')
        return redirect('aic_dashboard')
    
    if request.method == 'POST':
        form = TrendKnowledgeBankForm(request.POST, request.FILES)
        if form.is_valid():
            trend_knowledge_bank = form.save(commit=False)
            trend_knowledge_bank.created_by = request.user  # Associate with logged-in user
            trend_knowledge_bank.save()
            messages.success(request, 'Trend Knowledge Successfully Created.')
            return redirect('aic_dashboard')  # Redirect to dashboard or another relevant page
    else:
        form = TrendKnowledgeBankForm()
    
    return render(request, 'admin/aic/forum/create.html', {'form': form})

# View to create a discussion under a specific TrendKnowledgeBank
@login_required
def aic_discussion_trend_knowledge(request, pk):
    trend_knowledge_bank = get_object_or_404(TrendKnowledgeBank, pk=pk)
    
    if request.method == 'POST':
        form = TrendKnowledgeDiscussionForm(request.POST, request.FILES)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.trend_knowledge_bank = trend_knowledge_bank  # Link to the trend knowledge bank
            discussion.created_by = request.user  # Associate with logged-in user
            discussion.save()
            messages.success(request, 'Discussion added successfully.')
            return redirect('trend_knowledge_bank_detail', pk=pk)  # Redirect to the bank's detail page
    else:
        form = TrendKnowledgeDiscussionForm()
    
    return render(request, 'admin/aic/forum/discussion.html', {'form': form, 'trend_knowledge_bank': trend_knowledge_bank})

@login_required
def aic_trend_knowledge_bank_detail(request, pk):
    # Get the particular TrendKnowledgeBank entry
    trend_knowledge_bank = get_object_or_404(TrendKnowledgeBank, pk=pk)

    # Get all discussions related to this TrendKnowledgeBank
    discussions = TrendKnowledgeDiscussion.objects.filter(trend_knowledge_bank=trend_knowledge_bank).order_by('-created_at')

    # Handle discussion form submission
    if request.method == 'POST':
        discussion_form = TrendKnowledgeDiscussionForm(request.POST, request.FILES)
        if discussion_form.is_valid():
            new_discussion = discussion_form.save(commit=False)
            new_discussion.trend_knowledge_bank = trend_knowledge_bank
            new_discussion.created_by = request.user  # Set the logged-in user as the creator
            new_discussion.save()
            new_discussion.save_m2m()  # Save the many-to-many relationship
            messages.success(request, 'Your discussion has been added.')
            return redirect('trend_knowledge_bank_detail', pk=trend_knowledge_bank.pk)
    else:
        discussion_form = TrendKnowledgeDiscussionForm()

    return render(request, 'admin/aic/forum/detail.html', {
        'trend_knowledge_bank': trend_knowledge_bank,
        'discussions': discussions,
        'discussion_form': discussion_form
    })
    
##########################################################
############# Todo View ######################################
@login_required
def aic_create_todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.created_by = request.user
            todo.save()
            return JsonResponse({'success': True, 'message': 'Todo created successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return redirect('aic_todo_list')

@login_required
def aic_todo_list(request):
    todos = Todo.objects.filter(created_by=request.user)
    return render(request, 'admin/aic/todo/todo_list.html', {'todos': todos})

# @login_required
# def aic_create_todo(request):
#     if request.method == 'POST':
#         form = TodoForm(request.POST)
#         if form.is_valid():
#             todo = form.save(commit=False)
#             todo.created_by = request.user
#             todo.save()
#             return redirect('aic_todo_list')
#     else:
#         form = TodoForm()
#     return render(request, 'admin/aic/todo/create_todo.html', {'form': form})

@login_required
def aic_update_todo_state(request, pk, state):
    todo = get_object_or_404(Todo, pk=pk, created_by=request.user)
    if state in dict(Todo.TODOSTATE):  # Validate the state
        todo.todostate = state
        todo.save()
    return redirect('aic_todo_list')
 ############# End Todo View ######################################
 
@login_required
def harvest_summary_view(request):
    # Accumulated yield for the year
    current_year = timezone.now().year - 1
    accumulated_yield = Harvest.objects.filter(date__year=current_year).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total yield per crop
    total_yield_per_crop = Harvest.objects.filter(date__year=current_year).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Total yield per tunnel (greenhouse rooms)
    total_yield_per_tunnel = Harvest.objects.filter(date__year=current_year).values('greenhouse_room__room_name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Total yield for the 4 major crops and others
    major_crops = ['Crop1', 'Crop2', 'Crop3', 'Crop4']  # Replace with your actual crop names
    major_crops_yield = Harvest.objects.filter(date__year=current_year, crop__name__in=major_crops).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    other_crops_yield = Harvest.objects.filter(date__year=current_year).exclude(crop__name__in=major_crops).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total revenue earned over the period
    total_revenue = Harvest.objects.filter(date__year=current_year).aggregate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )['total_revenue']

    # Sales revenue per crop
    revenue_per_crop = Harvest.objects.filter(date__year=current_year).values('crop__name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )

    # Revenue contribution from clusters (greenhouses or greenhouse rooms)
    revenue_per_cluster = Harvest.objects.filter(date__year=current_year).values('greenhouse_room__room_name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )

    # Pass the calculated data to the template
    context = {
        'accumulated_yield': accumulated_yield,
        'total_yield_per_crop': total_yield_per_crop,
        'total_yield_per_tunnel': total_yield_per_tunnel,
        'major_crops_yield': major_crops_yield,
        'other_crops_yield': other_crops_yield,
        'total_revenue': total_revenue,
        'revenue_per_crop': revenue_per_crop,
        'revenue_per_cluster': revenue_per_cluster,
    }
    return render(request, 'admin/aic/harvest_summary.html', context)


#ACCOUNTING MODULES
#<<<<========================================================================================>>>>>
@login_required
def aic_accounting_summary(request):
    #AIC's view of all costs and revenue.
    
    # Total farm input costs distributed to beneficiaries
    farm_input_costs = InputDistribution.objects.aggregate(total_cost=Sum('total_cost'))['total_cost'] or Decimal(0)
    # Total cash loans assigned
    cash_loans = CashAssigned.objects.aggregate(total_loans=Sum('amount'))['total_loans'] or Decimal(0)
    # Total loan repayments
    total_repayments = Repayment.objects.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or Decimal(0)
    # Total maintenance costs
    total_maintenance = ServiceRequest.objects.aggregate(total_cost=Sum('total_amount'))['total_cost'] or Decimal(0)
    # Total harvest sales (credit purchases by AIC)
    total_harvest_sales = Harvest.objects.aggregate(total_sales=Sum('total_price'))['total_sales'] or Decimal(0)
    
    farm_inputs = FarmInput.objects.annotate(
            total_cost=ExpressionWrapper(
                F('quantity_received') * F('cost_per_unit'), output_field=DecimalField()
            )
        )

    # Then, sum the total_cost values across all records
    farm_inputs_total_amount = farm_inputs.aggregate(
            total=Coalesce(Sum('total_cost', output_field=DecimalField()), Decimal(0))
        )['total']
        
    # Total revenue available (Harvest sales minus deductions)
    #total_deductions = farm_input_costs + cash_loans + total_maintenance
    total_deductions = farm_inputs_total_amount + cash_loans + total_maintenance
    net_revenue = total_harvest_sales - total_deductions

    context = {
        'farm_input_costs': farm_input_costs,
        'farm_inputs_total_amount':farm_inputs_total_amount,
        'cash_loans': cash_loans,
        'total_repayments': total_repayments,
        'total_maintenance': total_maintenance,
        'total_harvest_sales': total_harvest_sales,
        'total_deductions': total_deductions,
        'net_revenue': net_revenue
    }

    return render(request, 'admin/aic/accounting/aic_summary.html', context)


@login_required
def aic_accounting_detail(request, category, beneficiary_id=None):
    #View detailed transactions of a selected category."""
    queryset = None
    title = ""
    total_amount = Decimal(0)  # Initialize total amount as Decimal

    if category == "farm_input_costs":
        title = "Farm Input Costs"
        queryset = InputDistribution.objects.all()
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('total_cost', output_field=DecimalField()), Decimal(0))
        )['total']

    elif category == "cash_loans":
        title = "Cash Loans"
        queryset = CashAssigned.objects.all()
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal(0))
        )['total']

    elif category == "total_repayments":
        title = "Loan Repayments"
        queryset = Repayment.objects.all()
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('amount_paid', output_field=DecimalField()), Decimal(0))
        )['total']

    elif category == "maintenance_costs":
        title = "Maintenance Costs"
        queryset = ServiceRequest.objects.all()
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal(0))
        )['total']

    elif category == "total_harvest_sales":
        title = "Harvest Sales"
        queryset = Harvest.objects.all()
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('total_price', output_field=DecimalField()), Decimal(0))
        )['total']
       
    elif category == "farm_inputs":  # Fixing Farm Inputs Aggregation
        title = "Farm Inputs Purchased"  
        
        # First, annotate each record with total_cost
        queryset = FarmInput.objects.annotate(
            total_cost=ExpressionWrapper(
                F('quantity_received') * F('cost_per_unit'), output_field=DecimalField()
            )
        )

        # Then, sum the total_cost values across all records
        total_amount = queryset.aggregate(
            total=Coalesce(Sum('total_cost', output_field=DecimalField()), Decimal(0))
        )['total']

    # Ensure total_amount is a valid Decimal
    total_amount = Decimal(total_amount or 0)
    
    context = {
        'title': title,
        'queryset': queryset,
        'total_amount': total_amount
    }
    return render(request, 'admin/aic/accounting/detail_view.html', context)


#=============================>>>>>>>>>>>>>>>>>>>>>>> COSTING MODULE====================>>>>>>>>>>>>>>>>>>>
# def distribute_general_maintenance_cost(maintenance_cost):
#     #Distribute maintenance cost evenly among all active beneficiaries."""
#     beneficiaries = Beneficiary.objects.all()
#     count = beneficiaries.count()
    
#     if count == 0:
#         return  # No beneficiaries to distribute cost to

#     share_amount = maintenance_cost.total_cost / count  # Equal split

#     for beneficiary in beneficiaries:
#         BeneficiaryMaintenanceShare.objects.create(
#             maintenance_cost=maintenance_cost,
#             beneficiary=beneficiary,
#             share_amount=share_amount,
#             created_by=maintenance_cost.created_by
#         )
        
# @login_required
# def aic_billable_items_list(request):
#     billable_items = BillableCostItems.objects.all()
#     return render(request, 'admin/aic/accounting/billing/billable_items_list.html', {'billable_items': billable_items})

# @login_required
# def aic_create_billable_item(request):
#     if request.method == "POST":
#         form = BillableCostItemsForm(request.POST, request.FILES)
#         if form.is_valid():
#             billable_item = form.save(commit=False)
#             billable_item.created_by = request.user  # Assign logged-in user
#             billable_item.save()
#             return redirect('aic_billable_items_list')
#     else:
#         form = BillableCostItemsForm()
#     return render(request, 'admin/aic/accounting/billing/create_billable_item.html', {'form': form})

# @login_required
# def aic_update_billable_item(request, billable_item_id):
#     billable_item = get_object_or_404(BillableCostItems, id=billable_item_id)
#     if request.method == "POST":
#         form = BillableCostItemsForm(request.POST, request.FILES, instance=billable_item)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_billable_items_list')
#     else:
#         form = BillableCostItemsForm(instance=billable_item)
#     return render(request, 'admin/aic/accounting/billing/create_billable_item.html', {'form': form})


# @login_required
# def aic_maintenance_costs_list(request):
#     maintenance_costs = MaintenanceCost.objects.select_related('billable_item', 'greenhouse', 'beneficiary')
#     return render(request, 'admin/aic/accounting/billing/maintenance_costs_list.html', {'maintenance_costs': maintenance_costs})

# @login_required
# def aic_create_maintenance_cost(request):
#     if request.method == "POST":
#         form = MaintenanceCostForm(request.POST)
#         if form.is_valid():
#             maintenance_cost = form.save(commit=False)
#             maintenance_cost.created_by = request.user
#             maintenance_cost.save()
            
#             # If cost applies to all beneficiaries, distribute it
#             if maintenance_cost.applies_to_all:
#                 distribute_general_maintenance_cost(maintenance_cost)

#             return redirect('aic_maintenance_costs_list')
#     else:
#         form = MaintenanceCostForm()
#     return render(request, 'admin/aic/accounting/billing/create_maintenance_cost.html', {'form': form})


# @login_required
# def aic_update_maintenance_item(request, maintenance_cost_id):
#     maintenance_cost = get_object_or_404(MaintenanceCost, id=maintenance_cost_id)
#     if request.method == "POST":
#         form = MaintenanceCostForm(request.POST, instance=maintenance_cost)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_maintenance_costs_list')
#     else:
#         form = MaintenanceCostForm(instance=maintenance_cost)
#     return render(request, 'admin/aic/accounting/billing/create_maintenance_cost.html', {'form': form})


# @login_required
# def aic_beneficiary_shares_list(request):
#     shares = BeneficiaryMaintenanceShare.objects.select_related('beneficiary', 'maintenance_cost__billable_item')
#     return render(request, 'admin/aic/accounting/billing/beneficiary_cost_shares_list.html', {'shares': shares})




# @login_required
# def aic_cost_item_list(request):
#     cost_items = MaintenanceCostItem.objects.all()
#     return render(request, 'admin/aic/accounting/billing/cost_item_list.html', {'cost_items': cost_items})

# @login_required
# def aic_cost_item_create(request):
#     if request.method == "POST":
#         form = MaintenanceCostItemForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_cost_item_list')
#     else:
#         form = MaintenanceCostItemForm()
#     return render(request, 'admin/aic/accounting/billing/cost_item_form.html', {'form': form})

# @login_required
# def aic_cost_item_update(request, item_cost_id):
#     maintenance_cost = get_object_or_404(MaintenanceCostItem, id=item_cost_id)
#     if request.method == "POST":
#         form = MaintenanceCostItemForm(request.POST, instance=maintenance_cost)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_maintenance_costs_list')
#     else:
#         form = MaintenanceCostItemForm(instance=maintenance_cost)
#     return render(request, 'admin/aic/accounting/billing/cost_item_form.html', {'form': form})


# @login_required
# def aic_maintenance_cost_list(request):
#     maintenance_costs = MaintenanceCosting.objects.all()
#     return render(request, 'admin/aic/accounting/billing/maintenance_cost_list.html', {'maintenance_costs': maintenance_costs})

# @login_required
# def aic_maintenance_cost_create(request):
#     if request.method == "POST":
#         form = MaintenanceCostingForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_maintenance_cost_list')
#     else:
#         form = MaintenanceCostingForm()
#     return render(request, 'admin/aic/accounting/billing/maintenance_cost_form.html', {'form': form})

# @login_required
# def aic_maintenance_cost_update(request, costing_id):
#     maintenance_cost = get_object_or_404(MaintenanceCosting, id=costing_id)
#     if request.method == "POST":
#         form = MaintenanceCostingForm(request.POST, instance=maintenance_cost)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_maintenance_costs_list')
#     else:
#         form = MaintenanceCostingForm(instance=maintenance_cost)
#     return render(request, 'admin/aic/accounting/billing/maintenance_cost_form.html', {'form': form})


# @login_required
# def aic_billing_list(request):
#     bills = MaintenanceBilling.objects.all()
#     return render(request, 'admin/aic/accounting/billing/billing_list.html', {'bills': bills})

# @login_required
# def aic_billing_create(request):
#     if request.method == "POST":
#         form = MaintenanceBillingForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_billing_list')
#     else:
#         form = MaintenanceBillingForm()
#     return render(request, 'admin/aic/accounting/billing/billing_form.html', {'form': form})

# @login_required
# def aic_billing_update(request, bill_id):
#     maintenance_cost = get_object_or_404(MaintenanceBilling, id=bill_id)
#     if request.method == "POST":
#         form = MaintenanceBillingForm(request.POST, instance=maintenance_cost)
#         if form.is_valid():
#             form.save()
#             return redirect('aic_maintenance_costs_list')
#     else:
#         form = MaintenanceBillingForm(instance=maintenance_cost)
#     return render(request, 'admin/aic/accounting/billing/billing_form.html', {'form': form})


#<<<<<<<<<<<<<<<<<============= DYNAMIC BILLING VIEW =================>>>>>>>>>>>>>>>>>>>>>>>>>

# Views
################## farm season#################################
@login_required
def aic_farm_season_index(request):
    if request.user.is_authenticated:        
        farmseasons = FarmSeason.objects.all()
        return render(request, 'admin/aic/accounting/billing/farmseason/list.html', {'farmseasons':farmseasons})
    else:
       return redirect('aic_farm_season_index')

@login_required
def aic_create_farm_season(request):
    if request.method == 'POST':
        form = FarmseasonForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Ensure form.save() supports user argument
            return redirect('aic_farm_season_index')
        else:
            # Return form with errors if validation fails
            return render(request, 'admin/aic/accounting/billing/farmseason/create.html', {'form':form})  

    # GET request: Render the empty form
    form = FarmseasonForm()
    return render(request, 'admin/aic/accounting/billing/farmseason/create.html', {'form':form})


@login_required
def aic_update_farm_season(request, farmseason_id):
    farm_season = get_object_or_404(FarmSeason, id=farmseason_id)
    if request.method == 'POST':
        form = FarmseasonForm(request.POST, instance=farm_season)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('aic_farm_season_index')  # Redirect to the list or any other page
    else:
        form = FarmseasonForm(instance=farm_season)

    return render(request, 'admin/aic/accounting/billing/farmseason/create.html', {'form':form, 'farm_season':farm_season}) 
############### eND OF FARM SEASON ############################################################

@login_required
def aic_billable_item_index(request):
    if request.user.is_authenticated:        
        billables = BillableItem.objects.all()
        return render(request, 'admin/aic/accounting/billable/billable_list.html', {'billables':billables})
    else:
       return redirect('aic_billable_item_index')

@login_required
def aic_create_billable_item(request):
    if request.method == 'POST':
        form = BillableItemForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Ensure form.save() supports user argument
            return redirect('aic_billable_item_index')
        else:
            # Return form with errors if validation fails
            return render(request, 'admin/aic/accounting/billable/billable_create.html', {'form': form})  

    # GET request: Render the empty form
    form = BillableItemForm()
    return render(request, 'admin/aic/accounting/billable/billable_create.html', {'form': form})

@login_required
def aic_update_billable_item(request, billable_item_id):
    billable_item = get_object_or_404(BillableItem, id=billable_item_id)
    if request.method == 'POST':
        form = BillableItemForm(request.POST, instance=billable_item)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('aic_billable_item_index')  # Redirect to the list or any other page
    else:
        form = BillableItemForm(instance=billable_item)

    return render(request, 'admin/aic/accounting/billable/billable_create.html', {'form':form, 'billable_item':billable_item}) 

################################################ END OF bILLABLE iTEMS##############################################
@login_required
def aic_item_cost_index(request):
    if request.user.is_authenticated:        
        itemcosts = BillableItemCost.objects.all()
        return render(request, 'admin/aic/accounting/billable/itemcost_list.html', {'itemcosts':itemcosts})
    else:
       return redirect('aic_item_cost_index')

@login_required
def aic_create_item_cost(request):
    if request.method == 'POST':
        form = BillableItemCostForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Ensure form.save() supports user argument
            return redirect('aic_item_cost_index')
        else:
            # Return form with errors if validation fails
            return render(request, 'admin/aic/accounting/billable/itemcost_create.html', {'form': form})  

    # GET request: Render the empty form
    form = BillableItemCostForm()
    return render(request, 'admin/aic/accounting/billable/itemcost_create.html', {'form': form})

@login_required
def aic_update_item_cost(request, item_cost_id):
    billable_item_cost = get_object_or_404(BillableItemCost, id=item_cost_id)
    if request.method == 'POST':
        form = BillableItemCostForm(request.POST, instance=billable_item_cost)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('aic_item_cost_index')  # Redirect to the list or any other page
    else:
        form = BillableItemCostForm(instance=billable_item_cost)

    return render(request, 'admin/aic/accounting/billable/itemcost_create.html', {'form':form, 'billable_item_cost':billable_item_cost}) 

############<<<<<<<<<<<<<----------- END OF BILLABLE ITEM COST --------->>>>>>>>>>>>>>>>>############################


#<<<<<<<<<<<<<<<=========================== SERVICE ITEMS CONFIGURATION ==============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#
@login_required
def aic_service_item_index(request):
    if request.user.is_authenticated:        
        serviceitems = ServiceItem.objects.all()
        return render(request, 'admin/aic/accounting/billing/serviceitem/list.html', {'serviceitems':serviceitems})
    else:
       return redirect('aic_service_item_index')

@login_required
def aic_create_service_item(request):
    if request.method == 'POST':
        form = ServiceItemForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Ensure form.save() supports user argument
            return redirect('aic_service_item_index')
        else:
            # Return form with errors if validation fails
            return render(request, 'admin/aic/accounting/billing/serviceitem/create.html', {'form':form})  

    # GET request: Render the empty form
    form = ServiceItemForm()
    return render(request, 'admin/aic/accounting/billing/serviceitem/create.html', {'form':form}) 


@login_required
def aic_update_service_item(request, serviceitem_id):
    service_item = get_object_or_404(ServiceItem, id=serviceitem_id)
    if request.method == 'POST':
        form = ServiceItemForm(request.POST, instance=service_item)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('aic_service_item_index')  # Redirect to the list or any other page
    else:
        form = ServiceItemForm(instance=service_item)
    return render(request, 'admin/aic/accounting/billing/serviceitem/create.html', {'form':form, 'service_item':service_item}) 

#<<<<<<<<<<<<<<<=========================== END OF SERVICE ITEMS ==============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#


#<<<<<<<<<<<<<<<<<<,, REQUEST MODULES ============================>>>>>>>>>>>>>>>>>>>>>>>>

# @login_required
# def aic_edo_service_requests(request):
#     try:
#         aic = AIC.objects.get(user=request.user)
#     except AIC.DoesNotExist:
#         messages.error(request, "You are not associated with an AIC account.")
#         return redirect('dashboard')

#     # Optimize by prefetching related ServiceRequestItems
#     servicerequests = ServiceRequest.objects.prefetch_related('servicerequest_items').order_by('-created_at')

#     context = {'servicerequests': servicerequests}
#     return render(request, 'admin/aic/services_edo/service_request.html', context)


@login_required
def aic_service_request_list(request):
    # Get all service requests
    #beneficary = request.user.beneficiary
    
    #servicerequests = ServiceRequest.objects.filter(beneficiary=beneficary)
    servicerequests = ServiceRequest.objects.all()
    
    for servicerequest in servicerequests:
        servicerequest.total_cost_sum = sum(
            service_item.quantity * service_item.unitcost for service_item in servicerequest.servicerequest_items.all()
        )
    
    # Calculate the grand total of all service requests
    grand_total = sum(servicerequest.total_cost_sum for servicerequest in servicerequests)

    return render(request, 'admin/aic/accounting/requests/request_bills.html', {'servicerequests': servicerequests, 'grand_total': grand_total })


@login_required
@csrf_exempt
def aic_approve_service_request(request):
    if request.method == "POST":
        request_id = request.POST.get("request_id")
        approve_note = request.POST.get("approve_note", "")
        
        try:
            service_request = ServiceRequest.objects.get(id=request_id)
            service_request.approve_by = request.user
            service_request.approve_at = now()
            service_request.approve_note = approve_note
            service_request.status = "completed"  # Update status
            service_request.save()
            
            return JsonResponse({"status": "success"})
        except ServiceRequest.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Service Request not found."})
    
    return JsonResponse({"status": "error", "message": "Invalid request."})
############<<<<<<<<<<<<<<<< END OF SERVICE APPROVED >>>>>>>>>>>>>>>>>>>>>>>##################################


@login_required
def aic_invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'admin/aic/accounting/new/invoice_list.html', {'invoices': invoices})

@login_required
def aic_invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'admin/aic/accounting/new/invoice_detail.html', {'invoice': invoice})

@login_required
def aic_invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('aic_invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'admin/aic/accounting/new/create_invoice.html', {'form': form})

@login_required
def aic_invoice_update(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('aic_invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'admin/aic/accounting/new/create_invoice.html', {'form': form, 'invoice':invoice})



@login_required
def aic_change_cash_status(request, cash_id, status):
    cash = get_object_or_404(CashAssigned, id=cash_id)
    if status in ['Approved', 'Denied']:
        cash.status = status
        cash.save()
    return redirect('aic_beneficiaries_cash_requests')


################################### TUNNEL AND SEEDLINGS #####################################################################
def get_time_difference(start_time, finish_time):
    if start_time and finish_time:
        # Convert time to a common date with datetime
        today = datetime.today()
        start_datetime = datetime.combine(today, start_time)
        finish_datetime = datetime.combine(today, finish_time)
        # Calculate the time difference
        return finish_datetime - start_datetime
    return None


#CREATE DATA, NURSERY====================================================================================================, 
#load crop varitey based on Crop selected
def get_crop_varieties(request):
    crop_id = request.GET.get('crop_id')
    if crop_id:
        crop_varieties = CropVariety.objects.filter(crop_id=crop_id).values('id', 'name')
        return JsonResponse({'cropvarieties': list(crop_varieties)})
    return JsonResponse({'cropvarieties': []})

# Create Views
@login_required
def aic_nursery_data_index(request):
    if request.user.is_authenticated:  
        # Get the logged-in supervisor
        # beneficiaries = supervisor.beneficiaries.all()  # Assuming a reverse relationship        
        # Fetch all NurseryData records belonging to these beneficiaries
        nursery_records = NurseryData.objects.filter()
        
        return render(request, 'admin/aic/tunnel/nursery_data.html', {'nursery_records': nursery_records})
    else:
        return redirect('aic_nursery_data_index')
    
#End of Nursery records ====================================================================================================

#height records ====================================================================================================
@login_required
def aic_height_data_index(request):
    if request.user.is_authenticated:                 
        height_records = HeightData.objects.all()
        # beneficiaries = supervisor.beneficiaries.all()  # Assuming a reverse relationship        
        # Fetch all NurseryData records belonging to these beneficiaries
        return render(request, 'admin/aic/tunnel/height_data.html', {'height_records':height_records})
    else:
       return redirect('beneficiary_login')

@login_required
def aic_spraying_data_index(request):
    if request.user.is_authenticated:  
        spraying_records = SprayingData.objects.all()
        
        #records = SprayingRecord.objects.all()
        for record in spraying_records:
            record.time_difference = get_time_difference(record.startTime, record.finishTime)
        #return spraying_records
  
        return render(request, 'admin/aic/tunnel/spraying_data.html', {'spraying_records':spraying_records})
    else:
       return redirect('beneficiary_login')


@login_required
def aic_spraying_submit_feedback(request):
    if request.method == "POST":
        spraying_data_id = request.POST.get("sprayingDataId")
        feedback_text = request.POST.get("feedback")

        # Ensure the logged-in user is an AIC
        try:
            aic = AIC.objects.get(user=request.user)
        except AIC.DoesNotExist:
            return JsonResponse({"status": "error", "message": "You are not authorized to give feedback."})

        spraying_data = get_object_or_404(SprayingData, id=spraying_data_id)

        # Update the feedback fields
        spraying_data.feedback = feedback_text
        spraying_data.feedback_by = request.user
        spraying_data.feedback_at = timezone.now()
        spraying_data.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error", "message": "Invalid request"})


@login_required
def aic_irrigation_data_index(request):
    if request.user.is_authenticated:  
        irrigation_records = IrrigationData.objects.all()

        #records = SprayingRecord.objects.all()
        for record in irrigation_records:
            record.time_difference = get_time_difference(record.startTime, record.finishTime)
        #return spraying_records
        
        return render(request, 'admin/aic/tunnel/irrigation_data.html', {'irrigation_records':irrigation_records})
    else:
       return redirect('beneficiary_login')



@login_required
def aic_trellising_data_index(request):
    if request.user.is_authenticated:  
        trellising_records = TrellisingData.objects.all()
  
        return render(request, 'admin/aic/tunnel/trellising_data.html', {'trellising_records':trellising_records})
    else:
       return redirect('beneficiary_login')
###################################  END OF TUNNELS AND SEEDLINGS ############################################################