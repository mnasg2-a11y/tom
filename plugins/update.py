# plugins/update.py
import os, sys, subprocess
from telethon import events
from __main__ import client

SECTION_NAME = "🔄 قـسـم الـتـحـديـث"
COMMANDS = "• `.تحديث` : لـجـلـب الأوامـر الـجـديـدة بـدون فـصـل الـجـلسة"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث'))
async def update_bot(event):
    await event.edit("🔄 **جـارِ الـتـحـديـث... سـيـبـقى الـحـسـاب مـتـصلاً.**")
    
    try:
        # جلب الكود الجديد فقط
        subprocess.check_output(["git", "pull"])
        
        # إعادة تشغيل السورس برمجياً (سيقرأ ملف .env الموجود مسبقاً)
        await event.edit("✅ **تـم الـتـحـديـث! جـارِ إعادة الـتـشـغـيـل الـتـلـقـائـي...**")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await event.edit(f"❌ **فشل التحديث:**\n`{e}`")
