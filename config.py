# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # بيانات API
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    STRING_SESSION = os.getenv("STRING_SESSION", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # إعدادات أخرى
    SUDO_USERS = [123456789]  # أرقام المطورين
    PREFIX = "."  # بادئة الأوامر
