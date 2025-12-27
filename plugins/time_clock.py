import asyncio
import time
from datetime import datetime
import pytz
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from __main__ import client #

# --- بيانات القسم للوحة الأوامر ---
SECTION_NAME = "⏰ قـسـم الـوقـت والـهـويـة"
COMMANDS = "• `.وقتي` : لـعـرض لـوحـة الـتـحـكـم الـزمـنـيـة الـخـمـاسـيـة"

# متغيرات النظام
CLOCK_RUNNING = False
START_TIME = time.time()

# 1. محرك الساعة التلقائية (يجلب اسمك تلقائياً ويضيف الوقت)
async def name_clock_engine():
    global CLOCK_RUNNING
    tz = pytz.timezone('Asia/Baghdad') # توقيت العراق
    last_min = ""
    
    # جلب الاسم الأصلي للحساب عند التشغيل لأول مرة
    me = await client.get_me()
    original_name = me.first_name
    
    while CLOCK_RUNNING:
        now = datetime.now(tz)
        current_min = now.strftime("%I:%M %p")
        
        if current_min != last_min:
            try:
                # تحديث الاسم: (اسمك الحالي | الوقت)
                new_display_name = f"{original_name} | {current_min}"
                await client(UpdateProfileRequest(first_name=new_display_name))
                last_min = current_min
            except Exception:
                pass 
        await asyncio.sleep(30) # فحص كل 30 ثانية

# --- الأمر الرئيسي: .وقتي ---

@client.on(events.NewMessage(outgoing=True, pattern=r'\.وقتي'))
async def time_master_menu(event):
    menu_text = (
        "╔════════════════════╗\n"
        "      **⏰ مـنـظـم الـوقـت الـاحـتـرافـي**\n"
        "╚════════════════════╝\n\n"
        "1️⃣ `.تفعيل_ساعة` : تـحـديـث اسـمـك بـالـوقـت تـلـقـائـيـاً\n"
        "2️⃣ `.الوقت` : عـرض الـسـاعـة والـتـاريـخ (الـعـراق)\n"
        "3️⃣ `.مؤقت` + ثواني : مـنـبـه تـنـازلـي ذكـي\n"
        "4️⃣ `.تذكير` + دقائق + نص : مـسـاعـدك الـشـخـصـي\n"
        "5️⃣ `.المدة` : وقـت تـشـغـيل سـورس كـومـن Pro\n"
        "───━━━━─ ● ─━━━━───\n"
        "💎 **S O U R C E  C O M M O N**"
    )
    await event.edit(menu_text)

# --- تفعيل الأوامر الخمسة ---

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تفعيل_ساعة'))
async def toggle_clock(event):
    global CLOCK_RUNNING
    if not CLOCK_RUNNING:
        CLOCK_RUNNING = True
        asyncio.create_task(name_clock_engine()) #
        await event.edit("✅ **تـم تـفـعـيل سـاعة الاسـم بـنـجـاح.**")
    else:
        CLOCK_RUNNING = False
        # إرجاع الاسم للأصل عند الإطفاء
        me = await client.get_me()
        clean_name = me.first_name.split(" | ")[0]
        await client(UpdateProfileRequest(first_name=clean_name))
        await event.edit("❌ **تـم تـعـطـيل سـاعة الاسـم.**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الوقت'))
async def show_iraq_time(event):
    tz = pytz.timezone('Asia/Baghdad')
    now = datetime.now(tz)
    await event.edit(f"🇮🇶 **تـوقـيت الـعـراق الـآن:**\n`{now.strftime('%I:%M:%S %p')}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.مؤقت (\d+)'))
async def timer_cmd(event):
    secs = int(event.pattern_match.group(1))
    await event.edit(f"⏳ **مـؤقـت لـمـدة {secs} ثانية...**")
    await asyncio.sleep(secs)
    await event.respond("🔔 **انـتـهى الـوقـت الـمـحدد!**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تذكير (\d+) (.*)'))
async def remind_cmd(event):
    mins = int(event.pattern_match.group(1))
    reason = event.pattern_match.group(2)
    await event.edit(f"📌 **سـأذكـرك بـعـد {mins} دقـيـقة.**")
    await asyncio.sleep(mins * 60)
    await event.respond(f"💡 **تـذكـيـر:** `{reason}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.المدة'))
async def uptime_cmd(event):
    uptime_sec = int(time.time() - START_TIME)
    mins, secs = divmod(uptime_sec, 60)
    await event.edit(f"🚀 **مـدة تـشـغـيل الـسـورس:** `{mins}` دقـيـقـة و `{secs}` ثـانـية.")
