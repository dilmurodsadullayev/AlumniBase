from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Faculty(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Graduate(models.Model):
    EDUCATION_FORM_CHOICES = [
        ('day', 'Kunduzgi'),
        ('evening', 'Kechki'),
        ('external', 'Sirtqi'),
        ('distance', 'Masofaviy ta’lim'),
    ]
    STUDENT_STATUS = [
        ('active', "O'qiyapti"),
        ('graduated', "Bitirgan"),
        ('expelled', "Haydalgan"),
    ]
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE) # OneToOneField da faqat bitta odam bog'lanish mumkin
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='graduates/images/')
    birth_date = models.DateField()
    education_form = models.CharField(max_length=50, choices=EDUCATION_FORM_CHOICES, default='day') # qanday ta'lim olgon
    academic_score = models.FloatField(default=0.0)# GPA
    enrollment_year = models.DateField() # o'qishga kirgan yil
    completed_year = models.DateField() # tugatgan yil
    status = models.CharField(max_length=50, choices=STUDENT_STATUS, default='graduated')

    def __str__(self):
        return f"{self.first_name} - {str(self.completed_year.strftime('%Y'))}"


class Company(models.Model):
    name = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    contact_email = models.EmailField()
    location = models.CharField(max_length=50)
    phone_number = PhoneNumberField(unique=True, region="UZ")
    website = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.sector}"


class EmploymentData(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', "To‘liq stavka"),
        ('part_time', 'Yarim stavka'),
        ('internship', 'Amaliyot'),
        ('freelance', 'Freelans (mustaqil)'),
    ]
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(max_length=50) #lavozim uchun
    stage = models.FloatField(default=0.5)
    salary = models.FloatField(default=0)
    start_date = models.DateField()
    employment_type = models.CharField(max_length=50,choices=EMPLOYMENT_TYPE_CHOICES, default='part_time')
    is_current_employed = models.BooleanField(default=False) # bu ishlayotgan bo'lsa True
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.position


class GraduateContact(models.Model):
    graduate = models.OneToOneField(Graduate, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = PhoneNumberField(unique=True, region="UZ")
    linkedin = models.URLField()
    telegram = models.URLField()

    def __str__(self):
        return self.email


class Contact(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.email