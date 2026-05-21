from django.contrib import admin
from .models import TimeSlot, Appointment


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'doctor']
    search_fields = ['doctor__user__email']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'time_slot', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['patient__email', 'doctor__user__email']