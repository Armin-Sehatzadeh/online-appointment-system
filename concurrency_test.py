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
    
token1 = "token1"
token2 = "token2"

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
