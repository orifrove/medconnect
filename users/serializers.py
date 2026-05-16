from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, DoctorProfile, PatientProfile


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['id', 'specialization', 'license_number', 'experience_years',
                  'bio', 'consultation_fee', 'rating', 'reviews_count', 'photo', 'is_available']
        read_only_fields = ['rating', 'reviews_count']


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'date_of_birth', 'blood_type', 'allergies',
                  'chronic_diseases', 'insurance_number', 'photo']


class UserSerializer(serializers.ModelSerializer):
    doctor_profile = DoctorProfileSerializer(read_only=True)
    patient_profile = PatientProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'role', 'created_at', 'doctor_profile', 'patient_profile']
        read_only_fields = ['created_at']


class RegisterDoctorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    profile = DoctorProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2', 'profile']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        validated_data.pop('password2')

        user = CustomUser.objects.create_user(
            **validated_data,
            role=CustomUser.Role.DOCTOR
        )

        DoctorProfile.objects.create(user=user, **profile_data)
        return user


class RegisterPatientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    profile = PatientProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2', 'profile']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        validated_data.pop('password2')

        user = CustomUser.objects.create_user(
            **validated_data,
            role=CustomUser.Role.PATIENT
        )

        PatientProfile.objects.create(user=user, **profile_data)
        return user