from django.urls import path
from appointments import views

urlpatterns = [
    path('<int:product_id>/', views.appointments, name='appointments'),
    path('purchase_appointment/<int:product_id>/', views.purchaseAppointment, name='purchase_appointment'),
    path('appointment_calendar/', views.appointmentCalendar.as_view(), name='appointment_calendar'),
    path('appointment_details/<int:appointment_details_id>/', views.appointmentDetails, name='appointment_details'),
    path('confirm_appointment/<int:appointment_details_id>/', views.confirmAppointment, name='confirm_appointment'),
    path('update_appointment/<int:appointment_details_id>/', views.updateAppointment, name='update_appointment'),
    path('delete_appointment/<int:appointment_details_id>/', views.deleteAppointment, name='delete_appointment'),
]