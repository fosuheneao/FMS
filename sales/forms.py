from django import forms
from django.db.models import Q, Sum  # Import Q for complex queries
# from aic import models
from yuapp.models import Buyer, City, CropVariety, HarvestMovement, HarvestStockAggregate, Order, OrderItem, Payment, PaymentMethod, PriceTable, SaleAgent, MarketingCentre, Spoilage # Import timezone to get the current date
from .forms import *
from django.core.exceptions import ValidationError
from django.utils import timezone



class SaleAgentForm(forms.ModelForm):
    # Gender choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    class Meta:
        model = SaleAgent
        fields = [                    
            'fullname', 'gender', 'age', 'email', 'phone_number', 
            'photo', 'nationalId', 'cardphoto', 'description', 'city'
        ]
    
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Age'}),
            'email': forms.EmailInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Phone Number'}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Passport Picture'}),
            'nationalId': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card No.'}),
            'cardphoto': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card Picture'}),
            'description': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
        }
    
    # Corrected gender field
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect  # Bootstrap class for radio buttons
    )
    
    # Filter only unassigned city
    city = forms.ModelMultipleChoiceField(
        queryset=City.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Greenhouse'}),
    )

    marketcentre = forms.ModelMultipleChoiceField(
        queryset=MarketingCentre.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Market Centre'}),
    )


# ##################################### END OF ORDER AND ORDER ITEMS ###########################################

#<<<<<<<<<<<<<<<<<<< OPERATIONAL COST SERVICE REQUEST ===============>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class OrderForm(forms.ModelForm):
    buyer = forms.ModelChoiceField(
        queryset=Buyer.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Buyer",
        required=True,
        help_text="Reference every order to a buyer."
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            try:
                saleagent = SaleAgent.objects.get(user=user)
                marketing_centre = saleagent.marketingcentre

                # Filter buyers who share this marketing centre
                self.fields['buyer'].queryset = Buyer.objects.filter(
                    market_center=marketing_centre
                ).distinct()

            except SaleAgent.DoesNotExist:
                self.fields['buyer'].queryset = Buyer.objects.none()
                
    class Meta:
        model = Order
        fields = ['buyer', 'notes', 'sale_order_type']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
            'sale_order_type': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Sale Order Type'
            }),
        }
    
    def save(self, commit=True, user=None):
        self.user = user
        instance = super().save(commit=False)

        if user:
            try:
                saleagent = SaleAgent.objects.get(user=user)
                instance.saleagent = saleagent
                instance.created_by = user
            except SaleAgent.DoesNotExist:
                pass

        if commit:
            instance.save()

        return instance
    
    
#Order item
class OrderItemForm(forms.ModelForm):
    harveststock = forms.ModelChoiceField(
        queryset=HarvestStockAggregate.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Order Item",
        required=True,
        help_text="Select from the list of available items with stock."
    )

    quantity = forms.DecimalField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Quantity'
        }),
        label="Quantity Requested"
    )

    class Meta:
        model = OrderItem
        fields = ['harveststock', 'quantity', 'unit_price', 'notes']
        widgets = {
            'unit_price': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'readonly': 'readonly'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Optional notes or description',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            try:
                saleagent = SaleAgent.objects.get(user=user)
                agent_marketcentre = saleagent.marketingcentre

                self.fields['harveststock'].queryset = HarvestStockAggregate.objects.filter(
                    market_centre=agent_marketcentre,
                    total_quantity__gt=0
                ).distinct()

                self.fields['harveststock'].label_from_instance = lambda obj: (
                    f"{obj.crop.name} - {obj.cropvariety.name if obj.cropvariety else 'N/A'} - "
                    f"{obj.grade.name} - {obj.unit.name if obj.unit else 'N/A'} - "
                    f"Qty: {obj.total_quantity}"
                )
            except SaleAgent.DoesNotExist:
                self.fields['harveststock'].queryset = HarvestStockAggregate.objects.none()
                self.fields['harveststock'].help_text = "No assigned marketing centre. Contact admin."

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        harveststock = self.cleaned_data.get('harveststock')
        if harveststock and quantity > harveststock.total_quantity:
            raise ValidationError(f"Only {harveststock.total_quantity} units available in stock.")
        return quantity

    def save(self, commit=True, user=None):
        orderitem = super().save(commit=False)

        if self.cleaned_data.get('harveststock'):
            orderitem.unit_price = orderitem.harveststock.unit_price.selling_price if orderitem.harveststock.unit_price else 0

        if user:
            orderitem.created_by = user

        if commit:
            orderitem.save()
            if orderitem.order:
                orderitem.order.update_totals()

        return orderitem


# from django import forms
# from django.core.exceptions import ValidationError
# from .models import Payment

# class OrderPaymentForm(forms.ModelForm):
#     # These fields must be declared if you want to use them in validation
#     payment_method_mobile = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Mobile Provider'})
#     )
#     payment_method_bank = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Bank Name'})
#     )

#     class Meta:
#         model = Payment
#         fields = ['order','amount_paid', 'payment_method','reference_number', 'transaction_code', 'payin_slip', 'notes']
#         widgets = {
#             'amount_paid': forms.NumberInput(attrs={'class': 'form-control-sm'}),
#             'payment_method': forms.Select(attrs={'class': 'form-control-sm', 'id': 'id_payment_method'}),
#             'reference_number': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_reference_number'}),
#             'transaction_code': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_transaction_code'}),
#             'payin_slip': forms.ClearableFileInput(attrs={'class': 'form-control-sm'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control-sm', 'rows': 2}),
#         }

#     def __init__(self, *args, **kwargs):
#         #self.worker = kwargs.pop('worker', None)  # Expect worker instance
#         self.order = kwargs.pop('order', None)  # Expect beneficiary instance
#         self.created_by = kwargs.pop('created_by', None)  # Expect created_by instance or user
#         super(OrderPaymentForm, self).__init__(*args, **kwargs)
        
#     def clean(self):
#         cleaned_data = super().clean()
#         method = cleaned_data.get("payment_method")

#         if method == PaymentMethod.MOBILE_MONEY and not cleaned_data.get("payment_method_mobile"):
#             self.add_error("payment_method_mobile", "Mobile provider required.")

#         if method == PaymentMethod.BANK_TRANSFER and not cleaned_data.get("payment_method_bank"):
#             self.add_error("payment_method_bank", "Bank provider required.")
            
#         method = cleaned_data.get('payment_method')
#         ref = cleaned_data.get('reference_number')
#         code = cleaned_data.get('transaction_code')

#         if method == 'Mobile Money':
#             mobile = cleaned_data.get('payment_method_mobile')
#             if not mobile:
#                 self.add_error('payment_method_mobile', "Mobile Payment Provider is required.")
#             if not ref or len(str(ref)) != 10 or not str(ref).isdigit():
#                 self.add_error('reference_number', "Mobile reference number must be exactly 10 digits.")
#             if not code:
#                 self.add_error('transaction_code', "Transaction code is required.")

#         elif method == 'Bank Transfer':
#             bank = cleaned_data.get('payment_method_bank')
#             if not bank:
#                 self.add_error('payment_method_bank', "Bank is required.")
#             if not ref or len(str(ref)) > 14 or not str(ref).isdigit():
#                 self.add_error('reference_number', "Bank reference number must be up to 14 digits.")
#             if not code:
#                 self.add_error('transaction_code', "Transaction code is required.")

#         elif method == 'Cash':
#             cleaned_data['payment_method_mobile'] = ''
#             cleaned_data['payment_method_bank'] = ''
#             cleaned_data['reference_number'] = ''
#             cleaned_data['transaction_code'] = ''

#         return cleaned_data
    
#     def save(self, commit=True):
#         orderPayment = super().save(commit=False)

#         orderPayment.order = self.order 
#         orderPayment.created_by = self.created_by 
#         orderPayment.mobile_provider = self.cleaned_data.get('payment_method_mobile', '')
#         orderPayment.bank_provider = self.cleaned_data.get('payment_method_bank', '')

#         if commit:
#             orderPayment.full_clean()  # Validate before saving
#             orderPayment.save()

#         return orderPayment

# class OrderPaymentForm(forms.ModelForm):
#     payment_method_mobile = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Mobile Provider'})
#     )
#     payment_method_bank = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Bank Name'})
#     )

#     class Meta:
#         model = Payment
#         fields = ['amount_paid', 'payment_method', 'reference_number',
#                   'transaction_code', 'payin_slip', 'notes']
#         widgets = {
#             'amount_paid': forms.NumberInput(attrs={'class': 'form-control-sm'}),
#             'payment_method': forms.Select(attrs={'class': 'form-control-sm', 'id': 'id_payment_method'}),
#             'reference_number': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_reference_number'}),
#             'transaction_code': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_transaction_code'}),
#             'payin_slip': forms.ClearableFileInput(attrs={'class': 'form-control-sm'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control-sm', 'rows': 2}),
#         }

#     def __init__(self, *args, **kwargs):
#         self.order = kwargs.pop('order', None)
#         self.created_by = kwargs.pop('created_by', None)
#         super().__init__(*args, **kwargs)

#     def clean(self):
#         cleaned_data = super().clean()
#         method = cleaned_data.get("payment_method")

#         # Standardized logic based on enum or choices
#         if method == PaymentMethod.MOBILE_MONEY:
#             mobile = cleaned_data.get("payment_method_mobile")
#             if not mobile:
#                 self.add_error("payment_method_mobile", "Mobile provider is required.")
#             ref = cleaned_data.get("reference_number")
#             code = cleaned_data.get("transaction_code")
#             if not ref or not ref.isdigit() or len(ref) != 10:
#                 self.add_error("reference_number", "Mobile reference number must be exactly 10 digits.")
#             if not code:
#                 self.add_error("transaction_code", "Transaction code is required.")

#         elif method == PaymentMethod.BANK_TRANSFER:
#             bank = cleaned_data.get("payment_method_bank")
#             if not bank:
#                 self.add_error("payment_method_bank", "Bank provider is required.")
#             ref = cleaned_data.get("reference_number")
#             code = cleaned_data.get("transaction_code")
#             if not ref or not ref.isdigit() or len(ref) > 14:
#                 self.add_error("reference_number", "Bank reference number must be up to 14 digits.")
#             if not code:
#                 self.add_error("transaction_code", "Transaction code is required.")

#         elif method == PaymentMethod.CASH:
#             # Clear unnecessary fields
#             cleaned_data["payment_method_mobile"] = ''
#             cleaned_data["payment_method_bank"] = ''
#             cleaned_data["reference_number"] = ''
#             cleaned_data["transaction_code"] = ''

#         return cleaned_data

#     def save(self, commit=True):
#         payment = super().save(commit=False)
#         payment.order = self.order
#         payment.created_by = self.created_by
#         payment.mobile_provider = self.cleaned_data.get('payment_method_mobile', '')
#         payment.bank_provider = self.cleaned_data.get('payment_method_bank', '')

#         if commit:
#             payment.full_clean()
#             payment.save()
#         return payment



# class OrderPaymentForm(forms.ModelForm):
#     payment_method_mobile = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Mobile Provider'})
#     )
#     payment_method_bank = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control-sm', 'placeholder': 'Bank Name'})
#     )

#     def __init__(self, *args, **kwargs):
#         self.order = kwargs.pop('order', None)
#         self.created_by = kwargs.pop('created_by', None)
#         super(OrderPaymentForm, self).__init__(*args, **kwargs)

#     class Meta:
#         model = Payment
#         fields = ['amount_paid', 'payment_method', 'reference_number',
#                   'transaction_code', 'payin_slip', 'notes']  # Removed 'order' here
#         widgets = {
#             'amount_paid': forms.NumberInput(attrs={'class': 'form-control-sm'}),
#             'payment_method': forms.Select(attrs={'class': 'form-control-sm', 'id': 'id_payment_method'}),
#             'reference_number': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_reference_number'}),
#             'transaction_code': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_transaction_code'}),
#             'payin_slip': forms.ClearableFileInput(attrs={'class': 'form-control-sm'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control-sm', 'rows': 2}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         method = cleaned_data.get("payment_method")

#         if method == PaymentMethod.MOBILE_MONEY:
#             mobile = cleaned_data.get("payment_method_mobile")
#             if not mobile:
#                 self.add_error("payment_method_mobile", "Mobile provider is required.")
#             ref = cleaned_data.get("reference_number")
#             code = cleaned_data.get("transaction_code")
#             if not ref or not ref.isdigit() or len(ref) != 10:
#                 self.add_error("reference_number", "Mobile reference number must be exactly 10 digits.")
#             if not code:
#                 self.add_error("transaction_code", "Transaction code is required.")

#         elif method == PaymentMethod.BANK_TRANSFER:
#             bank = cleaned_data.get("payment_method_bank")
#             if not bank:
#                 self.add_error("payment_method_bank", "Bank provider is required.")
#             ref = cleaned_data.get("reference_number")
#             code = cleaned_data.get("transaction_code")
#             if not ref or not ref.isdigit() or len(ref) > 14:
#                 self.add_error("reference_number", "Bank reference number must be up to 14 digits.")
#             if not code:
#                 self.add_error("transaction_code", "Transaction code is required.")

#         elif method == PaymentMethod.CASH:
#             cleaned_data["payment_method_mobile"] = ''
#             cleaned_data["payment_method_bank"] = ''
#             cleaned_data["reference_number"] = ''
#             cleaned_data["transaction_code"] = ''

#         return cleaned_data

#     def save(self, commit=True):
#         payment = super().save(commit=False)
#         payment.order = self.order
#         payment.created_by = self.created_by
#         payment.mobile_provider = self.cleaned_data.get('payment_method_mobile', '')
#         payment.bank_provider = self.cleaned_data.get('payment_method_bank', '')
#         payment.save()
#         return payment



class OrderPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['order', 'amount_paid', 'payment_method', 'reference_number',
                  'transaction_code', 'payin_slip', 'notes']
        
        widgets = {
             'amount_paid': forms.NumberInput(attrs={'class': 'form-control-sm'}),
             'payment_method': forms.Select(attrs={'class': 'form-control-sm', 'id': 'id_payment_method'}),
             'reference_number': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_reference_number'}),
             'transaction_code': forms.TextInput(attrs={'class': 'form-control-sm', 'id': 'id_transaction_code'}),
             'payin_slip': forms.ClearableFileInput(attrs={'class': 'form-control-sm'}),
             'notes': forms.Textarea(attrs={'class': 'form-control-sm', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.order:
            instance.order = self.order
        if self.created_by:
            instance.created_by = self.created_by
        if commit:
            instance.save()
        return instance



      
class ConfirmSpoilageForm(forms.ModelForm):
    class Meta:
        model = Spoilage
        fields = ['confirmation_note']
        
        widgets = {
            'confirmation_note': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Add notes here', 'rows': 3})
        }
    
    
class HarvestMovementForm(forms.ModelForm):
    class Meta:
        model = HarvestMovement
        fields = ['to_market_centre', 'crop', 'cropvariety', 'grade', 'unit', 'quantity']

        widgets = {
            'to_market_centre': forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Destination Market Centre'}),
            'crop': forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Crop'}),
            'cropvariety': forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Crop Variety'}),
            'grade': forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Grade'}),
            'unit': forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Unit'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Enter Quantity to Transfer'}), 
        }
    
    def __init__(self, *args, **kwargs):
        self.sale_agent = kwargs.pop('sale_agent', None)
        super().__init__(*args, **kwargs)

        if self.sale_agent and self.sale_agent.marketingcentre:
            available_stock = HarvestStockAggregate.objects.filter(
                market_centre=self.sale_agent.marketingcentre
            ).values_list('crop', flat=True).distinct()

            self.fields['crop'].queryset = self.fields['crop'].queryset.filter(id__in=available_stock)

            # Dynamically limit cropvariety choices ONLY if crop is selected (POST case)
            if 'crop' in self.data:
                try:
                    crop_id = int(self.data.get('crop'))
                    self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=crop_id)
                except (ValueError, TypeError):
                    self.fields['cropvariety'].queryset = CropVariety.objects.none()
            else:
                # On GET or initial load — empty queryset or a default
                self.fields['cropvariety'].queryset = CropVariety.objects.none()

            # Exclude current market centre from destination list
            self.fields['to_market_centre'].queryset = MarketingCentre.objects.exclude(id=self.sale_agent.marketingcentre.id)
        
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        crop = cleaned_data.get('crop')
        cropvariety = cleaned_data.get('cropvariety')
        grade = cleaned_data.get('grade')
        unit = cleaned_data.get('unit')

        if self.sale_agent and self.sale_agent.marketingcentre and crop and grade:
            available_stock = HarvestStockAggregate.objects.filter(
                market_centre=self.sale_agent.marketingcentre,
                crop=crop,
                cropvariety = cropvariety,
                grade=grade,
                unit=unit
            ).aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0

            if quantity > available_stock:
                raise forms.ValidationError(f"Insufficient stock: You have {available_stock} available.")
        return cleaned_data