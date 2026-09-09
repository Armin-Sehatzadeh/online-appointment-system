from django.shortcuts import render
from rest_framework import views, permissions
from rest_framework.response import Response
from .serializers import PatientRegistrationSerializer, PatientSerializer, DoctorSerializer, AvailabilitySerializer
from .models import Patient, Doctor, Availability
from rest_framework import viewsets
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, DoctorPermission, AvailabilityPermission

# Create your views here.


class PatientViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin, IsAdminOrReadOnly]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Patient.objects.all()
        
        return Patient.objects.filter(user=self.request.user)
        

class DoctorViewSet(viewsets.ModelViewSet):
    permission_classes = [DoctorPermission]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
    def get_queryset(self):
        if self.request.user.role in ['admin', 'patient']:
            return Doctor.objects.all()
        
        return Doctor.objects.filter(user=self.request.user)
        
      
    
class RegisterView(views.APIView):
    
    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors)
        
        patient = serializer.save()
        patient_serializer = PatientSerializer( patient )

        return Response(patient_serializer.data)
    

class AvailabilityViewSet(viewsets.ModelViewSet):
    permission_classes = [AvailabilityPermission]
    
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    
    def get_queryset(self):
        
        if self.request.user.role in ['admin', 'patient']:
            return Availability.objects.all()
    

        return Availability.objects.filter(doctor__user=self.request.user)
    
    def perform_create(self, serializer):
        
        if self.request.user.role == "doctor":
            doctor = Doctor.objects.get(user=self.request.user)
            
        else:
            doctor = serializer.validated_data['doctor']
            
        serializer.save(doctor=doctor)