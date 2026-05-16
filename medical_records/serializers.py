from rest_framework import serializers
from .models import MedicalRecord, Review


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'appointment', 'diagnosis', 'prescription',
                  'recommendations', 'next_visit_date', 'created_at']
        read_only_fields = ['created_at']

    def validate_appointment(self, value):
        if value.status != 'completed':
            raise serializers.ValidationError('Можно создать карту только для завершённого приёма')

        if hasattr(value, 'medical_record'):
            raise serializers.ValidationError('Карта для этого приёма уже существует')

        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'patient', 'doctor', 'score', 'comment', 'created_at']
        read_only_fields = ['patient', 'created_at']

    def validate(self, attrs):
        request = self.context['request']

        completed_visit = attrs['doctor'].appointments.filter(
            patient=request.user,
            status='completed'
        ).exists()

        if not completed_visit:
            raise serializers.ValidationError('Вы можете оставить отзыв только после завершённого приёма')

        already_reviewed = Review.objects.filter(
            patient=request.user,
            doctor=attrs['doctor']
        ).exists()

        if already_reviewed:
            raise serializers.ValidationError('Вы уже оставили отзыв этому врачу')

        return attrs

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)