from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser, DoctorProfile
from appointments.models import TimeSlot, Appointment
from .models import Review


class ReviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = CustomUser.objects.create_user(
            email='doctor3@test.com',
            username='doctor3',
            password='StrongPass123!',
            role='doctor'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Хирург',
            license_number='LIC-003',
            experience_years=10,
            consultation_fee='2000.00'
        )
        self.patient_user = CustomUser.objects.create_user(
            email='patient3@test.com',
            username='patient3',
            password='StrongPass123!',
            role='patient'
        )
        slot = TimeSlot.objects.create(
            doctor=self.doctor_profile,
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now() - timedelta(hours=23)
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor_profile,
            time_slot=slot,
            status='completed'
        )

    def test_patient_can_leave_review_after_completed_visit(self):
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'doctor': self.doctor_profile.id,
            'score': 5,
            'comment': 'Отличный врач!'
        }
        response = self.client.post(reverse('review-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rating_updates_after_review(self):
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'doctor': self.doctor_profile.id,
            'score': 4,
            'comment': 'Хороший врач'
        }
        self.client.post(reverse('review-list'), data, format='json')
        self.doctor_profile.refresh_from_db()
        self.assertEqual(float(self.doctor_profile.rating), 4.0)

    def test_cannot_review_without_completed_visit(self):
        new_patient = CustomUser.objects.create_user(
            email='newpatient@test.com',
            username='newpatient',
            password='StrongPass123!',
            role='patient'
        )
        self.client.force_authenticate(user=new_patient)
        data = {
            'doctor': self.doctor_profile.id,
            'score': 5,
            'comment': 'Тест'
        }
        response = self.client.post(reverse('review-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)