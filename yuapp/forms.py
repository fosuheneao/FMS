from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *

#supervisor login form
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


   
class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['description', 'todostate', 'expected_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Activity'}),
            'todostate': forms.Select(attrs={'class': 'form-control'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Task Date', 'type': 'date'}),
        }
        labels = {
            'description': 'Activity',
            'todostate': 'Status',
            'expected_date':'Completion Date',
        }
        
        
class PriceTableAdminForm(forms.ModelForm):
    class Meta:
        model = PriceTable
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # If crop is selected, filter cropvariety choices
        if 'crop' in self.data:
            try:
                crop_id = int(self.data.get('crop'))
                self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=crop_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.crop:
            self.fields['cropvariety'].queryset = CropVariety.objects.filter(crop=self.instance.crop)
        else:
            self.fields['cropvariety'].queryset = CropVariety.objects.none()
            
        