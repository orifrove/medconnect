from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver')

    @action(detail=False, methods=['get'], url_path='conversation/(?P<user_id>[^/.]+)')
    def conversation(self, request, user_id=None):
        user = request.user
        messages = Message.objects.filter(
            Q(sender=user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=user)
        ).order_by('created_at')

        messages.filter(receiver=user, is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)