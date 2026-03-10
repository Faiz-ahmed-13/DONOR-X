from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blood.urls')),  # Include the blood app's URLs at root level
    # Add other routes here
]