from django.shortcuts import render, redirect
from .forms import BeneficiaryWorkerForm

def create_beneficiary_worker(request):
    if request.method == 'POST':
        form = BeneficiaryWorkerForm(request.POST, user=request.user)  # Pass the logged-in user
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect to a success page
    else:
        form = BeneficiaryWorkerForm(user=request.user)  # Pass the logged-in user
    return render(request, 'template_name.html', {'form': form})
