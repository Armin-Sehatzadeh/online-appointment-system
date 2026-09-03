from django.shortcuts import render
from rest_framework import views, permissions
from rest_framework.response import Response
from .serializers import PatientRegistrationSerializer, PatientSerializer

# Create your views here.


class View(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            "username": request.user.username
        })
        

class RegisterView(views.APIView):
    
    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors)
        
        patient = serializer.save()
        patient_serializer = PatientSerializer( patient )

        return Response(patient_serializer.data)