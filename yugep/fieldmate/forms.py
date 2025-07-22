from django import forms
from yuapp.models import WorkerRole, Worker

class BeneficiaryWorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['beneficiary']  # List other fields you want to include

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance
