import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# توكن بوت التنصيب
BOT_TOKEN = "6729948368:8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"
GITHUB_REPO = "https://github.com/mnasg2-a11y/tom.git" # رابط سورسك

API_ID, API_HASH, SESSION, SOURCE_TOKEN = range(4)

async def finalize_and_deploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_token = update.message.text.strip()
    user_id = update.effective_user.id
    path = f"source_{user_id}"

    await update.message.reply_text("📥 **جـارِ سـحـب آخـر إصـدار مـن GitHub وتـنـصـيـب الـمـكـتـبـات...**")

    # 1. سحب السورس من جيثب لضمان جلب كل الـ plugins
    subprocess.run(["git", "clone", GITHUB_REPO, path])
    
    # 2. إنشاء ملف الإعدادات داخل مجلد المستخدم
    with open(f"{path}/.env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\nAPI_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\nBOT_TOKEN={user_token}\n")

    # 3. تثبيت المكتبات وتشغيل المحرك الأساسي
    subprocess.run(["pip", "install", "-r", f"{path}/requirements.txt"])
    subprocess.Popen(["python3", f"{path}/main.py"], cwd=path)

    await update.message.reply_text("✅ **تـم الـتـنـصـيـب بـنـجـاح!**\nكـل الـأوامـر والـإضافات تـم جـلـبـها مـن الـمـحـرك تـلـقـائـيـاً.")
    return ConversationHandler.END
