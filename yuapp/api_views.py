from rest_framework.decorators import api_view, permission_classes
from django.db.models import Case, When, IntegerField
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .serializers import *
from fieldmate.forms import HarvestForm
# from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Beneficiary, CashAssigned, Repayment, Supervisor, AIC, Transaction, Payment, Delivery, Buyer
# from .serializers import BeneficiarySerializer, CashAssignedSerializer, RepaymentSerializer


# User Login API
# @csrf_exempt
@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        if user.groups.filter(name='EDO').exists():
            return Response({'detail': 'Supervisor login successful', 'redirect': 'supervisor_dashboard'}, status=status.HTTP_200_OK)
        elif user.groups.filter(name='Beneficiary').exists():
            return Response({'detail': 'Beneficiary login successful', 'redirect': 'beneficiary_dashboard'}, status=status.HTTP_200_OK)
        elif user.groups.filter(name='AIC').exists():
            return Response({'detail': 'AIC login successful', 'redirect': 'aic_dashboard'}, status=status.HTTP_200_OK)
        elif user.groups.filter(name='Buyer').exists():
            return Response({'detail': 'Buyer login successful', 'redirect': 'buyer_dashboard'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Account type is not recognized.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)


# Supervisor Dashboard API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supervisor_dashboard(request):
    try:
        supervisor = Supervisor.objects.get(user=request.user)
        serializer = SupervisorSerializer(supervisor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Supervisor.DoesNotExist:
        return Response({'error': 'Supervisor not found'}, status=status.HTTP_404_NOT_FOUND)

# Beneficiary Dashboard API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def beneficiary_dashboard(request):
    try:
        beneficiary = Beneficiary.objects.get(user=request.user)
        cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
        repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)
        
        beneficiary_serializer = BeneficiarySerializer(beneficiary)
        cash_assigned_serializer = CashAssignedSerializer(cash_assigned_list, many=True)
        repayment_serializer = RepaymentSerializer(repayments, many=True)
        
        return Response({
            'beneficiary': beneficiary_serializer.data,
            'cash_assigned_list': cash_assigned_serializer.data,
            'repayments': repayment_serializer.data,
        }, status=status.HTTP_200_OK)
    except Beneficiary.DoesNotExist:
        return Response({'error': 'Beneficiary not found'}, status=status.HTTP_404_NOT_FOUND)

        
        
        
# AIC Dashboard API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def aic_dashboard(request):
    user_aic = AIC.objects.filter(created_by=request.user)
    
    total_volume_purchased = Transaction.objects.filter(aic__in=user_aic).aggregate(total_volume=Sum('volume'))['total_volume']
    total_payments = Payment.objects.filter(transaction__aic__in=user_aic).aggregate(total_paid=Sum('amount_paid'))['total_paid']
    total_volume_delivered = Delivery.objects.filter(transaction__aic__in=user_aic).aggregate(total_delivered=Sum('volume_delivered'))['total_delivered']
    
    return Response({
        'total_volume_purchased': total_volume_purchased,
        'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
    }, status=status.HTTP_200_OK)

# Buyer Dashboard API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_dashboard(request):
    try:
        buyer = Buyer.objects.get(user=request.user)
        beneficiary = Beneficiary.objects.all()
        
        cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
        repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)
        
        buyer_serializer = BuyerSerializer(buyer)
        cash_assigned_serializer = CashAssignedSerializer(cash_assigned_list, many=True)
        repayment_serializer = RepaymentSerializer(repayments, many=True)
        
        return Response({
            'buyer': buyer_serializer.data,
            'cash_assigned_list': cash_assigned_serializer.data,
            'repayments': repayment_serializer.data,
        }, status=status.HTTP_200_OK)
    except Buyer.DoesNotExist:
        return Response({'error': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)

# Custom Logout API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_logout(request):
    logout(request)
    return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def trend_knowledge_index(request):
    if request.method == 'GET':
        trends = TrendKnowledgeBank.objects.filter(created_by=request.user.id)
        serializer = TrendKnowledgeBankSerializer(trends, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TrendKnowledgeBankSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trend_knowledge_board(request):
    trs = TrendKnowledgeBank.objects.all()
    serializer = TrendKnowledgeBankSerializer(trs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_trend_knowledge(request):
    if not request.user.groups.filter(name='Beneficiary').exists():
        return Response({'error': 'You do not have permission to create a Trend Knowledge Topic.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = TrendKnowledgeBankSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def discussion_trend_knowledge(request, pk):
    trend_knowledge_bank = get_object_or_404(TrendKnowledgeBank, pk=pk)
    
    if request.method == 'GET':
        discussions = TrendKnowledgeDiscussion.objects.filter(trend_knowledge_bank=trend_knowledge_bank)
        serializer = TrendKnowledgeDiscussionSerializer(discussions, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TrendKnowledgeDiscussionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(trend_knowledge_bank=trend_knowledge_bank, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trend_knowledge_bank_detail(request, pk):
    trend_knowledge_bank = get_object_or_404(TrendKnowledgeBank, pk=pk)
    discussions = TrendKnowledgeDiscussion.objects.filter(trend_knowledge_bank=trend_knowledge_bank).order_by('-created_at')
    discussion_serializer = TrendKnowledgeDiscussionSerializer(discussions, many=True)
    return Response({
        'trend_knowledge_bank': trend_knowledge_bank,
        'discussions': discussion_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crop_index(request):
    beneficiary = request.user.beneficiary
    assigned_crops = beneficiary.crops.all()
    all_crops = Crop.objects.all().annotate(
        is_assigned=Case(
            When(id__in=assigned_crops.values_list('id', flat=True), then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('is_assigned')

    serializer = CropSerializer(all_crops, many=True)
    return Response({'all_crops': serializer.data, 'assigned_crops': assigned_crops})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tunnel_index(request):
    beneficiary = request.user.beneficiary
    assigned_tunels = beneficiary.assigned_tunnel

    all_tunels = GreenhouseRoom.objects.all().order_by(
        Case(
            When(id=assigned_tunels.id, then=0),
            default=1,
            output_field=IntegerField(),
        )
    )

    serializer = GreenhouseRoomSerializer(all_tunels, many=True)
    return Response({'all_tunels': serializer.data, 'assigned_tunel': assigned_tunels})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def changingroom_index(request):
    beneficiary = request.user.beneficiary
    assigned_changing_rooms = ChangingRoomAssign.objects.filter(beneficiary=beneficiary)

    serializer = ChangingRoomAssignSerializer(assigned_changing_rooms, many=True)
    return Response({'assigned_changing_rooms': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def changingroom_detail(request, pk):
    changeroom = get_object_or_404(ChangingRoom, pk=pk)
    assigned_beneficiaries = ChangingRoomAssign.objects.filter(changing_room=changeroom)
    serializer = ChangingRoomAssignSerializer(assigned_beneficiaries, many=True)

    return Response({
        'changeroom': changeroom,
        'assigned_beneficiaries': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_index(request):
    buyers = Buyer.objects.all()
    serializer = BuyerSerializer(buyers, many=True)
    return Response({'buyers': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_detail(request, pk):
    buyer = get_object_or_404(Buyer, pk=pk)
    serializer = BuyerSerializer(buyer)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_index(request):
    beneficiary = Beneficiary.objects.get(user=request.user)
    cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
    repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

    cash_assigned_serializer = CashAssignedSerializer(cash_assigned_list, many=True)
    repayments_serializer = RepaymentSerializer(repayments, many=True)

    return Response({
        'cash_assigned_list': cash_assigned_serializer.data,
        'repayments': repayments_serializer.data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_cash(request):
    serializer = CashRequestSerializer(data=request.data)
    if serializer.is_valid():
        cash_assigned = serializer.save(beneficiary=request.user.beneficiary, status='Pending')
        return Response(CashRequestSerializer(cash_assigned).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_repayment(request, cash_assigned_id):
    beneficiary = get_object_or_404(Beneficiary, user=request.user)
    cash_assigned = get_object_or_404(CashAssigned, id=cash_assigned_id, beneficiary=beneficiary)

    serializer = RepaymentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(beneficiary=beneficiary, cash_assigned=cash_assigned)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_payment_history(request):
    beneficiary = Beneficiary.objects.get(user=request.user)
    cash_assigned_list = CashAssigned.objects.filter(beneficiary=beneficiary)
    repayments = Repayment.objects.filter(cash_assigned__beneficiary=beneficiary)

    cash_assigned_serializer = CashAssignedSerializer(cash_assigned_list, many=True)
    repayments_serializer = RepaymentSerializer(repayments, many=True)

    return Response({
        'cash_assigned_list': cash_assigned_serializer.data,
        'repayments': repayments_serializer.data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def harvest_index(request):
    beneficiary = request.user.beneficiary
    assigned_crops = beneficiary.crops.all()

    all_crops = Crop.objects.annotate(
        is_assigned=Case(
            When(id__in=assigned_crops.values_list('id', flat=True), then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('is_assigned')

    return Response({
        'beneficiary': beneficiary,
        'assigned_crops': assigned_crops,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assigned_crops_and_harvests(request, beneficiary_id, crop_id):
    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_id)
    crop = get_object_or_404(Crop, pk=crop_id)

    assigned_crops = beneficiary.crops.all()
    harvest_records = Harvest.objects.filter(beneficiary_id=beneficiary_id, crop_id=crop_id)

    serializer = HarvestSerializer(harvest_records, many=True)
    return Response({
        'beneficiary': beneficiary,
        'assigned_crops': assigned_crops,
        'harvest_records': serializer.data,
        'selected_crop': crop,
    })

@api_view(['POST'])
def create_harvest(request, crop_assigned_id):
    if request.user.is_authenticated:
        beneficiary = request.user.beneficiary
        crop = get_object_or_404(Crop, id=crop_assigned_id)
        form = HarvestForm(request.data, crop=crop, beneficiary=beneficiary)

        if form.is_valid():
            form.save()
            return Response({'status': 'success', 'message': 'Harvest created successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'error', 'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'error', 'message': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def sales_dashboard(request):
    beneficiary = Beneficiary.objects.get(user=request.user)
    total_volume_purchased = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE).aggregate(total_volume=Sum('volume'))['total_volume']
    total_payments = Payment.objects.aggregate(total_paid=Sum('amount_paid'))['total_paid']
    total_volume_delivered = Delivery.objects.aggregate(total_delivered=Sum('volume_delivered'))['total_delivered']
    total_due_per_buyer = Transaction.objects.filter(buyer__isnull=False).annotate(
        total_due=F('total_price') - Sum('payment__amount_paid')
    ).values('buyer__client_name', 'total_due')
    total_cash_sales = Transaction.objects.filter(transaction_type=Transaction.CROP_PURCHASE, buyer__isnull=False).aggregate(total_cash=Sum('total_price'))['total_cash']

    data = {
        'beneficiary':beneficiary,
        'total_volume_purchased': total_volume_purchased,
        'total_payments': total_payments,
        'total_volume_delivered': total_volume_delivered,
        'total_due_per_buyer': list(total_due_per_buyer),
        'total_cash_sales': total_cash_sales,
    }

    return Response(data)

@api_view(['GET'])
def edo(request):
    if request.user.is_authenticated:
        beneficiary = Beneficiary.objects.get(user=request.user)
        supervisor = beneficiary.assigned_edo
        return Response({'edo': supervisor.name if supervisor else None})

    return Response({'status': 'error', 'message': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def edo_detail(request, edo_id):
    if request.user.is_authenticated:
        edo = get_object_or_404(Supervisor, id=edo_id)
        beneficiary = Beneficiary.objects.filter(user=request.user).first()
        supervisor_greenhouses = edo.greenhouse.all()
        beneficiary_greenhouses = beneficiary.crops.all() if beneficiary else None
        supervisor_cities = edo.city.all()

        data = {
            'beneficiary': beneficiary.name if beneficiary else None,
            'edo': edo.name,
            'supervisor_greenhouses': [gh.name for gh in supervisor_greenhouses],
            'beneficiary_greenhouses': [gh.name for gh in beneficiary_greenhouses] if beneficiary_greenhouses else [],
            'supervisor_cities': [city.name for city in supervisor_cities],
        }

        return Response(data)

    return Response({'status': 'error', 'message': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
