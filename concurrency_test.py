import requests
import threading

def create_appointment(token):
    url = "http://127.0.0.1:8000/api/appointments/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    data = {
        "doctor": 4,
        "date": "2026-10-05",
        "time": "11:00:00"
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print(response.status_code)
    print(response.json())
    
token1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg5MzY0NjczLCJpYXQiOjE3ODkzNjQzNzMsImp0aSI6ImU5NTdjM2Y3NzY0ZjRiNTFhMDFmZjY3YzJmY2EzZTVlIiwidXNlcl9pZCI6IjEwIn0.mJi6UQ5ErbYthL-AIf7bhQIy8qu7SOpaBqiwfsXtDts"
token2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg5MzY0Njk4LCJpYXQiOjE3ODkzNjQzOTgsImp0aSI6IjZhZWU1N2IxMGVmYzQ0ODViNzI3MTEzOThiNzY3ZTI2IiwidXNlcl9pZCI6IjEzIn0.SbNjuZa6Z_vfUzZbDohtO9nxV2iHAzndQSwM-tCvc4g"

thread1 = threading.Thread(
    target=create_appointment,
    args=(token1,)
)

thread2 = threading.Thread(
    target=create_appointment,
    args=(token2,)
)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
