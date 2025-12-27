import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# تـوكـن بـوت الـتـنـصـيـب الخاص بـك
BOT_TOKEN = "8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU"

# الـحـالـات
API_ID, API_HASH, SESSION, SOURCE_TOKEN = range(4)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 أهـلاً بـك يـا حـسـيـن! لـلـتـنـصـيـب أرسـل /install")

async def install_begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 **بـدء تـنـصـيـب كـومـن PRO...**\n\nارسل الـ API_ID:")
    return API_ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id'] = update.message.text
    await update.message.reply_text("✅ تـم. ارسل الـ API_HASH:")
    return API_HASH

async def get_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['hash'] = update.message.text
    await update.message.reply_text("✅ تـم. ارسل الـ STRING_SESSION:")
    return SESSION

async def get_sess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sess'] = update.message.text
    await update.message.reply_text("✅ تـم. ارسل تـوكـن بـوت الـسورس:")
    return SOURCE_TOKEN

async def finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text
    # كـتـابـة الـفارات تـلقائـيـاً
    with open(".env", "w") as f:
        f.write(f"API_ID={context.user_data['id']}\nAPI_HASH={context.user_data['hash']}\n")
        f.write(f"STRING_SESSION={context.user_data['sess']}\nBOT_TOKEN={token}\n")
    
    await update.message.reply_text("⚙️ **جـارِ تـثـبـيـت الـمـكـتـبات وتـشغـيـل الـسورس...**")
    
    # حـل مـشـكـلـة الـمـكـتـبات تـلـقـائـيـاً
    subprocess.run(["pip", "install", "urllib3==1.26.15", "telethon", "aiohttp"])
    
    # تـشغـيـل الـسورس
    subprocess.Popen(["python3", "main.py"])
    await update.message.reply_text("✅ **تـم الـتـشغـيـل! الـآن جـرب الـأوامـر فـي حـسابـك.**")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("install", install_begin)],
        states={
            API_ID: [MessageHandler(filters.TEXT, get_id)],
            API_HASH: [MessageHandler(filters.TEXT, get_hash)],
            SESSION: [MessageHandler(filters.TEXT, get_sess)],
            SOURCE_TOKEN: [MessageHandler(filters.TEXT, finalize)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__": main()
