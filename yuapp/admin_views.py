# admin_views.py or in views.py
from django.http import JsonResponse
from .models import CropVariety

def load_crop_varieties(request):
    crop_id = request.GET.get('crop_id')
    varieties = CropVariety.objects.filter(crop=crop_id).order_by('name')
    return JsonResponse(list(varieties.values('id', 'name')), safe=False)
