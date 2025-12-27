import requests
import json

class GeminiAI:
    def __init__(self):
        self.api_url = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
        self.headers = {
            'Content-Type': "application/json", 
            'x-goog-api-key': "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk", 
            'x-firebase-appid': "1:652803432695:android:c4341db6033e62814f33f2"
        }

    def chat(self, user_id, message):
        payload = {"contents": [{"role": "user", "parts": [{"text": message}]}]}
        try:
            res = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        except: return "⚠️ عـذراً، الـمـحـرك مـشـغـول."
