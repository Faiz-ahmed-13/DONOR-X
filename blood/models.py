from django.db import models
from patient import models as pmodels
from donor import models as dmodels

class Stock(models.Model):
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.bloodgroup} : {self.unit} units"

class BloodRequest(models.Model):
    request_by_patient = models.ForeignKey(pmodels.Patient, null=True, on_delete=models.CASCADE)
    patient_age = models.PositiveIntegerField(default=0)
    patient_gender = models.CharField(max_length=10, default='Not Specified')
    reason = models.CharField(max_length=500)
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="Pending")
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request_by_patient.user.username if self.request_by_patient else 'Anonymous'} requested {self.unit} units of {self.bloodgroup}"

class BloodDonate(models.Model):
    donor = models.ForeignKey(dmodels.Donor, on_delete=models.CASCADE, related_name='blood_donations')
    disease = models.CharField(max_length=100, default="None")
    age = models.PositiveIntegerField(default=0)
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="Pending")
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.donor.user.username} donated {self.unit} units of {self.bloodgroup}"

        