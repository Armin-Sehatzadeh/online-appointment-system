from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
        )
        
class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            (request.user.is_authenticated and request.user.role == 'admin')
            or
            request.user == obj.user
        )
        
class DoctorPermission(BasePermission):
    
    def has_permission(self, request, view):
        
        return request.user.is_authenticated
        
    
    def has_object_permission(self, request, view, obj):
        if (request.user.role == 'admin'):
            return True
        
        if (request.user.role == 'patient' and request.method in SAFE_METHODS):
            return True

        if (request.user.role == 'doctor' and request.method in SAFE_METHODS):
            return request.user == obj.user
        
        return False
        

class AvailabilityPermission(BasePermission):
        
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in ['admin', 'doctor']
            
        
    def has_object_permission(self, request, view, obj):
        
        if (request.user.role == 'admin'):
            return True

        if (request.user.role == 'patient' and request.method in SAFE_METHODS):
            return True
        
        if (request.user.role == 'doctor'):
            return request.user == obj.doctor.user
        
        return False
        

        
class AppointmentPermission(BasePermission):
    
    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        if request.method == 'POST' and not request.user.role in ['admin', 'patient']:
            return False
        
        return True
        
    def has_object_permission(self, request, view, obj):
        
        if (request.user.role == 'admin'):
            return True

        if (request.user.role == 'patient'  and request.method in ['GET','DELETE']):
            return request.user == obj.patient.user
        
        if (request.user.role == 'doctor' and request.method in ['GET', 'PATCH', 'PUT', 'DELETE']):
            return request.user == obj.doctor.user
        
        return False
    