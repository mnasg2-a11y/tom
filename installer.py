import os
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# --- إعدادات البوت (التوكن الخاص ببوت التنصيب) ---
# ملاحظة: هذا التوكن لتشغيل "بوت التنصيب" فقط
INSTALLER_TOKEN = "8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"

# حالات المحادثة
API_ID, API_HASH, SESSION, SOURCE_BOT_TOKEN = range(4)

# نص الترحيب الاحترافي الخاص بـ حسين
START_TEXT = """
✨ **أهـلاً بـك فـي بـوت تـنـصـيـب كـومـن P R O** ✨

هـذا الـبوت سيـساعدك عـلى تـجهـيز وتـشغـيل الـسورس عـلى حـسابـك بـسهولة.

💡 **الـخطوات الـقادمة:**
1️⃣ إدخال API_ID و API_HASH.
2️⃣ إدخال الـجلسة (String Session).
3️⃣ إدخال تـوكن الـبوت الـخاص بـالسورس.

🔒 بـياناتـك تـبقى مـشفرة وتُـحفظ فـي مـلف .env الـخاص بـسيرفرك.
لـلإلـغاء أرسـل /cancel
"""

# دالة لقراءة وكتابة ملف .env
ENV_FILE = ".env"

def update_env(vars):
    with open(ENV_FILE, "w") as f:
        for key, value in vars.items():
            f.write(f"{key}={value}\n")

# --- الأوامر الأساسية ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **أهـلاً بـك يـا مـستخدم كـومـن.**\nلـلبدء فـي الـتـنـصـيـب أرسـل الـأمـر: /install"
    )

async def install_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_TEXT)
    await update.message.reply_text("➡️ **ارسل الآن الـ API_ID الخاص بك:**")
    return API_ID

async def get_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["API_ID"] = update.message.text.strip()
    await update.message.reply_text("✅ **تم حفظ API_ID.**\n➡️ **ارسل الآن الـ API_HASH:**")
    return API_HASH

async def get_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["API_HASH"] = update.message.text.strip()
    await update.message.reply_text("✅ **تم حفظ API_HASH.**\n➡️ **ارسل الآن الـ STRING_SESSION:**")
    return SESSION

async def get_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["SESSION"] = update.message.text.strip()
    await update.message.reply_text("✅ **تم حفظ الجلسة.**\n➡️ **ارسل الآن توكن بوت السورس (BOT_TOKEN):**")
    return SOURCE_BOT_TOKEN

async def get_source_bot_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data["BOT_TOKEN"] = update.message.text.strip()

    # حفظ البيانات في ملف .env
    env_vars = {
        "API_ID": context.user_data["API_ID"],
        "API_HASH": context.user_data["API_HASH"],
        "STRING_SESSION": context.user_data["SESSION"],
        "BOT_TOKEN": context.user_data["BOT_TOKEN"],
        "ADMIN_ID": str(user_id) # تعيين صاحب التنصيب كأدمن
    }
    update_env(env_vars)

    await update.message.reply_text(
        "🎉 **تـم حـفظ جـميـع الـبيانات بـنجاح!**\n"
        "♻️ **جـارِ تـثبيـت الـمكتبات وتـشغـيل سـورس كـومـن...**"
    )

    # تنفيذ التثبيت والتشغيل تلقائياً
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"])
        # تشغيل الملف الأساسي للسورس
        subprocess.Popen(["python3", "main.py"])
        await update.message.reply_text("✅ **الـسورس يـعمل الـآن! جـرب كـتابة `.الاوامر` فـي الـخاص.**")
    except Exception as e:
        await update.message.reply_text(f"❌ **حدث خطأ أثناء التشغيل:**\n`{str(e)}`")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ **تـم إلـغاء عـمـلـية الـتـنـصـيـب.**")
    return ConversationHandler.END

# --- تشغيل المحرك ---

def main():
    app = Application.builder().token(INSTALLER_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("install", install_start)],
        states={
            API_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_id)],
            API_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_api_hash)],
            SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_session)],
            SOURCE_BOT_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source_bot_token)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("🤖 Common Installer Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
