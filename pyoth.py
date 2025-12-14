import requests
import json

API_KEY = ""

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful travel assistant."
        },
        {
            "role": "user",
            "content": "Plan a 3-day trip to Goa"
        }
    ],
    "stream": False
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    print("✅ Perplexity reply:\n")
    print(reply)
else:
    print("❌ Error")
    print("Status:", response.status_code)
    print("Response:", response.text)
