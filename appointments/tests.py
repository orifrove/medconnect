from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser, DoctorProfile
from .models import TimeSlot, Appointment


class TimeSlotTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = CustomUser.objects.create_user(
            email='doctor@test.com',
            username='doctor1',
            password='StrongPass123!',
            role='doctor'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Кардиолог',
            license_number='LIC-001',
            experience_years=5,
            consultation_fee='1500.00'
        )
        self.patient_user = CustomUser.objects.create_user(
            email='patient@test.com',
            username='patient1',
            password='StrongPass123!',
            role='patient'
        )

    def test_doctor_can_create_slot(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            'doctor': self.doctor_profile.id,
            'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post(reverse('timeslot-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patient_cannot_create_slot(self):
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'doctor': self.doctor_profile.id,
            'start_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post(reverse('timeslot-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_slot_in_past(self):
        self.client.force_authenticate(user=self.doctor_user)
        data = {
            'doctor': self.doctor_profile.id,
            'start_time': (timezone.now() - timedelta(days=1)).isoformat(),
            'end_time': (timezone.now() - timedelta(hours=23)).isoformat(),
        }
        response = self.client.post(reverse('timeslot-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AppointmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = CustomUser.objects.create_user(
            email='doctor2@test.com',
            username='doctor2',
            password='StrongPass123!',
            role='doctor'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Терапевт',
            license_number='LIC-002',
            experience_years=3,
            consultation_fee='1000.00'
        )
        self.patient_user = CustomUser.objects.create_user(
            email='patient2@test.com',
            username='patient2',
            password='StrongPass123!',
            role='patient'
        )
        self.slot = TimeSlot.objects.create(
            doctor=self.doctor_profile,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1)
        )

    def test_patient_can_create_appointment(self):
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'doctor': self.doctor_profile.id,
            'time_slot': self.slot.id,
            'reason': 'Болит голова'
        }
        response = self.client.post(reverse('appointment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_book_same_slot_twice(self):
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'doctor': self.doctor_profile.id,
            'time_slot': self.slot.id,
            'reason': 'Болит голова'
        }
        self.client.post(reverse('appointment-list'), data, format='json')
        response = self.client.post(reverse('appointment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_appointment(self):
        appointment = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor_profile,
            time_slot=self.slot,
            status='confirmed'
        )
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.post(
            reverse('appointment-cancel', kwargs={'pk': appointment.id}),
            {'confirm': True},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')