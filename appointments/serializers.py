from rest_framework import serializers
from .models import User, Patient, Doctor

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','role']
        extra_kwargs = {
            'role': {
                'read_only' : True
            }
        }
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['phone', 'birth_date', 'address']
        
        
class DoctorSerializer(serializers.ModelSerializer):

    def validate_user(self, user):
        if user.role != User.Role.DOCTOR:
            raise serializers.ValidationError(
                "Selected user must have doctor role."
            )

        return user

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'phone', 'address']
        read_only_fields = ['id']


    
class PatientRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    phone = serializers.CharField()
    birth_date = serializers.DateField()
    address = serializers.CharField()
    
    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        user = User.objects.create_user(username=username, password=password)
        patient = Patient.objects.create(user=user, **validated_data)
        
        return patient
    