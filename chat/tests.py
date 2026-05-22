from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class MessageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            email='user1@test.com',
            username='user1',
            password='StrongPass123!',
            role='patient'
        )
        self.user2 = CustomUser.objects.create_user(
            email='user2@test.com',
            username='user2',
            password='StrongPass123!',
            role='doctor'
        )

    def test_send_message(self):
        self.client.force_authenticate(user=self.user1)
        data = {'receiver': self.user2.id, 'text': 'Здравствуйте доктор!'}
        response = self.client.post(reverse('message-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_message_yourself(self):
        self.client.force_authenticate(user=self.user1)
        data = {'receiver': self.user1.id, 'text': 'Привет себе'}
        response = self.client.post(reverse('message-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_conversation_endpoint(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            reverse('message-conversation', kwargs={'user_id': self.user2.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_cannot_send(self):
        data = {'receiver': self.user2.id, 'text': 'Тест'}
        response = self.client.post(reverse('message-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)