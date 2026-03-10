from django.contrib import admin
from blood.models import BloodRequest
from donor.models import Donor, BloodDonate
from patient.models import Patient

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'blood_group', 'units', 'date']
    list_filter = ['blood_group', 'date']
    search_fields = ['patient__name', 'blood_group']

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'blood_group', 'age', 'city']
    list_filter = ['blood_group', 'city']
    search_fields = ['name', 'phone']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'blood_group', 'phone']
    list_filter = ['blood_group']
    search_fields = ['name', 'phone']

@admin.register(BloodDonate)
class BloodDonateAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_group', 'units', 'date']
    list_filter = ['blood_group', 'date']
