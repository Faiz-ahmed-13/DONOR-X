from django.urls import path
from . import views

urlpatterns = [
    path('patientlogin/', views.patient_login_view, name='patientlogin'),
    path('patientsignup/', views.patient_signup_view, name='patientsignup'),
    path('patient-dashboard/', views.patient_dashboard_view, name='patient-dashboard'),
    path('request-blood/', views.request_blood_view, name='request-blood'),
]
