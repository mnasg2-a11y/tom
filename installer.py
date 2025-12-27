import os
import sys
import subprocess
import asyncio

# =========================================================
# 📦 المرحلة 1: تثبيت المكتبات بأمان
# =========================================================
def setup_environment():
    print("⏳ جـارِ تـهيـئـة الـبـيـئـة...")
    libraries = ["python-telegram-bot", "telethon", "aiohttp", "requests"]
    for lib in libraries:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"✅ تـم تـثـبيـت {lib}")
        except:
            print(f"⚠️ خـطـأ فـي تـثـبيـت {lib}")
    
    print("✅ الـتـهيـئـة اكـتـمـلـت.")

setup_environment()

# =========================================================
# 🧠 المرحلة 2: ذكاء اصطناعي يعمل
# =========================================================
ai_code = '''
import google.generativeai as genai

class GeminiAI:
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def chat(self, text):
        try:
            response = self.model.generate_content(text)
            return response.text if response.text else "⚠️ لـم أحـصـل عـلـى رد"
        except Exception as e:
            return f"⚠️ خـطـأ: {str(e)}"

# إنشاء نسخة افتراضية
ai = GeminiAI()
'''

with open("ai_module.py", "w", encoding="utf-8") as f:
    f.write(ai_code)

# =========================================================
# 📲 المرحلة 3: بوت التنصيب المعدّل
# =========================================================
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# 🔴 استبدل هذا بالتوكين الصحيح من BotFather
BOT_TOKEN = "8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"  # مثال: "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
API_ID, API_HASH, SESSION, SOURCE_TOKEN = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **أهـلاً! نـظـام التـنـصـيب جـاهـز**\n"
        "أرسـل /install لـبـدء إعـداد الـسـورس"
    )

async def install_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("➡️ **أرسـل الـ API_ID:**")
    return API_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["id"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم، أرسـل الـ API_HASH:")
    return API_HASH

async def get_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hash"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم، أرسـل الـ STRING_SESSION:")
    return SESSION

async def get_sess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sess"] = update.message.text.strip()
    await update.message.reply_text("✅ تـم، أرسـل تـوكـن بـوت الـسـورس:")
    return SOURCE_TOKEN

async def finalize_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    
    # حفظ البيانات في ملف
    with open(".env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\n")
        f.write(f"API_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\n")
        f.write(f"BOT_TOKEN={token}\n")
    
    await update.message.reply_text("🚀 **جـاري تـشـغـيـل الـسـورس...**")
    
    # تشغيل الملف الرئيسي
    try:
        subprocess.Popen([sys.executable, "main.py"])
        await update.message.reply_text("✅ **تـم تـنـصـيب الـسـورس بـنـجـاح!**")
    except:
        await update.message.reply_text("⚠️ **خـطـأ فـي تـشـغـيـل main.py**")
    
    return ConversationHandler.END

def main():
    try:
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
        
        print("🤖 البوت يعمل الآن...")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
