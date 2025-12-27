import requests
import json
import logging

# إعدادات الـ Logging
logging.basicConfig(level=logging.INFO)

class GeminiAI:
    def __init__(self):
        self.conversation_history = {}
        # الرابط المباشر للمحرك المطور
        self.api_url = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
        
        # الهيدرز الاحترافية لضمان عدم الحظر
        self.headers = {
            'User-Agent': "Ktor client", 
            'Accept': "application/json", 
            'Content-Type': "application/json", 
            'x-goog-api-key': "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk", 
            'x-goog-api-client': "gl-kotlin/2.2.0-ai fire/16.5.0", 
            'x-firebase-appid': "1:652803432695:android:c4341db6033e62814f33f2", 
            'x-firebase-appversion': "79", 
            'x-firebase-appcheck': "eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ=="
        }

    def chat(self, user_id, user_message, system_prompt="أنت مساعد مبرمج ذكي."):
        """دالة التحدث مع المحرك بذكاء"""
        try:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            history = self.conversation_history[user_id][-4:]
            full_prompt = f"System: {system_prompt}\n\n"
            if history:
                for msg in history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    full_prompt += f"{role}: {msg['content']}\n"
            full_prompt += f"User: {user_message}\nAssistant:"

            payload = {
                "model": "projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite", 
                "contents": [{"role": "user", "parts": [{"text": full_prompt}]}]
            }

            response = requests.post(self.api_url, data=json.dumps(payload), headers=self.headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                ai_reply = result['candidates'][0]['content']['parts'][0]['text'].strip()
                self.conversation_history[user_id].extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_reply}
                ])
                return ai_reply
            return "❌ لم يصل رد من المحرك حالياً."
        except Exception as e:
            logging.error(f"AI Error: {e}")
            return "⚠️ حدث خطأ في معالجة الذكاء."
