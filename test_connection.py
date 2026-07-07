import os
import requests
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()  # reads the .env file and loads GROQ_API_KEY into the environment

api_key = os.environ.get("GROQ_API_KEY")
#api_key = os.environ.get("GROQ_API_KEY")
print("Key loaded:", api_key)   # temporary debug line

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Say hello and confirm you're working!"}]
    }
)

data = response.json()
print(data)