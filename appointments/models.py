from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


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
    
    
class Availability(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"
    
    start_time = models.TimeField()
    end_time = models.TimeField()       
    slot_duration = models.IntegerField() 
    weekday = models.IntegerField(choices=Weekday.choices)
    
    def clean(self):
        
        if self.start_time >= self.end_time:
            raise ValidationError(
                'Start time must be before end time.'
            )

        if self.slot_duration <= 0:
            raise ValidationError(
                'Slot duration must be greater than zero.'
            )
            
        duration = (
            self.end_time.hour * 60
            + self.end_time.minute
        ) - (
            self.start_time.hour * 60
            + self.start_time.minute
        )
        
        if duration % self.slot_duration != 0:
            raise ValidationError('Slot duration must divide the working time exactly.')
        
        
        existing = Availability.objects.filter(
            doctor=self.doctor,
            weekday=self.weekday   
        )
        
        if self.pk:
            existing = existing.exclude(pk=self.pk)
            
        for availability in existing:
            if (
                self.start_time < availability.end_time
                and
                self.end_time > availability.start_time
            ):
                raise ValidationError('This availability overlaps with an existing availability.')
    
    
    def __str__(self):
        return f"{self.doctor} - {self.Weekday(self.weekday).label} - {self.start_time} to {self.end_time}"
        
        
class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        
        
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
    
    date = models.DateField()
    time = models.TimeField()
    
    status = models.CharField(choices= Status.choices, default=Status.PENDING, max_length=50)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'],
                name= 'unique_doctor_appointment_slot'
            )
        ]
        
    
    def clean(self):
        availabilities = Availability.objects.filter(
            doctor = self.doctor,
            weekday = self.date.weekday()
        )
        
        if not availabilities.exists():
            raise ValidationError('Doctor is not available on this day.')
        
        
        valid = False

        for availability in availabilities:
            if availability.start_time <= self.time < availability.end_time:
                valid = True

                difference = (
                    self.time.hour * 60 + self.time.minute
                ) - (
                    availability.start_time.hour * 60
                    + availability.start_time.minute
                )

                if difference % availability.slot_duration != 0:
                    raise ValidationError(
                        'Appointment time is not a valid slot.'
                    )

                break

        if not valid:
            raise ValidationError(
                'Appointment time is outside doctor availability.'
            )
        
    def __str__(self):
        return f"{self.doctor} - {self.patient} - {self.date} - {self.time}"
    