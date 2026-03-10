from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Patient/', null=True, blank=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    bloodgroup = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES)
    disease = models.CharField(max_length=100)
    doctorname = models.CharField(max_length=50)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=10)
    
    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name
    
    @property
    def get_instance(self):
        return self
    
    def __str__(self):
        return self.user.first_name
    
    class Meta:
        ordering = ['user__first_name']