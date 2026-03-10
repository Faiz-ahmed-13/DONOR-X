from django import forms
from django.contrib.auth.models import User
from . import models


class BloodForm(forms.ModelForm):
    class Meta:
        model=models.Stock
        fields=['bloodgroup','unit']

class RequestForm(forms.ModelForm):
    class Meta:
        model = models.BloodRequest
        fields = ['bloodgroup', 'unit', 'reason']

class DonationForm(forms.ModelForm):
    class Meta:
        model = models.BloodDonate
        fields = ['bloodgroup', 'unit', 'disease']
