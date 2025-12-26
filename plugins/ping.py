from telethon import events
from telethon import TelegramClient

# العميل سيتم حقنه تلقائياً
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فحص'))
async def ping_handler(event):
    await event.edit("✅ **تمت الاستجابة بنجاح من داخل ملف الـ Plugins!**\n\n"
                    "السورس الآن يعمل بشكل صحيح من الـ plugins.")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ايدي'))
async def id_handler(event):
    await event.edit(f"👤 **ايديك هو:** `{event.sender_id}`")
