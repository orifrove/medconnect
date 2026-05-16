from rest_framework import serializers
from .models import Message
from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_detail = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'is_read', 'created_at', 'sender_detail']
        read_only_fields = ['sender', 'is_read', 'created_at']

    def validate(self, attrs):
        request = self.context['request']

        if attrs['receiver'] == request.user:
            raise serializers.ValidationError('Нельзя отправить сообщение самому себе')

        return attrs

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)