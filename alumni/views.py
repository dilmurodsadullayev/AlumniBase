from urllib import request

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.db.models import Q

from alumni.forms import RegistrationForm
from alumni.models import Graduate, EmploymentData, Company, Contact, Statistic
from django.core.mail import send_mail
from django.contrib import messages


# Create your views here.

def index_view(request):
    # O'qiyotgan talabalar soni (2025 yilda)
    graduates_count = Graduate.objects.filter(status='active', completed_year__year=2025).count()

    # Ishsizlar (employmentdata yo'q)
    ishsizlar_soni = Graduate.objects.filter(employmentdata__isnull=True).count()

    # Ishlayotganlar (is_current_employed=True bo'lganlar)
    ishlayotganlar = Graduate.objects.filter(employmentdata__is_current_employed=True).count()

    # Kompaniyalar soni
    companies_count = Company.objects.all().count()

    # Boshqa sohada ishlayotganlar
    boshqa_soha = Graduate.objects.filter(
        employmentdata__is_current_employed=False
    ).distinct().count()

    # Foiz hisoblash uchun funksiya
    def get_percentage(part, total):
        return round((part / total) * 100) if total > 0 else 0

    # Foizlar
    ishlayotganlar_percent = get_percentage(ishlayotganlar, graduates_count)
    boshqa_soha_percent = get_percentage(boshqa_soha, graduates_count)
    ishsizlar_percent = get_percentage(ishsizlar_soni, graduates_count)

    # Kontentni kontekstga joylash
    ctx = {
        'graduates_count': graduates_count,
        'ishlayotganlar': ishlayotganlar,
        'ishsizlar_soni': ishsizlar_soni,
        'companies_count': companies_count,
        'boshqa_soha': boshqa_soha,
        'ishlayotganlar_percent': ishlayotganlar_percent,
        'boshqa_soha_percent': boshqa_soha_percent,
        'ishsizlar_percent': ishsizlar_percent,
    }

    return render(request, 'alumni/index.html', ctx)


from datetime import datetime

@login_required(login_url="/login")
def annual_report(request):
    current_year = datetime.now().year
    selected_year = request.GET.get('year', current_year)

    # selected_year ni int turiga o'tkazish
    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = current_year

    # Sana oralig‘ini aniqlash
    start_date = datetime(selected_year, 1, 1)
    end_date = datetime(selected_year + 1, 1, 1)

    # Bitiruvchilar soni
    total_graduates = Graduate.objects.filter(
        completed_year__year=selected_year  # Faqqat yilga qarash
    ).count()

    # Ishga joylashganlar
    employed_graduates = Graduate.objects.filter(
        completed_year__year=selected_year,
        employmentdata__is_current_employed=True
    ).count()

    # Ishsizlar
    unemployed_graduates = Graduate.objects.filter(
        completed_year__year=selected_year,
        employmentdata__isnull=True
    ).count()

    # O‘z sohasida ishlayotganlar
    own_field_employed = Graduate.objects.filter(
        completed_year__year=selected_year,
        employmentdata__is_current_employed=True,
        employmentdata__employment_type="Own"
    ).count()

    # Boshqa sohada ishlayotganlar
    other_field_employed = Graduate.objects.filter(
        completed_year__year=selected_year,
        employmentdata__is_current_employed=True,
        employmentdata__employment_type="Other"
    ).count()

    # Foizlarni hisoblash
    employed_percentage = (employed_graduates / total_graduates) * 100 if total_graduates else 0
    unemployed_percentage = (unemployed_graduates / total_graduates) * 100 if total_graduates else 0
    own_field_percentage = (own_field_employed / total_graduates) * 100 if total_graduates else 0
    other_field_percentage = (other_field_employed / total_graduates) * 100 if total_graduates else 0

    # Faqat yilni olish uchun distinct so'rov
    years = Graduate.objects.dates('completed_year', 'year').distinct()

    context = {
        'total_graduates': total_graduates,
        'employed_graduates': employed_graduates,
        'unemployed_graduates': unemployed_graduates,
        'own_field_employed': own_field_employed,
        'other_field_employed': other_field_employed,
        'employed_percentage': employed_percentage,
        'unemployed_percentage': unemployed_percentage,
        'own_field_percentage': own_field_percentage,
        'other_field_percentage': other_field_percentage,
        'selected_year': selected_year,
        'years': years,
    }

    return render(request, 'alumni/annual_report.html', context)



def graduation_view(request):
    graduates = Graduate.objects.all()

    # Filtrlashlar
    name = request.GET.get('name')
    if name:
        graduates = graduates.filter(first_name__icontains=name)

    gpa_order = request.GET.get('gpa_order')
    if gpa_order == 'asc':
        graduates = graduates.order_by('academic_score')
    elif gpa_order == 'desc':
        graduates = graduates.order_by('-academic_score')

    status = request.GET.get('status')
    if status == 'bitirgan':
        graduates = graduates.filter(status='graduated')
    elif status == 'oqiyapti':
        graduates = graduates.filter(status='active')

    # AJAX so‘rovlarga JSON qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('alumni/partials/graduates_table.html', {'graduates': graduates})
        return JsonResponse({'html': html})

    return render(request, 'alumni/graduates.html', {'graduates': graduates})


@login_required(login_url="/login")
def graduate_detail(request, graduate_id):
    graduate = get_object_or_404(Graduate, id=graduate_id)
    employment_data = EmploymentData.objects.filter(graduate=graduate)
    context = {
        'graduate': graduate,
        'employment_data': employment_data
    }
    return render(request, 'alumni/graduate_detail.html', context)



def contact_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        Contact.objects.create(full_name=full_name, email=email, message=message)

        # # Email yuborish
        # send_mail(
        #     f"Xabar: {name}",
        #     message,
        #     email,
        #     ['admin@company.com'],  # Xabarni qayerga yuborish kerakligini ko'rsatish
        # )
        messages.success(request, 'Xabaringiz muvaffaqiyatli yuborildi!')
        return redirect('contact')  # Kontakt sahifasiga qaytish

    return render(request, 'alumni/contact.html')


@login_required(login_url="/login")
def graduate_search_ajax(request):
    name = request.GET.get('name', '').strip()
    faculty = request.GET.get('faculty', '').strip()

    graduates = Graduate.objects.all()

    if name:
        graduates = graduates.filter(
            Q(first_name__icontains=name) | Q(last_name__icontains=name)
        )
    if faculty:
        graduates = graduates.filter(
            faculty__name__icontains=faculty
        )

    data = []
    for g in graduates:
        data.append({
            'id': g.id,
            'first_name': g.first_name,
            'last_name': g.last_name,
            'faculty_name': g.faculty.name if g.faculty else '',
            'image_url': g.image.url if g.image else '',
            'education_form': g.get_education_form_display(),
            'academic_score': g.academic_score,
            'status': g.get_status_display(),
            'completed_year': g.completed_year.strftime('%Y') if g.completed_year else '',
        })

    return JsonResponse(data, safe=False)


def graduate_state(request):
    type_param = request.GET.get('type')
    print(type_param)
    if type_param == 'bitiruvchilar':
        graduates = Graduate.objects.filter(status='active')
        ctx = {'graduates': graduates}
        return render(request, 'alumni/graduate_state.html',ctx)

    elif type_param == 'ishsizlar':
        graduates = Graduate.objects.filter(status='active')
        ctx = {'graduates': graduates}
        return render(request, 'alumni/graduate_state.html',ctx)
    else:
        graduates = Graduate.objects.filter(status='graduated')
        ctx = {'graduates': graduates}
        return render(request, 'alumni/graduate_state.html',ctx)





def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Ma'lumotlaringizni to'g'ri kiriting.")  # Umumiy xato xabari
    else:
        form = RegistrationForm()

    ctx = {
        "form": form
    }

    return render(request, 'registration/register.html')


def companies_view(request):
    companies = Company.objects.all()
    ctx = {
        'companies': companies
    }
    return render(request, 'alumni/companies_list.html', ctx)


def our_veterans_view(request):
    ctx = {

    }

    return render(request, 'alumni/our_veterans.html', ctx)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)  # Foydalanuvchini tizimga kiritamiz
                return redirect('home')  # Bosh sahifaga yo'naltirish
            else:
                messages.error(request, "Foydalanuvchi nomi yoki parol noto‘g‘ri")
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto‘g‘ri")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html')


def yearly_statistics(request):
    # Yilni olish (default qiymat sifatida 2025 ni oling)
    year = request.GET.get('year', 2025)  # Yilni olish (agar yil berilmasa, 2025 bo'ladi)
    try:
        year = int(year)  # Yilni int ga aylantirish
    except ValueError:
        return JsonResponse({'error': 'Yil noto‘g‘ri formatda kiritilgan'}, status=400)

    # Yilga mos statistikalarni olish
    statistics = Statistic.objects.filter(year=year)

    # Statistikani JSON formatida saqlash
    statistics_data = []
    for stat in statistics:
        statistics_data.append({
            'year': stat.year,  # Yil
            'sum_number': stat.sum_number,  # Summa
            'self_field': stat.self_field,  # O'z soha
        })

    # JSON formatida qaytish
    return JsonResponse({'statistika': statistics_data})

def custom_404(request, exception):
    return render(request, '404.html', status=404)