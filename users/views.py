from rest_framework import generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import CustomUser, DoctorProfile
from .serializers import (
    RegisterDoctorSerializer, RegisterPatientSerializer,
    UserSerializer, DoctorProfileSerializer
)
from .permissions import IsDoctor, IsOwnerOrReadOnly


class RegisterDoctorView(generics.CreateAPIView):
    serializer_class = RegisterDoctorSerializer
    permission_classes = [permissions.AllowAny]


class RegisterPatientView(generics.CreateAPIView):
    serializer_class = RegisterPatientSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['specialization', 'user__first_name', 'user__last_name']
    ordering_fields = ['rating', 'experience_years', 'consultation_fee']

    def get_queryset(self):
        return DoctorProfile.objects.filter(is_available=True).select_related('user')

    @action(detail=True, methods=['get'], url_path='slots')
    def free_slots(self, request, pk=None):
        from appointments.models import TimeSlot
        from appointments.serializers import TimeSlotSerializer
        from django.utils import timezone

        doctor = self.get_object()
        slots = TimeSlot.objects.filter(
            doctor=doctor,
            is_booked=False,
            start_time__gt=timezone.now()
        )
        serializer = TimeSlotSerializer(slots, many=True)
        return Response(serializer.data)