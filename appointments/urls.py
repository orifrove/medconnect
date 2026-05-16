from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeSlotViewSet, AppointmentViewSet

router = DefaultRouter()
router.register(r'timeslots', TimeSlotViewSet, basename='timeslot')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]