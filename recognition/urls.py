from django.urls import path, include
from .views import start, stop, status, add_contact, sos_alert, danger_zone_check

urlpatterns = [
    path('start/', start, name='start'),
    path('stop/', stop, name='stop'),
    path('status/', status, name='status'),
    path('add_contact/', add_contact, name='add_contact'),
    path('sos/', sos_alert, name='sos_alert'),
    path('danger_zone/', danger_zone_check, name='danger_zone_check'),
    #path('api/', include('recognition.urls')),  # Include 'recognition' app URLs
]

