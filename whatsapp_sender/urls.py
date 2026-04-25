# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/debug/', views.get_debug_info, name='debug'),
    path('api/check-connection/', views.check_connection, name='check_connection'),
    path('api/reconnect/', views.reconnect_whatsapp, name='reconnect'),
    path('api/generate-message/', views.generate_ai_message, name='generate_message'),
    path('api/send-messages/', views.send_messages, name='send_messages'),
    path('api/check-numbers/', views.check_numbers, name='check_numbers'),
]