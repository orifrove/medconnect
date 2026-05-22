from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, DoctorProfile, PatientProfile


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_doctor(self):
        data = {
            'email': 'doctor@test.com',
            'username': 'doctor1',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'doctor_profile': {
                'specialization': 'Кардиолог',
                'license_number': 'LIC-001',
                'experience_years': 5,
                'consultation_fee': '1500.00'
            }
        }
        response = self.client.post(reverse('register-doctor'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(DoctorProfile.objects.count(), 1)

    def test_register_patient(self):
        data = {
            'email': 'patient@test.com',
            'username': 'patient1',
            'first_name': 'Мария',
            'last_name': 'Петрова',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(reverse('register-patient'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PatientProfile.objects.count(), 1)

    def test_register_password_mismatch(self):
        data = {
            'email': 'test@test.com',
            'username': 'test1',
            'password': 'StrongPass123!',
            'password2': 'WrongPass123!',
        }
        response = self.client.post(reverse('register-patient'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        CustomUser.objects.create_user(
            email='login@test.com',
            username='loginuser',
            password='StrongPass123!',
            role='patient'
        )
        response = self.client.post(reverse('token-obtain-pair'), {
            'email': 'login@test.com',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_me_endpoint(self):
        user = CustomUser.objects.create_user(
            email='me@test.com',
            username='meuser',
            password='StrongPass123!',
            role='patient'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@test.com')

    def test_me_unauthorized(self):
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_email(self):
        CustomUser.objects.create_user(
            email='dup@test.com',
            username='dup1',
            password='StrongPass123!',
            role='patient'
        )
        data = {
            'email': 'dup@test.com',
            'username': 'dup2',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(reverse('register-patient'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
