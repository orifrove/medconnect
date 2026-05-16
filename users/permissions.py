from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_doctor


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.user == request.user


class IsAppointmentParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in (obj.patient, obj.doctor.user)