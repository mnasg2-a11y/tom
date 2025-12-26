import os
import sys
from telethon import events
from __main__ import client

SECTION_NAME = "🔄 قـسـم الـتـحـديـث"
COMMANDS = "• `.تحديث` : لـجـلـب آخـر الأوامـر مـن جـيـت هـاب وإعـادة الـتـشـغـيل"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث'))
async def update_handler(event):
    await event.edit("🔄 **جـارِ فـحـص الـتـحـديـثـات وسـحـب الأوامـر الـجـديـدة...**")
    
    # سحب التحديثات من جيت هاب
    os.system("git pull")
    
    await event.edit("✅ **تـم سـحـب الـتـحـديـثـات! جـارِ إعادة تـشـغـيـل الـسـورس...**")
    
    # إعادة تشغيل الملف الأساسي دون فقدان الجلسة
    os.execl(sys.executable, sys.executable, *sys.argv)
