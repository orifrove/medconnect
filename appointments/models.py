from django.db import models
from django.utils import timezone
from users.models import CustomUser, DoctorProfile


class TimeSlot(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_slots', verbose_name='Врач')
    start_time = models.DateTimeField(verbose_name='Начало')
    end_time = models.DateTimeField(verbose_name='Конец')
    is_booked = models.BooleanField(default=False, verbose_name='Занят')

    class Meta:
        verbose_name = 'Временной слот'
        verbose_name_plural = 'Временные слоты'
        ordering = ['start_time']

    def __str__(self):
        return f'{self.doctor} | {self.start_time.strftime("%d.%m.%Y %H:%M")}'

    @property
    def is_future(self):
        return self.start_time > timezone.now()


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        CANCELLED = 'cancelled', 'Отменена'
        COMPLETED = 'completed', 'Завершена'

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments', verbose_name='Пациент')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments', verbose_name='Врач')
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment', verbose_name='Временной слот')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='Статус')
    reason = models.TextField(blank=True, verbose_name='Причина визита')
    doctor_notes = models.TextField(blank=True, verbose_name='Заметки врача')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient.email} → {self.doctor} [{self.status}]'

    def cancel(self):
        if self.status == self.Status.COMPLETED:
            raise ValueError('Нельзя отменить завершённый приём')
        if self.status == self.Status.CANCELLED:
            raise ValueError('Запись уже отменена')
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status', 'updated_at'])
        self.time_slot.is_booked = False
        self.time_slot.save(update_fields=['is_booked'])