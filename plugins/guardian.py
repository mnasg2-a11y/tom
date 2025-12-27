import asyncio
from telethon import events
from __main__ import client # استيراد العميل الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🛡️ قـسـم الـحـمـايـة والـخـصـوصـيـة"
COMMANDS = "• `.حمايتي` : لـعـرض لـوحـة الـتـحـكـم الـأمـنـيـة لـلـحـسـاب"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.حمايتي'))
async def security_dashboard(event):
    # جلب الإعدادات من كائن البوت الخاص بك
    # ملاحظة: الكود يفترض وجود كائن مستخدم نشط للوصول للـ config
    dashboard = (
        "╔════════════════════╗\n"
        "      **🛡️ درع كـومـن  P R O**\n"
        "╚════════════════════╝\n\n"
        "🔒 **إدارة نـظام الـخصوصية والـحماية:**\n\n"
        "1️⃣ `.شبح` : تـفعيل/تـعطيل وضع الـتخفي (عـدم الـقراءة)\n"
        "2️⃣ `.حفظ_المؤقت` : تـفعيل حـفظ الـميديا ذاتـية الـتدمير\n"
        "3️⃣ `.رد_الخاص` : تـفعيل الـرد الـتلقائي عـلى الـرسائل\n"
        "4️⃣ `.منع_السبام` : حـظر الـمتطفلين بـشكل تـلقائي\n"
        "5️⃣ `.كشف_الحساب` : فـحص الـ DC وتـاريخ الـإنشاء (OSINT)\n"
        "───━━━━─ ● ─━━━━───\n"
        "✅ **الـحالة:** الـنظام يـعمل بـأعلى مـعايير الـتشفير\n"
        "💎 **S O U R C E  C O M M O N**"
    )
    await event.edit(dashboard)

# --- تفعيل الأوامر الـ 5 الفرعية بناءً على منطق ملفك ---

@client.on(events.NewMessage(outgoing=True, pattern=r'\.شبح'))
async def toggle_ghost(event):
    # استخدام متغير الخصوصية من ملفك
    from التعديل_من_جديد import active_userbots
    me_id = (await client.get_me()).id
    bot = active_userbots[me_id]['userbot']
    bot.config['ghost'] = not bot.config['ghost']
    status = "مـفـعـل ✅" if bot.config['ghost'] else "مـعـطـل ❌"
    await event.edit(f"👻 **وضـع الـشـبح (إخـفاء الـقراءة):** `{status}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.حفظ_المؤقت'))
async def toggle_autosave(event):
    from التعديل_من_جديد import active_userbots
    me_id = (await client.get_me()).id
    bot = active_userbots[me_id]['userbot']
    bot.config['auto_save'] = not bot.config['auto_save']
    status = "مـفـعـل ✅" if bot.config['auto_save'] else "مـعـط_ل ❌"
    await event.edit(f"💾 **حـفظ الـميديا الـمؤقتة:** `{status}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.رد_الخاص'))
async def toggle_reply(event):
    from التعديل_من_جديد import active_userbots
    me_id = (await client.get_me()).id
    bot = active_userbots[me_id]['userbot']
    bot.config['reply'] = not bot.config['reply']
    status = "مـفـعـل ✅" if bot.config['reply'] else "مـعـطـل ❌"
    await event.edit(f"📨 **الـرد الـتـلقائي عـلى الـخاص:** `{status}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.منع_السبام'))
async def toggle_autoblock(event):
    from التعديل_من_جديد import active_userbots
    me_id = (await client.get_me()).id
    bot = active_userbots[me_id]['userbot']
    bot.config['auto_block'] = not bot.config['auto_block']
    status = "مـفـعـل ✅" if bot.config['auto_block'] else "مـعـطـل ❌"
    await event.edit(f"🛡 **حـظر الـسبام الـتـلـقائي:** `{status}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.كشف_الحساب'))
async def check_account_osint(event):
    await event.edit("🔍 **جـارِ كـشـف الـبـيـانـات الـأمـنـيـة...**")
    me = await client.get_me()
    full = await client(functions.users.GetFullUserRequest(me.id))
    dc_id = me.photo.dc_id if me.photo else "غـير مـعروف"
    msg = (
        f"🛡 **تـقـرير الـحـمـايـة لـحـسابك:**\n\n"
        f"🆔 **الايدي:** `{me.id}`\n"
        f"📡 **مـركز الـبيانات (DC):** `{dc_id}`\n"
        f"💎 **بـريميوم:** `{'نـعم' if me.premium else 'لـا'}`\n"
        f"📅 **الـسيرة الـذاتية:** `{full.full_user.about}`"
    )
    await event.edit(msg)
