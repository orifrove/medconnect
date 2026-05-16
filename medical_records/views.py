from rest_framework import viewsets, permissions
from .models import MedicalRecord, Review
from .serializers import MedicalRecordSerializer, ReviewSerializer
from users.permissions import IsDoctor, IsPatient


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor:
            return MedicalRecord.objects.filter(
                appointment__doctor=user.doctor_profile
            ).select_related('appointment')
        return MedicalRecord.objects.filter(
            appointment__patient=user
        ).select_related('appointment')


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor:
            return Review.objects.filter(doctor=user.doctor_profile)
        return Review.objects.filter(patient=user)