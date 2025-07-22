from datetime import datetime, time, timedelta
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db.models import Sum, F, Count
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models.functions import TruncDate
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
# from coworker.forms import CoworkerForm
from yuapp.models import Buyer, CashAssigned, PriceTable, GreenhouseRoom, Beneficiary, Repayment, Supervisor, Transaction, Payment, Delivery, Harvest
from aic.forms import *
from fieldmate.forms import *
from .forms import *



# Create your views here.
@login_required
def edo_price_index(request):
    if request.user.is_authenticated:        
        prices = PriceTable.objects.filter(created_by = request.user.id)
        return render(request, 'admin/edo/price/index.html', {'prices':prices})
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
def edo_create_beneficiary(request):
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
            return redirect('edo_beneficiary_index')  # Redirect to beneficiary login or desired page
        else:
            print(form.errors)
            messages.error(request, 'Error creating beneficiary. Please check the form.')
    else:
        form = BeneficiaryForm()

    return render(request, 'admin/edo/beneficiary/create_beneficiary.html', {'form': form})

@login_required
def edo_update_beneficiary(request, beneficiary_id):
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
            return redirect('edo_beneficiary_index')  # Redirect to the desired page after update
        else:
            print(form.errors)
            messages.error(request, 'Error updating beneficiary. Please check the form.')
    else:
        form = BeneficiaryForm(instance=beneficiary)

    return render(request, 'admin/edo/beneficiary/create_beneficiary.html', {'form': form, 'beneficiary': beneficiary})

 
@login_required
def edo_beneficiary_index(request):
    if request.user.is_authenticated:        
        
        # Get the logged-in supervisor
        supervisor = get_object_or_404(Supervisor, user=request.user)
        
        # Fetch all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
        
        return render(request, 'admin/edo/beneficiary/index.html', {'beneficiaries':beneficiaries})
    else:
       return redirect('edo_beneficiary_index')

# @login_required
# def edo_harvest_history(request):
#     if request.user.is_authenticated:        
#         # Get the logged-in supervisor
#         supervisor = get_object_or_404(Supervisor, user=request.user)        
#         # Fetch all beneficiaries assigned to this supervisor
#         beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
        
#         return render(request, 'admin/edo/harvest/history.html', {'beneficiaries':beneficiaries})
#     else:
#        return redirect('edo_beneficiary_index')

# @login_required
# def edo_harvest_history(request):
#     # Get the logged-in supervisor
#     supervisor = get_object_or_404(Supervisor, user=request.user)
#     # Fetch all beneficiaries assigned to this supervisor
#     beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
#     # Fetch all harvest records related to these beneficiaries
#     harvests = Harvest.objects.filter(beneficiary__in=beneficiaries).select_related('crop', 'grade', 'unit')
#     return render(request, 'admin/edo/harvest/history.html', {
#         'beneficiaries': beneficiaries,
#         'harvests': harvests
#     })  
   
@login_required
def edo_beneficiary_detail(request, beneficiary_id):
    # Get the specific beneficiary for the logged-in user
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    
     # Fetch related records
    harvests = beneficiary.beneficiary_harvest.all()  # Assuming `Harvest` has a ForeignKey to `Beneficiary` check related_name from harvest models
    coworkers = beneficiary.workers.all()  # Correctly use `related_name='workers'` check related_name from worker models
    contracts = beneficiary.contracts.all()  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    tunnel = beneficiary.assigned_tunnel  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    edo = beneficiary.assigned_edo  # Assuming `Contract` has a ForeignKey to `Beneficiary` check related_name from contracts models
    cashloans = beneficiary.cashloans.all()  # Assuming `CashAssigned` has a ForeignKey to `Beneficiary` check related_name from cash_assigned models
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
        'cashloans':cashloans,
        'contracts': contracts,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'workers_by_gender': workers_by_gender,
        'gender_labels': gender_labels,
        'gender_totals': gender_totals,
        'tunnel':tunnel,
        'edo':edo
    }
    
    return render(request, 'admin/edo/beneficiary/profile.html', context)


#Financials
@login_required
def edo_pricetale_index(request):
    if request.user.is_authenticated:        
        prices = PriceTable.objects.all()
        return render(request, 'admin/edo/finance/pricetable.html', {'prices':prices})
    else:
       return redirect('edo_pricetale_index')

@login_required
def edo_create_pricetable(request):
    if request.method == 'POST':
        form = PriceTableForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Pass the user to save method
            return redirect('edo_pricetale_index')
    else:
        form = PriceTableForm()
        return render(request, 'admin/edo/finance/create.html', {'form':form})  

@login_required
def edo_update_price_table(request, pk):
    price_table = get_object_or_404(PriceTable, pk=pk)
    if request.method == 'POST':
        form = PriceTableForm(request.POST, instance=price_table)
        if form.is_valid():
            form.save()  # Save the updated instance
            return redirect('edo_pricetale_index')  # Redirect to the list or any other page
    else:
        form = PriceTableForm(instance=price_table)

    return render(request, 'admin/edo/finance/create.html', {'form':form}) 

@login_required
def edo_price_detail(request, price_id):
    if request.user.is_authenticated: 
        # Get the specific order for the logged-in user
        price = get_object_or_404(PriceTable, id=price_id)
        return render(request, 'admin/edo/price/detail.html', {'price': price})
    else:
       return redirect('beneficiary_login')
     
@login_required
def edo_create_price(request):
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
    return render(request, 'admin/edo/price/create.html', {'form': form})


#update price record
@login_required
def edo_price_update(request, pk):
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
    
    return render(request, 'admin/edo/price/create.html', {'form': form, 'price':price})


def edo_fetch_price_record(harvest, greenhouse):
    #Helper function to fetch the price record based on the harvest and greenhouse."""
    return PriceTable.objects.filter(
        crop_id=harvest.crop,
        grade_id=harvest.grade,
        unit_id=harvest.unit,        
        market_center=greenhouse.marketing_centres
    ).order_by('-from_date').first()

 
    
@login_required
def edo_coworker_index(request):

    if request.user.is_authenticated:        
        coworkers = Worker.objects.filter(created_by = request.user.id)
        return render(request, 'admin/edo/worker/coworker.html', {'coworkers':coworkers})
    else:
       return redirect('beneficiary_login')

@login_required
def edo_beneficiary_coworker_index(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.user.is_authenticated:  
           
        coworkers = Worker.objects.filter(beneficiary = beneficiary)
        
        return render(request, 'admin/edo/worker/beneficiary_coworker.html', {'coworkers':coworkers, 'beneficiary':beneficiary})
    else:
       return redirect('beneficiary_login')

@login_required
def edo_coworker_detail(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    return render(request, 'admin/edo/worker/coworker_detail.html', {'coworker': coworker})

@login_required
def edo_coworker_create(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    # Check if logged-in user is an edo
    #if request.user.role == 'EDO':
    #if request.user.groups.filter(name='EDO').exists():
    if request.method == 'POST':
            form = CoworkerFormEDO(request.POST, request.FILES, beneficiary=beneficiary)
            if form.is_valid():
                # Save the form without committing to the database initially
                coworker = form.save(commit=False)
                # Assign current user and beneficiary to the form instance
                coworker.created_by = request.user
                coworker.beneficiary = beneficiary
                # Save the instance to the database
                coworker.save()
                
                messages.success(request, 'Coworker created successfully.')
                return redirect('edo_coworker_index')
    else:
            form = CoworkerFormEDO(beneficiary=beneficiary)
        
    return render(request, 'admin/edo/worker/coworker_create.html', {'form': form, 'beneficiary': beneficiary})
    # else:
    #     # If the user is not an edo, you can redirect or show an error message
    #     messages.error(request, 'You do not have permission to add a coworker for this beneficiary.')
    #     return redirect('edo_beneficiary_coworker_index')

@login_required
def edo_coworker_update(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    
    beneficiary = Beneficiary.objects.filter(id=coworker.beneficiary)
    
    if request.method == 'POST':
        form = CoworkerFormEDO(request.POST, request.FILES, instance=coworker)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coworker updated successfully.')
            return redirect('edo_beneficiary_coworker_index')
    else:
        form = CoworkerFormEDO(instance=coworker)  # Use the correct form here
    return render(request, 'admin/edo/worker/coworker_create.html', {'form': form, 'coworker': coworker, 'beneficiary':beneficiary})

@login_required
def edo_coworker_delete(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    coworker.delete()
    messages.success(request, 'Coworker deletion successful.')
    return redirect('edo_beneficiary_coworker_index')



#farm input distribution to beneficiaries
@login_required
def edo_beneficiary_distribution(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    distributions = InputDistribution.objects.filter(beneficiary=beneficiary).order_by('-distribution_date')
    
    return render(request, 'admin/edo/farminput/benficiary_distribute.html', 
                  {
                      'distributions': distributions, 
                      'beneficiary': beneficiary
                    }
                  )
    
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< HARVEST CREATION AND ACTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< HARVEST CREATION AND ACTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


#Harvest records for edo
@login_required
def edo_beneficiary_harvest(request, beneficiary_id):
    # Get the beneficiary based on the beneficiary_id
    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_id)

    # Fetch the harvest records specifically assigned to this beneficiary
    assigned_harvest_records = Harvest.objects.filter(beneficiary=beneficiary)

    # Fetch all harvest records, annotating whether they are assigned to the beneficiary or not
    all_harvest_records = Harvest.objects.annotate(
        is_assigned=Case(
            When(id__in=assigned_harvest_records.values_list('id', flat=True), then=0),  # 0 means assigned
            default=1,  # 1 means not assigned
            output_field=IntegerField(),
        )
    ).order_by('is_assigned', '-date', 'crop__name')  # Newest records first

    # Safely calculate total_quantity and total_sum
    total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in assigned_harvest_records)
    total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in assigned_harvest_records)

    # Render the template with the beneficiary and harvest records
    return render(request, 'admin/edo/harvest/beneficiary_harvest.html', {
        'beneficiary': beneficiary,
        'assigned_harvest_records': assigned_harvest_records,
        'all_harvest_records': all_harvest_records,
        'total_quantity': total_quantity,
        'total_sum': total_sum
    })
 
@login_required
def edo_harvest_history(request):
    # Get the logged-in supervisor
    supervisor = get_object_or_404(Supervisor, user=request.user)
    # Fetch all beneficiaries assigned to this supervisor
    beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
    # Fetch all harvest records related to these beneficiaries
    harvest_records = Harvest.objects.filter(beneficiary__in=beneficiaries).select_related('crop', 'grade', 'unit')
    
    # Fetch all harvest records without filtering by beneficiary
    #harvest_records = Harvest.objects.all()
    
    # Calculate total quantity and total price for all records
    total_quantity = harvest_records.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price = harvest_records.aggregate(Sum('total_price'))['total_price__sum'] or 0
                
    return render(request, 'admin/edo/harvest/allrecords.html', {
        'beneficiaries': beneficiaries,
        'assigned_harvest_records': harvest_records,
        'total_quantity': total_quantity,
        'total_price': total_price
    }) 
   
def edo_handle_harvest_form_submission(form, greenhouse, greenhouse_room):
    if form.is_valid():
        harvest = form.save(commit=False)
        price_record = edo_fetch_price_record(harvest, greenhouse)

        if price_record:
            harvest.price_record = price_record
            harvest.total_price = (harvest.quantity or 0) * (price_record.price or 0)
            harvest.greenhouse = greenhouse
            harvest.greenhouse_room = greenhouse_room
            harvest.save()
            return True
        else:
            form.add_error(None, "No price record found for the selected crop, grade, and unit.")
    return False

def edo_get_beneficiary_greenhouse(beneficiary):
    greenhouse_room = getattr(beneficiary, 'assigned_tunnel', None)
    return getattr(greenhouse_room, 'greenhouse', None)

def edo_get_beneficiary_greenhouse_room(beneficiary):
    return getattr(beneficiary, 'assigned_tunnel', None)
 

@login_required
def edo_create_harvest(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    created_by = request.user
    greenhouse = edo_get_beneficiary_greenhouse(beneficiary)
    greenhouse_room = edo_get_beneficiary_greenhouse_room(beneficiary)

    if request.method == 'POST':
        form = HarvestFormEdo(request.POST, beneficiary=beneficiary, created_by=created_by)
        if edo_handle_harvest_form_submission(form, greenhouse, greenhouse_room):
            messages.success(request, "Harvest record successfully created.")
            return redirect('edo_beneficiary_harvest', beneficiary_id=beneficiary.id)
        else:
            messages.error(request, "Error in submitting the harvest record. Please check the form.")

    else:
        form = HarvestFormEdo(beneficiary=beneficiary, created_by=created_by)

    return render(request, 'admin/edo/harvest/create_harvest.html', {
        'form': form,
        'beneficiary': beneficiary
    })


@login_required
def edo_update_harvest(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    beneficiary = harvest.beneficiary
    greenhouse = edo_get_beneficiary_greenhouse(beneficiary)
    greenhouse_room = edo_get_beneficiary_greenhouse_room(beneficiary)

    if request.method == 'POST':
        form = HarvestFormEdo(request.POST, instance=harvest, beneficiary=beneficiary)
        if edo_handle_harvest_form_submission(form, greenhouse, greenhouse_room):
            messages.success(request, 'Harvest updated successfully.')
            return redirect('edo_beneficiary_harvest', beneficiary_id=beneficiary.id)
        else:
            form = HarvestFormEdo(instance=harvest, beneficiary=beneficiary)
            messages.error(request, 'Error updating the harvest record. Please check your input.')

    else:
        form = HarvestFormEdo(instance=harvest)

    return render(request, 'admin/edo/harvest/create_harvest.html', {
        'form': form,
        'harvest': harvest,
        'beneficiary': beneficiary,
        'is_update': True  # <- make sure this is present
    })


@login_required
def edo_view_harvest(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    price_table = harvest.price_record

    # Filter only relevant harvest records
    harvest_records = Harvest.objects.filter(beneficiary=harvest.beneficiary)

    # Efficiently calculate total quantity and total sum
    totals = harvest_records.aggregate(
        total_quantity=Sum('quantity', default=0),
        total_sum=Sum('total_price', default=0)
    )

    return render(request, 'admin/edo/harvest/view_harvest.html', {
        'harvest': harvest,
        'price_table': price_table,
        'total_sum': totals['total_sum'],
        'total_quantity': totals['total_quantity']
    })


@login_required
def edo_get_price_for_grade_and_unit(request):
    grade_id = request.GET.get('grade_id')
    unit_id = request.GET.get('unit_id')
    crop_id = request.GET.get('crop_id')

    try:
        price = PriceTable.objects.filter(
            crop_id=crop_id, grade_id=grade_id, unit_id=unit_id
        ).order_by('-from_date').values_list('price', flat=True).first()

        return JsonResponse({'price': str(price) if price is not None else None})
    except Exception as e:
        return JsonResponse({'price': None, 'error': str(e)})

 
  
@login_required
def edo_view_harvest(request, harvest_id):
    # Retrieve the specific Harvest record by ID
    harvest = get_object_or_404(Harvest, id=harvest_id)
    #price = harvest.price_record
     # Retrieve the associated PriceTable instance directly
    price_table = harvest.price_record
    
    harvest_records = Harvest.objects.all()  # or your specific queryset
     # Safely calculate total_quantity and total_sum
    total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvest_records)
    total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvest_records)

    # if price_table:
    return render(request, 'admin/edo/harvest/view_harvest.html', {
        'harvest': harvest, 
        'price_table':price_table,
        'total_sum': total_sum,
        'total_quantity': total_quantity 
    })
    
#sales dashboard
def edo_sales_dashboard(request):
    # Volume of crop purchased
    total_volume_purchased = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE).aggregate(total_volume=Sum('volume'))['total_volume']
    todos = Todo.objects.filter(created_by=request.user)
    # Total payments (value)
    total_payments = Payment.objects.aggregate(total_paid=Sum('amount_paid'))['total_paid']
    
    # Total deliveries made (volume)
    total_volume_delivered = Delivery.objects.aggregate(total_delivered=Sum('volume_delivered'))['total_delivered']
    
    # Overview of debtors (buyers vs arrears)
    total_due_per_buyer = Transaction.objects.filter(buyer__isnull=False).annotate(
        total_due=F('total_price') - Sum('payment__amount_paid')
    ).values('buyer__client_name', 'total_due')  # Changed 'buyer__name' to 'buyer__client_name'

    # Total cash sales
    total_cash_sales = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE, buyer__isnull=False).aggregate(total_cash=Sum('total_price'))['total_cash']
    
    context = {
        'total_volume_purchased': total_volume_purchased,
        'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
        'total_due_per_buyer': total_due_per_buyer,
        'total_cash_sales': total_cash_sales,
        'todos':todos
    }
    
    return render(request, 'admin/edo/beneficiary/market/sales_dashboard.html', context)


@login_required
def edo_view_harvest(request, harvest_id):
    # Retrieve the specific Harvest record by ID
    harvest = get_object_or_404(Harvest, id=harvest_id)
    #price = harvest.price_record
     # Retrieve the associated PriceTable instance directly
    price_table = harvest.price_record
    # if pri
    # 
    # ce_table:
    return render(request, 'admin/edo/harvest/view_harvest.html', {
        'harvest': harvest, 'price_table':price_table
    })


# Views
################## farm season#################################
@login_required
def edo_farm_season_index(request):
    if request.user.is_authenticated:        
        farmseasons = FarmSeason.objects.all()
        return render(request, 'admin/edo/accounting/farmseason/list.html', {'farmseasons':farmseasons})
    else:
       return redirect('edo_farm_season_index')

@login_required
def edo_create_farm_season(request):
    if request.method == 'POST':
        form = FarmseasonForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Ensure form.save() supports user argument
            return redirect('edo_farm_season_index')
        else:
            # Return form with errors if validation fails
            return render(request, 'admin/edo/accounting/farmseason/create.html', {'form':form})  

    # GET request: Render the empty form
    form = FarmseasonForm()
    return render(request, 'admin/edo/accounting/farmseason/create.html', {'form':form})


@login_required
def edo_update_farm_season(request, farmseason_id):
    farm_season = get_object_or_404(FarmSeason, id=farmseason_id)
    if request.method == 'POST':
        form = FarmseasonForm(request.POST, instance=farm_season)
        if form.is_valid():
            form.save(user=request.user) 
            #form.save()  # Save the updated instance
            return redirect('edo_farm_season_index')  # Redirect to the list or any other page
    else:
        form = FarmseasonForm(instance=farm_season)

    return render(request, 'admin/edo/accounting/farmseason/create.html', {'form':form, 'farm_season':farm_season}) 
############### eND OF FARM SEASON ############################################################


#@csrf_exempt
@require_POST
@csrf_protect
def edo_confirm_harvest_ajax(request):
    harvest_id = request.POST.get("harvest_id")
    created_user = request.user

    try:
        with transaction.atomic():
            # Fetch the harvest record
            harvest = Harvest.objects.select_for_update().get(id=harvest_id, confirmation="Open", status="Pending")

            # Update harvest status
            harvest.confirmation = "Confirmed"
            harvest.status = "Completed"
            harvest.save(update_fields=["confirmation", "status"])

            # Get aggregation fields
            market_centre = harvest.greenhouse.marketing_centres  # Ensure this field is correctly referenced
            unit = harvest.unit

            # Check if an aggregate record exists
            aggregate = HarvestStockAggregate.objects.filter(
                market_centre=market_centre,
                crop=harvest.crop,
                grade=harvest.grade,
                unit_price = harvest.price_record,
                unit=unit,
                aggregation_date=harvest.created_at.date()
            ).first()

            if aggregate:
                # Update existing aggregate record
                aggregate.update_aggregate(harvest.quantity, harvest.total_price)
            else:
                # Create a new aggregate record
                HarvestStockAggregate.objects.create(
                    market_centre=market_centre,
                    crop=harvest.crop,
                    grade=harvest.grade,
                    unit_price = harvest.price_record,
                    unit=unit,
                    total_quantity=harvest.quantity,
                    total_value=harvest.total_price,
                    created_by=created_user,
                    aggregation_date=harvest.created_at.date()
                )

        return JsonResponse({"success": True, "message": "Harvest confirmed successfully!"})

    except Harvest.DoesNotExist:
        return JsonResponse({"success": False, "message": "Harvest record not found or already confirmed."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
    
 
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END OF HARVEST CREATION AND ACTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END OF HARVEST CREATION AND ACTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@login_required
def edo_farm_input_stock(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    
    stocks = InputEdoDistribution.objects.filter(supervisor=supervisor).order_by('-distribution_date')
    
    return render(request, 'admin/edo/farminput/farminput_stock.html', {'stocks': stocks})


@login_required
def edo_distribution_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    distributions = InputDistribution.objects.filter(distributed_by=supervisor).order_by('-distribution_date')
    return render(request, 'admin/edo/farminput/distribution_list.html', {'distributions': distributions})

@login_required
def supervisor_distribution_list(request):
    supervisor = request.user
    distributions = InputEdoDistribution.objects.filter(supervisor=supervisor)

    return render(request, 'supervisor_distribution_list.html', {
        'distributions': distributions,
    })


@login_required
def edo_get_farm_input_details(request):
    farm_input_id = request.GET.get('farm_input_id')
    user = request.user

    try:
        # Ensure the supervisor is associated with the logged-in user
        edo = Supervisor.objects.filter(user=user).first()
    
        if not edo:
            return JsonResponse({'error': 'Supervisor not found for the logged-in user'}, status=403)

        # Retrieve the InputEdoDistribution for the supervisor and farm_input
        input_edo_distribution = InputEdoDistribution.objects.get(
            id=farm_input_id, supervisor=edo
        )

        # Extract the quantity and unit cost
        quantity = int(input_edo_distribution.quantity)  # Convert to whole number
        unit_cost = f"{input_edo_distribution.unit_cost:,.2f}"  # Format as currency

        # Respond with the required details
        return JsonResponse({
            'quantity': quantity,
            'unit_cost': unit_cost,
        })
    except Supervisor.DoesNotExist:
        return JsonResponse({'error': 'Supervisor not found for the logged-in user'}, status=403)
    except InputEdoDistribution.DoesNotExist:
        return JsonResponse({
            'error': f'No InputEdoDistribution found for farm_input_id={farm_input_id} and supervisor={edo}'
        }, status=400)




@login_required
def edo_create_distribute_input(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    
    if request.method == 'POST':
        form = InputDistributionForm(request.POST, supervisor=supervisor)
        if form.is_valid():
            distribution = form.save(commit=False)
            distribution.distributed_by = supervisor
            distribution.created_by = request.user
            distribution.save()
            return redirect('edo_distribution_list')
        else:
            # Log errors for debugging
            print(form.errors)
    else:
        form = InputDistributionForm(supervisor=supervisor)

    return render(request, 'admin/edo/farminput/create_distribute_input.html', {'form': form})


#farm input received from input dealer
#create
@login_required
def edo_add_farm_input(request):
    if request.method == 'POST':
        form = FarmInputForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('edo_farm_input_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        form = FarmInputForm()

    return render(request, 'admin/edo/farminput/create_farminput.html', {'form': form})

#update

@login_required
def edo_update_farm_input(request, input_id):
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
            return redirect('edo_farm_input_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = FarmInputForm(instance=farm_input)

    return render(request, 'admin/edo/farminput/create_farminput.html', {'form': form, 'farm_input': farm_input})

#listsss
@login_required
def edo_farm_input_list(request):
    farm_inputs = FarmInput.objects.all().order_by('-created_at')
    
    #farm_inputs = FarmInput.objects.all().order_by('-created_at')
    farm_input_data = []

    for farm_input in farm_inputs:
        distributed_quantity = InputDistribution.objects.filter(
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
        
    return render(request, 'admin/edo/farminput/list_farminput.html', {'farm_inputs': farm_inputs, 'farm_input_data': farm_input_data})


#End of farm input received from input dealer


#input dealer module
@login_required
def edo_input_dealer_list(request):
    inputdealers = InputDealer.objects.all().order_by('-created_at')
    return render(request, 'admin/edo/farminput/inputdealer.html', {'inputdealers': inputdealers})

@login_required
def edo_create_inputdealer(request):
    if request.method == 'POST':
        form = InputDealerForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('edo_input_dealer_list')
    else:
        form = InputDealerForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/edo/farminput/create_input_dealer.html', {'form': form})

@login_required
def edo_update_farm_inputdealer(request, inputdealer_id):
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
            return redirect('edo_input_dealer_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = InputDealerForm(instance=inputdealer)

    return render(request, 'admin/edo/farminput/create_input_dealer.html', {'form': form, 'inputdealer': inputdealer})


#farm input category modeule
@login_required
def edo_input_category_list(request):
    inputcats = FarmInputCategory.objects.all().order_by('-created_at')
    return render(request, 'admin/edo/farminput/inputcategory.html', {'inputcats': inputcats})

@login_required
def edo_create_input_category(request):
    if request.method == 'POST':
        form = FarmInputCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            farm_input = form.save(commit=False)
            farm_input.created_by = request.user
            farm_input.save()
            return redirect('edo_input_category_list')
    else:
        form = FarmInputCategoryForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/edo/farminput/create_input_category.html', {'form': form})

@login_required
def edo_update_input_category(request, inputcategory_id):
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
            return redirect('edo_input_dealer_list')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = FarmInputCategoryForm(instance=inputcategory)

    return render(request, 'admin/edo/farminput/create_input_category.html', {'form': form, 'inputcategory': inputcategory})


#BUYER MODULE
@login_required
def edo_buyer_index(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        # Fetch all ChangingRoom assignments for this specific beneficiary
        buyers = Buyer.objects.all()

        return render(request, 'admin/edo/buyer/buyer.html', {
            'buyers': buyers,
        })
    else:
        return redirect('beneficiary_login')

@login_required
def edo_buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'admin/edo/buyer/detail.html', {'buyer': buyer})

@login_required
def edo_create_buyer(request):
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
            return redirect('edo_buyer_index')
    else:
        form = BuyerForm()

    # Ensure that this part always returns a response
    return render(request, 'admin/edo/buyer/create.html', {'form': form})

@login_required
def edo_update_buyer(request, buyer_id):
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
            return redirect('edo_buyer_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = BuyerForm(instance=buyer)

    return render(request, 'admin/edo/buyer/create.html', {'form': form, 'buyer': buyer})


#ENTERPRISE DEVELOPMENT OFFICER (Edo Module)@login_required
def edo_edo_index(request):
    if request.user.is_authenticated:        
            edos = Supervisor.objects.all()
            return render(request, 'admin/edo/edo/edo.html', {'edos':edos})
    else:
       return redirect('beneficiary_login')
   
   
@login_required
def edo_edo_detail(request, edo_id):
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
       
        
        return render(request, 'admin/edo/edo/detail.html', context)
    
@login_required
def edo_create_edo(request):
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
            
            return redirect('edo_edo_index')  # Redirect to the appropriate page after successful save
        # If the form is invalid, it will fall through and render the form with errors

    else:
        form = SupervisorForm()
    
    # Render the form template, whether it's a GET request or a failed POST submission
    return render(request, 'admin/edo/edo/create.html', {'form': form})


@login_required
def edo_update_edo(request, edo_id):
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
                
            return redirect('edo_buyer_index')
        # If form is invalid, it will continue to render the form with errors

    else:
        # Populate the form with existing data
        form = SupervisorForm(instance=edo)

    return render(request, 'admin/edo/buyer/create.html', {'form': form, 'edo': edo})


#FINANCIAL MODULE

# @login_required
# def edo_cash_loaned_list(request):
#     #supervisor = Supervisor.objects.get(id=edo_id)
#     supervisor = Supervisor.objects.get(user=request.user)
        
#     cash_load_records = CashAssigned.objects.prefetch_related('repayment_set').all()
#     return render(request, 'admin/edo/finance/cashloan_list.html', {'cash_load_records': cash_load_records})



# #Beneficiary Financials 
# @login_required
# def edo_beneficiaries_cash_requests(request):
#     beneficiaries = Beneficiary.objects.prefetch_related('cashassigned_set').all()
#     return render(request, 'admin/edo/finance/cash_request.html', {'beneficiaries': beneficiaries})

# @login_required
# def edo_beneficiaries_repayments(request):
#     repayments = Repayment.objects.select_related('cash_assigned__beneficiary')
#     return render(request, 'admin/edo/finance/repayment.html', {'repayments': repayments})

@login_required
def edo_cash_loaned_list(request):
    # Get the currently logged-in supervisor
    supervisor = get_object_or_404(Supervisor, user=request.user)

    # Get all cash loan records where the beneficiary is assigned to the logged-in supervisor
    cash_load_records = CashAssigned.objects.filter(
        beneficiary__assigned_edo=supervisor
    ).prefetch_related('repayment_set')

    return render(request, 'admin/edo/finance/cashloan_list.html', {'cash_load_records': cash_load_records})

@login_required
def edo_cashload_detail(request, cashload_id):
    # Get the currently logged-in supervisor
    supervisor = get_object_or_404(Supervisor, user=request.user)

    # Get all cash loan records where the beneficiary is assigned to the logged-in supervisor
    cash_load_records = CashAssigned.objects.filter(id=cashload_id,
        beneficiary__assigned_edo=supervisor
    ).prefetch_related('repayment_set')

    return render(request, 'admin/edo/finance/cashloan_detail.html', {'cash_load_records': cash_load_records})




@login_required
def edo_beneficiaries_cash_requests(request):
    # Get the currently logged-in supervisor
    supervisor = get_object_or_404(Supervisor, user=request.user)

    # Get all beneficiaries assigned to the logged-in supervisor
    beneficiaries = Beneficiary.objects.filter(
        assigned_edo=supervisor
    ).prefetch_related('cashloans')  # 'cashloans' is the related_name in CashAssigned

    return render(request, 'admin/edo/finance/cash_request.html', {'beneficiaries': beneficiaries})


@login_required
def edo_beneficiaries_repayments(request):
    # Get the currently logged-in supervisor
    supervisor = get_object_or_404(Supervisor, user=request.user)

    # Get all repayment records where the related beneficiary is assigned to the logged-in supervisor
    repayments = Repayment.objects.filter(
        cash_assigned__beneficiary__assigned_edo=supervisor
    ).select_related('cash_assigned__beneficiary')

    return render(request, 'admin/edo/finance/repayment.html', {'repayments': repayments})
 
@login_required
def edo_change_cash_status(request, cash_id, status):
    cash = get_object_or_404(CashAssigned, id=cash_id)
    if status in ['Approved', 'Denied']:
        cash.status = status
        cash.save()
    return redirect('edo_beneficiaries_cash_requests')

@login_required
def edo_change_repayment_status(request, repayment_id, status):
    repayment = get_object_or_404(Repayment, id=repayment_id)
    if status in ['Approved', 'Denied']:
        repayment.status = status
        repayment.save()
    return redirect('edo_beneficiaries_repayments')


@login_required
def edo_profile_index(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        try:
            # Fetch the beneficiary details associated with the logged-in user
            # edo = request.user.supervisor
            supervisor = Supervisor.objects.get(user=request.user)
            #supervisor = get_object_or_404(Supervisor, user=request.user)#
            
            # Fetch coworkers or any additional data you want to display
            coworkers = Worker.objects.filter(created_by=request.user.id)
            beneficiaries = Beneficiary.objects.filter(assigned_edo_id=supervisor.id)
            beneficiary_created_edo = Beneficiary.objects.filter(created_by=request.user.id)
            # beneficiaries = Beneficiary.objects.filter(assigned_supervisor_id=supervisor.id) 
            
            #supervisor = get_object_or_404(Supervisor, user=request.user)# Assuming 'beneficiary' is linked to user  
            # Get all greenhouses assigned to this supervisor
            greenhouses = supervisor.greenhouse.all()
        
            # Get all cities assigned to this supervisor
            cities = supervisor.city.all()
            # Get all greenhouse rooms related to the greenhouses assigned to this supervisor
            all_tunels = GreenhouseRoom.objects.filter(greenhouse__in=greenhouses)

            # Count male and female beneficiaries
            gender_counts = beneficiaries.values('gender').annotate(total=Count('id'))
    
                # Create a dictionary to store counts for easier access
            gender_count_dict = {
                    'Male': 0,
                    'Female': 0
                }

                # Populate the gender count dictionary
            for gender in gender_counts:
                    if gender['gender'] in gender_count_dict:
                        gender_count_dict[gender['gender']] += gender['total']

            context = {
                'edo': supervisor,
                'beneficiary_created_edo':beneficiary_created_edo,
                'coworkers': coworkers,
                'beneficiaries': beneficiaries,
                'gender_count': gender_count_dict,
                'greenhouses': greenhouses,
                'cities': cities,
                'all_tunels': all_tunels
            }
            # Render the profile page with the beneficiary details
            return render(request, 'admin/edo/profile.html', context)
        except Supervisor.DoesNotExist:
            # Handle case where the user is authenticated but not a beneficiary
            return redirect('edo_login')
    else:
        return redirect('beneficiary_login')
		
		
#crops
# topics for discussion.  
@login_required
def edo_crop_index(request):
    if request.user.is_authenticated:
        # Get the supervisor associated with the current authenticated user
        supervisor = Supervisor.objects.get(user=request.user)
        
        # Find all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
        
        # Extract crops assigned to the supervisor's beneficiaries
        assigned_crops = Crop.objects.filter(beneficiary__in=beneficiaries).distinct()
        
        # Retrieve all crops for comparison or display purposes
        all_crops = Crop.objects.all()

        return render(request, 'admin/edo/crop/crop.html', {
            'all_crops': all_crops,         # All crops from Crop model
            'assigned_crops': assigned_crops  # Only crops assigned to the supervisor's beneficiaries
        })
    else:
       return redirect('beneficiary_login')


# topics for discussion.  
@login_required
def edo_tunnel_index(request):

    if request.user.is_authenticated:        
        #crops = Crop.objects.all()
        supervisor = get_object_or_404(Supervisor, user=request.user)# Assuming 'beneficiary' is linked to user  
         # Get all greenhouses assigned to this supervisor
        greenhouses = supervisor.greenhouse.all()
    
        # Get all cities assigned to this supervisor
        cities = supervisor.city.all()
        # Get all greenhouse rooms related to the greenhouses assigned to this supervisor
        all_tunels = GreenhouseRoom.objects.filter(greenhouse__in=greenhouses)

        context = {
            'supervisor': supervisor,
            'greenhouses': greenhouses,
            'cities': cities,
            'all_tunels': all_tunels
        }
          
        return render(request, 'admin/edo/greenhouse/tunnel.html', context)
    else:
       return redirect('beneficiary_login')

#Changing room
# topics for discussion.  
@login_required
def edo_changingroom_index(request):
    if request.user.is_authenticated:
        # Get the supervisor associated with the logged-in user
        supervisor = Supervisor.objects.filter(user=request.user).first()
        

        if supervisor:
            # Find all beneficiaries assigned to this supervisor
            #beneficiaries = supervisor.beneficiary.assigned_edo.all()  # Assuming 'beneficiary_set' reverse relationship
           # supervisor = get_object_or_404(Supervisor, user=request.user)
        
            # Fetch all beneficiaries assigned to this supervisor
            beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor.id)

            # Retrieve all ChangingRoomAssign records for the supervisor's beneficiaries
            assigned_changing_rooms = ChangingRoomAssign.objects.filter(beneficiary__in=beneficiaries)
            
            # Extract the related ChangingRoom instances
            changing_rooms = [assign.changing_room for assign in assigned_changing_rooms]

            return render(request, 'admin/edo/greenhouse/changingroom.html', {
                'changing_rooms': changing_rooms,  # Only ChangingRooms assigned to the supervisor's beneficiaries
                'assigned_changing_rooms': assigned_changing_rooms
            })
        else:
            # Redirect or handle case where no supervisor is found for the user
            return redirect('beneficiary_login')
    else:
        return redirect('beneficiary_login')

@login_required
def edo_changingroom_detail(request, pk):
    # Get the specific changing room by primary key (pk)
    changeroom = get_object_or_404(ChangingRoom, pk=pk)
    
    # Get all assignments (beneficiaries) for this specific changing room
    assigned_beneficiaries = ChangingRoomAssign.objects.filter(changing_room=changeroom)
    
    return render(request, 'admin/edo/greenhouse/changingroom_detail.html', {
        'changeroom': changeroom,
        'assigned_beneficiaries': assigned_beneficiaries
    })


#FORUM CHANNEL=================================================================================
    
@login_required
def edo_trend_knowledge_index(request):

    if request.user.is_authenticated:        
        trends = TrendKnowledgeBank.objects.filter(created_by = request.user.id)
        return render(request, 'admin/edo/forum/index.html', {'trends':trends})
    else:
       return redirect('beneficiary_login')

# topics for discussion.  
@login_required
def edo_trend_knowledge_board(request):

    if request.user.is_authenticated:        
        trs = TrendKnowledgeBank.objects.all()
        return render(request, 'admin/edo/forum/discussion.html', {'trs':trs})
    else:
       return redirect('beneficiary_login')
   
# View to create a new TrendKnowledgeBank
@login_required
def edo_create_trend_knowledge(request):
    if not request.user.groups.filter(name='Beneficiary').exists():
        messages.error(request, 'You do not have permission to create a Trend Knowledge Topic.')
        return redirect('supervisor_dashboard')
    
    if request.method == 'POST':
        form = TrendKnowledgeBankForm(request.POST, request.FILES)
        if form.is_valid():
            trend_knowledge_bank = form.save(commit=False)
            trend_knowledge_bank.created_by = request.user  # Associate with logged-in user
            trend_knowledge_bank.save()
            messages.success(request, 'Trend Knowledge Successfully Created.')
            return redirect('supervisor_dashboard')  # Redirect to dashboard or another relevant page
    else:
        form = TrendKnowledgeBankForm()
    
    return render(request, 'admin/edo/forum/create.html', {'form': form})

# View to create a discussion under a specific TrendKnowledgeBank
@login_required
def edo_discussion_trend_knowledge(request, pk):
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
    
    return render(request, 'admin/edo/forum/discussion.html', {'form': form, 'trend_knowledge_bank': trend_knowledge_bank})

@login_required
def edo_trend_knowledge_bank_detail(request, pk):
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

    return render(request, 'admin/edo/forum/detail.html', {
        'trend_knowledge_bank': trend_knowledge_bank,
        'discussions': discussions,
        'discussion_form': discussion_form
    })
#======================= END OF FORUM==========================================================




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
def edo_nursery_data_index(request):
    if request.user.is_authenticated:  
        # Get the logged-in supervisor
        try:
            supervisor = get_object_or_404(Supervisor, user=request.user)
        except Supervisor.DoesNotExist:
            return redirect('beneficiary_login')        
        # Get all beneficiaries assigned to this supervisor
        
                
        # Fetch all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
        
        # beneficiaries = supervisor.beneficiaries.all()  # Assuming a reverse relationship        
        # Fetch all NurseryData records belonging to these beneficiaries
        nursery_records = NurseryData.objects.filter(beneficiary__in=beneficiaries)
        
        return render(request, 'admin/edo/tunnel/nursery_data.html', {'nursery_records': nursery_records, 'beneficiaries':beneficiaries})
    else:
        return redirect('beneficiary_login')
   
@login_required
def edo_create_nursery_data(request, beneficiary_id):
    if request.user.is_authenticated:
        #supervisor = request.user  
        #beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        
        if request.method == 'POST':
            form = NurseryDataFormEdo(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                nursery_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                #beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                nursery_data.greenhouse_room = assigned_tunnel
                nursery_data.greenhouse = greenhouse
                
                nursery_data.beneficiary = beneficiary  # Assuming you have a related Beneficiary instance
                nursery_data.created_by = request.user
                nursery_data.status = 'Confirmed'
                nursery_data.save()
            return redirect('edo_nursery_data_index')  # Redirect to the appropriate page
        else:
            form = NurseryDataFormEdo(beneficiary=beneficiary)
        return render(request, 'admin/edo/tunnel/create_nursery.html', {'form': form, 'beneficiary':beneficiary})

# Update Views
@login_required
def edo_update_nursery_data(request, nursery_id):
    # Retrieve the nursery data instance
    nursery_data = get_object_or_404(NurseryData, id=nursery_id)

    beneficiary = nursery_data.beneficiary
    crop = nursery_data.crop

    # Load cropvariety based on the selected crop
    if nursery_data.cropvariety:
        cropvariety = nursery_data.cropvariety
    else:
        cropvariety = CropVariety.objects.filter(crop=crop)

    if request.method == 'POST':
        form = NurseryDataFormEdo(request.POST, instance=nursery_data, beneficiary=beneficiary)

        if form.is_valid():
            nursery_data = form.save(commit=False)

            # Retrieve the assigned tunnel (greenhouse_room)
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse

            # Set dynamically retrieved greenhouse and greenhouse_room
            nursery_data.greenhouse_room = assigned_tunnel
            nursery_data.greenhouse = greenhouse
            nursery_data.beneficiary = beneficiary

            nursery_data.save()
            messages.success(request, 'Nursery record updated successfully.')
            return redirect('edo_nursery_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = NurseryDataFormEdo(instance=nursery_data, beneficiary=beneficiary)

    return render(request, 'admin/edo/tunnel/create_nursery.html', {
        'form': form,
        'nursery_data': nursery_data,
        'crop': crop,
        'cropvariety': cropvariety,
        'beneficiary': beneficiary
    })

    
#End of Nursery records ====================================================================================================
   
@login_required
def edo_create_spraying_data(request, beneficiary_id):
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    if request.method == 'POST':
        form = SprayingDataForm(request.POST)
        if form.is_valid():
            spraying_data = form.save(commit=False)
            spraying_data.beneficiary = beneficiary
            spraying_data.created_by = request.user
            spraying_data.status = 'Confirmed'
            spraying_data.save()
            return redirect('user_login')
    else:
        form = SprayingDataForm()
    return render(request, 'admin/edo/tunnel/create_spraying.html', {'form': form, 'beneficiary':beneficiary})

@login_required
def edo_create_trellising_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.method == 'POST':
        form = TrellisingDataForm(request.POST)
        if form.is_valid():
            trellising_data = form.save(commit=False)
            trellising_data.beneficiary = beneficiary
            trellising_data.created_by = request.user
            trellising_data.status = 'Confirmed'
            trellising_data.save()
            return redirect('user_login')
    else:
        form = TrellisingDataForm()
    return render(request, 'admin/edo/tunnel/create_trellising_data.html', {'form': form, 'beneficiary':beneficiary})

@login_required
def edo_create_irrigation_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.method == 'POST':
        form = IrrigationDataForm(request.POST)
        if form.is_valid():
            irrigation_data = form.save(commit=False)
            irrigation_data.beneficiary = beneficiary
            irrigation_data.created_by = request.user
            irrigation_data.status = 'Confirmed'
            irrigation_data.save()
            return redirect('user_login')
    else:
        form = IrrigationDataForm()
    return render(request, 'admin/edo/tunnel/create_irrigation_data.html', {'form': form, 'beneficiary':beneficiary})





#height records ====================================================================================================
# Create Views
@login_required
def edo_height_data_index(request):
    if request.user.is_authenticated:  
        
        try:
            supervisor = get_object_or_404(Supervisor, user=request.user)
        except Supervisor.DoesNotExist:
            return redirect('beneficiary_login') 
         # Fetch all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)        
        height_records = HeightData.objects.filter(beneficiary__in=beneficiaries)
        # beneficiaries = supervisor.beneficiaries.all()  # Assuming a reverse relationship        
        # Fetch all NurseryData records belonging to these beneficiaries
        return render(request, 'admin/edo/tunnel/height_data.html', {'height_records':height_records, 'beneficiaries':beneficiaries})
    else:
       return redirect('beneficiary_logo')
   
   
@login_required
def edo_create_height_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.user.is_authenticated:  
        #beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = HeightDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                height_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                #beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                height_data.greenhouse_room = assigned_tunnel
                height_data.greenhouse = greenhouse
                
                height_data.beneficiary = beneficiary  # Assuming you have a related Beneficiary instance
                height_data.created_by = request.user
                height_data.status = 'Confirmed'
                height_data.reviewed_by = request.user
                height_data.reviewed_at = timezone.now() 
                height_data.save()
            return redirect('edo_height_data_index')  # Redirect to the appropriate page
        else:
            form = HeightDataForm(beneficiary=beneficiary)
        return render(request, 'admin/edo/tunnel/create_height.html', {'form': form, 'beneficiary':beneficiary})

@login_required
def edo_update_height_data(request, height_id):
    #beneficiary = request.user.beneficiary
    
    heightdata = HeightData.objects.get(id=height_id)
    
    beneficiary = heightdata.beneficiary
     
    
    height_data = get_object_or_404(HeightData, id=height_id, beneficiary=beneficiary)
    crop = height_data.crop
    
    if request.method == 'POST':
        form = HeightDataForm(request.POST, instance=height_data)
        if form.is_valid():
            height_data = form.save(commit=False)
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse
            height_data.greenhouse_room = assigned_tunnel
            height_data.greenhouse = greenhouse
            height_data.beneficiary = beneficiary
            
            height_data.reviewed_by = request.user
            height_data.reviewed_at = timezone.now()            

            form.save()
            messages.success(request, 'Plant Height record updated successfully.')
            return redirect('edo_height_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = HeightDataForm(instance=height_data)

    return render(request, 'admin/edo/tunnel/create_height.html', {
        'form': form,
        'height_data': height_data,  # Ensure this matches the template
        'crop':crop,
        'beneficiary':beneficiary
    })
#end of height data===============================================================================================


def get_time_difference(start_time, finish_time):
    if start_time and finish_time:
        # Convert time to a common date with datetime
        today = datetime.today()
        start_datetime = datetime.combine(today, start_time)
        finish_datetime = datetime.combine(today, finish_time)
        # Calculate the time difference
        return finish_datetime - start_datetime
    return None

#Spraying records ====================================================================================================
# Create Views
@login_required
def edo_spraying_data_index(request):
    if request.user.is_authenticated: 
        
        try:
            supervisor = get_object_or_404(Supervisor, user=request.user)
        except Supervisor.DoesNotExist:
            return redirect('beneficiary_login') 
         # Fetch all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)               
        spraying_records = SprayingData.objects.filter(beneficiary__in=beneficiaries)

         #records = SprayingRecord.objects.all()
        for record in spraying_records:
            record.time_difference = get_time_difference(record.startTime, record.finishTime)
        #return spraying_records
        
        return render(request, 'admin/edo/tunnel/spraying_data.html', {'spraying_records':spraying_records, 'beneficiaries':beneficiaries})
    else:
       return redirect('beneficiary_logo')
   
   
@login_required
def edo_create_spraying_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.user.is_authenticated:  
        #beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = SprayingDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                spraying_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                #beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                spraying_data.greenhouse_room = assigned_tunnel
                spraying_data.greenhouse = greenhouse
                
                spraying_data.beneficiary = beneficiary  # Assuming you have a related Beneficiary instance
                spraying_data.created_by = request.user
                spraying_data.status = 'Confirmed'
                spraying_data.reviewed_by = request.user
                spraying_data.reviewed_at = timezone.now() 
            
                spraying_data.save()
            return redirect('edo_spraying_data_index')  # Redirect to the appropriate page
        else:
            form = SprayingDataForm(beneficiary=beneficiary)
        return render(request, 'admin/edo/tunnel/create_spraying.html', {'form': form, 'beneficiary':beneficiary})


@login_required
def edo_update_spraying_data(request, spraying_id, beneficiary_id):
#def edo_update_spraying_data(request, spraying_id, beneficiary_id):
    #beneficiary = request.user.beneficiary
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    spraying_data = get_object_or_404(SprayingData, id=spraying_id, beneficiary=beneficiary)
    crop = spraying_data.crop
    
    if request.method == 'POST':
        #form = SprayingDataForm(request.POST, instance=spraying_data)
        form = SprayingDataForm(request.POST, instance=spraying_data, beneficiary=beneficiary)
        if form.is_valid():
            spraying_data = form.save(commit=False)
            
            
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            
            greenhouse = greenhouse_room.greenhouse
            spraying_data.greenhouse_room = assigned_tunnel
            spraying_data.greenhouse = greenhouse
            spraying_data.beneficiary = beneficiary
            
            form.save()
            messages.success(request, 'Spraying record updated successfully.')
            return redirect('edo_spraying_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        #form = SprayingDataForm(instance=spraying_data)
         form = SprayingDataForm(instance=spraying_data, beneficiary=beneficiary)

    return render(request, 'admin/edo/tunnel/create_spraying.html', {
        'form': form,
        'spraying_data': spraying_data,  # Ensure this matches the template
        'crop':crop,
        'beneficiary':beneficiary
    })

#end of Spraying data===============================================================================================


#Irrigation records ====================================================================================================
# Create Views
@login_required
def edo_irrigation_data_index(request):
    if request.user.is_authenticated:  
            try:
                supervisor = get_object_or_404(Supervisor, user=request.user)
            except Supervisor.DoesNotExist:
                return redirect('beneficiary_login') 

            # Fetch all beneficiaries assigned to this supervisor
            beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor) 
            
            # Get the User instances associated with each beneficiary
            beneficiary_users = beneficiaries.values_list('user', flat=True)
            
            # Use beneficiary_users to filter trellising records
            irrigation_records = IrrigationData.objects.filter(beneficiary__user__in=beneficiary_users)

            #records = SprayingRecord.objects.all()
            for record in irrigation_records:
                record.time_difference = get_time_difference(record.startTime, record.finishTime)
            #return spraying_records
            
                return render(request, 'admin/edo/tunnel/irrigation_data.html', {
                'irrigation_records': irrigation_records,
                'beneficiaries': beneficiaries
            })
    else:
            return redirect('beneficiary_login')
     
@login_required
def edo_create_irrigation_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.user.is_authenticated:  
        #beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = IrrigationDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                irrigation_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                #beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                irrigation_data.greenhouse_room = assigned_tunnel
                irrigation_data.greenhouse = greenhouse
                
                irrigation_data.beneficiary = beneficiary  # Assuming you have a related Beneficiary instance
                irrigation_data.created_by = request.user
                irrigation_data.status = 'Confirmed'
                irrigation_data.reviewed_by = request.user
                irrigation_data.reviewed_at = timezone.now() 
                
                irrigation_data.save()
            return redirect('edo_irrigation_data_index')  # Redirect to the appropriate page
        else:
            form = IrrigationDataForm(beneficiary=beneficiary)
        return render(request, 'admin/edo/tunnel/create_irrigation.html', {'form': form, 'beneficiary':beneficiary})

@login_required
def edo_update_irrigation_data(request, irrigation_id):
    #beneficiary = request.user.beneficiary
    
    irrigationdata = IrrigationData.objects.get(id=irrigation_id)    
    beneficiary = irrigationdata.beneficiary
    
    irrigation_data = get_object_or_404(IrrigationData, id=irrigation_id, beneficiary=beneficiary)
    crop = irrigation_data.crop
    
    if request.method == 'POST':
        form = IrrigationDataForm(request.POST, instance=irrigation_data)
        if form.is_valid():
            irrigation_data = form.save(commit=False)
            
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse
            irrigation_data.greenhouse_room = assigned_tunnel
            irrigation_data.greenhouse = greenhouse
            irrigation_data.beneficiary = beneficiary
            
            irrigation_data.reviewed_by = request.user
            irrigation_data.reviewed_at = timezone.now() 

            form.save()
            messages.success(request, 'Irrigation record updated successfully.')
            return redirect('edo_irrigation_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = IrrigationDataForm(instance=irrigation_data)

    return render(request, 'admin/edo/tunnel/create_irrigation.html', {
        'form': form,
        'irrigation_data': irrigation_data,  # Ensure this matches the template
        'crop':crop
    })
#end of Irrigation data===============================================================================================


#TrellisingData records ====================================================================================================
# Create Views
@login_required
def edo_trellising_data_index(request):
    if request.user.is_authenticated:  
        try:
            supervisor = get_object_or_404(Supervisor, user=request.user)
        except Supervisor.DoesNotExist:
            return redirect('beneficiary_login') 

        # Fetch all beneficiaries assigned to this supervisor
        beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor) 
        
        # Get the User instances associated with each beneficiary
        beneficiary_users = beneficiaries.values_list('user', flat=True)
        
        # Use beneficiary_users to filter trellising records
        trellising_records = TrellisingData.objects.filter(beneficiary__user__in=beneficiary_users)

        return render(request, 'admin/edo/tunnel/trellising_data.html', {
            'trellising_records': trellising_records,
            'beneficiaries': beneficiaries
        })
    else:
       return redirect('beneficiary_login')
   
   
@login_required
def edo_create_trellising_data(request, beneficiary_id):
    
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    if request.user.is_authenticated:  
        #beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = TrellisingDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                trellising_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                #beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                trellising_data.greenhouse_room = assigned_tunnel
                trellising_data.greenhouse = greenhouse
                
                trellising_data.beneficiary = beneficiary  # Assuming you have a related Beneficiary instance
                trellising_data.created_by = request.user
                trellising_data.status = 'Confirmed'
                trellising_data.reviewed_by = request.user
                trellising_data.reviewed_at = timezone.now()
                
                trellising_data.save()
            return redirect('edo_trellising_data_index')  # Redirect to the appropriate page
        else:
            form = TrellisingDataForm(beneficiary=beneficiary)
        return render(request, 'admin/edo/tunnel/create_trellising.html', {'form': form, 'beneficiary':beneficiary})

@login_required
def edo_update_trellising_data(request, trellising_id):
    #beneficiary = request.user.beneficiary
    
    trelldata = HeightData.objects.get(id=trellising_id)    
    beneficiary = trelldata.beneficiary
    
    trellising_data = get_object_or_404(TrellisingData, id=trellising_id, beneficiary=beneficiary)
    crop = trellising_data.crop
    
    if request.method == 'POST':
        form = TrellisingDataForm(request.POST, instance=trellising_data)
        if form.is_valid():
            trellising_data = form.save(commit=False)
            
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse
            trellising_data.greenhouse_room = assigned_tunnel
            trellising_data.greenhouse = greenhouse
            trellising_data.beneficiary = beneficiary
            
            trellising_data.reviewed_by = request.user
            trellising_data.reviewed_at = timezone.now()

            form.save()
            messages.success(request, 'Trellising record updated successfully.')
            return redirect('edo_trellising_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = TrellisingDataForm(instance=trellising_data)

    return render(request, 'admin/edo/tunnel/create_trellising.html', {
        'form': form,
        'trellising_data': trellising_data,  # Ensure this matches the template
        'crop':crop
    })
#end of TrellisingData data===============================================================================================



#<<<<<<<<<<<<<<<=========================== SERVICE ITEMS CONFIGURATION ==============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#

@login_required
def edo_service_request_index(request):
    # Get all service requests
    edo = request.user
    servicerequests = ServiceRequest.objects.filter(created_by = edo)
    
    for servicerequest in servicerequests:
        servicerequest.total_cost_sum = sum(
            service_item.quantity * service_item.unitcost for service_item in servicerequest.servicerequest_items.all()
        )
    return render(request, 'admin/edo/servicerequest/list.html', {
        'servicerequests': servicerequests
    })

@login_required
def edo_create_service_request(request):
    if request.method == "POST":
        form = ServiceRequestForm(request.POST, user=request.user)  # Pass user to the form
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.created_by = request.user
            service_request.supervisor = request.user.supervisor
            service_request.save()
            return redirect('edo_edit_service_request', service_request.id)
    else:
        form = ServiceRequestForm(user=request.user)

    return render(request, 'admin/edo/servicerequest/create.html', {'form':form}) 

@login_required
def edo_update_service_request(request, servicerequest_id):
    service_request = get_object_or_404(ServiceRequest, id=servicerequest_id)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, instance=service_request, user=request.user)  # Pass user
        if form.is_valid():
            form.save(user=request.user)  # Save with user context
            return redirect('edo_service_request_index')  # Redirect after update
    else:
        form = ServiceRequestForm(instance=service_request, user=request.user)  # Pass user

    return render(request, 'admin/edo/servicerequest/create.html', {
        'form': form, 
        'service_request': service_request
    }) 




@login_required
def edo_edit_service_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    items = ServiceRequestItem.objects.filter(servicerequest=service_request)
    form = ServiceRequestForm(instance=service_request)
    item_form = ServiceRequestItemForm()
    return render(request, 'admin/edo/servicerequest/edit.html', {
        'form': form,
        'item_form': item_form,
        'items': items,
        'service_request': service_request
    })

@login_required
def add_service_request_item(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if request.method == 'POST':
        form = ServiceRequestItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.servicerequest = service_request
            item.created_by = request.user
            
            # Set the unit cost dynamically from the selected service item
            item.unitcost = item.serviceitem.cost
            item.save()
            
            return JsonResponse({'success': True, 'unitcost': str(item.unitcost)})  
        
    return JsonResponse({'success': False, 'errors': form.errors})


 
# Fetch ServiceItem details via AJAX
@login_required
def get_serviceitem_details(request):
    serviceitem_id = request.GET.get('serviceitem_id')
    serviceitem = get_object_or_404(ServiceItem, id=serviceitem_id)
    return JsonResponse({'unitcost': str(serviceitem.cost)})
#<<<<<<<<<<<<<<<=========================== END OF SERVICE ITEMS ==============>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#


#<<<<<<<<<<<<<<<<<<,, REQUEST MODULES ============================>>>>>>>>>>>>>>>>>>>>>>>>
@login_required
def beneficiary_service_request_list(request):
    # Get all service requests
    supervisor = get_object_or_404(Supervisor, user = request.user)
    beneficary = request.user.beneficiary
    
    #servicerequests = ServiceRequest.objects.filter(beneficary = beneficary)
    servicerequests = ServiceRequest.objects.filter(beneficiary=beneficary)
    
    for servicerequest in servicerequests:
        servicerequest.total_cost_sum = sum(
            service_item.quantity * service_item.unitcost for service_item in servicerequest.servicerequest_items.all()
        )
        
    return render(request, 'admin/edo/bills/request_bills.html', {'servicerequests': servicerequests, 'supervisor':supervisor })



#<<<<<<<<<<<<<<<<<<<<<============= ACCOUNTING ==========================================>>>>>>>>>>>>>>>>>>
@login_required
def edo_beneficiary_accounting_summary(request, beneficiary_id):
    #Beneficiary's view of all expenses, deductions, loans, repayments, and final balance.
    supervisor = get_object_or_404(Supervisor, user = request.user)
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    
    assigned_tunnel = beneficiary.assigned_tunnel
    # Ensure the greenhouse and city are linked properly
    greenhouse = assigned_tunnel.greenhouse if assigned_tunnel else None
    city = greenhouse.city if greenhouse else None    # Assuming ManyToManyField
    # Fetch associated marketing centre (assuming a ForeignKey relation)
    #marketing_centre = city.marketingcentre_set.first() if city else None  # If ManyToMany, use city.marketingcentre.all()

    eximbankLoan = assigned_tunnel.shared_cost
    
    # Total farm input costs for beneficiary
    farm_input_costs = InputDistribution.objects.filter(beneficiary=beneficiary).aggregate(total_cost=Sum('total_cost'))['total_cost'] or Decimal(0)
    # Cash loans assigned
    cash_loans = CashAssigned.objects.filter(beneficiary=beneficiary).aggregate(total_loans=Sum('amount'))['total_loans'] or Decimal(0)
    # Loan repayments made
    total_repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or Decimal(0)
    # Maintenance share costs
    maintenance_costs = ServiceRequest.objects.filter(beneficiary=beneficiary).aggregate(total_cost=Sum('total_amount'))['total_cost'] or Decimal(0)
    # Harvest sales revenue
    total_harvest_sales = Harvest.objects.filter(beneficiary=beneficiary).aggregate(total_sales=Sum('total_price'))['total_sales'] or Decimal(0)
    # Total deductions (farm input, loan, maintenance)
    total_deductions = farm_input_costs + cash_loans + maintenance_costs + eximbankLoan
    # Final balance (harvest sales - total deductions)
    final_balance = total_harvest_sales - total_deductions + total_repayments
    total_assets = total_harvest_sales + total_repayments
    
    context = {
        'beneficiary': beneficiary,
        'supervisor':supervisor,
        'farm_input_costs': farm_input_costs,
        'cash_loans': cash_loans,
        'total_repayments': total_repayments,
        'maintenance_costs': maintenance_costs,
        'total_harvest_sales': total_harvest_sales,
        'total_deductions': total_deductions,
        'eximbankLoan':eximbankLoan,
        'final_balance': final_balance,
        'total_assets':total_assets
    }
    return render(request, 'admin/edo/accounting/beneficiary_summary.html', context)

@login_required
def edo_beneficiary_accounting_detail(request, category, beneficiary_id=None):
    #View detailed transactions of a selected category for a specific beneficiary.
    supervisor = get_object_or_404(Supervisor, user = request.user)
     
    queryset = None
    title = ""
    total_amount = 0  # Initialize total amount

    if category == "farm_input_costs":
        title = "Farm Input Costs"
        queryset = InputDistribution.objects.filter(beneficiary_id=beneficiary_id) if beneficiary_id else InputDistribution.objects.all()
        total_amount = queryset.aggregate(total=Sum('total_cost'))['total'] or 0

    elif category == "cash_loans":
        title = "Cash Loans"
        queryset = CashAssigned.objects.filter(beneficiary_id=beneficiary_id) if beneficiary_id else CashAssigned.objects.all()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0

    elif category == "total_repayments":
        title = "Loan Repayments"
        queryset = Repayment.objects.filter(cash_assigned__beneficiary_id=beneficiary_id) if beneficiary_id else Repayment.objects.all()
        total_amount = queryset.aggregate(total=Sum('amount_paid'))['total'] or 0

    elif category == "maintenance_costs":
        title = "Maintenance Costs"
        queryset = ServiceRequest.objects.filter(beneficiary_id=beneficiary_id) if beneficiary_id else ServiceRequest.objects.all()
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0

    elif category == "total_harvest_sales":
        title = "Harvest Sales"
        queryset = Harvest.objects.filter(beneficiary_id=beneficiary_id) if beneficiary_id else Harvest.objects.all()
        total_amount = queryset.aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'title': title,
        'queryset': queryset,
        'total_amount': total_amount,
        'supervisor':supervisor
    }
    return render(request, 'admin/edo/accounting/detail_view.html', context)


#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
@login_required
def edo_beneficiary_balance_sheet(request, beneficiary_id):
    supervisor = request.user.supervisor
    beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    # Fetch assigned tunnel (GreenhouseRoom)
    assigned_tunnel = beneficiary.assigned_tunnel
    # Ensure the greenhouse and city are linked properly
    greenhouse = assigned_tunnel.greenhouse if assigned_tunnel else None
    city = greenhouse.city if greenhouse else None    # Assuming ManyToManyField
    # Fetch associated marketing centre (assuming a ForeignKey relation)
    marketing_centre = city.marketingcentre_set.first() if city else None  # If ManyToMany, use city.marketingcentre.all()

    eximbankLoan = assigned_tunnel.shared_cost
    
    # Fetch farm input costs
    farm_input_assigned_list = InputDistribution.objects.filter(beneficiary=beneficiary)
    total_farm_input_quantity = farm_input_assigned_list.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_farm_input_cost = farm_input_assigned_list.aggregate(Sum('total_cost'))['total_cost__sum'] or 0

    # Fetch cash loans and repayments
    cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
    repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

    # Calculate total repayments per loan
    total_repayments = {
        cash.id: repayments.filter(cash_assigned=cash).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        for cash in cash_assigned_list
    }

    # Calculate total cash loans (Loans - Repayments)
    total_cash_loans = sum(cash.amount for cash in cash_assigned_list)
    total_loan_repayments = sum(total_repayments.values())
    net_cash_loans = total_cash_loans - total_loan_repayments

   # Fetch service requests
    servicerequests = ServiceRequest.objects.filter(beneficiary=beneficiary).prefetch_related('servicerequest_items__serviceitem')

    # Store total cost for each service item separately
    service_items_data = []
    total_operational_cost = 0

    for servicerequest in servicerequests:
        for item in servicerequest.servicerequest_items.all():
            total_cost = (item.quantity or 0) * (item.unitcost or 0)
            total_operational_cost += total_cost
            service_items_data.append({
                'service_request': servicerequest.description,
                'service_item': item.serviceitem.service_name,
                'unit_cost': item.unitcost,
                'quantity': item.quantity,
                'total_cost': total_cost,
            })
    
   # Calculate Grand Total
    total_liability = total_farm_input_cost + net_cash_loans + total_operational_cost + eximbankLoan

    harvests = Harvest.objects.filter(beneficiary = beneficiary)
         # Safely calculate total_quantity and total_sum
    total_harvest_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvests)
    total_harvest_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvests)

    grand_total = total_harvest_sum - total_liability
    #print(type(total_repayments))  # Add this in your view
    #print(total_repayments)  # Check the actual value

    return render(request, 'admin/edo/accounting/balance_sheet.html', {
        #beneficiary assigned Greenhouse Tunnel
        'assigned_tunnel': assigned_tunnel,
        'greenhouse': greenhouse,
        'city': city,
        'marketing_centre': marketing_centre,
        'supervisor':supervisor, 
        
        'farm_input_assigned_list': farm_input_assigned_list,
        'total_farm_input_quantity': total_farm_input_quantity,
        'total_farm_input_cost': total_farm_input_cost,
        'beneficiary':beneficiary,
        'cash_assigned_list': cash_assigned_list,
        'total_cash_loans': total_cash_loans,
        'total_loan_repayments': total_loan_repayments,
        'net_cash_loans': net_cash_loans,

        'servicerequests': servicerequests,
        'total_operational_cost': total_operational_cost,

        'total_liability':total_liability,
        
        #assets same as HARVEST since this is the only avenue for beneficiary assets
        'harvests':harvests,
        'total_harvest_quantity':total_harvest_quantity,
        'total_harvest_sum':total_harvest_sum,
        
        'grand_total': grand_total
    })
#<<<<<<<<<<<<<<<<<<---------------- END OF BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>



########################## Equipment and Maintenance Modules ###################################################

@login_required
def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'admin/edo/equipment/list.html', {'equipments': equipments})

@login_required
def equipment_create(request):
    form = EquipmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('equipment_list')
    return render(request, 'admin/edo/equipment/create.html', {'form': form, 'title': 'Add Equipment'})

@login_required
def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    form = EquipmentForm(request.POST or None, instance=equipment)
    if form.is_valid():
        form.save()
        return redirect('equipment_list')
    return render(request, 'admin/edo/equipment/create.html', {'form': form, 'title': 'Edit Equipment'})

@login_required
def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equipment.delete()
        return redirect('equipment_list')
    return render(request, 'admin/edo/equipment/confirm_delete.html', {'object': equipment})


@login_required
def maintenance_list(request):
    logs = EquipmentMaintenanceLog.objects.select_related('code', 'part').all()
    return render(request, 'admin/edo/maintenance/list.html', {'logs': logs})

@login_required
def maintenance_create(request):
    form = EquipmentMaintenanceLogForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('maintenance_list')
    return render(request, 'admin/edo/maintenance/create.html', {'form': form, 'title': 'Add Maintenance Log'})

@login_required
def maintenance_update(request, pk):
    log = get_object_or_404(EquipmentMaintenanceLog, pk=pk)
    form = EquipmentMaintenanceLogForm(request.POST or None, instance=log)
    if form.is_valid():
        form.save()
        return redirect('maintenance_list')
    return render(request, 'admin/edo/maintenance/create.html', {'form': form, 'title': 'Edit Maintenance Log'})

@login_required
def maintenance_delete(request, pk):
    log = get_object_or_404(EquipmentMaintenanceLog, pk=pk)
    if request.method == 'POST':
        log.delete()
        return redirect('maintenance_list')
    return render(request, 'admin/edo/maintenance/confirm_delete.html', {'object': log})
########################## END OF Equipment and Maintenance Modules ############################################