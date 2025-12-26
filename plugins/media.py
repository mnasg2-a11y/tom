import os
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🖼️ أدوات الـمـيـديـا الـمـطـورة"
COMMANDS = (
    "• `.ملصق` : تـحـويـل أي صـورة إلـى مـلـصـق فـوري\n"
    "• `.لصورة` : تـحـويـل الـمـلـصـق إلـى صـورة فـوتـوغـرافـيـة\n"
    "• `.حفظ` : حـفـظ الـمـيـديـا (ذاتـيـة الـتـدمـيـر) بـسـريـة"
)

# 1. تحويل الصورة إلى ملصق
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ملصق'))
async def image_to_sticker(event):
    reply = await event.get_reply_message()
    if not reply or not reply.photo:
        return await event.edit("⚠️ **يـجـب الـرد عـلـى صـورة لـتـحـويـلـهـا.**")
    
    await event.edit("🎨 **جـارِ تـحـويـل الـصـورة إلـى مـلـصـق...**")
    path = await reply.download_media()
    await event.delete()
    await client.send_file(event.chat_id, path, force_document=False)
    if os.path.exists(path): os.remove(path)

# 2. تحويل الملصق إلى صورة
@client.on(events.NewMessage(outgoing=True, pattern=r'\.لصورة'))
async def sticker_to_image(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sticker:
        return await event.edit("⚠️ **يـجـب الـرد عـلـى مـلـصـق لـتـحـويـلـه.**")
    
    await event.edit("🖼️ **جـارِ تـحـويـل الـمـلـصـق إلـى صـورة...**")
    path = await reply.download_media()
    await event.delete()
    await client.send_file(event.chat_id, path, force_document=False)
    if os.path.exists(path): os.remove(path)

# 3. حفظ الميديا ذاتية التدمير
@client.on(events.NewMessage(outgoing=True, pattern=r'\.حفظ'))
async def save_media(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.edit("⚠️ **الـرجـاء الـرد عـلـى مـيـديـا لـحـفـظـهـا.**")
    
    await event.edit("💾 **جـارِ سـحـب الـمـيـديـا وحـفـظـهـا بـأمـان...**")
    path = await reply.download_media()
    await client.send_file("me", path, caption="✅ **تـم حـفـظ الـمـيـديـا بـنـجـاح بـواسطـة Common Pro**")
    await event.edit("✅ **تـم الـحـفـظ فـي الـرسـائـل الـمـحـفـوظـة!**")
    if os.path.exists(path): os.remove(path)
