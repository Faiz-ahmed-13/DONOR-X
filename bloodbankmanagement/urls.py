from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from blood import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('donor/', include('donor.urls')),
    path('patient/', include('patient.urls')),
    path('logout', views.logout_view, name='logout'),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),
    path('admin-login', views.admin_login_view, name='admin-login'),
    
    # ✅ ALL ADMIN VIEWS (exact matches from your views.py):
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),
    path('admin-blood', views.admin_blood_view, name='admin-blood'),
    path('admin-donor', views.admin_donor_view, name='admin-donor'),
    path('admin-patient', views.admin_patient_view, name='admin-patient'),
    path('admin-request', views.admin_request_view, name='admin-request'),
    path('admin-donation', views.admin_donation_view, name='admin-donation'),
    
    # ✅ STATUS UPDATES (exact matches):
    path('update-approve-status/<int:pk>', views.update_approve_status_view, name='update-approve-status'),
    path('update-reject-status/<int:pk>', views.update_reject_status_view, name='update-reject-status'),
    
    # ✅ DONATION APPROVAL (NO _view suffix):
    path('approve-donation/<int:donation_id>', views.approve_donation, name='approve-donation'),
    path('reject-donation/<int:donation_id>', views.reject_donation, name='reject-donation'),
    
    # ✅ UPDATE/DELETE (exact matches):
    path('update-donor/<int:pk>', views.update_donor_view, name='update-donor'),
    path('delete-donor/<int:pk>', views.delete_donor_view, name='delete-donor'),
    path('update-patient/<int:pk>', views.update_patient_view, name='update-patient'),
    path('delete-patient/<int:pk>', views.delete_patient_view, name='delete-patient'),
    
    # ✅ PREDICTION:
    path('predict-donation', views.predict_donation, name='predict_donation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
