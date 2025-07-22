from django import forms

from fieldmate import admin
from .models import *

class MyModelForm(forms.ModelForm):
    class Meta:
        model = StoreRoom
        fields = '__all__'
        widgets = {
            'beneficiary': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class MyModelAdmin(admin.ModelAdmin):
    form = MyModelForm

admin.site.register(StoreRoom, MyModelAdmin)
