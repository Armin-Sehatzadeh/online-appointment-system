from django.test import TestCase
from rest_framework.test import APITestCase

from .models import User, Patient, Appointment, Availability, Doctor, Holiday, DoctorLeave
# Create your tests here.

class RegisterAPITestCase(APITestCase):
    
    def test_patient_registration(self):
        data = {
            "username": "test_patient",
            "password": "12345678",
            "phone": "09120000000",
            "birth_date": "2000-01-01",
            "address": "Tehran"
        }

        response = self.client.post("/api/register/", data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="test_patient").exists())
        self.assertTrue(Patient.objects.filter(user__username="test_patient").exists())
        
    
    def test_duplicate_username(self):
        data = {
            "username": "test_patient",
            "password": "12345678",
            "phone": "09120000000",
            "birth_date": "2000-01-01",
            "address": "Tehran"
        }

        first_response = self.client.post("/api/register/", data)
        self.assertEqual(first_response.status_code, 200)

        second_response = self.client.post("/api/register/", data)

        self.assertEqual(second_response.status_code, 400)
        self.assertIn("username", second_response.data)


class AppointmentAPITestCase(APITestCase):

    def setUp(self):
        self.patient_user = User.objects.create_user(
            username="appointment_patient",
            password="12345678",
            role="patient"
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            phone="09120000000",
            birth_date="2000-01-01",
            address="Tehran"
        )
        
        self.patient_user_2 = User.objects.create_user(
            username="appointment_patient_2",
            password="12345678",
            role="patient"
        )

        self.patient_2 = Patient.objects.create(
            user=self.patient_user_2,
            phone="09123333333",
            birth_date="2000-02-02",
            address="Tehran"
        )

        self.doctor_user = User.objects.create_user(
            username="appointment_doctor",
            password="12345678",
            role="doctor"
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty="Cardiology",
            phone="09121111111",
            address="Tehran"
        )
        
        self.availability = Availability.objects.create(
        doctor=self.doctor,
        weekday=0,
        start_time="09:00",
        end_time="13:00",
        slot_duration=30
        )
        
        self.holiday = Holiday.objects.create(
        date="2026-09-21",
        reason="Test Holiday"
        )

        self.doctor_leave = DoctorLeave.objects.create(
        doctor=self.doctor,
        date="2026-09-22",
        reason="Doctor vacation"
        )
    
    def test_appointment_on_unavailable_day(self):
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-15",
            "time": "10:00"
        }

        response = self.client.post("/api/appointments/", data)

        self.assertEqual(response.status_code, 400)
        
        
    def test_valid_appointment(self):
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-14",
            "time": "10:00"
        }

        response = self.client.post("/api/appointments/", data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Appointment.objects.filter(doctor=self.doctor, patient=self.patient, date="2026-09-14", time="10:00").exists())
        
    
    def test_duplicate_appointment(self):
        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-14",
            "time": "10:00"
        }

        self.client.force_authenticate(user=self.patient_user)

        first_response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(first_response.status_code, 201)

        self.client.force_authenticate(user=self.patient_user_2)

        second_response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(second_response.status_code, 400)
        
        
    def test_patient_cannot_see_another_patient_appointment(self):
        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-14",
            "time": "10:00"
        }

        self.client.force_authenticate(user=self.patient_user)

        response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(response.status_code, 201)

        appointment_id = response.data["id"]

        self.client.force_authenticate(user=self.patient_user_2)

        response = self.client.get(
            f"/api/appointments/{appointment_id}/"
        )

        self.assertEqual(response.status_code, 404)
        
    
    def test_patient_cannot_update_another_patient_appointment(self):
        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-14",
            "time": "10:00"
        }

        self.client.force_authenticate(user=self.patient_user)

        response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(response.status_code, 201)

        appointment_id = response.data["id"]

        self.client.force_authenticate(user=self.patient_user_2)

        response = self.client.patch(
            f"/api/appointments/{appointment_id}/",
            {"status": "cancelled"}
        )

        self.assertEqual(response.status_code, 404)
        
    
    def test_appointment_on_holiday(self):
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-21",
            "time": "10:00"
        }

        response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "Doctor is not available on a holiday",
            response.data["__all__"]
        )
             
             
    def test_appointment_on_doctor_leave(self):
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "doctor": self.doctor.id,
            "date": "2026-09-22",
            "time": "10:00"
        }

        response = self.client.post(
            "/api/appointments/",
            data
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "Doctor is not available",
            response.data["__all__"]
        )   


class AvailabilityAPITestCase(APITestCase):

    def setUp(self):
        self.patient_user = User.objects.create_user(
            username="availability_patient",
            password="12345678",
            role="patient"
        )

        self.doctor_user = User.objects.create_user(
            username="availability_doctor",
            password="12345678",
            role="doctor"
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty="Cardiology",
            phone="09121111111",
            address="Tehran"
        )
        
        
    def test_patient_can_see_availability(self):
        self.client.force_authenticate(user=self.patient_user)

        Availability.objects.create(
            doctor=self.doctor,
            weekday=0,
            start_time="09:00",
            end_time="13:00",
            slot_duration=30
        )

        response = self.client.get("/api/availabilities/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
    
    def test_patient_cannot_create_availability(self):
        self.client.force_authenticate(user=self.patient_user)

        data = {
            "doctor": self.doctor.id,
            "weekday": 0,
            "start_time": "09:00",
            "end_time": "13:00",
            "slot_duration": 30
        }

        response = self.client.post(
            "/api/availabilities/",
            data
        )

        self.assertEqual(response.status_code, 403)
        
    
    def test_doctor_can_create_availability(self):
        self.client.force_authenticate(user=self.doctor_user)

        data = {
            "weekday": 0,
            "start_time": "09:00",
            "end_time": "13:00",
            "slot_duration": 30
        }

        response = self.client.post(
            "/api/availabilities/",
            data
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Availability.objects.filter(
                doctor=self.doctor,
                weekday=0
            ).exists()
        )
    
    
    def test_doctor_can_only_see_own_availability(self):
        other_doctor_user = User.objects.create_user(
            username="other_doctor",
            password="12345678",
            role="doctor"
        )

        other_doctor = Doctor.objects.create(
            user=other_doctor_user,
            specialty="Neurology",
            phone="09122222222",
            address="Tehran"
        )

        Availability.objects.create(
            doctor=self.doctor,
            weekday=0,
            start_time="09:00",
            end_time="13:00",
            slot_duration=30
        )

        Availability.objects.create(
            doctor=other_doctor,
            weekday=1,
            start_time="10:00",
            end_time="14:00",
            slot_duration=30
        )

        self.client.force_authenticate(user=self.doctor_user)

        response = self.client.get("/api/availabilities/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["doctor"], self.doctor.id)
        
    
    def test_doctor_cannot_update_other_doctors_availability(self):
        other_doctor_user = User.objects.create_user(
            username="other_doctor_update",
            password="12345678",
            role="doctor"
        )

        other_doctor = Doctor.objects.create(
            user=other_doctor_user,
            specialty="Neurology",
            phone="09122222222",
            address="Tehran"
        )

        availability = Availability.objects.create(
            doctor=other_doctor,
            weekday=1,
            start_time="10:00",
            end_time="14:00",
            slot_duration=30
        )

        self.client.force_authenticate(user=self.doctor_user)

        response = self.client.patch(
            f"/api/availabilities/{availability.id}/",
            {"start_time": "11:00"}
        )

        self.assertEqual(response.status_code, 404)
        
    
    def test_invalid_availability_time(self):
        self.client.force_authenticate(user=self.doctor_user)

        data = {
            "weekday": 0,
            "start_time": "13:00",
            "end_time": "09:00",
            "slot_duration": 30
        }

        response = self.client.post(
            "/api/availabilities/",
            data
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "Start time must be before end time.",
            response.data["__all__"]
        )
        
    
    def test_overlapping_availability(self):
        self.client.force_authenticate(user=self.doctor_user)

        Availability.objects.create(
            doctor=self.doctor,
            weekday=0,
            start_time="09:00",
            end_time="13:00",
            slot_duration=30
        )

        data = {
            "weekday": 0,
            "start_time": "11:00",
            "end_time": "15:00",
            "slot_duration": 30
        }

        response = self.client.post(
            "/api/availabilities/",
            data
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "This availability overlaps with an existing availability.",
            response.data["__all__"]
        )
        