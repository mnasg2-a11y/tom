import os
import sys
import subprocess
import logging

# =========================================================
# 📦 المرحلة 1: الفحص والتثبيت الآلي للمكتبات
# =========================================================
def setup_environment():
    print("⏳ جـارِ تـنـظـيـف وتـهـيـئـة الـبـيـئـة الـبـرمـجـيـة...")
    libraries = ["python-telegram-bot", "telethon", "aiohttp", "requests", "urllib3==1.26.15"]
    for lib in libraries:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
    print("✅ تـم تـجـهـيـز الـمـكـتـبـات بـنـجـاح.")

setup_environment()

# استيراد المكاتب بعد التأكد من صحتها
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# =========================================================
# 🧠 المرحلة 2: إصلاح ملف الذكاء (لحل مشكلة Pydroid)
# =========================================================
ai_fix = """
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
        except: return "⚠️ الـمـحـرك مـشـغـول حـالـيـاً."
"""
with open("common_ai.py", "w", encoding="utf-8") as f:
    f.write(ai_fix) # إنشاء الملف بالاسم الصحيح لتجنب ModuleNotFoundError

# =========================================================
# 📲 المرحلة 3: بوت التنصيب والاتصال
# =========================================================

BOT_TOKEN = "6729948368:8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"
API_ID, API_HASH, SESSION, SOURCE_TOKEN = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **أهـلاً يـا حـسـيـن! الـنـظـام جـاهـز 100%.**\n"
        "تـم حـل جـمـيـع مـشـاكـل الـاسـتـيـراد والـمـكـتـبـات تـلـقـائـيـاً.\n\n"
        "أرسـل /install لـتـشـغـيـل الـسورس الـآن."
    )

async def install_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("➡️ **ارسل الـ API_ID الـخاص بـك:**")
    return API_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["id"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم. ارسل الـ API_HASH:")
    return API_HASH

async def get_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hash"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم. ارسل الـ STRING_SESSION:")
    return SESSION

async def get_sess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sess"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم. ارسل تـوكـن بـوت الـسورس:")
    return SOURCE_TOKEN

async def finalize_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    # حـفـظ الـبـيـانـات فـي مـلـف الـتـهـيـئـة
    with open(".env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\nAPI_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\nBOT_TOKEN={token}\n")
    
    await update.message.reply_text("🚀 **جـارِ تـشـغـيـل سـورس كـومـن وجـلـب جـمـيـع الـأوامـر...**")
    
    # تـشـغـيـل الـمـحـرك الـأسـاسـي
    subprocess.Popen([sys.executable, "main.py"])
    await update.message.reply_text("✅ **الـسـورس يـعـمـل الـآن! اكـتـب .الاوامر فـي حـسـابـك.**")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("install", install_init)],
        states={
            API_ID: [MessageHandler(filters.TEXT, get_id)],
            API_HASH: [MessageHandler(filters.TEXT, get_hash)],
            SESSION: [MessageHandler(filters.TEXT, get_sess)],
            SOURCE_TOKEN: [MessageHandler(filters.TEXT, finalize_setup)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    print("🚀 مـنـظـومـة كـومـن تـعـمـل الـآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
