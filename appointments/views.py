from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TimeSlot, Appointment
from .serializers import TimeSlotSerializer, AppointmentSerializer, AppointmentCancelSerializer
from users.permissions import IsDoctor, IsPatient


class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor and hasattr(user, 'doctor_profile'):
            return TimeSlot.objects.filter(doctor=user.doctor_profile)
        return TimeSlot.objects.filter(is_booked=False)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctor_profile)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor and hasattr(user, 'doctor_profile'):
            return Appointment.objects.filter(
                doctor=user.doctor_profile
            ).select_related('patient', 'doctor', 'time_slot')
        return Appointment.objects.filter(
            patient=user
        ).select_related('patient', 'doctor', 'time_slot')

    def get_permissions(self):
        if self.action == 'create':
            return [IsPatient()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if request.user != appointment.patient and request.user != appointment.doctor.user:
            return Response({'detail': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            appointment.cancel()
            return Response({'detail': 'Запись отменена'})
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='complete', permission_classes=[IsDoctor])
    def complete(self, request, pk=None):
        appointment = self.get_object()

        if appointment.doctor.user != request.user:
            return Response({'detail': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)

        appointment.status = Appointment.Status.COMPLETED
        appointment.doctor_notes = request.data.get('doctor_notes', '')
        appointment.save(update_fields=['status', 'doctor_notes', 'updated_at'])

        return Response(AppointmentSerializer(appointment).data)