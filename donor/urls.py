from django.urls import path
from . import views

urlpatterns = [
    path('donorlogin/', views.donor_login_view, name='donorlogin'),
    path('donorsignup/', views.donor_signup_view, name='donorsignup'),
    path('donor-dashboard/', views.donor_dashboard_view, name='donor-dashboard'),
    path('donate-blood/', views.donate_blood_view, name='donate-blood'),
    path('donation-history/', views.donation_history_view, name='donation-history'),
]