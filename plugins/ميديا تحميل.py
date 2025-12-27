import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events
from __main__ import client #

os.environ['SSL_CERT_FILE'] = certifi.where()

SECTION_NAME = "🚀 مـحـرك الـتـحـمـيـل الـعـالـمـي"
COMMANDS = "• `.ميديا` : لـوحـة الـتـحـمـيـل الـشـامـلـة"

def get_pro_opts(is_audio=False):
    return {
        'format': 'bestaudio/best' if is_audio else 'best[height<=720]',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'source_address': '0.0.0.0',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'referer': 'https://www.google.com/',
    }

async def universal_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("⚡ **جاري فحص الرابط...**")
    
    if "spotify.com" in url:
        is_search = True
        await event.edit("🎧 **جاري البحث...**")

    try:
        def start():
            target = f"ytsearch1:{url}" if is_search else url
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio)) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info: 
                    info = info['entries'][0]
                path = ydl.prepare_filename(info)
                if is_audio:
                    new_path = path.rsplit(".", 1)[0] + ".mp3"
                    if os.path.exists(path): 
                        os.rename(path, new_path)
                    path = new_path
                return path, info

        file_path, info = await asyncio.to_thread(start)
        await event.edit("🚀 **تم التحميل! جاري الرفع...**")
        
        # الحصول على العنوان بشكل آمن
        title = info.get('title', 'ميديا')
        if title and len(title) > 40:
            title = title[:40]
        
        # **الحل النهائي**: إرسال كفيديو مباشر
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **{title}**\n💎 **S O U R C E  C O M M O N**",
            video=not is_audio,  # هذا السطر هو التعديل المطلوب
            supports_streaming=True
        )
        
        await event.delete()
        if os.path.exists(file_path): 
            os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خطأ:** `{str(e)[:100]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def v_d(event): 
    await universal_downloader(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def a_d(event): 
    await universal_downloader(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def s_v(event): 
    await universal_downloader(event, event.pattern_match.group(1), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def s_a(event): 
    await universal_downloader(event, event.pattern_match.group(1), True, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def m_m(event):
    await event.edit("""╔════════════════════╗
      ⚡ **محرك تحميل كومن الصاروخي**
╚════════════════════╝

**التحميل (جميع المنصات):**
• `.فيديو` + الرابط
• `.صوت` + الرابط

**البحث السريع:**
• `.بحث_فيد` + الاسم
• `.بحث_صوت` + الاسم""")
