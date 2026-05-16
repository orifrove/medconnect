from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterDoctorView, RegisterPatientView, MeView, DoctorViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('auth/register/doctor/', RegisterDoctorView.as_view(), name='register-doctor'),
    path('auth/register/patient/', RegisterPatientView.as_view(), name='register-patient'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]