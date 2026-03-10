from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
import joblib
import pandas as pd
import os
import pickle
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from donor import models as donor_models
import random

def home(request):
    """Professional DONOR-X Homepage for Recruiters & Hospitals"""
    total_donors = dmodels.Donor.objects.count()
    total_patients = pmodels.Patient.objects.count()
    total_requests = models.BloodRequest.objects.count()
    total_donations = dmodels.BloodDonate.objects.filter(status='Approved').count()
    
    blood_stock = {
        'A+': random.randint(10, 50),
        'A-': random.randint(5, 30),
        'B+': random.randint(10, 50),
        'B-': random.randint(5, 30),
        'O+': random.randint(15, 60),
        'O-': random.randint(5, 30),
        'AB+': random.randint(5, 25),
        'AB-': random.randint(2, 15)
    }
    
    context = {
        'total_donors': total_donors,
        'total_patients': total_patients,
        'total_requests': total_requests,
        'total_donations': total_donations,
        'blood_stock': blood_stock,
    }
    return render(request, 'blood/index.html', context)

# Load the trained model
model_path = os.path.join(os.path.dirname(__file__), '../ML_Models/transfusion_model.pkl')
try:
    model = joblib.load(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@login_required(login_url='donorlogin')
def donor_dashboard_view(request):
    donations = donor_models.BloodDonate.objects.filter(donor=request.user.donor).order_by('-date')
    return render(request, 'donor/donor_dashboard.html', {'donations': donations})

@login_required(login_url='donorlogin')
def donate_blood_view(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        bloodgroup = request.user.donor.bloodgroup
        
        donation = donor_models.BloodDonate(
            donor=request.user.donor,
            bloodgroup=bloodgroup,
            unit=unit,
            status='Pending'
        )
        donation.save()
        
        messages.success(request, 'Blood donation request submitted successfully!')
        return redirect('donor-dashboard')
    
    return redirect('donor-dashboard')

def index(request):
    # Generate random blood stock numbers
    blood_stock = {
        'A_plus': random.randint(10, 50),
        'A_minus': random.randint(5, 30),
        'B_plus': random.randint(10, 50),
        'B_minus': random.randint(5, 30),
        'O_plus': random.randint(15, 60),
        'O_minus': random.randint(5, 30),
        'AB_plus': random.randint(5, 25),
        'AB_minus': random.randint(2, 15)
    }
    
    return render(request, 'blood/index.html', {'blood_stock': blood_stock})

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()

def afterlogin_view(request):
    if is_donor(request.user):
        return redirect('donor-dashboard')
    elif is_patient(request.user):
        return redirect('patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='patientlogin')
def patient_dashboard_view(request):
    requests = models.BloodRequest.objects.filter(request_by_patient=request.user.patient).order_by('-date')
    return render(request, 'patient/patient_dashboard.html', {'requests': requests})

@login_required(login_url='patientlogin')
def request_blood_view(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        reason = request.POST.get('reason')
        bloodgroup = request.user.patient.bloodgroup
        
        blood_request = models.BloodRequest(
            request_by_patient=request.user.patient,
            bloodgroup=bloodgroup,
            unit=unit,
            reason=reason,
            status='Pending'
        )
        blood_request.save()
        
        messages.success(request, 'Blood request submitted successfully!')
        return redirect('patient-dashboard')
    
    return redirect('patient-dashboard')

@login_required(login_url='admin-login')
def admin_dashboard_view(request):
    total_donors = donor_models.Donor.objects.count()
    total_patients = pmodels.Patient.objects.count()
    total_blood_requests = models.BloodRequest.objects.count()
    total_approved_donations = models.BloodDonate.objects.filter(status='Approved').count()
    
    # Get all blood donations that need approval
    pending_donations = models.BloodDonate.objects.filter(status='Pending')
    
    # Get all blood requests
    blood_requests = models.BloodRequest.objects.all().order_by('-date')
    
    # Get current blood stock
    blood_stock = models.Stock.objects.all()
    
    context = {
        'total_donors': total_donors,
        'total_patients': total_patients,
        'total_blood_requests': total_blood_requests,
        'total_approved_donations': total_approved_donations,
        'pending_donations': pending_donations,
        'blood_requests': blood_requests,
        'blood_stock': blood_stock,
    }
    
    return render(request, 'blood/admin_dashboard.html', context)

@login_required(login_url='admin-login')
def update_blood_stock(request):
    if request.method == 'POST':
        bloodgroup = request.POST.get('bloodgroup')
        units = request.POST.get('units')
        
        if not bloodgroup or not units:
            messages.error(request, 'Please provide both blood group and units')
            return redirect('admin-dashboard')
            
        try:
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit = int(units)
            stock.save()
            messages.success(request, f'Blood stock for {bloodgroup} updated successfully!')
        except models.Stock.DoesNotExist:
            stock = models.Stock(bloodgroup=bloodgroup, unit=int(units))
            stock.save()
            messages.success(request, f'Blood stock for {bloodgroup} created successfully!')
        except ValueError:
            messages.error(request, 'Please enter a valid number for units')
        except Exception as e:
            messages.error(request, f'Error updating blood stock: {str(e)}')
            
    return redirect('admin-dashboard')

@login_required(login_url='admin-login')
def approve_donation(request, donation_id):
    try:
        donation = models.BloodDonate.objects.get(id=donation_id)
        donation.status = 'Approved'
        donation.save()
        
        # Update blood stock
        stock = models.Stock.objects.get(bloodgroup=donation.bloodgroup)
        stock.unit += donation.unit
        stock.save()
        
        messages.success(request, 'Blood donation approved successfully!')
    except:
        messages.error(request, 'Error approving donation.')
        
    return redirect('admin-dashboard')

@login_required(login_url='admin-login')
def reject_donation(request, donation_id):
    try:
        donation = models.BloodDonate.objects.get(id=donation_id)
        donation.status = 'Rejected'
        donation.save()
        messages.success(request, 'Blood donation rejected.')
    except:
        messages.error(request, 'Error rejecting donation.')
        
    return redirect('admin-dashboard')

@login_required(login_url='admin-login')
def admin_blood_view(request):
    dict = {
        'bloodForm': forms.BloodForm(),
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method == 'POST':
        bloodForm = forms.BloodForm(request.POST)
        if bloodForm.is_valid():
            bloodgroup = bloodForm.cleaned_data['bloodgroup']
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit = bloodForm.cleaned_data['unit']
            stock.save()
        return HttpResponseRedirect('admin-blood')
    return render(request, 'blood/admin_blood.html', context=dict)

@login_required(login_url='admin-login')
def admin_donor_view(request):
    donors = dmodels.Donor.objects.all()
    return render(request, 'blood/admin_donor.html', {'donors': donors})

@login_required(login_url='admin-login')
def update_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    user = dmodels.User.objects.get(id=donor.user_id)
    userForm = dforms.DonorUserForm(instance=user)
    donorForm = dforms.DonorForm(request.FILES, instance=donor)
    mydict = {'userForm': userForm, 'donorForm': donorForm}
    if request.method == 'POST':
        userForm = dforms.DonorUserForm(request.POST, instance=user)
        donorForm = dforms.DonorForm(request.POST, request.FILES, instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            donor = donorForm.save(commit=False)
            donor.user = user
            donor.bloodgroup = donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request, 'blood/update_donor.html', context=mydict)

@login_required(login_url='admin-login')
def delete_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    user = User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect(reverse('admin-donor'))

@login_required(login_url='admin-login')
def admin_patient_view(request):
    patients = pmodels.Patient.objects.all()
    return render(request, 'blood/admin_patient.html', {'patients': patients})

@login_required(login_url='admin-login')
def update_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    user = pmodels.User.objects.get(id=patient.user_id)
    userForm = pforms.PatientUserForm(instance=user)
    patientForm = pforms.PatientForm(request.FILES, instance=patient)
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = pforms.PatientUserForm(request.POST, instance=user)
        patientForm = pforms.PatientForm(request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request, 'blood/update_patient.html', context=mydict)

@login_required(login_url='admin-login')
def delete_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    user = User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='admin-login')
def admin_request_view(request):
    requests = models.BloodRequest.objects.all().filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests})

@login_required(login_url='admin-login')
def admin_request_history_view(request):
    requests = models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request, 'blood/admin_request_history.html', {'requests': requests})

@login_required(login_url='admin-login')
def admin_donation_view(request):
    donations = dmodels.BloodDonate.objects.all()
    return render(request, 'blood/admin_donation.html', {'donations': donations})

@login_required(login_url='admin-login')
def update_approve_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    message = None
    bloodgroup = req.bloodgroup
    unit = req.unit
    stock = models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit = stock.unit - unit
        stock.save()
        req.status = "Approved"
    else:
        message = "Stock Does Not Have Enough Blood To Approve This Request, Only " + str(stock.unit) + " Unit Available"
    req.save()

    requests = models.BloodRequest.objects.all().filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests, 'message': message})

@login_required(login_url='admin-login')
def update_reject_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    req.status = "Rejected"
    req.save()
    return HttpResponseRedirect(reverse('admin-request'))

from django.http import JsonResponse
import pandas as pd

def predict_donation(request):
    if request.method == 'POST':
        try:
            # Get input data from the form
            recency = float(request.POST.get('Recency'))
            frequency = float(request.POST.get('Frequency'))
            monetary = float(request.POST.get('Monetary'))
            time = float(request.POST.get('Time'))
            
            # Create input data array
            input_data = [[recency, frequency, monetary, time]]
            
            # Make a prediction
            prediction = model.predict(input_data)
            return JsonResponse({'prediction': int(prediction[0])})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'blood/predict.html')  # Template path is correct

def donor_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_donor(user):
            login(request, user)
            return redirect('donor-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a donor')
    form = dforms.DonorUserForm()
    return render(request, 'donor/donor_login.html', {'form': form})

def patient_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_patient(user):
            login(request, user)
            return redirect('patient-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a patient')
    form = pforms.PatientUserForm()
    return render(request, 'patient/patient_login.html', {'form': form})

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'admin/admin_login.html')

def logout_view(request):
    logout(request)
    return redirect('home')