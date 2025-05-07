from django.shortcuts import render
from django.db.models import Q
from django.db.models.functions import ExtractYear
from .models import Graduate, EmploymentData
#
# def dashboard(request):
#
#     context = {
#     }
#     return render(request, 'alumni/base.html', context)
