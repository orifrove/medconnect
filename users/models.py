from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator


def doctor_photo_path(instance, filename):
    return f'doctors/{instance.user.id}/{filename}'


def patient_photo_path(instance, filename):
    return f'patients/{instance.user.id}/{filename}'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'doctor')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        DOCTOR = 'doctor', 'Врач'
        PATIENT = 'patient', 'Пациент'

    role = models.CharField(max_length=10, choices=Role.choices, verbose_name='Роль')
    email = models.EmailField(unique=True, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT


class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, verbose_name='Специализация')
    license_number = models.CharField(max_length=50, unique=True, verbose_name='Номер лицензии')
    experience_years = models.PositiveIntegerField(default=0, verbose_name='Опыт (лет)')
    bio = models.TextField(blank=True, verbose_name='О враче')
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Стоимость приёма')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='Рейтинг')
    reviews_count = models.PositiveIntegerField(default=0, verbose_name='Количество отзывов')
    photo = models.ImageField(upload_to=doctor_photo_path, null=True, blank=True, verbose_name='Фото')
    is_available = models.BooleanField(default=True, verbose_name='Принимает пациентов')

    class Meta:
        verbose_name = 'Профиль врача'
        verbose_name_plural = 'Профили врачей'

    def __str__(self):
        return f'Др. {self.user.get_full_name()} — {self.specialization}'

    def update_rating(self, new_score):
        total_score = float(self.rating) * self.reviews_count + new_score
        self.reviews_count += 1
        self.rating = round(total_score / self.reviews_count, 2)
        self.save(update_fields=['rating', 'reviews_count'])


class PatientProfile(models.Model):
    class BloodType(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    blood_type = models.CharField(max_length=3, choices=BloodType.choices, null=True, blank=True, verbose_name='Группа крови')
    allergies = models.TextField(blank=True, verbose_name='Аллергии')
    chronic_diseases = models.TextField(blank=True, verbose_name='Хронические заболевания')
    insurance_number = models.CharField(max_length=50, blank=True, verbose_name='Номер полиса')
    photo = models.ImageField(upload_to=patient_photo_path, null=True, blank=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Профиль пациента'
        verbose_name_plural = 'Профили пациентов'

    def __str__(self):
        return f'Пациент: {self.user.get_full_name()}'