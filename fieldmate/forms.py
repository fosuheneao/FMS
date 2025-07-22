from django.core.exceptions import ValidationError
from django import forms
from yuapp.models import Crop, CropVariety, Greenhouse, GreenhouseRoom, HarvestStockAggregate, HeightData, PriceTable, IrrigationData, NurseryData, SprayingData, SprayingMedthod, TrellisingData, TrendKnowledgeBank, User, TrendKnowledgeDiscussion, Beneficiary, CashAssigned, Repayment, Harvest, Grade, ProductUnit, Contract, Worker
from django.utils import timezone  # Import timezone to get the current date
from django.db import transaction

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



class CashRequestForm(forms.ModelForm):
    class Meta:
        model = CashAssigned
        fields = ['amount', 'repayment_period_from', 'repayment_period_to', 'notes']
        
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder':'amount requested'}),
            'repayment_period_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'repayment_period_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }
         
class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['amount_paid', 'notes', 'photo']  # Exclude date_paid field

    def __init__(self, *args, **kwargs):
        self.beneficiary = kwargs.pop('beneficiary', None)
        self.cash_assigned = kwargs.pop('cash_assigned', None)
        super(RepaymentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        repayment = super().save(commit=False)
        repayment.cash_assigned = self.cash_assigned
        repayment.bal_amount = self.cash_assigned.amount - repayment.amount_paid  # Calculate balance
        repayment.created_by = self.beneficiary.user
        repayment.date_paid = timezone.now().date()  # Automatically set the date_paid to the current date

        if commit:
            repayment.save()

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

class HarvestForm(forms.ModelForm):
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
                'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm', 'placeholder': 'Date'}),
                'description': forms.Textarea(attrs={ 'class': 'form-control form-control-sm','placeholder': 'Detail','rows': 3}),
                'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm','placeholder': 'Quantity','min': 0,'step': 0.01 }),
                'greenhouse': forms.Select(attrs={'class': 'form-control form-control-sm','placeholder': 'Select Greenhouse'}),
                'greenhouse_room': forms.Select(attrs={'class': 'form-control form-control-sm','placeholder': 'Select Greenhouse Room'}),
                'reviewed_at': forms.DateInput(attrs={'type': 'datetime-local','class': 'form-control form-control-sm','placeholder': 'Reviewed Date'}),
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
        self.beneficiary = kwargs.pop('beneficiary', None)  # Get logged-in beneficiary
        self.crop = kwargs.pop('crop', None)  # Get crop from view
        self.created_by = kwargs.pop('created_by', None)  # Get logged-in user
        super(HarvestForm, self).__init__(*args, **kwargs)
        
        
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
            if harvest.reviewed_status == 'Agree':
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


class NurseryDataForm(forms.ModelForm):
    class Meta:
        model = NurseryData
        fields = ['date_planted', 'crop', 'seeds_sown', 'seeds_germinated', 'seedlings_transplanted', 'avg_germination_rate', 'avg_survival_rate', 'description']
        
        widgets = {
            'date_planted': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Planted'}),
            'seeds_sown': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Sown'}),
            'seeds_germinated': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Germinated'}),
            'seedlings_transplanted': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Seeds Transplanted'}),
            'avg_germination_rate': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Avg Germination Rate'}),
            'avg_survival_rate': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Avg Survival Rate'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }
   

    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
        
        if beneficiary:
            # Filter the crop queryset to only include crops assigned to the beneficiary
            self.fields['crop'].queryset = beneficiary.crops.all()
        
        # Set widget attributes
        self.fields['crop'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Crop'
        })
        
        self.fields['crop'].empty_label = "Select Crop"
        self.fields['crop'].required = False
    
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
        # if beneficiary:
        #     self.fields['sprayed_by'].queryset = Worker.objects.filter(beneficiary=beneficiary, active=True)
        #     self.fields['crop'].queryset = beneficiary.crops.all()  # Assuming the beneficiary has a related crops attribute
        # else:
        #     self.fields['sprayed_by'].queryset = Worker.objects.none()
        #     self.fields['crop'].queryset = Crop.objects.none()

        # # Add CSS and placeholders to dynamically filtered fields
        # self.fields['sprayed_by'].widget.attrs.update({'class': 'form-control form-control-sm', 'placeholder': 'Select Sprayer'})
        # self.fields['crop'].widget.attrs.update({'class': 'form-control form-control-sm', 'placeholder': 'Select Crop'})

class TrellisingDataForm(forms.ModelForm):
    class Meta:
        model = TrellisingData
        fields = ['crop', 'date_trellised', 'method', 'description']        
         
        widgets = {
            'date_trellised': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Trellised'}),
            'method': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Method', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),   
        }
   
   
    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
        
        # If beneficiary is passed, filter the crop queryset
        if beneficiary:
            self.fields['crop'].queryset = beneficiary.crops.all()  # Assuming the beneficiary has a related crops attribute
            
        # Set widget attributes for the crop field
        self.fields['crop'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Crop'
        })
        
        self.fields['crop'].empty_label = "Select Crop"
        self.fields['crop'].required = False
        

class IrrigationDataForm(forms.ModelForm):
    class Meta:
        model = IrrigationData
        fields = ['date_irrigated', 'crop', 'area_covered','water_quantity', 'method', 'description','startTime','finishTime']

        widgets = {
           'date_irrigated': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Irrigated'}),           
           'area_covered': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Area Covered'}),
           'water_quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Water Quantity'}),
           'method': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Irrigation Method', 'rows': 3}),
           'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}), 
           'startTime': forms.TimeInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'text',  # Ensure this matches the flatpickr setup
                    'placeholder': 'Start Time'
                },
                format='%H:%M'  # Matches the "H:i" format of flatpickr
            ),
            'finishTime': forms.TimeInput(
                attrs={
                    'class': 'form-control form-control-sm',
                    'type': 'text',
                    'placeholder': 'Finish Time'
                },
                format='%H:%M'
            ),  
        }
   
   
    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
        
        if beneficiary:
            # Filter the crop queryset to only include crops assigned to the beneficiary
            self.fields['crop'].queryset = beneficiary.crops.all()
        
        # Set widget attributes
        self.fields['crop'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Crop'
        })
        
        # self.startTime = forms.TimeField(
        # widget=forms.TextInput(attrs={
        #     'class': 'form-control form-control-sm timepicker',  # Add 'timepicker' class
        #     'placeholder': 'Start Time'
        # })
        # )
        # self.finishTime = forms.TimeField(
        #     widget=forms.TextInput(attrs={
        #         'class': 'form-control form-control-sm timepicker',  # Add 'timepicker' class
        #         'placeholder': 'Finish Time'
        #     })
        # )
        
        self.fields['crop'].empty_label = "Select Crop"
        self.fields['crop'].required = False
        
        
class HeightDataForm(forms.ModelForm):
    class Meta:
        model = HeightData
        fields = ['measurement_date', 'average_height', 'description', 'crop']  # Ensure 'crop' is included if it exists

        widgets = {
            'measurement_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'placeholder': 'Date Planted'}),
            'average_height': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'type': 'number', 'placeholder': 'Avg Height'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Description', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        beneficiary = kwargs.pop('beneficiary', None)  # Get the beneficiary from kwargs
        super().__init__(*args, **kwargs)
        
        # If beneficiary is passed, filter the crop queryset
        if beneficiary:
            self.fields['crop'].queryset = beneficiary.crops.all()  # Assuming the beneficiary has a related crops attribute
            
        # Set widget attributes for the crop field
        self.fields['crop'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'placeholder': 'Select Crop'
        })
        
        self.fields['crop'].empty_label = "Select Crop"
        self.fields['crop'].required = False
