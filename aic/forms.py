from django.core.exceptions import ValidationError
from django import forms
from yuapp.models import BillableItemCost, Buyer, City, Greenhouse,BillableItem, Invoice, FarmSeason, Harvest, Order, OrderItem, PriceTable, Grade, MarketingCentre, SaleAgent, ProductUnit, Crop, MarketingCentre, Beneficiary, GreenhouseRoom, ServiceItem, ServiceRequest, ServiceRequestItem, SprayingData, SprayingMedthod, Supervisor,FarmInput, FarmInputCategory, InputDealer, InputEdoDistribution, Worker  # Import timezone to get the current date
from .forms import *
from django.utils import timezone



class PriceTableForm(forms.ModelForm):
    class Meta:
        model = PriceTable
        fields = ['crop', 'grade', 'unit', 'price', 'selling_price', 'from_date', 'to_date', 'notes', 'market_center']  # Ensure 'unit' is included
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Price'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Selling Price'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Notes', 'rows': 3}),
        }

     # Fields for market_center price
    market_center = forms.ModelChoiceField(
        queryset=MarketingCentre.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Market Center'}),
        empty_label="Select Market Center"
    )

    # Fields for crop and unit
    crop = forms.ModelChoiceField(
        queryset=Crop.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Crop'}),
        empty_label="Select Crop"
    )
    
    # Fields for grade
    grade = forms.ModelChoiceField(
        queryset=Grade.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Grade'}),
        empty_label="Select Grade"
    )
    
    # Fields for unit
    unit = forms.ModelChoiceField(
        queryset=ProductUnit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Measure Unit'}),
        empty_label="Select Measure Unit"
    )

    # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        price_table = super().save(commit=False)

        if user is not None:
            price_table.created_by = user  # Dynamically assign the logged-in user

        if commit:
            price_table.save()

        return price_table
    
# class BeneficiaryForm2(forms.ModelForm):
#     class Meta:
#         model = Beneficiary
#         fields = ['full_name', 'gender', 'enterprise_name', 'age', 'email', 'phone_number', 
#                   'photo', 'nationalId', 'cardphoto', 'description', 'assigned_tunnel','assigned_edo', 
#                   'crops']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }
 
class BeneficiaryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Additional initialization here
        
    # Gender choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    class Meta:
        model = Beneficiary
        fields = [                    
            'full_name', 'gender', 'enterprise_name', 'age', 'email', 'phone_number', 
            'photo', 'nationalId', 'cardphoto', 'description', 'assigned_tunnel','assigned_edo', 'crops'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Full Name'}),
            'enterprise_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Enterprise Name'}),
            #'role': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Role'}),
            'age': forms.NumberInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Age'}),
            'email': forms.EmailInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Phone Number'}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Passport Picture'}),
            'nationalId': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card No.'}),
            'cardphoto': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card Picture'}),
            'description': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
        }
    
    # Filter only unassigned tunnels
    assigned_tunnel = forms.ModelChoiceField(
        queryset=GreenhouseRoom.objects.exclude(beneficiary_tunnel__isnull=False),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Tunnel'}),
        empty_label="Select Tunnel"  # Default label for empty option
    )
    # Corrected gender field
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect  # Bootstrap class for radio buttons
    )
   
    # crops = forms.ModelMultipleChoiceField(
    #         queryset=Crop.objects.all(),
    #         widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Crop'}),
    # )
    
    crops = forms.ModelMultipleChoiceField(
        queryset=Crop.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False  # Set to False if you want to allow no crop selection
    )
     
    assigned_edo = forms.ModelChoiceField(
            queryset=Supervisor.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select EDO'}),
            empty_label="Select EDO"  # Default label for empty option
    )

class InputDealerForm(forms.ModelForm):
    class Meta:
        model = InputDealer
        fields = ['name', 'email', 'address', 'contactperson', 'telephone', 'website', 'notes', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),  # Corrected widget type
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),  # Added missing widget for address
            'contactperson': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),  # Using TextInput for phone numbers
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),  # Corrected placeholder
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),  # Added widget for photo upload
        }
class FarmInputCategoryForm(forms.ModelForm):
    class Meta:
        model = FarmInputCategory
        fields = ['name', 'description',  'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }

class FarmInputForm(forms.ModelForm):
    # Gender choices
    CONFIRMATION_CHOICES = [
        (0, 'Not Confirm'),
        (1, 'Confirm')
    ]
    class Meta:
        model = FarmInput
        fields = ['inputcategory', 'inputdealer', 'description', 'quantity_received', 'cost_per_unit', 'expiry_date', 'photo', 'confirmation']
        widgets = {            
            'inputdealer': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select Input Dealer'}),
            'inputcategory': forms.Select(attrs={'class': 'form-control', 'placeholder':'Select Input Category' }),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Receiving Quantity'}),
            'cost_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Unit Cost'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder':'Expiry Date'}),            
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Description', 'rows':3, 'style': 'width: 100%;'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
     # Corrected gender field
    confirmation = forms.ChoiceField(
        choices=CONFIRMATION_CHOICES,
        widget=forms.RadioSelect  # Bootstrap class for radio buttons
    )

  
class InputEdoDistributionForm(forms.ModelForm):
    class Meta:
        model = InputEdoDistribution
        fields = ['supervisor', 'farm_input', 'quantity']
        widgets = {
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'farm_input': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
        }

    def __init__(self, *args, **kwargs):
        aic = kwargs.pop('aic', None)
        super().__init__(*args, **kwargs)

               
class BuyerForm(forms.ModelForm):
    # Buyer status
    ACTIVE_CHOICES = [
        (0, 'Inactive'),
        (1, 'Active')
    ]
    class Meta:
        model = Buyer
        fields = ['client_name', 'location', 'contact_person', 'phone', 'email', 'photo', 'shipping_address', 'notes', 'active']  # Ensure 'unit' is included
        widgets = {
            'client_name': forms.TextInput(attrs={
                'type': 'text', 
                'class': 'form-control form-control-sm', 
                'placeholder': 'Buyer Name'
            }),
            'location': forms.TextInput(attrs={
                'type': 'text', 
                'class': 'form-control form-control-sm', 
                'placeholder': 'Buyer Location'
            }),
            'contact_person': forms.TextInput(attrs={
                'type': 'text', 
                'class': 'form-control form-control-sm', 
                'placeholder': 'Contact Person'
            }),             
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Mobile Number',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Buyer Email',
            }),
            'shipping_address': forms.TextInput(attrs={
                'type': 'text', 
                'class': 'form-control form-control-sm', 
                'placeholder': 'Shipping Address'
            }), 
             'notes': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Detail', 
                'rows': 3
            }),
        }

     # Corrected gender field
    active = forms.ChoiceField(
        choices=ACTIVE_CHOICES,
        widget=forms.RadioSelect  # Bootstrap class for radio buttons
    )
   
   
class SupervisorForm(forms.ModelForm):
    # Gender choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    class Meta:
        model = Supervisor
        fields = [                    
            'fullname', 'gender', 'age', 'email', 'phone_number', 
            'photo', 'nationalId', 'cardphoto', 'description', 'city','greenhouse'
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

    greenhouse = forms.ModelMultipleChoiceField(
        queryset=Greenhouse.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Greenhouse'}),
    )

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
            'photo', 'nationalId', 'cardphoto', 'description', 'city', 'marketingcentre'
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

    # greenhouse = forms.ModelMultipleChoiceField(
    #     queryset=Greenhouse.objects.all(),
    #     widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Greenhouse'}),
    # )
    
    marketingcentre = forms.ModelMultipleChoiceField(
        queryset=MarketingCentre.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Market Centre'}),
    )
    
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['harvest_record', 'quantity_ordered', 'notes']

    # Customize the harvest selection and quantity input
    harvest_record = forms.ModelChoiceField(
        queryset=Harvest.objects.filter(confirmation='Open'),
        label="Select Harvest"
    )
    quantity_ordered = forms.IntegerField(min_value=1, label="Quantity Ordered")
    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['buyer', 'status', 'notes']
        widgets = {
            'status': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={'placeholder': 'Any additional information...'}),
        }
    
    buyer = forms.ModelChoiceField(
            queryset=Buyer.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Buyer'}),
            empty_label="Select Buyer"  # Default label for empty option
    )
 
OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)


#<<<<<<<<<<<<<<<<<<<<< DYNAMIC BILLING MODULES =======================>>>>>>>>>>>>>>>>
# Forms
class FarmseasonForm(forms.ModelForm):
    class Meta:
        model = FarmSeason
        fields = ['name', 'description', 'season_start_date', 'season_end_date']

        widgets = {
                 'name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Farming Season'}),
                 'season_start_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder':'Effective Date'}),
                 'season_end_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder':'Date Valid To'}),
                 'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
             }
        
         # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        farmseason = super().save(commit=False)

        if user is not None:
            farmseason.created_by = user  # Dynamically assign the logged-in user

        if commit:
            farmseason.save()

        return farmseason
    
class BillableItemForm(forms.ModelForm):
    class Meta:
        model = BillableItem
        fields = ['name', 'farmseason', 'description', 'is_public', 'greenhouse']

        widgets = {
                 'name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Farming Season'}),
                 'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
             }
        
        farmseason = forms.ModelChoiceField(
            queryset=FarmSeason.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
            empty_label="Select Farm Season",  # Updated label
            required=True,  # Make it optional
            help_text="Reference every billable item to a farming season"  # New Help Text
        )


        greenhouse = forms.ModelMultipleChoiceField(
        queryset=Greenhouse.objects.all(),
                widget=forms.CheckboxSelectMultiple(),  # Use checkboxes instead of a dropdown
                required=False,  # Allow empty selection
                help_text="Select applicable greenhouses, or leave empty if applies to all."
        )

        is_public = forms.BooleanField(
            required=False,
            initial=False,  # Ensure it is unchecked by default
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            help_text="Check if this applies to all greenhouse locations or all beneficiaries."
        )
        
        
         # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        billitem = super().save(commit=False)

        if user is not None:
            billitem.created_by = user  # Dynamically assign the logged-in user

        if commit:
            billitem.save()

        return billitem

# class BillableItemForm(forms.ModelForm):
#     class Meta:
#         model = BillableItem
#         fields = '__all__'



class BillableItemCostForm(forms.ModelForm):
    class Meta:
        model = BillableItemCost
        fields = ['billable_item', 'greenhouse', 'cost', 'description']

        widgets = {
                 'cost': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Item Cost'}),
                 'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
             }
        
        billable_item = forms.ModelChoiceField(
          queryset=BillableItem.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
            empty_label="Select Bill Item",  # Updated label
            required=True,  # Make it optional
            help_text="Create Cost for this Bill Item for the Farming Season"  # New Help Text
        )


        greenhouse = forms.ModelMultipleChoiceField(
        queryset=Greenhouse.objects.all(),
                widget=forms.CheckboxSelectMultiple(),  # Use checkboxes instead of a dropdown
                required=False,  # Allow empty selection
                help_text="Select applicable greenhouses, or leave empty if applies to all."
        )
        
         # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        billitemcost = super().save(commit=False)

        if user is not None:
            billitemcost.created_by = user  # Dynamically assign the logged-in user

        if commit:
            billitemcost.save()

        return billitemcost


#SERVICE ITEM SET BY AIC FORM
class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ['service_name', 'farmseason', 'cost', 'description']
        
        widgets = {
                 'service_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Farming Season'}),
                 'cost': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'Item Cost'}),
                 'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
             }
        
        # farmseason = forms.ModelChoiceField(
        #     queryset=FarmSeason.objects.all(),
        #     widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        #     empty_label="Select Farm Season",  # Updated label
        #     required=True,  # Make it optional
        #     help_text="Reference every service item chargeable to a farming cycle"  # New Help Text
        # )  
    
        farmseason = forms.ModelChoiceField(
            queryset=FarmSeason.objects.all(),
            widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Farming Cycle'}),
            empty_label="Select Farm Season",  # Updated label
            required=True,  # Make it optional
            help_text="Reference every service item chargeable to a farming cycle"  # New Help Text
        )
         # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        serviceitem = super().save(commit=False)

        if user is not None:
            serviceitem.created_by = user  # Dynamically assign the logged-in user

        if commit:
            serviceitem.save()

        return serviceitem

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['status', 'description']
        widgets = {
            'status': forms.HiddenInput(),
             'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
        }
  
         # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        servicerequest = super().save(commit=False)

        if user is not None:
            servicerequest.supervisor = user
            servicerequest.created_by = user  # Dynamically assign the logged-in user

        if commit:
            servicerequest.save()

        return servicerequest
    
class ServiceRequestItemForm(forms.ModelForm):
    # Move serviceitem and quantity outside the Meta class
    serviceitem = forms.ModelChoiceField(
        queryset=ServiceItem.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Service Item",  # Updated label
        required=True,  
        help_text="Select from the list, service item you want to request."
    )

    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Quantity'}),
        min_value=1, 
        label="Quantity Requested"
    )

    class Meta:
        model = ServiceRequestItem
        fields = ['serviceitem', 'quantity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }
    
     # Override the save method to include the logged-in user
    def save(self, commit=True, user=None):
        servicerequestitem = super().save(commit=False)

        if user is not None:
            servicerequestitem.created_by = user  # Dynamically assign the logged-in user

        if commit:
            servicerequestitem.save()

        return servicerequestitem
     
ServiceRequestItemFormSet = forms.inlineformset_factory(
    ServiceRequest, ServiceRequestItem, form=ServiceRequestItemForm, extra=1, can_delete=True
)


# OrderItemFormSet = inlineformset_factory(
#     Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
# )

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


######################################## TUNNEL MANAGEMENT FORMS ####################################################
class SprayingDataForm(forms.ModelForm):
    class Meta:
        model = SprayingData
        fields = ['date_sprayed', 'crop', 'chemical_used', 'dosage', 'purpose', 'description', 'sprayingMethod', 'sprayed_by', 'startTime', 'finishTime']
        
        widgets = {
            'date_sprayed': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Sprayed'}),
            'chemical_used': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Chemical Used'}),
            'dosage': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Dosage'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Purpose', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
            'startTime': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-sm', 
                'type': 'datetime-local', 
                'placeholder': 'Start Time'
            }),
            'finishTime': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-sm', 
                'type': 'datetime-local', 
                'placeholder': 'Finish Time'
            }),
        }
        
    #Fields for spraying method
        sprayingMethod = forms.ModelChoiceField(
            queryset=SprayingMedthod.objects.all(),
            widget=forms.Select(attrs={
                'class': 'form-select form-control-sm', 
                'placeholder': 'Please Select'  # Optional: JS hook to update price
            }),
            empty_label="Please Select"
        )
        
        # Fields for worker method
        sprayed_by = forms.ModelChoiceField(
            queryset=Worker.objects.all(),
            widget=forms.Select(attrs={
                'class': 'form-select form-control-sm', 
                'placeholder': 'Please Select'  # Optional: JS hook to update price
            }),
            empty_label="Please Select"
        )
       
    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
        self.fields['sprayed_by'].widget.attrs.update({
            'class': 'form-select form-control-sm',  # Adjust for your Bootstrap version
            'placeholder': 'Please Select Sprayer'
        })
        
        self.fields['crop'].widget.attrs.update({
            'class': 'form-select form-control-sm',  # Adjust for your Bootstrap version
            'placeholder': 'Please Select Crop'
        })
        
        self.fields['sprayingMethod'].widget.attrs.update({
            'class': 'form-select form-control-sm',  # Adjust for your Bootstrap version
            'placeholder': 'Please Select Spraying Method'
        })

        self.startTime = forms.TimeField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm timepicker',  # Add 'timepicker' class
            'placeholder': 'Start Time'
        })
        )
        self.finishTime = forms.TimeField(
            widget=forms.TextInput(attrs={
                'class': 'form-control form-control-sm timepicker',  # Add 'timepicker' class
                'placeholder': 'Finish Time'
            })
        )
        
        # Filter fields based on the beneficiary
        if beneficiary:
            self.fields['sprayed_by'].queryset = Worker.objects.filter(beneficiary=beneficiary, active=True)
            self.fields['crop'].queryset = beneficiary.crops.all()

            # Pre-select the current instance values if editing
            if 'instance' in kwargs and kwargs['instance']:
                instance = kwargs['instance']
                if instance.sprayed_by:
                    self.fields['sprayed_by'].initial = instance.sprayed_by
                if instance.crop:
                    self.fields['crop'].initial = instance.crop
        else:
            self.fields['sprayed_by'].queryset = Worker.objects.none()
            self.fields['crop'].queryset = Crop.objects.none()
      

######################################## END OF TUNNEL MANAGEMENT FORM ##############################################