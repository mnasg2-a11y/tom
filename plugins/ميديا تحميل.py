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
    # **تسريع التحميل**: تحميل فقط الجودة الأساسية
    if is_audio:
        return {
            'format': 'bestaudio[filesize<50M]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': '0',
        }
    else:
        return {
            'format': 'best[height<=720][filesize<100M]/best[height<=480]',  # تحميل سريع
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'concurrent_fragment_downloads': 5,  # تحميل متعدد
            'external_downloader': 'aria2c',  # أسرع
            'external_downloader_args': ['--max-connection-per-server=16', '--split=16'],
        }

async def universal_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("⚡ **جاري التحميل بسرعة الصاروخ...**")
    
    if "spotify.com" in url:
        is_search = True
        await event.edit("🎧 **جاري البحث عن الموسيقى...**")

    try:
        def start():
            target = f"ytsearch1:{url}" if is_search else url
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio)) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info: 
                    info = info['entries'][0]
                path = ydl.prepare_filename(info)
                if is_audio and not path.endswith('.mp3'):
                    new_path = path.rsplit(".", 1)[0] + ".mp3"
                    if os.path.exists(path): 
                        os.rename(path, new_path)
                    path = new_path
                return path, info

        file_path, info = await asyncio.to_thread(start)
        await event.edit("🚀 **تم التحميل! جاري الرفع...**")
        
        # **الحل النهائي**: إرسال كفيديو مباشر
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **{info.get('title', 'ميديا')[:40]}**\n💎 **S O U R C E  C O M M O N**",
            video=not is_audio,  # هذا يحدد إذا كان فيديو أو لا
            supports_streaming=True if not is_audio else False
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
