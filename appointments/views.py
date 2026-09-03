from django.shortcuts import render
from rest_framework import views, permissions
from rest_framework.response import Response

# Create your views here.


class View(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            "username": request.user.username
        })
    