from django.shortcuts import render
from rest_framework import views, permissions, serializers
from rest_framework.response import Response
from .serializers import PatientRegistrationSerializer, PatientSerializer, DoctorSerializer, AvailabilitySerializer, AppointmentSerializer, HolidaySerializer, DoctorLeaveSerializer
from .models import Patient, Doctor, Availability, Appointment, Holiday, DoctorLeave
from rest_framework import viewsets
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, DoctorPermission, AvailabilityPermission, AppointmentPermission
from django.db import transaction
from django.db import IntegrityError
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
            return Response(serializer.errors, status=400)
        
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
        

class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [AppointmentPermission]
    
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
    filterset_fields = ['status', 'date', 'doctor', 'patient']
    
    ordering_fields = ['date', 'time', 'status']
    
    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            'doctor',
            'patient'
        )

        if self.request.user.role == 'admin':
            return queryset

        if self.request.user.role == 'doctor':
            return queryset.filter(doctor__user=self.request.user)

        if self.request.user.role == 'patient':
            return queryset.filter(patient__user=self.request.user)       
        
    def perform_create(self, serializer):
        
        try:
            with transaction.atomic():
                
                doctor = serializer.validated_data['doctor']
                doctor = Doctor.objects.select_for_update().get(id=doctor.id)
            
                if self.request.user.role == "patient":
                    patient = Patient.objects.get(user=self.request.user)
                    
                else:
                    patient = serializer.validated_data['patient']
                
                serializer.save(patient=patient)

        except IntegrityError:
            raise serializers.ValidationError(
                "This appointment slot is already booked."
            )
            

class HolidayViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrReadOnly
    ]
    
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    

class DoctorLeaveViewSet(viewsets.ModelViewSet):
    permission_classes = [AvailabilityPermission]
    
    queryset = DoctorLeave.objects.all()
    serializer_class = DoctorLeaveSerializer
    
    def perform_create(self, serializer):
        if self.request.user.role == "doctor":
            doctor = Doctor.objects.get(user=self.request.user)
        else:
            doctor = serializer.validated_data['doctor']

        serializer.save(doctor=doctor)