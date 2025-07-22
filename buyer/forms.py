from django import forms
from yuapp.models import Harvest, Order, OrderItem, Payment, Spoilage
# You can also create a formset for multiple OrderItems if needed
from django.forms import inlineformset_factory

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['harvest_record', 'quantity', 'notes']

    # Customize the harvest selection and quantity input
    harvest_record = forms.ModelChoiceField(
        queryset=Harvest.objects.filter(confirmation='Open'),
        label="Select Harvest"
    )
    quantity = forms.IntegerField(min_value=1, label="Quantity Ordered")
    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']
        widgets = {
            'status': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'placeholder': 'Any additional information...'}),
        }
        
 
OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)


# class ConfirmOrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['confirmation_note', 'delivery_date']

#         widgets = {
#             'delivery_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Delivery Date'}),
#             'confirmation_note': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Add notes here', 'rows': 3})
#         }
    
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_date', 'amount_paid', 'payment_method', 'notes', 'payin_slip']

        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'notes': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Add notes here', 'rows': 3})
        }
      
class SpoilageForm(forms.ModelForm):
    class Meta:
        model = Spoilage
        fields = ['orderitem', 'quantity_spoiled', 'photo_evidence', 'notes']
        widgets = {
            'quantity_spoiled': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Quantity Spoiled'}),
            'notes': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Add notes here', 'rows': 3})
        }