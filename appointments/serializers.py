from rest_framework import serializers
from django.utils import timezone
from .models import TimeSlot, Appointment
from users.serializers import DoctorProfileSerializer, UserSerializer


class TimeSlotSerializer(serializers.ModelSerializer):
    is_future = serializers.ReadOnlyField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor', 'start_time', 'end_time', 'is_booked', 'is_future']
        read_only_fields = ['is_booked']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('Время начала должно быть раньше времени конца')

        if attrs['start_time'] < timezone.now():
            raise serializers.ValidationError('Нельзя создать слот в прошлом')

        overlapping = TimeSlot.objects.filter(
            doctor=attrs['doctor'],
            start_time__lt=attrs['end_time'],
            end_time__gt=attrs['start_time']
        ).exists()

        if overlapping:
            raise serializers.ValidationError('У врача уже есть слот в это время')

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    patient_detail = UserSerializer(source='patient', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'time_slot', 'status',
                  'reason', 'doctor_notes', 'created_at', 'updated_at',
                  'doctor_detail', 'patient_detail']
        read_only_fields = ['patient', 'status', 'doctor_notes', 'created_at', 'updated_at']

    def validate(self, attrs):
        time_slot = attrs['time_slot']
        request = self.context['request']

        if time_slot.is_booked:
            raise serializers.ValidationError('Этот слот уже занят')

        if not time_slot.is_future:
            raise serializers.ValidationError('Нельзя записаться на прошедшее время')

        if time_slot.doctor != attrs['doctor']:
            raise serializers.ValidationError('Слот не принадлежит этому врачу')

        already_booked = Appointment.objects.filter(
            patient=request.user,
            doctor=attrs['doctor'],
            status__in=['pending', 'confirmed']
        ).exists()

        if already_booked:
            raise serializers.ValidationError('У вас уже есть активная запись к этому врачу')

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['patient'] = request.user

        time_slot = validated_data['time_slot']
        time_slot.is_booked = True
        time_slot.save(update_fields=['is_booked'])

        return super().create(validated_data)


class AppointmentCancelSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError('Подтвердите отмену записи')
        return value