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
from django.contrib.auth import authenticate, login, logout
from blood import views as b
from blood import models as blood_models


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)

        if userForm.is_valid() and patientForm.is_valid():
            try:
                # Check if username already exists
                if User.objects.filter(username=userForm.cleaned_data['username']).exists():
                    messages.error(request, 'Username already exists. Please choose a different username.')
                    return render(request, 'patient/patientsignup.html', context=mydict)

                # Create user
                user = userForm.save(commit=False)
                user.set_password(userForm.cleaned_data['password'])
                user.save()

                # Create patient profile
                patient = patientForm.save(commit=False)
                patient.user = user
                patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
                patient.save()

                # Add user to patient group
                my_patient_group = Group.objects.get_or_create(name='PATIENT')
                my_patient_group[0].user_set.add(user)

                messages.success(request, 'Patient account created successfully! Please login.')
                return redirect('patientlogin')

            except Exception as e:
                messages.error(request, f'An error occurred while creating your account: {str(e)}')
                return render(request, 'patient/patientsignup.html', context=mydict)
        else:
            messages.error(request, 'Please correct the errors below.')
            if not userForm.is_valid():
                for field, errors in userForm.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            if not patientForm.is_valid():
                for field, errors in patientForm.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

    return render(request, 'patient/patientsignup.html', context=mydict)

@login_required(login_url='patientlogin')  # ✅ FIXED: was 'patient-login'
def patient_dashboard_view(request):
    try:
        patient = models.Patient.objects.get(user_id=request.user.id)
    except models.Patient.DoesNotExist:
        # Create a new patient record if it doesn't exist
        patient = models.Patient.objects.create(
            user=request.user,
            bloodgroup='A+',  # Default blood group, user can update later
            address='Please update your address',
            mobile='0000000000',  # Default mobile number
            age=1,  # Minimum valid age
            profile_pic=None,
            disease='None',
            doctorname='Please update your doctor name'  # Required field
        )
        messages.warning(request, "Please update your profile with your correct age, blood group, doctor name, and contact information.")

    # Get blood requests for this patient
    blood_requests = blood_models.BloodRequest.objects.filter(request_by_patient=patient).order_by('-date')

    # Get blood donation statistics
    total_requests = blood_requests.count()
    approved_requests = blood_requests.filter(status='Approved').count()
    pending_requests = blood_requests.filter(status='Pending').count()
    rejected_requests = blood_requests.filter(status='Rejected').count()

    context = {
        'patient': patient,
        'blood_requests': blood_requests,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'pending_requests': pending_requests,
        'rejected_requests': rejected_requests,
    }

    return render(request, 'patient/patient_dashboard.html', context)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return HttpResponseRedirect('my-request')
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    blood_request = models.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request, 'patient/my_request.html', {'blood_request': blood_request})

def patient_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and b.is_patient(user):
            login(request, user)
            return redirect('patient-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a patient')
    form = forms.PatientUserForm()
    return render(request, 'patient/patient_login.html', {'form': form})

@login_required(login_url='patientlogin')  # ✅ FIXED: was 'patient-login'
def request_blood_view(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        reason = request.POST.get('reason')
        bloodgroup = request.user.patient.bloodgroup

        blood_request = blood_models.BloodRequest(
            request_by_patient=request.user.patient,
            bloodgroup=bloodgroup,
            unit=unit,
            reason=reason,
            status='Pending'
        )
        blood_request.save()

        messages.success(request, 'Your blood request has been submitted successfully!')
        return render(request, 'patient/request_success.html', {
            'request': blood_request,
            'patient': request.user.patient
        })

    return render(request, 'patient/request_blood.html', {'patient': request.user.patient})
