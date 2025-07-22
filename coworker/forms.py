from django import forms
from django.contrib.auth.forms import AuthenticationForm
from yuapp.models import *

class BeneficiaryLoginForm(AuthenticationForm):
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
    
class CoworkerForm(forms.ModelForm):
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
    
    
    