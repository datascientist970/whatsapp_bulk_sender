from django.urls import path, include

urlpatterns = [
    path('', include('whatsapp_sender.urls')),
]