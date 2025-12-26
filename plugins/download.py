import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client # استيراد العميل الأساسي

# --- إعدادات القسم للوحة التلقائية ---
SECTION_NAME = "🚀 مـركـز الـتـحـمـيـل الـسـريـع"
COMMANDS = "• `.ميديا` : لـعـرض كـافـة خـيـارات الـتـحـمـيـل والـبـحـث"

# إعدادات yt-dlp المحسنة للسرعة القصوى وتجاوز الحظر
def get_fast_opts(is_audio=False):
    return {
        'format': 'bestaudio/best' if is_audio else 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'no_warnings': True,
        'quiet': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

# 1. الأمر الرئيسي (لوحة التحكم)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def media_hub(event):
    await event.edit("""
╔════════════════════╗
      **🎬 مـركـز مـيـديـا كـومـن Pro**
╚════════════════════╝

**📥 أوامر التحميل المباشر:**
• `.فيديو` <رابط> : تـحـمـيل فـيـديـو سـريـع
• `.صوت` <رابط> : تـحـمـيل مـلـف صـوتـي

**🔍 أوامر البحث والتحميل:**
• `.بحث_فيد` <اسم> : تـحـمـيل أول نـتـيـجـة فـيـديـو
• `.بحث_صوت` <اسم> : تـحـمـيل أول نـتـيـجـة صـوت

───━━━━─ ● ─━━━━───
🚀 **السرعة:** فـائـقـة (uvloop Active)
💎 **المطور:** @iomk0 | **القناة:** @iomk3
""")

# دالة التحميل المشتركة فائقة السرعة
async def download_engine(event, url, audio=False):
    try:
        def start_down():
            with yt_dlp.YoutubeDL(get_fast_opts(audio)) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info: info = info['entries'][0]
                return ydl.prepare_filename(info), info.get('title', 'Common_File')

        # تشغيل التحميل في خيط منفصل لعدم تعليق السورس
        path, title = await asyncio.to_thread(start_down)
        
        await event.edit(f"📤 **جـارِ رفـع: {title}...**")
        await client.send_file(event.chat_id, path, caption=f"✅ **تـم الـتـحـمـيـل بـنـجـاح**\n📌 `{title}`")
        await event.delete()
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        await event.edit(f"❌ **خـطأ:** `{str(e)[:50]}`")

# --- محركات التشغيل الخلفية ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def dv(event): await download_engine(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def da(event): await download_engine(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def sv(event): await download_engine(event, f"ytsearch1:{event.pattern_match.group(1)}", False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def sa(event): await download_engine(event, f"ytsearch1:{event.pattern_match.group(1)}", True)
