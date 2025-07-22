from django.shortcuts import render

# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from .models import *

def index(request):
    #begin slider
    # menus = SectionMenu.objects.all()
    slides = Beneficiary.objects.all()
    
    context = {}
    
    
    return render(request, 'index.html', context)