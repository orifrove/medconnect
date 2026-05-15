from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser, DoctorProfile
from appointments.models import Appointment


class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record', verbose_name='Запись')
    diagnosis = models.CharField(max_length=255, verbose_name='Диагноз')
    prescription = models.TextField(verbose_name='Назначения')
    recommendations = models.TextField(blank=True, verbose_name='Рекомендации')
    next_visit_date = models.DateField(null=True, blank=True, verbose_name='Следующий визит')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Медицинская карта'
        verbose_name_plural = 'Медицинские карты'

    def __str__(self):
        return f'Карта: {self.appointment}'


class Review(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews', verbose_name='Пациент')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews', verbose_name='Врач')
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Оценка')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['patient', 'doctor']

    def __str__(self):
        return f'{self.patient.email} → {self.doctor} : {self.score}★'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.doctor.update_rating(self.score)