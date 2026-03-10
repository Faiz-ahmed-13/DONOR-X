from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from django.contrib import messages
from django.contrib.auth import authenticate, login
from blood import views as b

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
            messages.success(request, 'Donor account created successfully! Please login.')
            return redirect('donorlogin')
        else:
            messages.error(request, 'Please correct the errors below.')
    mydict={'userForm':userForm,'donorForm':donorForm}
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donations = bmodels.BloodDonate.objects.filter(donor=donor)
    
    dict = {
        'pending_donations': donations.filter(status='Pending').count(),
        'approved_donations': donations.filter(status='Approved').count(),
        'total_donations': donations.count(),
        'rejected_donations': donations.filter(status='Rejected').count(),
        'recent_donations': donations.order_by('-date')[:5],
        'donor': donor
    }
    return render(request, 'donor/donor_dashboard.html', context=dict)


@login_required(login_url='donor-login')
def donate_blood_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        bloodgroup = request.POST.get('bloodgroup')
        unit = request.POST.get('unit')
        disease = request.POST.get('disease', 'None')
        
        if not bloodgroup or not unit:
            messages.error(request, 'Please provide both blood group and units')
            return render(request, 'donor/donate_blood.html', {'donor': donor})
            
        try:
            blood_donate = bmodels.BloodDonate(
                donor=donor,
                disease=disease if disease else 'None',
                bloodgroup=bloodgroup,
                unit=int(unit),
                age=donor.age
            )
            blood_donate.save()
            messages.success(request, 'Blood donation request submitted successfully!')
            return render(request, 'donor/donation_success.html', {
                'donation': blood_donate,
                'donor': donor
            })
        except Exception as e:
            messages.error(request, f'Error submitting donation: {str(e)}')
            
    return render(request, 'donor/donate_blood.html', {'donor': donor})

def donation_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donations = bmodels.BloodDonate.objects.filter(donor=donor).order_by('-date')
    return render(request, 'donor/donation_history.html', {'donations': donations})

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})

def donor_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and b.is_donor(user):
            login(request, user)
            return redirect('donor-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a donor')
    form = forms.DonorUserForm()
    return render(request, 'donor/donor_login.html', {'form': form})