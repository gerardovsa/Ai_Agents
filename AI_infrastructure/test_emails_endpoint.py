import urllib.request
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMiwiZW1haWwiOiJnZXJhcmRvQHZldHN1Y2Nlc3NhY2FkZW15LmNvbSIsInVzZXJuYW1lIjoiZ2VyYXJkbyIsImV4cCI6MTc3NzY0NTcyNH0.JcUicGqX55T4loe1RgYLaHRfttYIQDfuh3LmKDr-ffw"

req = urllib.request.Request(
    "https://ai-agents-v10.onrender.com/api/communication-hub/emails?limit=5",
    headers={"Authorization": f"Bearer {token}"}
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode()
        print(f"STATUS: {resp.status}")
        data = json.loads(body)
        print(f"Keys: {list(data.keys())}")
        print(f"Email count: {data.get('count', 'N/A')}")
        print(f"Has gmail: {data.get('has_gmail', 'N/A')}")
        print(f"Success: {data.get('success', 'N/A')}")
        if data.get('error'):
            print(f"Error: {data.get('error')}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP ERROR {e.code}: {body[:500]}")
except Exception as ex:
    print(f"Exception: {ex}")
