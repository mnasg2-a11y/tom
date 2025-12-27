import os
import sys
import subprocess
import logging

# =========================================================
# 🛠 الخطوة 1: فحص وتثبيت المكتبات تلقائياً
# =========================================================
def install_requirements():
    print("⏳ جارِ فحص وتحديث المكتبات لضمان أفضل أداء...")
    reqs = ["python-telegram-bot", "telethon", "aiohttp", "requests", "urllib3==1.26.15"]
    for req in reqs:
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    print("✅ تم تجهيز البيئة البرمجية بنجاح.")

install_requirements()

# الآن نستورد المكاتب بعد التأكد من تثبيتها
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# =========================================================
# 🧠 الخطوة 2: إنشاء ملف الذكاء الاصطناعي (لحل مشكلة Pydroid)
# =========================================================
ai_code = """
import requests
class GeminiAI:
    def __init__(self):
        self.api_url = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
        self.headers = {'Content-Type': 'application/json', 'x-goog-api-key': 'AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk'}
    def chat(self, text):
        payload = {"contents": [{"role": "user", "parts": [{"text": text}]}]}
        try:
            res = requests.post(self.api_url, json=payload, headers=self.headers, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        except: return "⚠️ المحرك مشغول."
"""
with open("common_ai.py", "w", encoding="utf-8") as f:
    f.write(ai_code)

# =========================================================
# 📲 الخطوة 3: بوت التنصيب وجلب الأوامر
# =========================================================

# توكن بوت التنصيب الخاص بك
BOT_TOKEN = "6729948368:8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"
# حالات المحادثة
API_ID, API_HASH, SESSION, SOURCE_BOT_TOKEN = range(4)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **أهلاً بك يا مبرمج حسين في نظام كومن الشامل!**\n\n"
        "تم حل جميع مشاكل المكتبات والأسماء تلقائياً.\n"
        "أرسل /install للبدء في تشغيل السورس."
    )

async def install_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("➡️ **ارسل الآن الـ API_ID الخاص بك:**")
    return API_ID

async def get_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["id"] = update.message.text.strip()
    await update.message.reply_text("✅ تم الحفظ. ارسل الـ API_HASH:")
    return API_HASH

async def get_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hash"] = update.message.text.strip()
    await update.message.reply_text("✅ تم الحفظ. ارسل الـ STRING_SESSION:")
    return SESSION

async def get_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sess"] = update.message.text.strip()
    await update.message.reply_text("✅ تم الحفظ. ارسل الآن توكن بوت السورس:")
    return SOURCE_BOT_TOKEN

async def finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["token"] = update.message.text.strip()
    
    # كتابة الفارات في ملف .env
    with open(".env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\nAPI_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\nBOT_TOKEN={context.user_data['token']}\n")
    
    await update.message.reply_text("🎉 **تم التجهيز! جاري تشغيل سورس كومن وجلب الأوامر...**")
    
    # تشغيل السورس (main.py)
    subprocess.Popen([sys.executable, "main.py"])
    await update.message.reply_text("✅ **السورس يعمل الآن! جرب كتابة .الاوامر في حسابك.**")
    return ConversationHandler.END

# تشغيل محرك البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("install", install_start)],
        states={
            API_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_id)],
            API_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_hash)],
            SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_session)],
            SOURCE_BOT_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalize)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    print("🚀 المنظومة الشاملة تعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
