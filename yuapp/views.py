from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from geopy.distance import geodesic
from django.http import JsonResponse
from datetime import date
import json
from .forms import UserLoginForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django .views import View
from django.db.models import Sum, F, Value, Count, DecimalField, Subquery, OuterRef
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import Coalesce, TruncWeek
from collections import defaultdict
from django.utils.timezone import now
# Create your views here.
from .models import *
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from yuapp.forms import TodoForm


def index(request):
    #begin slider
    # menus = SectionMenu.objects.all()
    slides = Beneficiary.objects.all()
    
    context = {}
    
    
    return render(request, 'index.html', context)

def user_login(request):
    if request.method == 'POST':
        # Capture geo-reference proximity to greenhouse for a supervisor
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            latitude = request.POST.get('latitude')  # Get latitude
            longitude = request.POST.get('longitude')  # Get longitude

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Check if user is a Supervisor or Beneficiary
                if user.groups.filter(name='EDO').exists():
                    try:
                        if not (latitude and longitude):
                            messages.error(request, 'Latitude and Longitude are required.')
                            return redirect('user_login')

                        # Ensure the user is a supervisor
                        supervisor = user.supervisor  # Assuming one-to-one relationship exists
                        greenhouse = supervisor.greenhouse.first()  # Fetch the first assigned greenhouse

                        if greenhouse:
                            # Calculate the distance between the supervisor's login location and greenhouse location
                            greenhouse_coords = (greenhouse.latitude, greenhouse.longitude)
                            login_coords = (float(latitude), float(longitude))
                            distance = geodesic(greenhouse_coords, login_coords).meters  # Distance in meters

                            # Define the allowed proximity (e.g., 50 meters)
                            #proximity_threshold = 50
                            proximity_threshold = 50000000

                            if distance <= proximity_threshold:
                                # Log attendance
                                SupervisorAttendance.objects.create(
                                    supervisor=supervisor,
                                    greenhouse=greenhouse,
                                    login_latitude=latitude,
                                    login_longitude=longitude,
                                    is_valid=True,  # Mark as valid
                                )
                                return redirect('supervisor_dashboard')  # Redirect Supervisor to their dashboard
                            else:
                                # Log invalid attendance
                                SupervisorAttendance.objects.create(
                                    supervisor=supervisor,
                                    greenhouse=greenhouse,
                                    login_latitude=latitude,
                                    login_longitude=longitude,
                                    is_valid=False,  # Mark as invalid
                                )
                                messages.error(request, 'You are able to login because you are not within greenhouse proximity!')
                                return redirect('user_login')
                        else:
                            messages.error(request, 'No greenhouse assigned to you.')
                            return redirect('user_login')

                    except Exception as e:
                        messages.error(request, str(e))
                        return redirect('user_login')

                elif user.groups.filter(name='Beneficiary').exists():
                    return redirect('beneficiary_dashboard')  # Redirect Beneficiary to their dashboard                
                elif user.groups.filter(name='SALES').exists():
                    if hasattr(user, 'sale_agent'):
                         return redirect('sale_dashboard')
                    else:
                         messages.error(request, 'No Sale Agent recognized.')
                         return redirect('user_login')
                elif user.groups.filter(name='SALES_HEAD').exists():
                    if hasattr(user, 'sale_agent'):
                         return redirect('mainsale_dashboard')
                    else:
                         messages.error(request, 'No Sales Head recognized.')
                         return redirect('user_login')
                elif user.groups.filter(name='FINANCE').exists():
                    if hasattr(user, 'finance'):
                         return redirect('finance_dashboard')
                    else:
                         messages.error(request, 'No Finance Member recognized.')
                         return redirect('user_login')
                elif user.groups.filter(name='AIC').exists():
                    return redirect('aic_dashboard')  # Redirect AIC to their dashboard
                elif user.groups.filter(name='Buyer').exists():
                    if hasattr(user, 'buyer_profile'):
                        return redirect('buyer_dashboard')
                    else:
                        messages.error(request, 'No Buyer profile found for this user.')
                        return redirect('user_login')
                else:
                    messages.error(request, 'Account type is not recognized.')
                    return redirect('user_login')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')

    form = UserLoginForm()
    messages.get_messages(request)  # This clears messages before rendering the login page
    return render(request, 'auth/login.html', {'form': form})

@login_required
def supervisor_dashboard(request):
    # Get the supervisor based on the logged-in user
    supervisor = Supervisor.objects.get(user=request.user)    
    # Filter beneficiaries assigned to the logged-in supervisor
    beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
  
    
     # Todos
    todos = Todo.objects.filter(created_by=request.user)
    #finding number of days left for event to happen
    for todo in todos:
        if todo.expected_date:
            days_left = (todo.expected_date - now()).days
            todo.days_left = days_left
        else:
            todo.days_left = None
    #passing the todo form
        
     # Total volume purchased
    total_volume_purchased = Transaction.objects.filter(
            transaction_type=Transaction.CROP_PURCHASE
        ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0

        # Total payments
    # total_payments = Payment.objects.aggregate(
    #         total_paid=Sum('amount_paid')
    #     )['total_paid'] or 0

        # Total deliveries made
    total_volume_delivered = Transaction.objects.aggregate(
            total_delivered=Sum('volume')
        )['total_delivered'] or 0

        # Todos
        #todos = Todo.objects.all()
    todos = Todo.objects.filter(created_by=request.user)
        #finding number of days left for event to happen
    for todo in todos:
            if todo.expected_date:
                days_left = (todo.expected_date - now()).days
                todo.days_left = days_left
            else:
                todo.days_left = None
        #passing the todo form
            
    form = TodoForm()
        #passing the todo form

        # Get beneficiary-specific data
    #beneficiary = Beneficiary.objects.get(user=request.user)

    # Get the list of cash assigned to the beneficiaries
    cash_assigned_list = CashAssigned.objects.filter(beneficiary__in=beneficiaries)
    # Get repayments related to the cash assigned to these beneficiaries
    repayments = Repayment.objects.filter(cash_assigned__beneficiary__in=beneficiaries)

    # Total cash loans and repayments
    total_cash_loan = cash_assigned_list.aggregate(total=Sum('amount'))['total'] or 0
    total_loan_repayment = repayments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_cash_loan_arrears = total_cash_loan - total_loan_repayment

    # Harvest totals
    # Filter harvests for the beneficiaries assigned to this supervisor
    harvests = Harvest.objects.filter(beneficiary__in=beneficiaries)
     # Calculate total quantity and total sum
    total_quantity = harvests.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_sum = harvests.aggregate(total_sum=Sum(F('quantity') * F('price_record__price')))['total_sum'] or 0

    # Filter transactions for these beneficiaries
    total_cash_sales = Transaction.objects.filter(
        transaction_type=Transaction.CROP_PURCHASE,
        supervisor=supervisor
    ).aggregate(total_cash=Sum('total_amount'))['total_cash'] or 0

    # Total volume purchased for assigned beneficiaries
    total_volume_purchased = Transaction.objects.filter(
        supervisor=supervisor
    ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0

    # Todos
    todos = Todo.objects.filter(created_by=request.user)
    #finding number of days left for event to happen
    for todo in todos:
        if todo.expected_date:
            days_left = (todo.expected_date - now()).days
            todo.days_left = days_left
        else:
            todo.days_left = None
    #passing the todo form
        
    form = TodoForm()
    # Get the current year
    current_year = now().year

    ################## CROP YIELD YEARLY PRODUCTION CHART##############################################
    # Filter harvests for the beneficiaries assigned to this supervisor
    harvestss = Harvest.objects.filter(beneficiary__in=beneficiaries, date__year__lte=current_year)

    # Calculate total yield per crop
    total_yield_per_crop = harvestss.values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Prepare data for the chart
    crop_names = [item['crop__name'] for item in total_yield_per_crop]
    crop_quantities = [float(item['total_quantity']) for item in total_yield_per_crop]

    # JSON structure for the chart
    chart_datas = json.dumps({'labels': crop_names, 'data': crop_quantities}) if crop_names else json.dumps({'labels': [], 'data': []})
    #####################END OF CROP YIELD YEARLY PRODUCTION CHART ##########################################
    # Filter harvests for the beneficiaries assigned to this supervisor and group by week
    total_yield_per_week_by_crop = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).annotate(
        week=TruncWeek('date')
    ).values('crop__name', 'week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week', 'crop__name')

    # Prepare data for the chart
    crops = list(set([item['crop__name'] for item in total_yield_per_week_by_crop]))  # Unique crop names
    weeks = sorted(list(set([item['week'].strftime('%Y-%W') for item in total_yield_per_week_by_crop])))  # Unique weeks sorted

    # Create a dataset for each crop
    datasets = []
    for crop in crops:
        crop_data = []
        for week in weeks:
            # Find the quantity for the crop in the specific week, or default to 0
            quantity = next(
                (item['total_quantity'] for item in total_yield_per_week_by_crop if item['crop__name'] == crop and item['week'].strftime('%Y-%W') == week),
                0
            )
            crop_data.append(float(quantity))
        datasets.append({
            'label': crop,
            'data': crop_data,
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        })

    # JSON structure for the chart
    weekly_crop_production_chart_datas = json.dumps({'labels': weeks, 'datasets': datasets}) if weeks else json.dumps({'labels': [], 'datasets': []})

    ########################################## END OF WEEKLY PRODUCTION BY CROP ###############################################
     
    # Total yield per week for assigned beneficiaries
    total_yield_per_week = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week')

    # Prepare data for the chart
    week_labels = [item['week'].strftime('%Y-%W') for item in total_yield_per_week]  # Format as "Year-Week"
    weekly_quantities = [float(item['total_quantity']) for item in total_yield_per_week]

    # JSON structure for the chart
    weekly_chart_datas = json.dumps({'labels': week_labels, 'data': weekly_quantities}) if week_labels else json.dumps({'labels': [], 'data': []})

    # Total yield per tunnel (greenhouse rooms) for assigned beneficiaries
    total_yield_per_tunnel = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).values('greenhouse_room__room_name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Fetch weekly production data grouped by week and greenhouse room
    weekly_total_yield_per_tunnel = (
        Harvest.objects.filter(
            beneficiary__in=beneficiaries, date__year__lte=current_year
        )
        .annotate(week=TruncWeek('date'))
        .values('week', 'greenhouse_room__room_name')  # Include greenhouse room in grouping
        .annotate(
            total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
        )
        .order_by('week', 'greenhouse_room__room_name')
    )

    # Organize data into labels and datasets
    data_by_room = defaultdict(lambda: defaultdict(float))
    labels = []

    for item in weekly_total_yield_per_tunnel:
        week_label = item['week'].strftime('%Y-%W')  # Format as "Year-Week"
        if week_label not in labels:
            labels.append(week_label)
        data_by_room[item['greenhouse_room__room_name']][week_label] = float(item['total_quantity'])

    # Prepare datasets
    datasets = []
    for room_name, data in data_by_room.items():
        datasets.append({
            'label': room_name,
            'data': [data.get(week_label, 0) for week_label in labels],
            'backgroundColor': [],  # Colors can be added dynamically in the frontend
            'borderColor': [],
            'borderWidth': 1
        })

    # JSON structure for the chart
    yield_per_tunnel_weekly_chart_datas = json.dumps({
        'labels': labels,
        'datasets': datasets
    }) if labels else json.dumps({'labels': [], 'datasets': []})

    ############################# CROP YIELD WEEKLY PRODUCTION CHARTS ########################################
    
    # Accumulated yield for assigned beneficiaries
    accumulated_yield = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total yield for the 4 major crops and others for assigned beneficiaries
    major_crops = ['Crop1', 'Crop2', 'Crop3', 'Crop4']  # Replace with your actual crop names
    major_crops_yield = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year, crop__name__in=major_crops
    ).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    other_crops_yield = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).exclude(crop__name__in=major_crops).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total revenue earned over the period for assigned beneficiaries
    total_revenue = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).aggregate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )['total_revenue']

    # Sales revenue per crop for assigned beneficiaries
    revenue_per_crop = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).values('crop__name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_crop_chart_data = json.dumps({
        'labels': [item['crop__name'] for item in revenue_per_crop],
        'data': [float(item['total_revenue']) for item in revenue_per_crop]
    }, cls=DjangoJSONEncoder)

    # Revenue contribution from clusters (greenhouses or greenhouse rooms) for assigned beneficiaries
    revenue_per_cluster = Harvest.objects.filter(
        beneficiary__in=beneficiaries, date__year__lte=current_year
    ).values('greenhouse_room__room_name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_cluster_chart_data = json.dumps({
        'labels': [item['greenhouse_room__room_name'] for item in revenue_per_cluster],
        'data': [float(item['total_revenue']) for item in revenue_per_cluster]
    }, cls=DjangoJSONEncoder)
    
    ########################################################################################################
    
    # Calculate the accumulated total cost of farm inputs received from input dealers for the specific supervisor
    result = InputEdoDistribution.objects.filter(supervisor=supervisor).aggregate(
        total_cost=Sum(F('quantity') * F('unit_cost'), output_field=models.DecimalField())
    )
    # Get the total cost of farm inputs for this supervisor, or set it to 0 if None
    accumulated_farminput_total_cost = result['total_cost'] if result['total_cost'] else Decimal(0)


    # Calculate the accumulated total cost of farm inputs distributed to EDOs by AIC
    edo_dist_result = InputDistribution.objects.filter(beneficiary__in=beneficiaries).aggregate(
        total_cost=Sum(F('quantity') * F('farm_input__unit_cost'), output_field=models.DecimalField())
    )

    # Get the total cost of farm inputs distributed to EDOs by AIC or set it to 0 if None
    accumulated_farminput_total_cost_distributed_edo = edo_dist_result['total_cost'] if edo_dist_result['total_cost'] else Decimal(0)
        
    # Calculate the total quantity received for each farm input by a supervisor
    received_data = InputEdoDistribution.objects.filter(supervisor=supervisor).values(
        'farm_input__id', 
        'farm_input__inputcategory__name', 
        'farm_input__description'
    ).annotate(
        total_received_quantity=Sum('quantity')
    )

    # Calculate the total quantity distributed for each farm input by the supervisor to beneficiaries
    distributed_data = InputDistribution.objects.filter(
        farm_input__in=[item['farm_input__id'] for item in received_data],
        distributed_by=supervisor
    ).values('farm_input__id').annotate(
        total_distributed_quantity=Sum('quantity')
    )
        

    # Now, map the total received and distributed quantities together for each farm input
    received_distributed_data = []
    for received in received_data:
        # Find the distributed quantity for the same farm input
        distributed = next((item['total_distributed_quantity'] for item in distributed_data if item['farm_input__id'] == received['farm_input__id']), 0)
        received_distributed_data.append({
            'farm_input_id': received['farm_input__id'],
            'farm_input_category': received['farm_input__inputcategory__name'],
            'farm_input_description': received['farm_input__description'],
            'total_received_quantity': float(received['total_received_quantity']),
            'total_distributed_quantity': float(distributed)
        })
        
    # Prepare the chart labels and datasets
    #labels_INPUT = [f"{item['farm_input_category']} - {item['farm_input_description']}" for item in received_distributed_data]
    labels_INPUT = [f"{item['farm_input_category']}" for item in received_distributed_data]
    received_quantities = [item['total_received_quantity'] for item in received_distributed_data]
    distributed_quantities = [item['total_distributed_quantity'] for item in received_distributed_data]

    # Prepare the dataset for the chart
    datasets_INPUT = [
        {
            'label': 'Total Received Quantity',
            'data': received_quantities,
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        },
        {
            'label': 'Total Distributed Quantity',
            'data': distributed_quantities,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1
        }
    ]

    # Create JSON data for the chart
    chart_data_edo_dist_chart = json.dumps({
        'labels': labels_INPUT,
        'datasets': datasets_INPUT
    })
    ################################### END OF THE CHART #########################################
    # Print or use the accumulated total cost
    #print(f"Accumulated Total Cost: {accumulated_total_cost}")
    orders = Order.objects.filter(status='Pending')
    
     # Query all TrendKnowledgeBank entries with their related discussions
    trend_knowledge_banks = TrendKnowledgeBank.objects.prefetch_related('trendknowledgediscussion_set')

    # Query the FarmInput model
    data = (
        FarmInput.objects.values(
            'inputdealer__name',  # Dealer name
            'inputcategory__name',  # Category name
            'quantity_received',  # Quantity received
            'cost_per_unit',  # Cost per unit
        )
        .annotate(
            total_quantity=Sum('quantity_received'),
            total_cost=Sum(F('quantity_received') * F('cost_per_unit'), output_field=models.DecimalField())
        )
        .order_by('inputdealer__name', 'inputcategory__name')
    )

    # total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    # Initialize the data structure
    farminput_chart_data = {}

    # Process the data
    for entry in data:
        dealer = entry['inputdealer__name']
        category = entry['inputcategory__name']
        quantity_received = Decimal(entry.get('quantity_received', 0))  # Convert to Decimal
        cost_per_unit = Decimal(entry.get('cost_per_unit', 0.0))  # Convert to Decimal

        # Initialize dealer if not present
        if dealer not in farminput_chart_data:
            farminput_chart_data[dealer] = {}

        # Initialize category if not present
        if category not in farminput_chart_data[dealer]:
            farminput_chart_data[dealer][category] = {
                'total_quantity': Decimal(0),
                'total_cost': Decimal(0.0),
            }

        # Update totals
        farminput_chart_data[dealer][category]['total_quantity'] += quantity_received
        farminput_chart_data[dealer][category]['total_cost'] += quantity_received * cost_per_unit

    # Convert the data to JSON format
    # Ensure decimals are converted to strings for JSON serialization
    farminput_chart_datas = json.dumps(
        farminput_chart_data,
        default=lambda o: str(o) if isinstance(o, Decimal) else o
    )
       ######### End of farm input costing and charts
    #passing the todo form
    context = {
        #'total_volume_purchased': total_volume_purchased,
        'supervisor': supervisor, 
        'beneficiaries':beneficiaries, 
        
        #'total_payments': total_payments,
        #'total_volume_delivered': total_volume_delivered,
        'cash_assigned_list': cash_assigned_list,
        'repayments': repayments,
        'total_volume_purchased': total_volume_purchased,
        #'total_payments': total_payments,
        #'total_volume_delivered': total_volume_delivered,
         #'buyers': buyers,
        'total_cash_sales': total_cash_sales,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'total_cash_loan': total_cash_loan,
        'total_loan_repayment': total_loan_repayment,
        'total_cash_loan_arrears': total_cash_loan_arrears,
        'todos':todos, 
        'form': form,
        
        #orders
        'orders':orders,
        
        #DASHBOARD SUMMARY RECORDS
        'accumulated_yield': accumulated_yield,
        'total_yield_per_crop': total_yield_per_crop,
        'total_yield_per_tunnel': total_yield_per_tunnel,
        'major_crops_yield': major_crops_yield,
        'other_crops_yield': other_crops_yield,
        'total_revenue': total_revenue,
        'revenue_per_crop': revenue_per_crop,
        'revenue_per_cluster': revenue_per_cluster,
        'chart_datas': chart_datas,
        
        ############# weekly chart data
        'total_yield_per_week': total_yield_per_week,
        'weekly_chart_datas': weekly_chart_datas,
        'weekly_crop_production_chart_datas':weekly_crop_production_chart_datas,
        
        #weekly tunnel yield chart data
        'weekly_total_yield_per_tunnel':weekly_total_yield_per_tunnel,
        'yield_per_tunnel_weekly_chart_datas':yield_per_tunnel_weekly_chart_datas,
        
        #review per crop and revenue per cluster charts
        'revenue_per_crop_chart_data': revenue_per_crop_chart_data,
        'revenue_per_cluster_chart_data': revenue_per_cluster_chart_data,
        
        #farm input records
        'farminput_chart_datas': farminput_chart_datas,
        'accumulated_farminput_total_cost':accumulated_farminput_total_cost,
        'accumulated_farminput_total_cost_distributed_edo':accumulated_farminput_total_cost_distributed_edo,
        #'accumulated_farminput_total_cost_distributed_beneficiary':accumulated_farminput_total_cost_distributed_beneficiary,
        
        #edo farm input distributed chart
        'chart_data_edo_dist_chart':chart_data_edo_dist_chart,
        
        #trend knowledge
        'trend_knowledge_banks':trend_knowledge_banks,
    }
    return render(request, 'admin/edo/dashboard.html', context)



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

@login_required
def beneficiary_dashboard(request):
    # Get the supervisor based on the logged-in user
    beneficiary = Beneficiary.objects.get(user=request.user)    
    # Filter beneficiaries assigned to the logged-in supervisor
    #beneficiaries = Beneficiary.objects.filter(assigned_edo=supervisor)
    
     # Todos
    todos = Todo.objects.filter(created_by=beneficiary.user)
    #finding number of days left for event to happen
    for todo in todos:
        if todo.expected_date:
            days_left = (todo.expected_date - now()).days
            todo.days_left = days_left
        else:
            todo.days_left = None
    #passing the todo form
            
     # Total volume purchased
    total_volume_purchased = Transaction.objects.filter(
            transaction_type=Transaction.CROP_PURCHASE
        ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0
        # Total deliveries made
    total_volume_delivered = Transaction.objects.aggregate(
            total_delivered=Sum('volume')
        )['total_delivered'] or 0

            
    form = TodoForm()
        #passing the todo form
    # Get the list of cash assigned to the beneficiaries
    cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
    # Get repayments related to the cash assigned to these beneficiaries
    # Fetch all repayments related to the beneficiary
    repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

    # Total cash loans and repayments
    total_cash_loan = cash_assigned_list.aggregate(total=Sum('amount'))['total'] or 0
    total_loan_repayment = repayments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_cash_loan_arrears = total_cash_loan - total_loan_repayment

    # Harvest totals
    # Filter harvests for the beneficiaries assigned to this supervisor
    harvests = Harvest.objects.filter(beneficiary=beneficiary)
     # Calculate total quantity and total sum
    total_quantity = harvests.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_sum = harvests.aggregate(total_sum=Sum(F('quantity') * F('price_record__price')))['total_sum'] or 0

    form = TodoForm()
    current_year = now().year

    ################## CROP YIELD YEARLY PRODUCTION CHART##############################################
    # Filter harvests for the beneficiaries assigned to this supervisor
    harvestss = Harvest.objects.filter(beneficiary=beneficiary, date__year__lte=current_year)

    # Calculate total yield per crop
    total_yield_per_crop = harvestss.values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    
    # Prepare data for the chart
    crop_names = [item['crop__name'] for item in total_yield_per_crop]
    crop_quantities = [float(item['total_quantity']) for item in total_yield_per_crop]

    # JSON structure for the chart
    chart_datas = json.dumps({'labels': crop_names, 'data': crop_quantities}) if crop_names else json.dumps({'labels': [], 'data': []})
    #####################END OF CROP YIELD YEARLY PRODUCTION CHART ##########################################
    # Filter harvests for the beneficiaries assigned to this supervisor and group by week
    total_yield_per_week_by_crop = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).annotate(
        week=TruncWeek('date')
    ).values('crop__name', 'week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week', 'crop__name')

    # Prepare data for the chart
    crops = list(set([item['crop__name'] for item in total_yield_per_week_by_crop]))  # Unique crop names
    weeks = sorted(list(set([item['week'].strftime('%Y-%W') for item in total_yield_per_week_by_crop])))  # Unique weeks sorted

    # Create a dataset for each crop
    datasets = []
    for crop in crops:
        crop_data = []
        for week in weeks:
            # Find the quantity for the crop in the specific week, or default to 0
            quantity = next(
                (item['total_quantity'] for item in total_yield_per_week_by_crop if item['crop__name'] == crop and item['week'].strftime('%Y-%W') == week),
                0
            )
            crop_data.append(float(quantity))
        datasets.append({
            'label': crop,
            'data': crop_data,
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        })

    # JSON structure for the chart
    weekly_crop_production_chart_datas = json.dumps({'labels': weeks, 'datasets': datasets}) if weeks else json.dumps({'labels': [], 'datasets': []})

    ########################################## END OF WEEKLY PRODUCTION BY CROP ###############################################
     
    # Total yield per week for assigned beneficiaries
    total_yield_per_week = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week')

    # Prepare data for the chart
    week_labels = [item['week'].strftime('%Y-%W') for item in total_yield_per_week]  # Format as "Year-Week"
    weekly_quantities = [float(item['total_quantity']) for item in total_yield_per_week]

    # JSON structure for the chart
    weekly_chart_datas = json.dumps({'labels': week_labels, 'data': weekly_quantities}) if week_labels else json.dumps({'labels': [], 'data': []})

    # Total yield per tunnel (greenhouse rooms) for assigned beneficiaries
    total_yield_per_tunnel = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).values('greenhouse_room__room_name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Fetch weekly production data grouped by week and greenhouse room
    weekly_total_yield_per_tunnel = (
        Harvest.objects.filter(
            beneficiary=beneficiary, date__year__lte=current_year
        )
        .annotate(week=TruncWeek('date'))
        .values('week', 'greenhouse_room__room_name')  # Include greenhouse room in grouping
        .annotate(
            total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
        )
        .order_by('week', 'greenhouse_room__room_name')
    )

    # Organize data into labels and datasets
    data_by_room = defaultdict(lambda: defaultdict(float))
    labels = []

    for item in weekly_total_yield_per_tunnel:
        week_label = item['week'].strftime('%Y-%W')  # Format as "Year-Week"
        if week_label not in labels:
            labels.append(week_label)
        data_by_room[item['greenhouse_room__room_name']][week_label] = float(item['total_quantity'])

    # Prepare datasets
    datasets = []
    for room_name, data in data_by_room.items():
        datasets.append({
            'label': room_name,
            'data': [data.get(week_label, 0) for week_label in labels],
            'backgroundColor': [],  # Colors can be added dynamically in the frontend
            'borderColor': [],
            'borderWidth': 1
        })

    # JSON structure for the chart
    yield_per_tunnel_weekly_chart_datas = json.dumps({
        'labels': labels,
        'datasets': datasets
    }) if labels else json.dumps({'labels': [], 'datasets': []})

    ############################# CROP YIELD WEEKLY PRODUCTION CHARTS ########################################
        
    # Accumulated yield for assigned beneficiaries
    accumulated_yield = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total yield for the 4 major crops and others for assigned beneficiaries
    major_crops = ['Crop1', 'Crop2', 'Crop3', 'Crop4']  # Replace with your actual crop names
    major_crops_yield = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year, crop__name__in=major_crops
    ).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    other_crops_yield = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).exclude(crop__name__in=major_crops).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total revenue earned over the period for assigned beneficiaries
    total_revenue = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).aggregate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )['total_revenue']

    # Sales revenue per crop for assigned beneficiaries
    revenue_per_crop = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).values('crop__name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_crop_chart_data = json.dumps({
        'labels': [item['crop__name'] for item in revenue_per_crop],
        'data': [float(item['total_revenue']) for item in revenue_per_crop]
    }, cls=DjangoJSONEncoder)

    # Revenue contribution from clusters (greenhouses or greenhouse rooms) for assigned beneficiaries
    revenue_per_cluster = Harvest.objects.filter(
        beneficiary=beneficiary, date__year__lte=current_year
    ).values('greenhouse_room__room_name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_cluster_chart_data = json.dumps({
        'labels': [item['greenhouse_room__room_name'] for item in revenue_per_cluster],
        'data': [float(item['total_revenue']) for item in revenue_per_cluster]
    }, cls=DjangoJSONEncoder)
    
    
    # servicerequests = ServiceRequest.objects.filter(beneficiary = beneficiary)
    servicerequests = ServiceRequest.objects.filter(beneficiary=beneficiary)

    # Calculate total cost per service request
    for servicerequest in servicerequests:
        servicerequest.total_cost_sum = sum(
            service_item.quantity * service_item.unitcost 
            for service_item in servicerequest.servicerequest_items.all()
        )

    # Calculate grand total for all service requests
    total_requests_bill_totals = sum(servicerequest.total_cost_sum for servicerequest in servicerequests)
        
    ########################################################################################################    
    #END OF DASHBOARD SUMMARY RECORDS

    # Calculate the accumulated total cost of farm inputs received from input dealers for the specific supervisor
    result = InputEdoDistribution.objects.filter(supervisor=beneficiary.assigned_edo).aggregate(
        total_cost=Sum(F('quantity') * F('unit_cost'), output_field=models.DecimalField())
    )
    # Get the total cost of farm inputs for this supervisor, or set it to 0 if None
    accumulated_farminput_total_cost = result['total_cost'] if result['total_cost'] else Decimal(0)

    # Calculate the accumulated total cost of farm inputs distributed to EDOs by AIC
    edo_dist_result = InputDistribution.objects.filter(beneficiary=beneficiary).aggregate(
        total_cost=Sum(F('quantity') * F('farm_input__unit_cost'), output_field=models.DecimalField())
    )
    
     # Calculate the accumulated total cost of farm inputs distributed to EDOs by AIC
    edo_dist_result_qty = InputDistribution.objects.filter(beneficiary=beneficiary).aggregate(
        total_qty=Sum(F('quantity'), output_field=models.DecimalField())
    )
    # Get the total cost of farm inputs distributed to EDOs by AIC or set it to 0 if None
    accumulated_farminput_qty_distributed_edo = edo_dist_result_qty['total_qty'] if edo_dist_result_qty['total_qty'] else Decimal(0)
    
    # Get the total cost of farm inputs distributed to EDOs by AIC or set it to 0 if None
    accumulated_farminput_total_cost_distributed_edo = edo_dist_result['total_cost'] if edo_dist_result['total_cost'] else Decimal(0)
   
  ############################################################################
     ################### To generate a chart that visualizes the farm input received 
     # by a supervisor and the quantity distributed to beneficiaries 
     # Calculate the total quantity received for each FarmInput and the total quantity distributed via InputDistribution
    ############################################################################ 
        
    # Calculate the total quantity received for each farm input by a supervisor
    received_data = InputEdoDistribution.objects.filter(supervisor=beneficiary.assigned_edo).values(
        'farm_input__id', 
        'farm_input__inputcategory__name', 
        'farm_input__description'
    ).annotate(
        total_received_quantity=Sum('quantity')
    )

    # Calculate the total quantity distributed for each farm input by the supervisor to beneficiaries
    distributed_data = InputDistribution.objects.filter(
        farm_input__in=[item['farm_input__id'] for item in received_data],
        distributed_by=beneficiary.assigned_edo
    ).values('farm_input__id').annotate(
        total_distributed_quantity=Sum('quantity')
    )
        

    # Now, map the total received and distributed quantities together for each farm input
    received_distributed_data = []
    for received in received_data:
        # Find the distributed quantity for the same farm input
        distributed = next((item['total_distributed_quantity'] for item in distributed_data if item['farm_input__id'] == received['farm_input__id']), 0)
        received_distributed_data.append({
            'farm_input_id': received['farm_input__id'],
            'farm_input_category': received['farm_input__inputcategory__name'],
            'farm_input_description': received['farm_input__description'],
            'total_received_quantity': float(received['total_received_quantity']),
            'total_distributed_quantity': float(distributed)
        })
        
    # Prepare the chart labels and datasets
    #labels_INPUT = [f"{item['farm_input_category']} - {item['farm_input_description']}" for item in received_distributed_data]
    labels_INPUT = [f"{item['farm_input_category']}" for item in received_distributed_data]
    received_quantities = [item['total_received_quantity'] for item in received_distributed_data]
    distributed_quantities = [item['total_distributed_quantity'] for item in received_distributed_data]

    # Prepare the dataset for the chart
    datasets_INPUT = [
        {
            'label': 'Total Received Quantity',
            'data': received_quantities,
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        },
        {
            'label': 'Total Distributed Quantity',
            'data': distributed_quantities,
            'backgroundColor': 'rgba(255, 99, 132, 0.2)',
            'borderColor': 'rgba(255, 99, 132, 1)',
            'borderWidth': 1
        }
    ]

    # Create JSON data for the chart
    chart_data_edo_dist_chart = json.dumps({
        'labels': labels_INPUT,
        'datasets': datasets_INPUT
    })
    ################################### END OF THE CHART #########################################
    # Print or use the accumulated total cost
    #print(f"Accumulated Total Cost: {accumulated_total_cost}")
    orders = Order.objects.filter(status='Pending')
    
     # Query all TrendKnowledgeBank entries with their related discussions
    trend_knowledge_banks = TrendKnowledgeBank.objects.filter(created_by=beneficiary.user).prefetch_related('trendknowledgediscussion_set')

    # Query the FarmInput model
    data = (
        FarmInput.objects.values(
            'inputdealer__name',  # Dealer name
            'inputcategory__name',  # Category name
            'quantity_received',  # Quantity received
            'cost_per_unit',  # Cost per unit
        )
        .annotate(
            total_quantity=Sum('quantity_received'),
            total_cost=Sum(F('quantity_received') * F('cost_per_unit'), output_field=models.DecimalField())
        )
        .order_by('inputdealer__name', 'inputcategory__name')
    )

    # total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    # Initialize the data structure
    farminput_chart_data = {}

    # Process the data
    for entry in data:
        dealer = entry['inputdealer__name']
        category = entry['inputcategory__name']
        quantity_received = Decimal(entry.get('quantity_received', 0))  # Convert to Decimal
        cost_per_unit = Decimal(entry.get('cost_per_unit', 0.0))  # Convert to Decimal

        # Initialize dealer if not present
        if dealer not in farminput_chart_data:
            farminput_chart_data[dealer] = {}

        # Initialize category if not present
        if category not in farminput_chart_data[dealer]:
            farminput_chart_data[dealer][category] = {
                'total_quantity': Decimal(0),
                'total_cost': Decimal(0.0),
            }

        # Update totals
        farminput_chart_data[dealer][category]['total_quantity'] += quantity_received
        farminput_chart_data[dealer][category]['total_cost'] += quantity_received * cost_per_unit

    # Convert the data to JSON format
    # Ensure decimals are converted to strings for JSON serialization
    farminput_chart_datas = json.dumps(
        farminput_chart_data,
        default=lambda o: str(o) if isinstance(o, Decimal) else o
    )
    # Convert the data to JSON format
    #farminput_chart_datas = json.dumps(farminput_chart_data)
        
    ######### End of farm input costing and charts
    #passing the todo form
    context = {
        #'total_volume_purchased': total_volume_purchased,
        #'supervisor': supervisor, 
        'assigned_edo':beneficiary, 
        'servicerequests':servicerequests,
        'total_requests_bill_totals':total_requests_bill_totals,
        #'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
        'cash_assigned_list': cash_assigned_list,
        'repayments': repayments,
        'total_volume_purchased': total_volume_purchased,
        #'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
         #'buyers': buyers,
       # 'total_cash_sales': total_cash_sales,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'total_cash_loan': total_cash_loan,
        'total_loan_repayment': total_loan_repayment,
        'total_cash_loan_arrears': total_cash_loan_arrears,
        'todos':todos, 
        'form': form,
        
        #orders
        'orders':orders,
        
        #DASHBOARD SUMMARY RECORDS
        'accumulated_yield': accumulated_yield,
        'total_yield_per_crop': total_yield_per_crop,
        'total_yield_per_tunnel': total_yield_per_tunnel,
        'major_crops_yield': major_crops_yield,
        'other_crops_yield': other_crops_yield,
        'total_revenue': total_revenue,
        'revenue_per_crop': revenue_per_crop,
        'revenue_per_cluster': revenue_per_cluster,
        'chart_datas': chart_datas,
        
        ############# weekly chart data
        'total_yield_per_week': total_yield_per_week,
        'weekly_chart_datas': weekly_chart_datas,
        'weekly_crop_production_chart_datas':weekly_crop_production_chart_datas,
        
        #weekly tunnel yield chart data
        'weekly_total_yield_per_tunnel':weekly_total_yield_per_tunnel,
        'yield_per_tunnel_weekly_chart_datas':yield_per_tunnel_weekly_chart_datas,
        
        #review per crop and revenue per cluster charts
        'revenue_per_crop_chart_data': revenue_per_crop_chart_data,
        'revenue_per_cluster_chart_data': revenue_per_cluster_chart_data,
        
        #farm input records
        'farminput_chart_datas': farminput_chart_datas,
        'accumulated_farminput_total_cost':accumulated_farminput_total_cost,
        'accumulated_farminput_total_cost_distributed_edo':accumulated_farminput_total_cost_distributed_edo,
        'accumulated_farminput_qty_distributed_edo':accumulated_farminput_qty_distributed_edo,
        
        #edo farm input distributed chart
        'chart_data_edo_dist_chart':chart_data_edo_dist_chart,
        
        #trend knowledge
        'trend_knowledge_banks':trend_knowledge_banks,
    }
    return render(request, 'admin/beneficiary/dashboard.html', context)



@login_required
def aic_dashboard(request):
    
    user_aic = AIC.objects.all()
    
    # Total volume purchased
    total_volume_purchased = Transaction.objects.filter(
            transaction_type=Transaction.CROP_PURCHASE
        ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0

        # Total payments
    total_payments = Payment.objects.aggregate(
            total_paid=Sum('amount_paid')
        )['total_paid'] or 0

        # Total deliveries made
    total_volume_delivered = Transaction.objects.aggregate(
            total_delivered=Sum('volume')
        )['total_delivered'] or 0

        # Todos
        #todos = Todo.objects.all()
    todos = Todo.objects.filter(created_by=request.user)
        #finding number of days left for event to happen
    for todo in todos:
            if todo.expected_date:
                days_left = (todo.expected_date - now()).days
                todo.days_left = days_left
            else:
                todo.days_left = None
        #passing the todo form
            
    form = TodoForm()
        #passing the todo form

        # Get beneficiary-specific data
    #beneficiary = Beneficiary.objects.get(user=request.user)

    cash_assigned_list = CashAssigned.objects.filter()
    repayments = Repayment.objects.filter()

        # Total cash loans and repayments
    total_cash_loan = cash_assigned_list.aggregate(total=Sum('amount'))['total'] or 0
    total_loan_repayment = repayments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_cash_loan_arrears = total_cash_loan - total_loan_repayment

        # Harvest totals
    harvests = Harvest.objects.filter()
    total_quantity = sum(harvest.quantity or 0 for harvest in harvests)
    total_sum = sum(harvest.total_price or 0 for harvest in harvests)
       # Total cash sales
    total_cash_sales = Transaction.objects.filter(
        transaction_type=Transaction.CROP_PURCHASE,
            buyer__isnull=False
      ).aggregate(total_cash=Sum('total_amount'))['total_cash'] or 0
    
    # Aggregate data for your dashboard
    total_volume_purchased = Transaction.objects.all().aggregate(total_volume=Sum('volume'))['total_volume']
    total_payments = Payment.objects.all().aggregate(total_paid=Sum('amount_paid'))['total_paid']

    # Adjust the filter for total_volume_delivered to first get relevant OrderItems
    order_items = OrderItem.objects.all()
    total_volume_delivered = Delivery.objects.all().aggregate(total_delivered=Sum('volume_delivered'))['total_delivered']

     # Todos
    todos = Todo.objects.filter(created_by=request.user)
    #finding number of days left for event to happen
    for todo in todos:
        if todo.expected_date:
            days_left = (todo.expected_date - now()).days
            todo.days_left = days_left
        else:
            todo.days_left = None
    #passing the todo form
        
    form = TodoForm()
    
    #DASHBOARD SUMMARY RECORDS
     # Accumulated yield for the year
    #current_year = timezone.now().year - 1
    # Get the current year
    current_year = now().year

    ################## CROP YIELD YEARLY PRODUCTION CHART##############################################
    
    # Fetch all data up to and including the current year
    total_yield_per_crop = Harvest.objects.filter(date__year__lte=current_year).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )

    # Prepare data for the chart
    crop_names = [item['crop__name'] for item in total_yield_per_crop]
    crop_quantities = [float(item['total_quantity']) for item in total_yield_per_crop]
    # JSON structure for the chart
    chart_datas = json.dumps({'labels': crop_names, 'data': crop_quantities}) if crop_names else json.dumps({'labels': [], 'data': []})
    #####################END OF CROP YIELD YEARLY PRODUCTION CHART ##########################################
    
     # Fetch data grouped by crop and week
    total_yield_per_week_by_crop = Harvest.objects.filter(date__year__lte=current_year).annotate(
        week=TruncWeek('date')
    ).values('crop__name', 'week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week', 'crop__name')

    # Prepare data for the chart
    crops = list(set([item['crop__name'] for item in total_yield_per_week_by_crop]))  # Unique crop names
    weeks = sorted(list(set([item['week'].strftime('%Y-%W') for item in total_yield_per_week_by_crop])))  # Unique weeks sorted

    # Create a dataset for each crop
    datasets = []
    for crop in crops:
        crop_data = []
        for week in weeks:
            # Find the quantity for the crop in the specific week, or default to 0
            quantity = next(
                (item['total_quantity'] for item in total_yield_per_week_by_crop if item['crop__name'] == crop and item['week'].strftime('%Y-%W') == week),
                0
            )
            crop_data.append(float(quantity))
        datasets.append({
            'label': crop,
            'data': crop_data,
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1,
        })

    # JSON structure for the chart
    weekly_crop_production_chart_datas = json.dumps({'labels': weeks, 'datasets': datasets}) if weeks else json.dumps({'labels': [], 'datasets': []})
  
    ########################################## END OF WEEKLY PRODUCTION BY CROP ###############################################
      # Fetch all data up to and including the current year, grouped by week
    total_yield_per_week = Harvest.objects.filter(date__year__lte=current_year).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    ).order_by('week')

    # Prepare data for the chart
    week_labels = [item['week'].strftime('%Y-%W') for item in total_yield_per_week]  # Format as "Year-Week"
    weekly_quantities = [float(item['total_quantity']) for item in total_yield_per_week]

    # JSON structure for the chart
    weekly_chart_datas = json.dumps({'labels': week_labels, 'data': weekly_quantities}) if week_labels else json.dumps({'labels': [], 'data': []})


    # Total yield per tunnel (greenhouse rooms)
    total_yield_per_tunnel = Harvest.objects.filter(date__year__lte=current_year).values('greenhouse_room__room_name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    
    
    # Fetch weekly production data grouped by week and greenhouse room
    weekly_total_yield_per_tunnel = (
        Harvest.objects.filter(date__year__lte=current_year)
        .annotate(week=TruncWeek('date'))
        .values('week', 'greenhouse_room__room_name')  # Include greenhouse room in grouping
        .annotate(
            total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
        )
        .order_by('week', 'greenhouse_room__room_name')
    )

    # Organize data into labels and datasets
    data_by_room = defaultdict(lambda: defaultdict(float))
    labels = []

    for item in weekly_total_yield_per_tunnel:
        week_label = item['week'].strftime('%Y-%W')  # Format as "Year-Week"
        if week_label not in labels:
            labels.append(week_label)
        data_by_room[item['greenhouse_room__room_name']][week_label] = float(item['total_quantity'])

    # Prepare datasets
    datasets = []
    for room_name, data in data_by_room.items():
        datasets.append({
            'label': room_name,
            'data': [data.get(week_label, 0) for week_label in labels],
            'backgroundColor': [],  # Colors can be added dynamically in the frontend
            'borderColor': [],
            'borderWidth': 1
        })

    # JSON structure for the chart
    yield_per_tunnel_weekly_chart_datas = json.dumps({
        'labels': labels,
        'datasets': datasets
    }) if labels else json.dumps({'labels': [], 'datasets': []})

    ############################# CROP YIELD WEEKLY PRODUCTION CHARTS ########################################
    
    accumulated_yield = Harvest.objects.filter(date__year__lte=current_year).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total yield for the 4 major crops and others
    major_crops = ['Crop1', 'Crop2', 'Crop3', 'Crop4']  # Replace with your actual crop names
    major_crops_yield = Harvest.objects.filter(date__year__lte=current_year, crop__name__in=major_crops).values('crop__name').annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )
    other_crops_yield = Harvest.objects.filter(date__year__lte=current_year).exclude(crop__name__in=major_crops).aggregate(
        total_quantity=Coalesce(Sum('quantity'), Value(0), output_field=DecimalField())
    )['total_quantity']

    # Total revenue earned over the period
    total_revenue = Harvest.objects.filter(date__year__lte=current_year).aggregate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )['total_revenue']
    

    # Sales revenue per crop
    revenue_per_crop = Harvest.objects.filter(date__year__lte=current_year).values('crop__name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_crop_chart_data = json.dumps({
        'labels': [item['crop__name'] for item in revenue_per_crop],
        'data': [float(item['total_revenue']) for item in revenue_per_crop]
    }, cls=DjangoJSONEncoder)

    # Revenue contribution from clusters (greenhouses or greenhouse rooms)
    revenue_per_cluster = Harvest.objects.filter(date__year__lte=current_year).values('greenhouse_room__room_name').annotate(
        total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    )
    # Prepare JSON data for charts
    revenue_per_cluster_chart_data = json.dumps({
        'labels': [item['greenhouse_room__room_name'] for item in revenue_per_cluster],
        'data': [float(item['total_revenue']) for item in revenue_per_cluster]
    }, cls=DjangoJSONEncoder)
    #END OF DASHBOARD SUMMARY RECORDS
  
    # Calculate the accumulated total cost of farm inputs received from input dealers
    result = FarmInput.objects.aggregate(
        total_cost=Sum(F('quantity_received') * F('cost_per_unit'), output_field=models.DecimalField())
    )

    # Get the total cost of farm inputs received from input dealers or set it to 0 if None
    accumulated_farminput_total_cost = result['total_cost'] if result['total_cost'] else Decimal(0)

    # Calculate the accumulated total cost of farm inputs distributed to EDOs by AIC
    edo_dist_result = InputEdoDistribution.objects.aggregate(
        total_cost=Sum(F('quantity') * F('unit_cost'), output_field=models.DecimalField())
    )

    # Get the total cost of farm inputs distributed to EDOs by AIC or set it to 0 if None
    accumulated_farminput_total_cost_distributed_edo = edo_dist_result['total_cost'] if edo_dist_result['total_cost'] else Decimal(0)
    
    # Calculate the accumulated total cost of farm inputs distributed to beneficiaries by an EDOs
    beneficiary_dist_result = InputDistribution.objects.aggregate(
        #total_cost=Sum(F('quantity') * F('unit_cost'), output_field=models.DecimalField())
        total_cost=Sum(F('quantity') * F('farm_input__unit_cost'), output_field=models.DecimalField())
    )

    # Get the total cost of farm inputs distributed to beneficiaries by an EDOs or set it to 0 if None
    accumulated_farminput_total_cost_distributed_beneficiary = beneficiary_dist_result['total_cost'] if beneficiary_dist_result['total_cost'] else Decimal(0)

    # Print or use the accumulated total cost
    #print(f"Accumulated Total Cost: {accumulated_total_cost}")
    orders = Order.objects.filter(status='Pending')
    # Query the FarmInput model
    data = (
        FarmInput.objects.values(
            'inputdealer__name',  # Dealer name
            'inputcategory__name',  # Category name
            'quantity_received',  # Quantity received
            'cost_per_unit',  # Cost per unit
        )
        .annotate(
            total_quantity=Sum('quantity_received'),
            total_cost=Sum(F('quantity_received') * F('cost_per_unit'), output_field=models.DecimalField())
        )
        .order_by('inputdealer__name', 'inputcategory__name')
    )

    # total_revenue=Coalesce(Sum('total_price'), Value(0), output_field=DecimalField())
    # Initialize the data structure
    farminput_chart_data = {}

    # Process the data
    for entry in data:
        dealer = entry['inputdealer__name']
        category = entry['inputcategory__name']
        quantity_received = Decimal(entry.get('quantity_received', 0))  # Convert to Decimal
        cost_per_unit = Decimal(entry.get('cost_per_unit', 0.0))  # Convert to Decimal

        # Initialize dealer if not present
        if dealer not in farminput_chart_data:
            farminput_chart_data[dealer] = {}

        # Initialize category if not present
        if category not in farminput_chart_data[dealer]:
            farminput_chart_data[dealer][category] = {
                'total_quantity': Decimal(0),
                'total_cost': Decimal(0.0),
            }

        # Update totals
        farminput_chart_data[dealer][category]['total_quantity'] += quantity_received
        farminput_chart_data[dealer][category]['total_cost'] += quantity_received * cost_per_unit

    # Convert the data to JSON format
    # Ensure decimals are converted to strings for JSON serialization
    farminput_chart_datas = json.dumps(
        farminput_chart_data,
        default=lambda o: str(o) if isinstance(o, Decimal) else o
    )
    # Convert the data to JSON format
        
    ######### End of farm input costing and charts
    context = {
        #'total_volume_purchased': total_volume_purchased,
        'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
        'cash_assigned_list': cash_assigned_list,
        'repayments': repayments,
        'total_volume_purchased': total_volume_purchased,
        'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
         #'buyers': buyers,
        'total_cash_sales': total_cash_sales,
        'total_sum': total_sum,
        'total_quantity': total_quantity,
        'total_cash_loan': total_cash_loan,
        'total_loan_repayment': total_loan_repayment,
        'total_cash_loan_arrears': total_cash_loan_arrears,
        'todos':todos, 
        'form': form,
        
        #orders
        'orders':orders,
        
        #DASHBOARD SUMMARY RECORDS
        'accumulated_yield': accumulated_yield,
        'total_yield_per_crop': total_yield_per_crop,
        'total_yield_per_tunnel': total_yield_per_tunnel,
        'major_crops_yield': major_crops_yield,
        'other_crops_yield': other_crops_yield,
        'total_revenue': total_revenue,
        'revenue_per_crop': revenue_per_crop,
        'revenue_per_cluster': revenue_per_cluster,
        'chart_datas': chart_datas,
        
        ############# weekly chart data
        'total_yield_per_week': total_yield_per_week,
        'weekly_chart_datas': weekly_chart_datas,
        'weekly_crop_production_chart_datas':weekly_crop_production_chart_datas,
        
        #weekly tunnel yield chart data
        'weekly_total_yield_per_tunnel':weekly_total_yield_per_tunnel,
        'yield_per_tunnel_weekly_chart_datas':yield_per_tunnel_weekly_chart_datas,
        
        #review per crop and revenue per cluster charts
        'revenue_per_crop_chart_data': revenue_per_crop_chart_data,
        'revenue_per_cluster_chart_data': revenue_per_cluster_chart_data,
        
        #farm input records
        'farminput_chart_datas': farminput_chart_datas,
        'accumulated_farminput_total_cost':accumulated_farminput_total_cost,
        'accumulated_farminput_total_cost_distributed_edo':accumulated_farminput_total_cost_distributed_edo,
        'accumulated_farminput_total_cost_distributed_beneficiary':accumulated_farminput_total_cost_distributed_beneficiary,
    }
    
    return render(request, 'admin/aic/dashboard.html', context)


########### FINANCE DASHBOARD
@login_required
def finance_dashboard(request):
    finance_user = Finance.objects.get(user=request.user)
    today = now().date()

    # ========================== TODOs =============================
    todos = Todo.objects.filter(created_by=request.user)
    for todo in todos:
        todo.days_left = (todo.expected_date - now()).days if todo.expected_date else None
    todo_form = TodoForm()

    # =================== Aggregated Dashboard Metrics ===================
    confirmed_harvests = Harvest.objects.filter(confirmation='Confirmed')
    harvest_summary = confirmed_harvests.aggregate(
        total_quantity=Sum('quantity'),
        total_price=Sum('total_price')
    )

    stock_summary = HarvestStockAggregate.objects.aggregate(
        total_quantity=Sum('total_quantity'),
        total_value=Sum('total_value')
    )

    stock_movement_summary = HarvestMovement.objects.aggregate(
        total_quantity=Sum('quantity'),
        total_value=Sum('grade')
    )
   
    order_summary = Order.objects.aggregate(
        total_amount=Sum('total_amount'),
        total_orders=Count('id')
    )
    
    order_summary_item = Order.objects.aggregate(
        total_items=Sum('total_items'),
        total_orders=Count('id')
    )
    
    spoilage_summary = Spoilage.objects.aggregate(
        total_spoilage_items=Sum('quantity_spoiled'),
        total_spoilages=Count('id')
    )

    payment_summary = Payment.objects.aggregate(total_paid=Sum('amount_paid'))
    balance_summary = Balance.objects.aggregate(
        total_due=Sum('total_due'),
        amount_paid=Sum('amount_paid')
    )

    # =================== Chart Data (Serialized) ===================
    harvest_by_crop = list(confirmed_harvests
        .values('greenhouse__name', 'greenhouse_room__room_name','crop__name','cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    stock_by_centre = list(HarvestStockAggregate.objects
        .values('market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('total_quantity'))
    )

    movement_summary = list(HarvestMovement.objects
        .values('from_market_centre__name', 'to_market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    order_status_summary = list(Order.objects
        .values('status')
        .annotate(count=Count('id'))
    )

    payment_status_summary = list(Payment.objects
        .values('payment_status')
        .annotate(count=Count('id'))
    )

    paid_orders = Balance.objects.select_related('order__buyer') \
        .filter(total_due__gt=0).order_by('-total_due')
    
    outstanding_balances = Balance.objects.select_related('order__buyer').filter(
        Q(order__is_paid=False) |
        Q(total_due__gt=0) |
        Q(amount_paid__lt=F('total_due'))
    ).order_by('-total_due')

   
    unpaid_orders = Order.objects.select_related('buyer', 'sales_agent', 'balance').filter(
        Q(is_paid=False) |
        Q(balance__total_due__gt=0) |
        Q(balance__amount_paid__lt=F('balance__total_due'))
    ).order_by('-total_amount')

    
    total_sales = harvest_summary.get('total_price') or 0
    total_stock = stock_summary.get('total_quantity') or 0
    total_stock_movement = stock_movement_summary.get('total_quantity') or 0
    bal_outstanding = balance_summary.get('total_due') or 0
    total_ordered_items = order_summary_item.get('total_items') or 0
    total_spoilage = spoilage_summary.get('quantity_spoiled') or 0
    
    dashboard_cards = [
        {'title': 'Total Sales', 'value': total_sales, 'color': 'primary', 'icon': 'fa-money', 'tooltip': 'Total cash sales'},
        {'title': 'Available Stock', 'value': total_stock, 'color': 'success', 'icon': 'fa-balance-scale', 'tooltip': 'Total stock'},
        {'title': 'Stock Moved', 'value': total_stock_movement, 'color': 'secondary', 'icon': 'fa-refresh', 'tooltip': 'Stocks Moved'},
        {'title': 'Bal Outstanding', 'value': bal_outstanding, 'color': 'warning', 'icon': 'fa-money', 'tooltip': 'Stocks Moved'},
        {'title': 'Total Ordered Items', 'value': total_ordered_items, 'color': 'danger', 'icon': 'fa-shopping-basket', 'tooltip': 'Total Ordered Items'},
        {'title': 'Total Spoilage', 'value': total_spoilage, 'color': 'info', 'icon': 'fa-shopping-basket', 'tooltip': 'Total Spoilage Items'},
        # Add more as needed
    ]
    
    #spoilage Trends
    # Spoilage Trend Aggregations
    daily_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(day=TruncDay('spoilage_date'))
        .values('day')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('day')
    )

    weekly_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(week=TruncWeek('spoilage_date'))
        .values('week')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('week')
    )

    monthly_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(month=TruncMonth('spoilage_date'))
        .values('month')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('month')
    )

    #Harvest vs HarvestStockAggregate
    #HarvestStockAggregate vs HarvestMovement
    # Daily, Weekly, Monthly trends
    def get_trends():
        # 1. Harvest Trends
        daily_harvest = Harvest.objects.annotate(day=TruncDay('date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_harvest = Harvest.objects.annotate(week=TruncWeek('date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_harvest = Harvest.objects.annotate(month=TruncMonth('date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        # 2. Stock Trends
        daily_stock = HarvestStockAggregate.objects.annotate(day=TruncDay('created_at')) \
            .values('day').annotate(total_qty=Sum('total_quantity')).order_by('day')
        weekly_stock = HarvestStockAggregate.objects.annotate(week=TruncWeek('created_at')) \
            .values('week').annotate(total_qty=Sum('total_quantity')).order_by('week')
        monthly_stock = HarvestStockAggregate.objects.annotate(month=TruncMonth('created_at')) \
            .values('month').annotate(total_qty=Sum('total_quantity')).order_by('month')

        # 3. Movement Trends
        daily_move = HarvestMovement.objects.annotate(day=TruncDay('movement_date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_move = HarvestMovement.objects.annotate(week=TruncWeek('movement_date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_move = HarvestMovement.objects.annotate(month=TruncMonth('movement_date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        return {
            'daily_harvest': list(daily_harvest),
            'weekly_harvest': list(weekly_harvest),
            'monthly_harvest': list(monthly_harvest),

            'daily_stock': list(daily_stock),
            'weekly_stock': list(weekly_stock),
            'monthly_stock': list(monthly_stock),

            'daily_move': list(daily_move),
            'weekly_move': list(weekly_move),
            'monthly_move': list(monthly_move),
        }
    
    # =================== Context ===================
    context = {
        'finance': finance_user,
        'todos': todos,
        'todo_form': todo_form,

        # QuerySets for tables
        'orders': Order.objects.select_related('buyer', 'sales_agent'),
        'order_items': OrderItem.objects.select_related('harveststock', 'order'),
        'payments': Payment.objects.all(),
        'balances': Balance.objects.select_related('order__buyer'),

        #spoilage Trends
        'daily_spoilage': daily_spoilage,
        'weekly_spoilage': weekly_spoilage,
        'monthly_spoilage': monthly_spoilage,
    
        # JSON-serializable chart data
        'harvest_by_crop': harvest_by_crop,
        'stock_by_centre': stock_by_centre,
        'movement_summary': movement_summary,
        'order_status_summary': order_status_summary,
        'payment_status_summary': payment_status_summary,
        'paid_orders':paid_orders,
        'outstanding_balances': outstanding_balances,
        'unpaid_orders':unpaid_orders,
        
        'dashboard_cards': dashboard_cards,

        # Metrics for cards
        'total_cash_sales': harvest_summary.get('total_price') or 0,
        'total_quantity': stock_summary.get('total_quantity') or 0,
        'total_value': stock_summary.get('total_value') or 0,
        'total_volume_purchased': order_summary.get('total_amount') or 0,
        'total_orders': order_summary.get('total_orders') or 0,
        'total_paid': payment_summary.get('total_paid') or 0,
        'total_due': balance_summary.get('total_due') or 0,
        'amount_paid': balance_summary.get('amount_paid') or 0,

        # Add these if used in template
        'total_volume_delivered': 0,  # Replace with actual value if needed
        'accumulated_farminput_total_cost': 0,  # Replace with real computation
        'accumulated_farminput_total_cost_distributed_edo': 0,  # Replace if needed
        'total_sum': harvest_summary.get('total_price') or 0,  # Same as cash sales
    }

    context.update(get_trends())

    return render(request, 'admin/finance/financedashboard.html', context)


@login_required
def sale_dashboard(request):
    saleagent = SaleAgent.objects.get(user=request.user)
    today = now().date()

    # ========================== TODOs =============================
    todos = Todo.objects.filter(created_by=request.user)
    for todo in todos:
        todo.days_left = (todo.expected_date - now()).days if todo.expected_date else None
    todo_form = TodoForm()

    # =================== Aggregated Dashboard Metrics (filtered by saleagent) ===================
    confirmed_harvests = Harvest.objects.filter(confirmation='Confirmed', created_by=request.user)
    harvest_summary = confirmed_harvests.aggregate(
        total_quantity=Sum('quantity'),
        total_price=Sum('total_price')
    )

    stock_summary = HarvestStockAggregate.objects.filter(created_by=request.user).aggregate(
        total_quantity=Sum('total_quantity'),
        total_value=Sum('total_value')
    )

    stock_movement_summary = HarvestMovement.objects.filter(created_by=request.user).aggregate(
        total_quantity=Sum('quantity'),
        total_value=Sum('grade')
    )

    order_summary = Order.objects.filter(sales_agent=saleagent).aggregate(
        total_amount=Sum('total_amount'),
        total_orders=Count('id')
    )

    order_summary_item = Order.objects.filter(sales_agent=saleagent).aggregate(
        total_items=Sum('total_items'),
        total_orders=Count('id')
    )

    spoilage_summary = Spoilage.objects.filter(confirmed_by=request.user).aggregate(
        total_spoilage_items=Sum('quantity_spoiled'),
        total_spoilages=Count('id')
    )

    payment_summary = Payment.objects.filter(created_by=request.user).aggregate(total_paid=Sum('amount_paid'))
    balance_summary = Balance.objects.filter(order__sales_agent=saleagent).aggregate(
        total_due=Sum('total_due'),
        amount_paid=Sum('amount_paid')
    )

    # =================== Chart Data (Serialized) ===================
    harvest_by_crop = list(confirmed_harvests
        .values('greenhouse__name', 'greenhouse_room__room_name','crop__name','cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    stock_by_centre = list(HarvestStockAggregate.objects.filter(created_by=request.user)
        .values('market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('total_quantity'))
    )

    movement_summary = list(HarvestMovement.objects.filter(created_by=request.user)
        .values('from_market_centre__name', 'to_market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    order_status_summary = list(Order.objects.filter(sales_agent=saleagent)
        .values('status')
        .annotate(count=Count('id'))
    )

    payment_status_summary = list(Payment.objects.filter(created_by=request.user)
        .values('payment_status')
        .annotate(count=Count('id'))
    )

    paid_orders = Balance.objects.select_related('order__buyer').filter(order__sales_agent=saleagent, total_due__gt=0).order_by('-total_due')

    outstanding_balances = Balance.objects.select_related('order__buyer').filter(
        Q(order__sales_agent=saleagent),
        Q(order__is_paid=False) |
        Q(total_due__gt=0) |
        Q(amount_paid__lt=F('total_due'))
    ).order_by('-total_due')

    unpaid_orders = Order.objects.select_related('buyer', 'sales_agent', 'balance').filter(
        Q(sales_agent=saleagent) & (
            Q(is_paid=False) |
            Q(balance__total_due__gt=0) |
            Q(balance__amount_paid__lt=F('balance__total_due'))
        )
    ).order_by('-total_amount')

    total_sales = harvest_summary.get('total_price') or 0
    total_stock = stock_summary.get('total_quantity') or 0
    total_stock_movement = stock_movement_summary.get('total_quantity') or 0
    bal_outstanding = balance_summary.get('total_due') or 0
    total_ordered_items = order_summary_item.get('total_items') or 0
    total_spoilage = spoilage_summary.get('total_spoilage_items') or 0

    dashboard_cards = [
        {'title': 'Total Sales', 'value': total_sales, 'color': 'primary', 'icon': 'fa-money', 'tooltip': 'Total cash sales'},
        {'title': 'Available Stock', 'value': total_stock, 'color': 'success', 'icon': 'fa-balance-scale', 'tooltip': 'Total stock'},
        {'title': 'Stock Moved', 'value': total_stock_movement, 'color': 'secondary', 'icon': 'fa-refresh', 'tooltip': 'Stocks Moved'},
        {'title': 'Bal Outstanding', 'value': bal_outstanding, 'color': 'warning', 'icon': 'fa-money', 'tooltip': 'Balance Outstanding'},
        {'title': 'Total Ordered Items', 'value': total_ordered_items, 'color': 'danger', 'icon': 'fa-shopping-basket', 'tooltip': 'Total Ordered Items'},
        {'title': 'Total Spoilage', 'value': total_spoilage, 'color': 'info', 'icon': 'fa-trash', 'tooltip': 'Total Spoilage Items'},
    ]

    # Spoilage Trends
    daily_spoilage = list(
        Spoilage.objects.filter(status='Approved', confirmed_by=request.user)
        .annotate(day=TruncDay('spoilage_date'))
        .values('day')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('day')
    )

    weekly_spoilage = list(
        Spoilage.objects.filter(status='Approved', confirmed_by=request.user)
        .annotate(week=TruncWeek('spoilage_date'))
        .values('week')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('week')
    )

    monthly_spoilage = list(
        Spoilage.objects.filter(status='Approved', confirmed_by=request.user)
        .annotate(month=TruncMonth('spoilage_date'))
        .values('month')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('month')
    )

    def get_trends():
        daily_harvest = Harvest.objects.filter(created_by=request.user).annotate(day=TruncDay('date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_harvest = Harvest.objects.filter(created_by=request.user).annotate(week=TruncWeek('date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_harvest = Harvest.objects.filter(created_by=request.user).annotate(month=TruncMonth('date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        daily_stock = HarvestStockAggregate.objects.filter(created_by=request.user).annotate(day=TruncDay('created_at')) \
            .values('day').annotate(total_qty=Sum('total_quantity')).order_by('day')
        weekly_stock = HarvestStockAggregate.objects.filter(created_by=request.user).annotate(week=TruncWeek('created_at')) \
            .values('week').annotate(total_qty=Sum('total_quantity')).order_by('week')
        monthly_stock = HarvestStockAggregate.objects.filter(created_by=request.user).annotate(month=TruncMonth('created_at')) \
            .values('month').annotate(total_qty=Sum('total_quantity')).order_by('month')

        daily_move = HarvestMovement.objects.filter(created_by=request.user).annotate(day=TruncDay('movement_date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_move = HarvestMovement.objects.filter(created_by=request.user).annotate(week=TruncWeek('movement_date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_move = HarvestMovement.objects.filter(created_by=request.user).annotate(month=TruncMonth('movement_date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        return {
            'daily_harvest': list(daily_harvest),
            'weekly_harvest': list(weekly_harvest),
            'monthly_harvest': list(monthly_harvest),

            'daily_stock': list(daily_stock),
            'weekly_stock': list(weekly_stock),
            'monthly_stock': list(monthly_stock),

            'daily_move': list(daily_move),
            'weekly_move': list(weekly_move),
            'monthly_move': list(monthly_move),
        }

    context = {
        'saleagent': saleagent,
        'todos': todos,
        'todo_form': todo_form,

        'orders': Order.objects.filter(sales_agent=saleagent).select_related('buyer', 'sales_agent'),
        'order_items': OrderItem.objects.filter(order__sales_agent=saleagent).select_related('harveststock', 'order'),
        'payments': Payment.objects.filter(created_by=request.user),
        'balances': Balance.objects.filter(order__sales_agent=saleagent).select_related('order__buyer'),

        'daily_spoilage': daily_spoilage,
        'weekly_spoilage': weekly_spoilage,
        'monthly_spoilage': monthly_spoilage,

        'harvest_by_crop': harvest_by_crop,
        'stock_by_centre': stock_by_centre,
        'movement_summary': movement_summary,
        'order_status_summary': order_status_summary,
        'payment_status_summary': payment_status_summary,
        'paid_orders': paid_orders,
        'outstanding_balances': outstanding_balances,
        'unpaid_orders': unpaid_orders,

        'dashboard_cards': dashboard_cards,

        'total_cash_sales': total_sales,
        'total_quantity': total_stock,
        'total_value': stock_summary.get('total_value') or 0,
        'total_volume_purchased': order_summary.get('total_amount') or 0,
        'total_orders': order_summary.get('total_orders') or 0,
        'total_paid': payment_summary.get('total_paid') or 0,
        'total_due': balance_summary.get('total_due') or 0,
        'amount_paid': balance_summary.get('amount_paid') or 0,

        'total_volume_delivered': 0,
        'accumulated_farminput_total_cost': 0,
        'accumulated_farminput_total_cost_distributed_edo': 0,
        'total_sum': total_sales,
    }

    context.update(get_trends())

    return render(request, 'admin/sales/dashboard.html', context)


########### SALES HEAD DASHBOARD
@login_required
def mainsale_dashboard(request):
    saleagent = SaleAgent.objects.get(user=request.user)
    today = now().date()

    # ========================== TODOs =============================
    todos = Todo.objects.filter(created_by=request.user)
    for todo in todos:
        todo.days_left = (todo.expected_date - now()).days if todo.expected_date else None
    todo_form = TodoForm()

    # =================== Aggregated Dashboard Metrics ===================
    confirmed_harvests = Harvest.objects.filter(confirmation='Confirmed')
    harvest_summary = confirmed_harvests.aggregate(
        total_quantity=Sum('quantity'),
        total_price=Sum('total_price')
    )

    stock_summary = HarvestStockAggregate.objects.aggregate(
        total_quantity=Sum('total_quantity'),
        total_value=Sum('total_value')
    )

    stock_movement_summary = HarvestMovement.objects.aggregate(
        total_quantity=Sum('quantity'),
        total_value=Sum('grade')
    )
   
    order_summary = Order.objects.aggregate(
        total_amount=Sum('total_amount'),
        total_orders=Count('id')
    )
    
    order_summary_item = Order.objects.aggregate(
        total_items=Sum('total_items'),
        total_orders=Count('id')
    )
    
    spoilage_summary = Spoilage.objects.aggregate(
        total_spoilage_items=Sum('quantity_spoiled'),
        total_spoilages=Count('id')
    )

    payment_summary = Payment.objects.aggregate(total_paid=Sum('amount_paid'))
    balance_summary = Balance.objects.aggregate(
        total_due=Sum('total_due'),
        amount_paid=Sum('amount_paid')
    )

    # =================== Chart Data (Serialized) ===================
    harvest_by_crop = list(confirmed_harvests
        .values('greenhouse__name', 'greenhouse_room__room_name','crop__name','cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    stock_by_centre = list(HarvestStockAggregate.objects
        .values('market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('total_quantity'))
    )

    movement_summary = list(HarvestMovement.objects
        .values('from_market_centre__name', 'to_market_centre__name', 'crop__name', 'cropvariety__name')
        .annotate(total_qty=Sum('quantity'))
    )

    order_status_summary = list(Order.objects
        .values('status')
        .annotate(count=Count('id'))
    )

    payment_status_summary = list(Payment.objects
        .values('payment_status')
        .annotate(count=Count('id'))
    )

    paid_orders = Balance.objects.select_related('order__buyer') \
        .filter(total_due__gt=0).order_by('-total_due')
    
    outstanding_balances = Balance.objects.select_related('order__buyer').filter(
        Q(order__is_paid=False) |
        Q(total_due__gt=0) |
        Q(amount_paid__lt=F('total_due'))
    ).order_by('-total_due')

   
    unpaid_orders = Order.objects.select_related('buyer', 'sales_agent', 'balance').filter(
        Q(is_paid=False) |
        Q(balance__total_due__gt=0) |
        Q(balance__amount_paid__lt=F('balance__total_due'))
    ).order_by('-total_amount')

    
    total_sales = harvest_summary.get('total_price') or 0
    total_stock = stock_summary.get('total_quantity') or 0
    total_stock_movement = stock_movement_summary.get('total_quantity') or 0
    bal_outstanding = balance_summary.get('total_due') or 0
    total_ordered_items = order_summary_item.get('total_items') or 0
    total_spoilage = spoilage_summary.get('quantity_spoiled') or 0
    
    dashboard_cards = [
        {'title': 'Total Sales', 'value': total_sales, 'color': 'primary', 'icon': 'fa-money', 'tooltip': 'Total cash sales'},
        {'title': 'Available Stock', 'value': total_stock, 'color': 'success', 'icon': 'fa-balance-scale', 'tooltip': 'Total stock'},
        {'title': 'Stock Moved', 'value': total_stock_movement, 'color': 'secondary', 'icon': 'fa-refresh', 'tooltip': 'Stocks Moved'},
        {'title': 'Bal Outstanding', 'value': bal_outstanding, 'color': 'warning', 'icon': 'fa-money', 'tooltip': 'Stocks Moved'},
        {'title': 'Total Ordered Items', 'value': total_ordered_items, 'color': 'danger', 'icon': 'fa-shopping-basket', 'tooltip': 'Total Ordered Items'},
        {'title': 'Total Spoilage', 'value': total_spoilage, 'color': 'info', 'icon': 'fa-shopping-basket', 'tooltip': 'Total Spoilage Items'},
        # Add more as needed
    ]
    
    #spoilage Trends
    # Spoilage Trend Aggregations
    daily_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(day=TruncDay('spoilage_date'))
        .values('day')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('day')
    )

    weekly_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(week=TruncWeek('spoilage_date'))
        .values('week')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('week')
    )

    monthly_spoilage = list(
        Spoilage.objects.filter(status='Approved')
        .annotate(month=TruncMonth('spoilage_date'))
        .values('month')
        .annotate(total_qty=Sum('quantity_spoiled'))
        .order_by('month')
    )

    #Harvest vs HarvestStockAggregate
    #HarvestStockAggregate vs HarvestMovement
    # Daily, Weekly, Monthly trends
    def get_trends():
        # 1. Harvest Trends
        daily_harvest = Harvest.objects.annotate(day=TruncDay('date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_harvest = Harvest.objects.annotate(week=TruncWeek('date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_harvest = Harvest.objects.annotate(month=TruncMonth('date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        # 2. Stock Trends
        daily_stock = HarvestStockAggregate.objects.annotate(day=TruncDay('created_at')) \
            .values('day').annotate(total_qty=Sum('total_quantity')).order_by('day')
        weekly_stock = HarvestStockAggregate.objects.annotate(week=TruncWeek('created_at')) \
            .values('week').annotate(total_qty=Sum('total_quantity')).order_by('week')
        monthly_stock = HarvestStockAggregate.objects.annotate(month=TruncMonth('created_at')) \
            .values('month').annotate(total_qty=Sum('total_quantity')).order_by('month')

        # 3. Movement Trends
        daily_move = HarvestMovement.objects.annotate(day=TruncDay('movement_date')) \
            .values('day').annotate(total_qty=Sum('quantity')).order_by('day')
        weekly_move = HarvestMovement.objects.annotate(week=TruncWeek('movement_date')) \
            .values('week').annotate(total_qty=Sum('quantity')).order_by('week')
        monthly_move = HarvestMovement.objects.annotate(month=TruncMonth('movement_date')) \
            .values('month').annotate(total_qty=Sum('quantity')).order_by('month')

        return {
            'daily_harvest': list(daily_harvest),
            'weekly_harvest': list(weekly_harvest),
            'monthly_harvest': list(monthly_harvest),

            'daily_stock': list(daily_stock),
            'weekly_stock': list(weekly_stock),
            'monthly_stock': list(monthly_stock),

            'daily_move': list(daily_move),
            'weekly_move': list(weekly_move),
            'monthly_move': list(monthly_move),
        }
    
    # =================== Context ===================
    context = {
        'saleagent': saleagent,
        'todos': todos,
        'todo_form': todo_form,

        # QuerySets for tables
        'orders': Order.objects.select_related('buyer', 'sales_agent'),
        'order_items': OrderItem.objects.select_related('harveststock', 'order'),
        'payments': Payment.objects.all(),
        'balances': Balance.objects.select_related('order__buyer'),

        #spoilage Trends
        'daily_spoilage': daily_spoilage,
        'weekly_spoilage': weekly_spoilage,
        'monthly_spoilage': monthly_spoilage,
    
        # JSON-serializable chart data
        'harvest_by_crop': harvest_by_crop,
        'stock_by_centre': stock_by_centre,
        'movement_summary': movement_summary,
        'order_status_summary': order_status_summary,
        'payment_status_summary': payment_status_summary,
        'paid_orders':paid_orders,
        'outstanding_balances': outstanding_balances,
        'unpaid_orders':unpaid_orders,
        
        'dashboard_cards': dashboard_cards,

        # Metrics for cards
        'total_cash_sales': harvest_summary.get('total_price') or 0,
        'total_quantity': stock_summary.get('total_quantity') or 0,
        'total_value': stock_summary.get('total_value') or 0,
        'total_volume_purchased': order_summary.get('total_amount') or 0,
        'total_orders': order_summary.get('total_orders') or 0,
        'total_paid': payment_summary.get('total_paid') or 0,
        'total_due': balance_summary.get('total_due') or 0,
        'amount_paid': balance_summary.get('amount_paid') or 0,

        # Add these if used in template
        'total_volume_delivered': 0,  # Replace with actual value if needed
        'accumulated_farminput_total_cost': 0,  # Replace with real computation
        'accumulated_farminput_total_cost_distributed_edo': 0,  # Replace if needed
        'total_sum': harvest_summary.get('total_price') or 0,  # Same as cash sales
    }

    context.update(get_trends())

    return render(request, 'admin/sales/maindashboard.html', context)


@login_required
def buyer_dashboard(request):
    if request.user.is_authenticated:
        try:
            buyer = Buyer.objects.get(user=request.user)
            orders = Order.objects.filter(buyer=buyer)
        except Buyer.DoesNotExist:
            buyer = None
            orders = None

    form = TodoForm()
    #passing the todo form
    # Todos
    todos = Todo.objects.filter(created_by=request.user)
    return render(request, 'admin/buyer/dashboard.html', {
        'buyer': buyer,
        'orders': orders,
        'form':form,
        'todos':todos
    })
class CustomLogoutView(LogoutView):
    next_page = 'user_login'  # Set your default next page

    def dispatch(self, request, *args, **kwargs):
        # Call the parent class's dispatch method to perform the logout
        response = super().dispatch(request, *args, **kwargs)
        
        # Add a success message after the user logs out
        messages.success(request, "You have successfully logged out.")
        
        # Redirect to the next page specified
        messages.get_messages(request)  # This clears messages before rendering the login page
        return redirect(self.get_next_page())

    def get_next_page(self):
        messages.get_messages(self)  # This clears messages before rendering the login page
        return self.next_page  # Return the next page from the attribute


