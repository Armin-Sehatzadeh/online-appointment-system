from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        DOCTOR = 'doctor', 'Doctor'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )

    def __str__(self):
        return self.username
    

class Doctor(models.Model):
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE
    )
    specialty = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"DR. {self.user.username}"
    
    
class Patient(models.Model):
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=50)
    birth_date = models.DateField()
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.username}"
    