from rest_framework import serializers
from .models import User, Patient, Doctor, Availability, Appointment
from django.core.exceptions import ValidationError


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
    
    
class AvailabilitySerializer(serializers.ModelSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if not request or getattr(request.user, 'role', None) != User.Role.ADMIN:
            self.fields['doctor'].read_only = True

    def create(self, validated_data):
        
        availability = Availability(**validated_data)
        try:
            availability.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        availability.save()
        return availability
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance

    class Meta:
        model = Availability
        fields = ['id', 'doctor', 'weekday', 'start_time', 'end_time', 'slot_duration']
        read_only_fields = ['id']
        
        
class AppointmentSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        if request:
            if request.user.role == User.Role.PATIENT:
                self.fields['patient'].read_only = True

            elif request.user.role == User.Role.DOCTOR:
                self.fields['doctor'].read_only = True
                self.fields['patient'].read_only = True

    def create(self, validated_data):

        appointment = Appointment(**validated_data)

        try:
            appointment.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        appointment.save()
        return appointment

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'date', 'time', 'status']
        