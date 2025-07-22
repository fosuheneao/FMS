from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Case, When, IntegerField
from django.urls import reverse
from django.db.models import Sum, F
from django.contrib import messages
from yuapp.models import *
from .forms import *


# Helper to check if user is a supervisor
def is_supervisor(user):
    return user.groups.filter(name='EDO').exists()

#my trend knowledge list
# Create your views here.
def user_login(request):
        messages.error(request, 'Account type is not recognized.')
        return redirect('user_login')
    
@login_required
def trend_knowledge_index(request):

    if request.user.is_authenticated:        
        trends = TrendKnowledgeBank.objects.filter(created_by = request.user.id)
        return render(request, 'admin/beneficiary/forum/index.html', {'trends':trends})
    else:
       return redirect('user_login')

# topics for discussion.  
@login_required
def trend_knowledge_board(request):

    if request.user.is_authenticated:        
        trs = TrendKnowledgeBank.objects.all()
        return render(request, 'admin/beneficiary/forum/discussion.html', {'trs':trs})
    else:
       return redirect('user_login')
   
# View to create a new TrendKnowledgeBank
@login_required
def create_trend_knowledge(request):
    if not request.user.groups.filter(name='Beneficiary').exists():
        messages.error(request, 'You do not have permission to create a Trend Knowledge Topic.')
        return redirect('beneficiary_dashboard')
    
    if request.method == 'POST':
        form = TrendKnowledgeBankForm(request.POST, request.FILES)
        if form.is_valid():
            trend_knowledge_bank = form.save(commit=False)
            trend_knowledge_bank.created_by = request.user  # Associate with logged-in user
            trend_knowledge_bank.save()
            messages.success(request, 'Trend Knowledge Successfully Created.')
            return redirect('beneficiary_dashboard')  # Redirect to dashboard or another relevant page
    else:
        form = TrendKnowledgeBankForm()
    
    return render(request, 'admin/beneficiary/forum/create.html', {'form': form})

# View to create a discussion under a specific TrendKnowledgeBank
@login_required
def discussion_trend_knowledge(request, pk):
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
    
    return render(request, 'admin/beneficiary/forum/discussion.html', {'form': form, 'trend_knowledge_bank': trend_knowledge_bank})

@login_required
def trend_knowledge_bank_detail(request, pk):
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

    return render(request, 'admin/beneficiary/forum/detail.html', {
        'trend_knowledge_bank': trend_knowledge_bank,
        'discussions': discussions,
        'discussion_form': discussion_form
    })


#crops
# topics for discussion.  
@login_required
def crop_index(request):

    if request.user.is_authenticated:        
        #crops = Crop.objects.all()
        beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        
        # Fetch the crops assigned to this specific beneficiary
        assigned_crops = beneficiary.crops.all()
        
        # Fetch all crops and prioritize the ones assigned to the beneficiary
        all_crops = Crop.objects.annotate(
            is_assigned=Case(
                When(id__in=assigned_crops.values_list('id', flat=True), then=0),  # Assigned crops come first
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('is_assigned')  # Sort by the is_assigned field

        return render(request, 'admin/beneficiary/crop.html', {
            'all_crops': all_crops,
            'assigned_crops': assigned_crops,
        })
    else:
       return redirect('user_login')

#crops
# topics for discussion.  
@login_required
def tunnel_index(request):

    if request.user.is_authenticated:        
        #crops = Crop.objects.all()
        beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user  
        # Fetch all crops available in the system
        #all_tunels = GreenhouseRoom.objects.all()
        # Fetch the crops assigned to this specific beneficiary
        assigned_tunels = beneficiary.assigned_tunnel
        
         # Fetch all tunnels but prioritize the assigned tunnel
        all_tunels = GreenhouseRoom.objects.all().order_by(
        models.Case(
                models.When(id=assigned_tunels.id, then=0),  # Put assigned tunnel first
                default=1,
                output_field=models.IntegerField(),
            )
        )
        
        return render(request, 'admin/beneficiary/tunnel.html', {
            'all_tunels': all_tunels,
            'assigned_tunel': assigned_tunels,
        })
    else:
       return redirect('user_login')

#Changing room
# topics for discussion.  
@login_required
def changingroom_index(request):
    if request.user.is_authenticated:        
        beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user

        # Fetch all ChangingRoom assignments for this specific beneficiary
        assigned_changing_rooms = ChangingRoomAssign.objects.filter(beneficiary=beneficiary)

        return render(request, 'admin/beneficiary/changingroom.html', {
            'assigned_changing_rooms': assigned_changing_rooms,
        })
    else:
        return redirect('user_login')

@login_required
def changingroom_detail(request, pk):
    # Get the specific changing room by primary key (pk)
    changeroom = get_object_or_404(ChangingRoom, pk=pk)
    
    # Get all assignments (beneficiaries) for this specific changing room
    assigned_beneficiaries = ChangingRoomAssign.objects.filter(changing_room=changeroom)
    
    return render(request, 'admin/beneficiary/changingroom_detail.html', {
        'changeroom': changeroom,
        'assigned_beneficiaries': assigned_beneficiaries
    })

@login_required
def buyer_index(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user

        # Fetch all ChangingRoom assignments for this specific beneficiary
        buyers = Buyer.objects.all()

        return render(request, 'admin/beneficiary/buyer.html', {
            'buyers': buyers,
        })
    else:
        return redirect('user_login')

@login_required
def buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    return render(request, 'admin/beneficiary/buyer_detail.html', {'buyer': buyer})



    
#Beneficiary Financials 
@login_required
def farm_input_index(request):
    if request.user.is_authenticated:        
        beneficiary = Beneficiary.objects.get(user=request.user)
        farm_input_assigned_list = InputDistribution.objects.filter(beneficiary=beneficiary)
        repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

        # Calculate totals
        total_quantity = farm_input_assigned_list.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_cost = farm_input_assigned_list.aggregate(Sum('total_cost'))['total_cost__sum'] or 0

        return render(request, 'admin/beneficiary/finance/farminput_cost.html', {
            'farm_input_assigned_list': farm_input_assigned_list,
            'repayments': repayments,
            'total_quantity': total_quantity,
            'total_cost': total_cost,
        })
 

def farm_input_assigned_detail(request, farm_input_assigned_id):
    assignedInput = get_object_or_404(InputDistribution, pk=farm_input_assigned_id)
    #repayment_history = Repayment.objects.filter(cash_assigned=cash_assigned).order_by('-date_paid')  # Fetch repayments related to this cash assigned, ordered by most recent

    context = {
        'assignedInput': assignedInput,
        #'repayment_history': repayment_history
    }
    return render(request, 'admin/beneficiary/finance/farminput_costdetail.html', context)

@login_required
def finance_index(request):
    if request.user.is_authenticated:
        beneficiary = Beneficiary.objects.get(user=request.user)
        cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)

        # Get repayments and calculate total repayment per cash assigned
        repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

        # Create a dictionary to store total repayments per loan (cash assigned)
        total_repayments = {
            cash.id: repayments.filter(cash_assigned=cash).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            for cash in cash_assigned_list
        }
        
        return render(request, 'admin/beneficiary/finance/cashbank.html', {
            'cash_assigned_list': cash_assigned_list,
            'repayments': repayments,
            'total_repayments': total_repayments,  # Pass this dictionary to the template
        })
    
    
@login_required
def request_cash(request):
    if request.method == 'POST':
        form = CashRequestForm(request.POST)
        if form.is_valid():
            cash_assigned = form.save(commit=False)
            cash_assigned.beneficiary = request.user.beneficiary
            cash_assigned.status = 'Pending'
            cash_assigned.save()
            return redirect('beneficiary_dashboard')
    else:
        form = CashRequestForm()

    return render(request, 'admin/beneficiary/finance/request_cash.html', {'form': form})

@login_required
def submit_repayment(request, cash_assigned_id):
    beneficiary = get_object_or_404(Beneficiary, user=request.user)
    cash_assigned = get_object_or_404(CashAssigned, id=cash_assigned_id, beneficiary=beneficiary)

    if request.method == 'POST':
        form = RepaymentForm(request.POST, request.FILES, beneficiary=beneficiary, cash_assigned=cash_assigned)
        if form.is_valid():
            form.save()  # Save repayment, which will handle balance calculation
            return redirect('finance_index')
    else:
        form = RepaymentForm(beneficiary=beneficiary, cash_assigned=cash_assigned)

    return render(request, 'admin/beneficiary/finance/repayment.html', {
        'form': form,
        'form_title': 'Submit Repayment'
    })

#payment history
@login_required
def finance_payment_history(request):
    if request.user.is_authenticated:        
       # beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user
        beneficiary = Beneficiary.objects.get(user=request.user)
        cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
        repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/finance/payment_history.html', {
            'cash_assigned_list': cash_assigned_list,
            'repayments': repayments,
        })
    else:
        return redirect('user_login')


def cash_assigned_detail(request, cash_assigned_id):
    cash_assigned = get_object_or_404(CashAssigned, pk=cash_assigned_id)
    repayment_history = Repayment.objects.filter(cash_assigned=cash_assigned).order_by('-date_paid')  # Fetch repayments related to this cash assigned, ordered by most recent

    context = {
        'cash_assigned': cash_assigned,
        'repayment_history': repayment_history
    }
    return render(request, 'admin/beneficiary/finance/payment_history.html', context)


#BENEFICIARY CASH ASSIGNED PAYMENT HISTORY

@login_required
def cash_assigned_payment_history(request):
    # Get the beneficiary associated with the logged-in user
    beneficiary = request.user.beneficiary  

    # Get all cash assignments related to this beneficiary
    cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)

    # Get all repayments related to this beneficiary's cash assignments
    repayment_history = Repayment.objects.filter(cash_assigned__in=cash_assigned_list).order_by('-date_paid')

    context = {
        'cash_assigned_list': cash_assigned_list,
        'repayment_history': repayment_history
    }
    return render(request, 'admin/beneficiary/finance/paymenthistory.html', context)


#Beneficiary Financials 
def group_income_by_crop_and_grade(harvests):
    grouped_data = {}
    
    for harvest in harvests:
        crop_name = harvest.crop.name
        grade_name = harvest.grade.name if harvest.grade else "Unknown Grade"
        unit_expression = harvest.unit.expression if harvest.unit else "Unknown Unit"
        
        if crop_name not in grouped_data:
            grouped_data[crop_name] = {}
        
        if grade_name not in grouped_data[crop_name]:
            grouped_data[crop_name][grade_name] = {
                'total_quantity': 0,
                'total_revenue': 0,
                'unit': unit_expression
            }
        
        grouped_data[crop_name][grade_name]['total_quantity'] += harvest.quantity
        grouped_data[crop_name][grade_name]['total_revenue'] += harvest.total_price
    
    return grouped_data

@login_required
def beneficiary_income(request):
    try:
        beneficiary = request.user.beneficiary
    except AttributeError:
        return render(request, 'admin/beneficiary/finance/income.html', {'error': "No associated beneficiary found."})
    
    crop_id = request.GET.get('crop_id')
    selected_crop = get_object_or_404(Crop, pk=crop_id) if crop_id else None
    assigned_crops = beneficiary.crops.all()
    
    harvest_query = Harvest.objects.filter(beneficiary=beneficiary, confirmation='Confirmed')
    if selected_crop:
        harvest_query = harvest_query.filter(crop=selected_crop)
    
    grouped_income = group_income_by_crop_and_grade(harvest_query)
    
    total_quantity = sum(sum(grade_data['total_quantity'] for grade_data in crop_data.values()) for crop_data in grouped_income.values())
    total_revenue = sum(sum(grade_data['total_revenue'] for grade_data in crop_data.values()) for crop_data in grouped_income.values())
    
    context = {
        'beneficiary': beneficiary,
        'selected_crop': selected_crop,
        'assigned_crops': assigned_crops,
        'grouped_income': grouped_income,
        'total_quantity': total_quantity,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'admin/beneficiary/finance/income.html', context)



#Beneficiary Financials 
@login_required
def harvest_index(request):
    if request.user.is_authenticated:        
        #crops = Crop.objects.all() 
        beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to user        
        # Fetch the crops assigned to this specific beneficiary
        assigned_crops = beneficiary.crops.all()  
        # # Fetch all crops and prioritize the ones assigned to the beneficiary
        all_crops = Crop.objects.annotate(
             is_assigned=Case(
                 When(id__in=assigned_crops.values_list('id', flat=True), then=0),  # Assigned crops come first
                 default=1,
                 output_field=IntegerField(),
             )
         ).order_by('is_assigned')  # Sort by the is_assigned field

        return render(request, 'admin/beneficiary/harvest/index.html', {
            'beneficiary': beneficiary,  # Pass the beneficiary object
            'assigned_crops': assigned_crops,
        })
    else:
       return redirect('user_login')

#beneficiary review and confirmation of harvest record
@csrf_exempt
@login_required
def review_harvest(request):
    harvest_id = request.GET.get('harvestId')
    review_status = request.Get.get("reviewStatus")
    if request.method == "POST":
        harvest = get_object_or_404(Harvest, id=harvest_id)

        # Ensure the logged-in user is the beneficiary
        if request.user != harvest.beneficiary:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized action'}, status=403)

        review_status = request.POST.get("review_status")
        
        if review_status not in dict(Harvest.HARVEST_REVIEW_STATUS):
            return JsonResponse({'status': 'error', 'message': 'Invalid review status'}, status=400)

        # Update the harvest record
        harvest.reviewed_by = request.user
        harvest.reviewed_at = now()
        harvest.reviewed_status = review_status
        harvest.save()

        return JsonResponse({'status': 'success', 'message': 'Harvest reviewed successfully'})    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def assigned_crops_and_harvests(request, beneficiary_id, crop_id):
    # Retrieve the beneficiary object by its ID
    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_id)
    
    # Retrieve the crop object by its ID
    crop = get_object_or_404(Crop, pk=crop_id)
    
    # Get the assigned crops for the beneficiary (ManyToManyField relationship)
    assigned_crops = beneficiary.crops.all()

    # Fetch harvest records where both beneficiary_id and crop_id match
    harvest_records = Harvest.objects.filter(beneficiary_id=beneficiary_id, crop_id=crop_id)
    #harvest_records = Harvest.objects.all()  # or your specific queryset
     # Safely calculate total_quantity and total_sum
    total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvest_records)
    total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvest_records)

    # Add context for rendering the template
    context = {
        'beneficiary': beneficiary,
        'assigned_crops': assigned_crops,
        'harvest_records': harvest_records,
        'selected_crop': crop,  # Pass the selected crop object to the template for reference
        'total_quantity':total_quantity,
        'total_sum':total_sum
    }

    return render(request, 'admin/beneficiary/harvest/records.html', context)


def fetch_price_record(harvest, greenhouse):
    #Helper function to fetch the price record based on the harvest and greenhouse."""
    return PriceTable.objects.filter(
        grade_id=harvest.grade,
        unit_id=harvest.unit,
        crop_id=harvest.crop,
        market_center__in=greenhouse.marketing_centres.all()
    ).order_by('-from_date').first()

def handle_harvest_form_submission(form, harvest_instance, greenhouse, greenhouse_room):
    # Helper function to handle form submission logic for saving harvest records.
   
    if form.is_valid():
        # Save the form instance without committing to the database
        harvest = form.save(commit=False)

        # Assign greenhouse and greenhouse_room
        harvest.greenhouse = greenhouse
        harvest.greenhouse_room = greenhouse_room

        # Fetch the price record based on the harvest details
        price_record = fetch_price_record(harvest, greenhouse)

        if price_record:
            harvest.price_record = price_record
            harvest.total_price = harvest.quantity * price_record.price  # Calculate total price

        # Save the harvest instance to the database
        harvest.save()

        return True
    return False


@login_required
def create_harvest(request, crop_assigned_id):
    #if request.user.is_authenticated:
        beneficiary = request.user.beneficiary
        crop = get_object_or_404(Crop, id=crop_assigned_id)
        created_by = request.user

        # Ensure the beneficiary has an assigned tunnel/greenhouse
        if beneficiary.assigned_tunnel:
            greenhouse = beneficiary.assigned_tunnel.greenhouse
            greenhouse_room = beneficiary.assigned_tunnel
        else:
            # Handle the case where there's no assigned tunnel (e.g., set a default or raise an error)
            messages.error(request, "Beneficiary does not have an assigned tunnel.")
            return None  # Or handle appropriately

        if request.method == 'POST':
            form = HarvestForm(request.POST, crop=crop, beneficiary=beneficiary, created_by=created_by)

            if form.is_valid():
                harvest = form.save(commit=False)

                # Dynamically set the greenhouse and greenhouse room before saving the harvest
                harvest.greenhouse = greenhouse
                harvest.greenhouse_room = greenhouse_room
                harvest.created_by = created_by
                # Assign the crop and beneficiary directly
                harvest.crop = crop
                harvest.beneficiary = beneficiary
              
                # Save the harvest instance
                harvest.save()

                # Redirect to harvest index or any other relevant page
                return redirect('harvest_index')

        else:
            # If it's a GET request, simply initialize the form
            form = HarvestForm(crop=crop, beneficiary=beneficiary, created_by=created_by)

        return render(request, 'admin/beneficiary/harvest/create_harvest.html', {
            'form': form,
            'crop': crop,
        })

    # else:
    #     # If the user is not authenticated, redirect them to the login page
    #     return redirect('login')
          
@login_required
def update_harvest(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    crop = harvest.crop
    beneficiary = harvest.beneficiary

    # Retrieve greenhouse room and greenhouse for the beneficiary
    # greenhouse = get_beneficiary_greenhouse(beneficiary)
    # greenhouse_room = get_beneficiary_greenhouse_room(beneficiary)
    
    # Ensure the beneficiary has an assigned tunnel/greenhouse
    if beneficiary.assigned_tunnel:
            greenhouse = beneficiary.assigned_tunnel.greenhouse
            greenhouse_room = beneficiary.assigned_tunnel
    else:
            # Handle the case where there's no assigned tunnel (e.g., set a default or raise an error)
            messages.error(request, "Beneficiary does not have an assigned tunnel.")
            return None  # Or handle appropriately

    if request.method == 'POST':
        form = HarvestForm(request.POST, instance=harvest, crop=crop, beneficiary=beneficiary)

        if handle_harvest_form_submission(form, harvest, greenhouse, greenhouse_room):
            messages.success(request, 'Harvest updated successfully.')
            return redirect('harvest_index')
        else:
            messages.error(request, 'The crop must be set for this harvest record.')
            return render(request, 'admin/beneficiary/harvest/create_harvest.html', {
                'form': form,
                'crop': crop,
                'harvest': harvest,
                'beneficiary': beneficiary,
                'price_table': harvest.price_record
            })
    else:
        form = HarvestForm(instance=harvest)

    return render(request, 'admin/beneficiary/harvest/create_harvest.html', {
        'form': form,
        'crop': crop,
        'harvest': harvest,
        'beneficiary': beneficiary
    })

@login_required
def get_price_for_grade_and_unit(request):
    grade_id = request.GET.get('grade_id')
    unit_id = request.GET.get('unit_id')
    crop_id = request.GET.get('crop_id')

    try:
        price_entry = PriceTable.objects.get(grade_id=grade_id, unit_id=unit_id, crop_id=crop_id)
        return JsonResponse({'price': price_entry.price, 'price_id': price_entry.id})
    except PriceTable.DoesNotExist:
        return JsonResponse({'error': 'Price not found'}, status=404)
    
def get_price_for_grade_and_unit(request):
    grade_id = request.GET.get('grade_id')
    unit_id = request.GET.get('unit_id')
    crop_id = request.GET.get('crop_id')

    try:
        # Get the most recent price for the combination of crop, grade, and unit
        price_record = PriceTable.objects.filter(grade_id=grade_id,unit_id=unit_id, crop_id=crop_id).order_by('-from_date').first()
        return JsonResponse({'price': price_record.price, 'price_id': price_record.id})
    except PriceTable.DoesNotExist:
        return JsonResponse({'error': 'Price not found'}, status=404)
    #     if price_record:
    #         return JsonResponse({'price': str(price_record.price), 'price_id': str(price_record.id)})
    #     else:
    #         return JsonResponse({'price': None})
    # except Exception as e:
    #     return JsonResponse({'price': None, 'error': str(e)})
  
@login_required
def view_harvest(request, harvest_id):
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
    return render(request, 'admin/beneficiary/harvest/view_harvest.html', {
        'harvest': harvest, 'price_table':price_table,
        'total_sum': total_sum,
        'total_quantity': total_quantity 
    })

@login_required
def harvest_history(request):
    if request.user.is_authenticated:        
        #crops = Crop.objects.all()
        beneficiary = get_object_or_404(Beneficiary, user=request.user)
        #beneficiary = request.user  # Assuming 'beneficiary' is linked to user  
        harvests = Harvest.objects.filter(beneficiary = beneficiary.id)
         # Safely calculate total_quantity and total_sum
        total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvests)
        total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvests)

        
         #harvest associated quantity and sales amount
        # total_sum = sum(harvest.total_price for harvest in harvests)
        # total_quantity = sum(harvest.quantity for harvest in harvests)
    
    return render(
                  request, 'admin/beneficiary/harvest/history.html', 
                  {
                      'harvests': harvests,
                      'beneficiary':beneficiary,
                      'total_sum': total_sum,
                      'total_quantity': total_quantity                    
                   }
                )    

# @require_POST
# def confirm_harvest_ajax(request):
#     harvest_id = request.POST.get('harvest_id')
#     status = request.POST.get('status')
#     reason = request.POST.get('reason', '')

#     if not harvest_id:
#         return JsonResponse({'success': False, 'message': 'Harvest ID not provided.'})

#     try:
#         harvest = Harvest.objects.get(pk=harvest_id)
#         harvest.reviewed_by = request.user
#         harvest.reviewed_at = now()
#         harvest.reviewed_status = status

#         if status == 'Agree':
#             harvest.confirmation = 'Confirmed'
#         elif status == 'Disagree':
#             harvest.confirmation = 'Open'
#             harvest.review_note = f"Disagreement Reason: {reason}"  # Save reason

#         harvest.save()
#         return JsonResponse({'success': True, 'message': f'Harvest {status.lower()}d successfully.'})
#     except Harvest.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Harvest not found.'})

@login_required
@require_POST
def confirm_harvest_ajax(request):
    harvest_id = request.POST.get('harvest_id')
    status = request.POST.get('status')
    reason = request.POST.get('reason', '')

    if not harvest_id:
        return JsonResponse({'success': False, 'message': 'Harvest ID not provided.'})

    try:
        harvest = Harvest.objects.get(pk=harvest_id)

        harvest.reviewed_by = request.user
        harvest.reviewed_at = now()
        harvest.reviewed_status = status

        aggregation_message = ''

        if status == 'Agree':
            harvest.confirmation = 'Confirmed'
        elif status == 'Disagree':
            harvest.confirmation = 'Open'
            harvest.review_note = f"Disagreement Reason: {reason}"

        harvest.save()

        if status == 'Agree':
            form = HarvestForm(instance=harvest)
            form.aggregate_harvest_stock(harvest)

            aggregation_message = (
                f"Harvest successfully aggregated into stock at "
                f"{harvest.greenhouse.marketing_centres.name} for {harvest.crop.name} "
                f"({harvest.grade.name}, {harvest.quantity} {harvest.unit.name})."
            )

        return JsonResponse({
            'success': True,
            'message': f'Harvest {status.lower()}d successfully.',
            'aggregation_message': aggregation_message
        })

    except Harvest.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Harvest not found.'})
    
      
#Function to Calculate the Sum of All CashAssigned Amounts Given to a Beneficiary with Status = 'Approved
def get_total_cash_assigned(beneficiary):
    total_cash_assigned = CashAssigned.objects.filter(
        beneficiary=beneficiary,
        status='Approved'
    ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return total_cash_assigned

#Calculate the Sum of All Repayment Cash Made Towards CashAssigned with Status = 'Approved'
def get_total_repayment(beneficiary):
    total_repayment = Repayment.objects.filter(
        cash_assigned__beneficiary=beneficiary,
        cash_assigned__status='Approved'
    ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
    return total_repayment

#entries on beneficiary dashboard     
def sales_dashboard(request):
    if request.user.is_authenticated:
        # Volume of crop purchased
        total_volume_purchased = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE).aggregate(
            total_volume=Sum('volume')
        )['total_volume']

        # Total payments (value)
        todos = Todo.objects.filter(created_by=request.user)
        total_payments = Payment.objects.aggregate(
            total_paid=Sum('amount_paid')
        )['total_paid']

        # Total deliveries made (volume)
        total_volume_delivered = Delivery.objects.aggregate(
            total_delivered=Sum('volume_delivered')
        )['total_delivered']

        # Overview of debtors (buyers vs arrears)
        total_due_per_buyer = Transaction.objects.filter(buyer__isnull=False).annotate(
            total_due=F('total_amount') - Sum('payments__amount_paid')
        ).values('buyer__client_name', 'total_due')

        #beneficiary = Beneficiary.objects.get(id=some_id)
        beneficiary = Beneficiary.objects.get(user=request.user) 
        harvests = Harvest.objects.filter(beneficiary=beneficiary)
        # cashLoans = CashAssigned.objects.filter(beneficiary = beneficiary)
        # cashLoans = Repayment.objects.filter(beneficiary = beneficiary)
            
        total_cashLoan = get_total_cash_assigned(beneficiary)
        total_Loan_repayment = get_total_repayment(beneficiary)
        
        total_cashLoan_arrears = total_cashLoan - total_Loan_repayment
         # Safely calculate total_quantity and total_sum
        total_quantity = sum(harvest.quantity if harvest.quantity is not None else 0 for harvest in harvests)
        total_sum = sum(harvest.total_price if harvest.total_price is not None else 0 for harvest in harvests)
        # Total cash sales
        total_cash_sales = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE, buyer__isnull=False).aggregate(total_cash=Sum('total_amount'))['total_cash']
        
        context = {
            'total_volume_purchased': total_volume_purchased,
            'total_payments': total_payments,
            'total_volume_delivered': total_volume_delivered,
            'total_due_per_buyer': total_due_per_buyer,
            'total_cash_sales': total_cash_sales,
            'total_sum': total_sum,
            'total_quantity': total_quantity,
            'total_cashLoan': total_cashLoan,
            'total_Loan_repayment': total_Loan_repayment,
            'total_cashLoan_arrears':total_cashLoan_arrears,
            'todos':todos,   
        }
        
    return render(request, 'admin/beneficiary/market/sales_dashboard.html', context)

@login_required
def edo(request):

    if request.user.is_authenticated:        
        beneficiary = Beneficiary.objects.get(user=request.user)
        #beneficiary = Beneficiary.objects.get(id=some_beneficiary_id)  # Get a specific beneficiary
        supervisor = beneficiary.assigned_edo  # This will give you the assigned supervisor instance


        return render(request, 'admin/beneficiary/edo.html', {'edo':supervisor})
    else:
       return redirect('user_login')

@login_required
def edo_detail(request, edo_id):
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
       
        
        return render(request, 'admin/beneficiary/edo_detail.html', context)

#contract
@login_required
def create_contract(request, worker_id):
    if request.user.is_authenticated:
        # Get the beneficiary and crop based on the user and crop_id
        beneficiary = request.user.beneficiary  # Assuming 'beneficiary' is linked to the user
        worker = get_object_or_404(Worker, id=worker_id)
        created_by = request.user
        if request.method == 'POST':
            form = ContractForm(request.POST, worker=worker, beneficiary=beneficiary, created_by=created_by)
            
            if form.is_valid():
                try:
                    contract = form.save(commit=False)
                    contract.beneficiary = beneficiary
                    contract.worker = worker
                    contract.created_by = created_by  # Assuming there's a created_by field
                    contract.save()  # Attempt to save the contract
                    
                    messages.success(request, 'Contract created successfully.')
                    return redirect('contract_list')  # Redirect to the contract list page
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
            else:
                print("Form is invalid: ", form.errors)  # Print validation errors to console
                messages.error(request, 'There were errors in your submission. Please correct them.')
        else:
            form = ContractForm(worker=worker, beneficiary=beneficiary, created_by=created_by)
        
        return render(request, 'admin/beneficiary/worker/create.html', {'form': form, 'worker': worker})
    else:
        return redirect('user_login')


@login_required
def update_contract(request, contract_id):
    # Fetch the contract by ID
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        
        if form.is_valid():
            # Ensure the beneficiary is maintained
            contract.beneficiary = contract.beneficiary  # Keep the existing beneficiary
            contract.save()  # Save the contract with the updated information
            
            messages.success(request, 'Contract updated successfully.')
            return redirect('contracts')
        else:
            messages.error(request, 'There were errors in your submission. Please correct them.')
    
    else:
        # Pre-fill the form with the existing contract data
        form = ContractForm(instance=contract)
    
    # Render the form
    return render(request, 'admin/beneficiary/worker/create.html', {'form': form, 'contract': contract})


@login_required
def list_contracts(request):
    if request.user.is_authenticated:
        
        contracts = Contract.objects.filter(beneficiary = request.user.beneficiary)
        return render(request, 'admin/beneficiary/worker/contracts.html', {'contracts': contracts})


#CREATE DATA, NURSERY====================================================================================================, 
# Create Views
@login_required
def nursery_data_index(request):
    if request.user.is_authenticated:  
        nursery_records = NurseryData.objects.filter(beneficiary__user=request.user)
  
        return render(request, 'admin/beneficiary/tunnel/nursery_data.html', {'nursery_records':nursery_records})
    else:
       return redirect('beneficiary_logo')
   
@login_required
def create_nursery_data(request):
    if request.user.is_authenticated:  
        beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = NurseryDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                nursery_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                nursery_data.greenhouse_room = assigned_tunnel
                nursery_data.greenhouse = greenhouse
                
                nursery_data.beneficiary = request.user.beneficiary  # Assuming you have a related Beneficiary instance
                nursery_data.created_by = request.user
                nursery_data.status = 'Pending'
                nursery_data.save()
            return redirect('nursery_data_index')  # Redirect to the appropriate page
        else:
            form = NurseryDataForm(beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/tunnel/create_nursery.html', {'form': form})

# Update Views
@login_required
def update_nursery_data(request, nursery_id):
    # Retrieve the beneficiary and nursery data
    beneficiary = request.user.beneficiary
    nursery_data = get_object_or_404(NurseryData, id=nursery_id, beneficiary=beneficiary)
    crop = nursery_data.crop
    
    if request.method == 'POST':
        form = NurseryDataForm(request.POST, instance=nursery_data)
        if form.is_valid():
            nursery_data = form.save(commit=False)

            # Dynamically retrieve the assigned tunnel (greenhouse_room)
            assigned_tunnel = beneficiary.assigned_tunnel
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse

            # Set the dynamically retrieved greenhouse and greenhouse_room
            nursery_data.greenhouse_room = assigned_tunnel
            nursery_data.greenhouse = greenhouse
            nursery_data.beneficiary = beneficiary

            form.save()
            messages.success(request, 'Nursery record updated successfully.')
            return redirect('nursery_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    # Render the form with the existing nursery data for GET requests
    else:
        form = NurseryDataForm(instance=nursery_data)

    return render(request, 'admin/beneficiary/tunnel/create_nursery.html', {
        'form': form,
        'nursery_data': nursery_data,
        'crop':crop
    })
#End of Nursery records ====================================================================================================


@login_required
def create_trellising_data(request):
    if request.method == 'POST':
        form = TrellisingDataForm(request.POST)
        if form.is_valid():
            trellising_data = form.save(commit=False)
            trellising_data.beneficiary = request.user.beneficiary
            trellising_data.created_by = request.user
            trellising_data.status = 'Pending'
            trellising_data.save()
            return redirect('user_login')
    else:
        form = TrellisingDataForm()
    return render(request, 'admin/beneficiary/tunnel/create_trellising_data.html', {'form': form})

@login_required
def create_irrigation_data(request):
    if request.method == 'POST':
        form = IrrigationDataForm(request.POST)
        if form.is_valid():
            irrigation_data = form.save(commit=False)
            irrigation_data.beneficiary = request.user.beneficiary
            irrigation_data.created_by = request.user
            irrigation_data.status = 'Pending'
            irrigation_data.save()
            return redirect('user_login')
    else:
        form = IrrigationDataForm()
    return render(request, 'admin/beneficiary/tunnel/create_irrigation_data.html', {'form': form})





#height records ====================================================================================================
# Create Views
@login_required
def height_data_index(request):
    if request.user.is_authenticated:  
        height_records = HeightData.objects.filter(beneficiary__user=request.user)
  
        return render(request, 'admin/beneficiary/tunnel/height_data.html', {'height_records':height_records})
    else:
       return redirect('beneficiary_logo')
@login_required
def create_height_data(request):
    if request.user.is_authenticated:  
        beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = HeightDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                height_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                height_data.greenhouse_room = assigned_tunnel
                height_data.greenhouse = greenhouse
                
                height_data.beneficiary = request.user.beneficiary  # Assuming you have a related Beneficiary instance
                height_data.created_by = request.user
                height_data.status = 'Pending'
                height_data.save()
            return redirect('height_data_index')  # Redirect to the appropriate page
        else:
            form = HeightDataForm(beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/tunnel/create_height.html', {'form': form})

@login_required
def update_height_data(request, height_id):
    beneficiary = request.user.beneficiary
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

            form.save()
            messages.success(request, 'Plant Height record updated successfully.')
            return redirect('height_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = HeightDataForm(instance=height_data)

    return render(request, 'admin/beneficiary/tunnel/create_height.html', {
        'form': form,
        'height_data': height_data,  # Ensure this matches the template
        'crop':crop
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
def spraying_data_index(request):
    if request.user.is_authenticated:  
        spraying_records = SprayingData.objects.filter(beneficiary__user=request.user)
        
        #records = SprayingRecord.objects.all()
        for record in spraying_records:
            record.time_difference = get_time_difference(record.startTime, record.finishTime)
        #return spraying_records
  
        return render(request, 'admin/beneficiary/tunnel/spraying_data.html', {'spraying_records':spraying_records})
    else:
       return redirect('beneficiary_login')
   

   
# @login_required
# def create_spraying_data(request):
#     if request.method == 'POST':
#         form = SprayingDataForm(request.POST)
#         if form.is_valid():
#             spraying_data = form.save(commit=False)
#             spraying_data.beneficiary = request.user.beneficiary
#             spraying_data.created_by = request.user
#             spraying_data.status = 'Pending'
#             spraying_data.save()
#             return redirect('user_login')
#     else:
#         form = SprayingDataForm()
#     return render(request, 'admin/beneficiary/tunnel/create_spraying_data.html', {'form': form})
  
@login_required
def create_spraying_data(request):
    if request.user.is_authenticated:  
        beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = SprayingDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                spraying_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                spraying_data.greenhouse_room = assigned_tunnel
                spraying_data.greenhouse = greenhouse
                
                spraying_data.beneficiary = request.user.beneficiary  # Assuming you have a related Beneficiary instance
                spraying_data.created_by = request.user
                spraying_data.status = 'Pending'
                spraying_data.save()
            return redirect('spraying_data_index')  # Redirect to the appropriate page
        else:
            form = SprayingDataForm(beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/tunnel/create_spraying.html', {'form': form})

@login_required
def update_spraying_data(request, spraying_id):
    beneficiary = request.user.beneficiary
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
            return redirect('spraying_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        #form = SprayingDataForm(instance=spraying_data)
         form = SprayingDataForm(instance=spraying_data, beneficiary=beneficiary)

    return render(request, 'admin/beneficiary/tunnel/create_spraying.html', {
        'form': form,
        'spraying_data': spraying_data,  # Ensure this matches the template
        'crop':crop
    })
#end of Spraying data===============================================================================================


#Irrigation records ====================================================================================================
# Create Views
@login_required
def irrigation_data_index(request):
    if request.user.is_authenticated:  
        irrigation_records = IrrigationData.objects.filter(beneficiary__user=request.user)

        #records = SprayingRecord.objects.all()
        for record in irrigation_records:
            record.time_difference = get_time_difference(record.startTime, record.finishTime)
        #return spraying_records
        
        return render(request, 'admin/beneficiary/tunnel/irrigation_data.html', {'irrigation_records':irrigation_records})
    else:
       return redirect('beneficiary_login')
   
   
@login_required
def create_irrigation_data(request):
    if request.user.is_authenticated:  
        beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = IrrigationDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                irrigation_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                irrigation_data.greenhouse_room = assigned_tunnel
                irrigation_data.greenhouse = greenhouse
                
                irrigation_data.beneficiary = request.user.beneficiary  # Assuming you have a related Beneficiary instance
                irrigation_data.created_by = request.user
                irrigation_data.status = 'Pending'
                irrigation_data.save()
            return redirect('irrigation_data_index')  # Redirect to the appropriate page
        else:
            form = IrrigationDataForm(beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/tunnel/create_irrigation.html', {'form': form})

@login_required
def update_irrigation_data(request, irrigation_id):
    beneficiary = request.user.beneficiary
    irrigation_data = get_object_or_404(IrrigationData, id=irrigation_id, beneficiary=beneficiary)
    crop = irrigation_data.crop
    
    if request.method == 'POST':
        form = IrrigationDataForm(request.POST, instance=irrigation_data)
        if form.is_valid():
            irrigation_data = form.save(commit=False)
            
            assigned_tunnel = beneficiary.assigned_tu
            
            greenhouse_room = get_object_or_404(GreenhouseRoom, id=assigned_tunnel.id)
            greenhouse = greenhouse_room.greenhouse
            irrigation_data.greenhouse_room = assigned_tunnel
            irrigation_data.greenhouse = greenhouse
            irrigation_data.beneficiary = beneficiary

            form.save()
            messages.success(request, 'Irrigation record updated successfully.')
            return redirect('irrigation_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = IrrigationDataForm(instance=irrigation_data)

    return render(request, 'admin/beneficiary/tunnel/create_irrigation.html', {
        'form': form,
        'irrigation_data': irrigation_data,  # Ensure this matches the template
        'crop':crop
    })
#end of Irrigation data===============================================================================================


#TrellisingData records ====================================================================================================
# Create Views
@login_required
def trellising_data_index(request):
    if request.user.is_authenticated:  
        trellising_records = TrellisingData.objects.filter(beneficiary__user=request.user)
  
        return render(request, 'admin/beneficiary/tunnel/trellising_data.html', {'trellising_records':trellising_records})
    else:
       return redirect('beneficiary_login')
   
   
@login_required
def create_trellising_data(request):
    if request.user.is_authenticated:  
        beneficiary = request.user.beneficiary
        #print(f'Beneficiary: {beneficiary}') 
        
        if request.method == 'POST':
            form = TrellisingDataForm(request.POST, beneficiary=beneficiary)
            if form.is_valid():
                trellising_data = form.save(commit=False)
                
                # Assuming each user has a related Beneficiary instance
                beneficiary = request.user.beneficiary
                
                # Dynamically retrieve the assigned tunnel (greenhouse_room)
                assigned_tunnel = beneficiary.assigned_tunnel

                # Pull the corresponding Greenhouse from the GreenhouseRoom model
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_tunnel.id)
                greenhouse = greenhouse_room.greenhouse

                # Set the dynamically retrieved greenhouse and greenhouse_room
                trellising_data.greenhouse_room = assigned_tunnel
                trellising_data.greenhouse = greenhouse
                
                trellising_data.beneficiary = request.user.beneficiary  # Assuming you have a related Beneficiary instance
                trellising_data.created_by = request.user
                trellising_data.status = 'Pending'
                trellising_data.save()
            return redirect('trellising_data_index')  # Redirect to the appropriate page
        else:
            form = TrellisingDataForm(beneficiary=beneficiary)
        return render(request, 'admin/beneficiary/tunnel/create_trellising.html', {'form': form})

@login_required
def update_trellising_data(request, trellising_id):
    beneficiary = request.user.beneficiary
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

            form.save()
            messages.success(request, 'Trellising record updated successfully.')
            return redirect('trellising_data_index')
        else:
            messages.error(request, 'Sorry, the update could not be completed. Please review the errors and try again.')

    else:
        form = TrellisingDataForm(instance=trellising_data)

    return render(request, 'admin/beneficiary/tunnel/create_trellising.html', {
        'form': form,
        'trellising_data': trellising_data,  # Ensure this matches the template
        'crop':crop
    })
#end of TrellisingData data===============================================================================================


#<<<<<<<<<<<<<<<<<<<<<============= ACCOUNTING ==========================================>>>>>>>>>>>>>>>>>>
@login_required
def beneficiary_accounting_summary(request, beneficiary_id):
    #Beneficiary's view of all expenses, deductions, loans, repayments, and final balance.
    
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
    return render(request, 'admin/beneficiary/accounting/beneficiary_summary.html', context)

@login_required
def beneficiary_accounting_detail(request, category, beneficiary_id=None):
    #View detailed transactions of a selected category for a specific beneficiary."""
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
        'total_amount': total_amount
    }
    return render(request, 'admin/beneficiary/accounting/detail_view.html', context)

#<<<<<<<<<<<<<<<<<<,, REQUEST MODULES ============================>>>>>>>>>>>>>>>>>>>>>>>>
@login_required
def beneficiary_service_request_list(request):
    # Get all service requests
    beneficary = request.user.beneficiary
    
    #servicerequests = ServiceRequest.objects.filter(beneficary = beneficary)
    servicerequests = ServiceRequest.objects.filter(beneficiary=beneficary)
    
    for servicerequest in servicerequests:
        servicerequest.total_cost_sum = sum(
            service_item.quantity * service_item.unitcost for service_item in servicerequest.servicerequest_items.all()
        )
        
    return render(request, 'admin/beneficiary/bills/request_bills.html', {'servicerequests': servicerequests })


#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
#<<<<<<<<<<<<<<<<<<---------------- BENEFICIARY BALANCE SHEET------------------------------------->>>>>>>>>>>>>>>>>>>
@login_required
def beneficiary_balance_sheet(request):
    beneficiary = request.user.beneficiary

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

    return render(request, 'admin/beneficiary/accounting/balance_sheet.html', {
        #beneficiary assigned Greenhouse Tunnel
        'assigned_tunnel': assigned_tunnel,
        'greenhouse': greenhouse,
        'city': city,
        'marketing_centre': marketing_centre,
    
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