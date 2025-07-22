from django import forms
from django.contrib.auth.forms import AuthenticationForm
from yuapp.models import *
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone  # Import timezone to get the current date




class TrendKnowledgeBankForm(forms.ModelForm):
     class Meta:
        model = TrendKnowledgeBank
        fields = [                    
            'title',
            'description', 
            'latitude',
            'longitude',
            'photo'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Topic'}),
            'description': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'longitude': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Attach Picture'})        
        }
    
class TrendKnowledgeDiscussionForm(forms.ModelForm):
    tagged_beneficiaries = forms.ModelMultipleChoiceField(
        queryset=Beneficiary.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = TrendKnowledgeDiscussion
        fields = ['discussion', 'photo', 'tagged_beneficiaries']
        widgets = {
            'discussion': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Share your thoughts here...','rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Attach Picture'}),
            'tagged_beneficiaries': forms.SelectMultiple(attrs={'class': 'form-control form-control-sm'}),
        }

class EdoLoginForm(AuthenticationForm):
    # username = forms.CharField(label='Beneficiary Email', max_length=255)
    # password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    username = forms.CharField(
        label='Username',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-md',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-md',
            'placeholder': 'Enter your password',
        })
    )
 

class HarvestFormEdo(forms.ModelForm):
    HARVEST_STATUS = [
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Open', 'Open')
    ]
    
    class Meta:
        model = Harvest
        fields = [
            'date', 'crop','cropvariety', 'description', 'grade', 'quantity', 'unit', 'price_record',
            'greenhouse', 'greenhouse_room'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control form-control-sm', 
                'placeholder': 'Date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Detail', 
                'rows': 3
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm', 
                'placeholder': 'Quantity',
                'min': 0,
                'step': 0.01
            }),
            'greenhouse': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Select Greenhouse'
            }),
            'greenhouse_room': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Select Greenhouse Room'
            }),
            'reviewed_at': forms.DateInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control form-control-sm',
                'placeholder': 'Reviewed Date'
            }),
        }

    grade = forms.ModelChoiceField(
        queryset=Grade.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm', 
            'placeholder': 'Select Grade',
            'onchange': 'updatePriceAndTotal();'  
        }),
        empty_label="Select Grade"
    )
    
    unit = forms.ModelChoiceField(
        queryset=ProductUnit.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm', 
            'placeholder': 'Select Measure Unit',
            'onchange': 'updatePriceAndTotal();'  
        }),
        empty_label="Select Measure Unit"
    )
    
    crop = forms.ModelChoiceField(
        queryset=Crop.objects.all(),  # Default queryset for all crops
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Crop'
        }),
        empty_label="Select Crop"
    )
    
    cropvariety = forms.ModelChoiceField(
        queryset=CropVariety.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Crop Variety",
        required=False
    )
  
    def __init__(self, *args, **kwargs):
        self.beneficiary = kwargs.pop('beneficiary', None)
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)
      
        if self.beneficiary:
            self.fields['crop'].queryset = self.beneficiary.crops.all()

         # If POST data exists, dynamically filter cropvariety queryset
        if 'crop' in self.data:
            try:
                crop_id = int(self.data.get('crop'))
                self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop_id=crop_id)
            except (ValueError, TypeError):
                self.fields['cropvariety'].queryset = CropVariety.objects.none()
        elif self.instance and self.instance.pk and self.instance.crop:
            self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=self.instance.crop)
        else:
            self.fields['cropvariety'].queryset = CropVariety.objects.none()
        
        if self.instance and self.instance.pk:
            self.fields['grade'].initial = self.instance.grade
            self.fields['unit'].initial = self.instance.unit
            self.fields['greenhouse'].initial = self.instance.greenhouse
            self.fields['greenhouse_room'].initial = self.instance.greenhouse_room
            self.fields['crop'].initial = self.instance.crop
            self.fields['cropvariety'].initial = self.instance.cropvariety
      
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        crop = cleaned_data.get('crop')
        cropvariety = cleaned_data.get('cropvariety')
        grade = cleaned_data.get('grade')
        unit = cleaned_data.get('unit')
        quantity = cleaned_data.get('quantity')

        # Ensure crop, grade, and unit exist before proceeding
        if not (crop and grade and unit and date):
            raise ValidationError('All fields must be selected.')

        
        # Ensure quantity is greater than 0
        if quantity is not None and quantity <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        
         # Only run this check if it's a new instance (i.e., no primary key yet)
        if not self.instance.pk:
            if Harvest.objects.filter(
                crop=crop,
                cropvariety=cropvariety,
                grade=grade,
                unit=unit,
                quantity=quantity,
                date=date,
                beneficiary=self.beneficiary
            ).exists():
                raise ValidationError(
                    'A harvest record for the same crop, variety, grade, unit, quantity, and date already exists.'
            )
       
        return cleaned_data

    def save(self, commit=True):
        is_new = self.instance._state.adding  # More reliable check
        harvest = super().save(commit=False)

        harvest.beneficiary = self.beneficiary

        if is_new:
            harvest.created_by = self.created_by
            harvest.reviewed_by = self.created_by
            harvest.reviewed_at = timezone.now()

        harvest.calculate_price()

        if commit:
            harvest.save()
            if harvest.confirmation == 'Confirmed' and harvest.status == 'Completed'  and is_new:
                self.aggregate_harvest_stock(harvest)

        return harvest
   
    
    #def aggregate_harvest_stock(self, harvest):
    def aggregate_harvest_stock(self, harvest, is_update=False, old_values=None):
          # Aggregates harvest stock into HarvestStockAggregate when status is confirmed.
          # Handles both creation and update scenarios.
        if not harvest.greenhouse:
            return

        harvest_date = harvest.date.date()
        new_market_centre = harvest.greenhouse.marketing_centres
    
        #market_centre = harvest.greenhouse.marketing_centres
        #harvest_date = harvest.date.date()

        with transaction.atomic():
            # If update, reverse the old aggregation
            if is_update and old_values:
                try:
                    old_aggregate = HarvestStockAggregate.objects.get(
                        market_centre=old_values['market_centre'],
                        crop=old_values['crop'],
                        cropvariety=old_values['cropvariety'],
                        grade=old_values['grade'],
                        unit=old_values['unit'],
                        unit_price=old_values['unit_price'],
                        aggregation_date=old_values['aggregation_date'],
                    )
                    old_aggregate.total_quantity -= old_values['quantity'] or 0
                    old_aggregate.total_value -= old_values['total_price'] or 0
                    old_aggregate.save()
                except HarvestStockAggregate.DoesNotExist:
                    pass  # In case the old aggregate no longer exists

            # Aggregate into (new or existing) matching record
            aggregate, created = HarvestStockAggregate.objects.get_or_create(
                market_centre=new_market_centre,
                crop=harvest.crop,
                cropvariety=harvest.cropvariety,
                grade=harvest.grade,
                unit=harvest.unit,
                unit_price=harvest.price_record,
                aggregation_date=harvest_date,
                defaults={'total_quantity': 0, 'total_value': 0}
            )

            aggregate.total_quantity += harvest.quantity or 0
            aggregate.total_value += harvest.total_price or 0
            aggregate.save()
        
   
      
class CoworkerFormEDO(forms.ModelForm):
    # Gender choices
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    class Meta:
        model = Worker
        fields = [                    
            'full_name',
            'gender', 
            'role',
            'age',
            'email',
            'phone_number',
            'photo',
            'nationalId',
            'cardphoto',
            'from_date', 
            'to_date',
            'description'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Full Name'}),
            #'gender': forms.RadioSelect(attrs={'class': 'form-control form-control-sm'}),
            #'role': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Role'}),
            'age': forms.NumberInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Age'}),
            'email': forms.EmailInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Phone Number'}),
            'photo': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Passport Picture'}),
            'nationalId': forms.TextInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card No.'}),
            'cardphoto': forms.ClearableFileInput(attrs={'class':'form-control form-control-sm', 'placeholder': 'Ghana Card Picture'}),
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm', 'placeholder': 'From'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm', 'placeholder': 'To'}),            
            'description': forms.Textarea(attrs={'class':'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
        }
    
    # Dynamically load roles from WorkerRole model
    role = forms.ModelChoiceField(
        queryset=WorkerRole.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Role'}),
        empty_label="Select Role"  # Default label for empty option
    )
    
    # Corrected gender field
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})  # Bootstrap class for radio buttons
    )
    
    def __init__(self, *args, **kwargs):
        self.beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        coworker = super().save(commit=False)
        
        coworker.beneficiary = self.beneficiary  # Ensure beneficiary is set from form
        #coworker.created_by = self.created_by  # Set the creator if needed

        if commit:
            coworker.save()  # Save the contract to the database
        return coworker


class InputDistributionForm(forms.ModelForm):
    class Meta:
        model = InputDistribution
        fields = ['beneficiary', 'farm_input', 'quantity']
        widgets = {
            'beneficiary': forms.Select(attrs={'class': 'form-control'}),
            'farm_input': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
        }

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor', None)
        super().__init__(*args, **kwargs)

        if supervisor:
            # Filter InputEdoDistribution assigned to this supervisor
            self.fields['farm_input'].queryset = InputEdoDistribution.objects.filter(
                supervisor=supervisor
            )

            # Customize the display of the farm input dropdown
            self.fields['farm_input'].label_from_instance = lambda obj: (
                f"{obj.farm_input.inputcategory.name} - Quantity Received: {obj.farm_input.quantity_received} - "
                f"Quantity Distributed: {obj.quantity} - Unit Cost: {obj.farm_input.cost_per_unit}"
            )
            
            # Correct queryset for beneficiaries assigned to the supervisor
            self.fields['beneficiary'].queryset = Beneficiary.objects.filter(
                assigned_edo=supervisor
            )

    def clean_quantity(self):
        quantity_new = self.cleaned_data.get('quantity')
        farm_input = self.cleaned_data.get('farm_input')  # This is an `InputEdoDistribution` instance

        if not farm_input:
            raise forms.ValidationError("Please select a valid farm input.")

        # Ensure the distributed quantity is valid
        available_quantity = farm_input.quantity

        if quantity_new > available_quantity:
            raise forms.ValidationError("You cannot distribute more than the available quantity.")

        return quantity_new
    
class ContractForm(forms.ModelForm):
    CONTRACT_STATUS = [
        ('Active', 'Active'),
        ('Terminated', 'Terminated')
    ]

    status = forms.ChoiceField(
        choices=CONTRACT_STATUS,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Select Status'})
    )

    class Meta:
        model = Contract
        fields = ['beneficiary', 'worker', 'contract_type', 'description', 'from_date', 'to_date', 'payment_mode_type', 'charge_per_day', 'status']
        widgets = {
            'from_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'contract_type': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
            'payment_mode_type': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'charge_per_day': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.worker = kwargs.pop('worker', None)  # Expect worker instance
        self.beneficiary = kwargs.pop('beneficiary', None)  # Expect beneficiary instance
        self.created_by = kwargs.pop('created_by', None)  # Expect created_by instance or user
        super(ContractForm, self).__init__(*args, **kwargs)

        # Set worker field
        if self.worker:
            self.fields['worker'].queryset = Worker.objects.filter(id=self.worker.id)  # Limit to selected worker
            self.fields['worker'].initial = self.worker.full_name
            self.fields['worker'].widget = forms.HiddenInput()  # Hide the worker field

        # Set beneficiary field
        if self.beneficiary:
            self.fields['beneficiary'].initial = self.beneficiary.full_name
            self.fields['beneficiary'].widget = forms.HiddenInput()  # Hide the beneficiary field

    def clean(self):
        cleaned_data = super().clean()
        contract_type = cleaned_data.get('contract_type')
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        # Ensure from_date is before to_date
        if from_date and to_date and from_date > to_date:
            raise ValidationError("The 'from' date cannot be later than the 'to' date.")

        # Check if a contract with the same worker, beneficiary, type, and date range already exists
        if Contract.objects.filter(
            beneficiary=self.beneficiary,
            worker=self.worker,
            contract_type=contract_type,
            from_date=from_date,
            to_date=to_date
        ).exists():
            raise ValidationError('A contract with the same Worker, Beneficiary, and date range already exists.')

        return cleaned_data

    def save(self, commit=True):
        contract = super().save(commit=False)
        contract.worker = self.worker  # Ensure worker is set from form
        contract.beneficiary = self.beneficiary  # Ensure beneficiary is set from form
        contract.created_by = self.created_by  # Set the creator if needed

        if commit:
            contract.save()  # Save the contract to the database
        return contract
    

class NurseryDataFormEdo(forms.ModelForm):
    class Meta:
        model = NurseryData
        fields = [
            'date_planted', 'crop', 'cropvariety', 'seeds_sown', 
            'seeds_germinated', 'seedlings_transplanted', 
            'avg_germination_rate', 'avg_survival_rate', 'description'
        ]
        
        widgets = {
            'date_planted': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Planted'}),
            'seeds_sown': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Sown'}),
            'seeds_germinated': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Germinated'}),
            'seedlings_transplanted': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Transplanted'}),
            'avg_germination_rate': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Avg Germination Rate'}),
            'avg_survival_rate': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Avg Survival Rate'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }

    crop = forms.ModelChoiceField(
        queryset=Crop.objects.all(),  
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Crop"
    )

    cropvariety = forms.ModelChoiceField(
        queryset=CropVariety.objects.none(),  
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Crop Variety",
        required=False
    )

    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)
        super().__init__(*args, **kwargs)

        if beneficiary:
            self.fields['crop'].queryset = beneficiary.crops.all()

        if self.instance and self.instance.pk:
            crop = self.instance.crop
            if self.instance.cropvariety:
                # If cropvariety exists, load only varieties linked to this crop
                self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=crop)
            else:
                # If cropvariety is empty, load all varieties associated with the crop
                self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=crop)
        else:
            # If it's a new form, initially keep cropvariety empty
            self.fields['cropvariety'].queryset = CropVariety.objects.none()

    
#<<<<<<<<<<<<<<<<<<< OPERATIONAL COST SERVICE REQUEST ===============>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class ServiceRequestForm(forms.ModelForm):
    beneficiary = forms.ModelChoiceField(
        queryset=Beneficiary.objects.none(),  # Set an empty queryset initially
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Beneficiary",
        required=True,
        help_text="Reference every service request to a beneficiary."
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get logged-in user
        super().__init__(*args, **kwargs)

        if user:
            try:
                supervisor = Supervisor.objects.get(user=user)  # Get Supervisor linked to user
                self.fields['beneficiary'].queryset = Beneficiary.objects.filter(assigned_edo=supervisor)
            except Supervisor.DoesNotExist:
                self.fields['beneficiary'].queryset = Beneficiary.objects.none()  # No supervisor found
                
    class Meta:
        model = ServiceRequest
        fields = ['beneficiary', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3})
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not instance.pk:  # Only set created_by when creating a new record
            if hasattr(self, 'user') and self.user:
                instance.supervisor = self.user
                instance.created_by = self.user  # Assign the logged-in user

        if commit:
            instance.save()

        return instance

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
        fields = ['serviceitem', 'quantity', 'unitcost', 'description']
        widgets = {
            'unitcost': forms.TextInput(attrs={'class': 'form-control form-control-sm','readonly': 'readonly'}),  # Make unitcost non-editable
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['serviceitem'].queryset = ServiceItem.objects.all()
        self.fields['serviceitem'].label_from_instance = lambda obj: f"{obj.service_name} - {obj.farmseason.name}"
        
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

############## Equipment and Maintenance Module ####################################
class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['category', 'name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class EquipmentMaintenanceLogForm(forms.ModelForm):
    class Meta:
        model = EquipmentMaintenanceLog
        fields = [
            'date', 'code', 'part', 'part_use', 'status',
            'description', 'approved_by', 'performed_by', 'performed_by_phone',
            'tested_by', 'tested_by_phone', 'test_feedback',
            'maintenance_duration', 'maintenance_cost', 'remarks'
        ]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            #'code': forms.Select(attrs={'class': 'form-control'}),
            #'part': forms.Select(attrs={'class': 'form-control'}),
            'part_use': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'approved_by': forms.TextInput(attrs={'class': 'form-control'}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'performed_by_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'tested_by': forms.TextInput(attrs={'class': 'form-control'}),
            'tested_by_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'test_feedback': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'maintenance_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


    code = forms.ModelChoiceField(
        queryset=MaintenanceCode.objects.all(),  
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Maintenance Log Code"
    )
    
    part = forms.ModelChoiceField(
        queryset=EquipmentPart.objects.all(),  
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
        empty_label="Select Equipment Part"
    )