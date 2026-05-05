from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/check-connection/', views.check_connection),
    path('api/generate-message/', views.generate_message),
    path('api/send-messages/', views.send_messages),
    path('api/check-numbers/', views.check_numbers),
    path('api/debug/', views.get_debug),
    path('api/task-status/', views.get_task_status),
    path('api/cancel-task/', views.cancel_task),
]
