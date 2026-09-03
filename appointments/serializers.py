from rest_framework import serializers
from .models import User, Patient

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
    