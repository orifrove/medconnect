from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalRecordViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]