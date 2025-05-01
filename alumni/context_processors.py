from django.shortcuts import render
from django.db.models import Q
from .models import Graduate

def dashboard(request):
    # Ishga joylashganlar (employment bor va is_current_employed = True)
    ishlayotganlar = Graduate.objects.filter(
        employmentdata__is_current_employed=True
    ).distinct().count()

    # Ishsizlar (employment yo‘q yoki is_current_employed = False)
    ishsizlar = Graduate.objects.filter(
        Q(employmentdata__isnull=True) |
        Q(employmentdata__is_current_employed=False)
    ).distinct().count()

    return  {
        'ishlayotganlar_soni': ishlayotganlar,
        'ishsizlar_soni': ishsizlar
    }
