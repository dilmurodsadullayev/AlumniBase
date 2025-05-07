from django.contrib import admin
from .models import Faculty, Graduate, Company, EmploymentData, GraduateContact, Contact, Statistic


# Faculty model admin
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Faculty, FacultyAdmin)

# Graduate model admin
class GraduateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'faculty', 'status', 'enrollment_year', 'completed_year', 'academic_score')
    list_filter = ('faculty', 'status', 'education_form')
    search_fields = ('first_name', 'last_name', 'faculty__name')
    date_hierarchy = 'enrollment_year'

admin.site.register(Graduate, GraduateAdmin)

# Company model admin
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'contact_email', 'location', 'phone_number', 'website', 'timestamp')
    search_fields = ('name', 'sector', 'contact_email', 'location')

admin.site.register(Company, CompanyAdmin)

# EmploymentData model admin
class EmploymentDataAdmin(admin.ModelAdmin):
    list_display = ('graduate', 'company', 'position', 'salary', 'start_date', 'employment_type', 'is_current_employed', 'timestamp')
    list_filter = ('employment_type', 'is_current_employed')
    search_fields = ('graduate__first_name', 'graduate__last_name', 'company__name', 'position')

admin.site.register(EmploymentData, EmploymentDataAdmin)

# GraduateContact model admin
class GraduateContactAdmin(admin.ModelAdmin):
    list_display = ('graduate', 'email', 'phone', 'linkedin', 'telegram')
    search_fields = ('graduate__first_name', 'graduate__last_name', 'email')

admin.site.register(GraduateContact, GraduateContactAdmin)
admin.site.register(Contact)
admin.site.register(Statistic)