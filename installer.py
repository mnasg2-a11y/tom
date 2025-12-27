import os
import sys
import subprocess

# حل مشكلة timezone
os.environ['TZ'] = 'Asia/Riyadh'

print("⏳ تـحـضـيـر الـبـيـئـة لـ Termux...")

# تأكد من تثبيت pytz لحل مشكلة timezone
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytz"])
    print("✅ تـم تـثـبيـت pytz")
except:
    print("⚠️ pytz مـثـبـت مـسـبـقـاً")

# =========================================================
# 🔴 🔴 🔴 ضع توكن البوت الصحيح هنا 🔴 🔴 🔴
BOT_TOKEN = "8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"  # من @BotFather
# =========================================================

# استيراد المكتبات بعد التأكد
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

API_ID, API_HASH, SESSION, SOURCE_TOKEN = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **نـظـام تـنـصـيب Common جـاهـز**\n"
        "اكـتـب /install لـبـدء الـتـنـصـيب"
    )

async def install_init(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 أرسـل الـ API_ID:")
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
    
    # حفظ البيانات
    with open(".env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\n")
        f.write(f"API_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\n")
        f.write(f"BOT_TOKEN={token}\n")
    
    await update.message.reply_text("⚡ جـاري تـشـغـيـل الـسـورس...")
    
    # تشغيل main.py
    try:
        subprocess.Popen([sys.executable, "main.py"])
        await update.message.reply_text("🎉 **تـم تـنـصـيب Common بـنـجـاح!**")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خـطـأ: {str(e)}")
    
    return ConversationHandler.END

def main():
    if BOT_TOKEN == "ضع_التوكن_الجديد_هنا":
        print("❌ **يجب وضع توكن البوت أولاً!**")
        print("🔹 اذهب إلى @BotFather")
        print("🔹 أنشئ بوت جديد")
        print("🔹 ضع التوكن في السطر 19")
        return
    
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
        
        print("🤖 البوت يعمل...")
        print(f"🔗 رابط البوت: https://t.me/{BOT_TOKEN.split(':')[0]}_bot")
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()
