from django.contrib import admin
from .models import MedicalRecord, Review


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'diagnosis', 'next_visit_date', 'created_at']
    search_fields = ['diagnosis', 'appointment__patient__email']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'score', 'created_at']
    list_filter = ['score']
    search_fields = ['patient__email', 'doctor__user__email']