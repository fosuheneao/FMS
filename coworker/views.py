from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CoworkerForm
from django.contrib import messages
from django.db.models import Count
# Create your views here.
from django.shortcuts import render,redirect, get_object_or_404
from yuapp.models import *

@login_required
def beneficiary_profile(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        try:
            # Fetch the beneficiary details associated with the logged-in user
            beneficiary = request.user.beneficiary
            beneficiary = Beneficiary.objects.get(user=request.user)
            
            # Fetch coworkers or any additional data you want to display
            coworkers = Worker.objects.filter(created_by=request.user.id)
            # beneficiaries = Beneficiary.objects.filter(assigned_supervisor_id=supervisor.id) 
            

            # Count male and female beneficiaries
            gender_counts = coworkers.values('gender').annotate(total=Count('id'))
    
                # Create a dictionary to store counts for easier access
            gender_count_dict = {
                    'Male': 0,
                    'Female': 0
                }

                # Populate the gender count dictionary
            for gender in gender_counts:
                    if gender['gender'] in gender_count_dict:
                        gender_count_dict[gender['gender']] += gender['total']

            # Render the profile page with the beneficiary details
            return render(request, 'admin/beneficiary/profile.html', {
                'beneficiary': beneficiary,
                'coworkers': coworkers,
                'gender_count': gender_count_dict
            })
        except Supervisor.DoesNotExist:
            # Handle case where the user is authenticated but not a beneficiary
            return redirect('edo_login')
    else:
        return redirect('edo_login')
    
@login_required
def coworker_index(request):

    if request.user.is_authenticated:        
        coworkers = Worker.objects.filter(created_by = request.user.id)
        return render(request, 'admin/beneficiary/worker/coworker.html', {'coworkers':coworkers})
    else:
       return redirect('beneficiary_login')



@login_required
def coworker_detail(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    return render(request, 'admin/beneficiary/worker/coworker_detail.html', {'coworker': coworker})

@login_required
def coworker_create(request):
    if request.method == 'POST':
        form = CoworkerForm(request.POST, request.FILES)  # Use the form, not the model directly
        if form.is_valid():
            # Return an object without saving to the DB
            obj = form.save(commit=False)
            # Add an author field which will contain current user's id
            obj.created_by = request.user  # Assign the current logged-in user
            # Save the final "real form" to the DB
            obj.save()
            
            messages.success(request, 'Coworker created successfully.')
            return redirect('beneficiary_coworker')
    else:
        form = CoworkerForm()
    
    return render(request, 'admin/beneficiary/worker/coworker_create.html', {'form': form})


@login_required
def coworker_update(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    if request.method == 'POST':
        form = CoworkerForm(request.POST, request.FILES, instance=coworker)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coworker updated successfully.')
            return redirect('beneficiary_coworker')
    else:
        form = CoworkerForm(instance=coworker)  # Use the correct form here
    return render(request, 'admin/beneficiary/worker/coworker_create.html', {'form': form, 'coworker': coworker})

@login_required
def coworker_delete(request, pk):
    coworker = get_object_or_404(Worker, pk=pk)
    coworker.delete()
    messages.success(request, 'Coworker deletion successful.')
    return redirect('beneficiary_coworker')


