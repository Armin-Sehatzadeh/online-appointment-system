from django.shortcuts import render
from rest_framework import views, permissions
from rest_framework.response import Response
from .serializers import PatientRegistrationSerializer, PatientSerializer
from .models import Patient
from rest_framework import viewsets

# Create your views here.


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
        

class RegisterView(views.APIView):
    
    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors)
        
        patient = serializer.save()
        patient_serializer = PatientSerializer( patient )

        return Response(patient_serializer.data)