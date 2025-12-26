import os, sys, subprocess
from telethon import events
from __main__ import client

SECTION_NAME = "🔄 قـسـم الـتـحـديـث"
COMMANDS = "• `.تحديث` : جـلـب الأوامـر الـجـديـدة وإعـادة الـتـشـغـيل"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحديث'))
async def update_source(event):
    await event.edit("🔄 **جـارِ جـلـب الـتـحـديـثـات مـن GitHub...**")
    
    try:
        # سحب التحديثات (تأكد من تنصيب git في الترمكس)
        subprocess.check_output(["git", "pull"])
        await event.edit("✅ **تـم سـحـب الأوامر بنجاح! جـارِ إعـادة الـتـشـغـيل...**")
        
        # إعادة تشغيل السورس فوراً
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await event.edit(f"❌ **فـشـل الـتـحديث:**\n`{str(e)}`")
