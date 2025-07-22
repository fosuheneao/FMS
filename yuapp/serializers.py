from rest_framework import serializers
from .models import (
    Beneficiary, CashAssigned, Repayment, Supervisor, AIC, Transaction, Payment, Delivery, Buyer,
    TrendKnowledgeBank,
    TrendKnowledgeDiscussion,
    CashAssigned,
    Repayment,
    Crop,
    GreenhouseRoom,
    ChangingRoom,
    ChangingRoomAssign,
    Buyer,
    Beneficiary,
    Harvest,
)
class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = '__all__'

class CashAssignedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashAssigned
        fields = '__all__'

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'

class AICSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIC
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'

# Serializer for TrendKnowledgeBank
class TrendKnowledgeBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendKnowledgeBank
        fields = '__all__'  # or specify fields: ['id', 'title', 'created_by', ...]

# Serializer for TrendKnowledgeDiscussion
class TrendKnowledgeDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendKnowledgeDiscussion
        fields = '__all__'  # or specify fields: ['id', 'content', 'trend_knowledge_bank', 'created_by', ...]

# Serializer for CashAssigned
class CashAssignedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashAssigned
        fields = '__all__'  # or specify fields: ['id', 'beneficiary', 'amount', 'status', ...]

# Serializer for Repayment
class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'  # or specify fields: ['id', 'cash_assigned', 'amount', 'date_paid', ...]

# Serializer for Crop
class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'  # or specify fields: ['id', 'name', 'description', ...]

# Serializer for GreenhouseRoom
class GreenhouseRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreenhouseRoom
        fields = '__all__'  # or specify fields: ['id', 'location', 'size', ...]

# Serializer for ChangingRoom
class ChangingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangingRoom
        fields = '__all__'  # or specify fields: ['id', 'location', 'size', ...]

# Serializer for ChangingRoomAssign
class ChangingRoomAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangingRoomAssign
        fields = '__all__'  # or specify fields: ['id', 'beneficiary', 'changing_room', ...]

# Serializer for Buyer
class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'  # or specify fields: ['id', 'name', 'contact_info', ...]

# Serializer for Beneficiary
class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'  # or specify fields: ['id', 'user', 'crops', ...]

# Serializer for Harvest
class HarvestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Harvest
        fields = '__all__'  # or specify fields: ['id', 'beneficiary', 'crop', 'quantity', 'date', confirmation, date,crop,unit,grade,quantity,beneficiary, description ...]


# Serializer for Cash Request
class CashRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashAssigned
        fields = '__all__'  # or specify fields: ['id', 'beneficiary', 'crop', 'quantity', 'date', ...]

