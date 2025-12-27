import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events
from __main__ import client #

# إعداد شهادات الأمان لمنع خطأ Errno 7
os.environ['SSL_CERT_FILE'] = certifi.where()

SECTION_NAME = "🚀 مـحـرك الـتـحـمـيـل الـعـالـمـي"
COMMANDS = "• `.ميديا` : لـوحـة الـتـحـمـيـل الـشـامـلـة"

def get_pro_opts(is_audio=False, hook=None):
    return {
        'format': 'bestaudio/best' if is_audio else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'source_address': '0.0.0.0', # حل مشكلة No address associated
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'progress_hooks': [hook] if hook else [],
    }

def progress_bar(current, total):
    percentage = (current * 100) / total
    blocks = int(percentage / 10)
    bar = "█" * blocks + "░" * (10 - blocks)
    return f"[{bar}] {percentage:.1f}%"

def pro_hook(d, event, loop, last_upd):
    if d['status'] == 'downloading':
        curr = time.time()
        if curr - last_upd[0] > 2.5: # تحديث كل 2.5 ثانية لتجنب الحظر
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                bar = progress_bar(downloaded, total)
                speed = d.get('_speed_str', 'N/A')
                loop.create_task(event.edit(f"⏳ **جـارِ الـتـحـمـيـل الـحـقـيـقـي...**\n\n{bar}\n🚀 **الـسـرعـة:** `{speed}`"))
                last_upd[0] = curr

async def universal_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("📡 **جـارِ فـحـص الـرابـط وتـجـاوز الـقـيـود...**")
    last_upd = [time.time()]
    loop = asyncio.get_event_loop()
    
    # دعم Spotify عبر البحث التلقائي
    if "spotify.com" in url:
        is_search = True
        await event.edit("🎧 **رابـط Spotify.. جـارِ الـبـحـث فـي YouTube Music...**")

    try:
        def start():
            target = f"ytsearch1:{url}" if is_search else url
            hook = lambda d: pro_hook(d, event, loop, last_upd)
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio, hook)) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info: info = info['entries'][0]
                path = ydl.prepare_filename(info)
                if is_audio:
                    new_path = path.rsplit(".", 1)[0] + ".mp3"
                    if os.path.exists(path): os.rename(path, new_path)
                    path = new_path
                return path, info

        file_path, info = await asyncio.to_thread(start)
        await event.edit("📤 **تـم الـتـحـمـيـل! جـارِ الـرفـع الـآن...**")
        
        await client.send_file(event.chat_id, file_path, caption=f"✅ **تـم الـتـحـمـيـل بـنـجـاح**\n📌 `{info.get('title')[:50]}`\n💎 **S O U R C E  C O M M O N**", video_note=False, supports_streaming=False)
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خـطأ فـي الـمـحـرك:**\n`{str(e)[:150]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def v_d(event): await universal_downloader(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def a_d(event): await universal_downloader(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def s_v(event): await universal_downloader(event, event.pattern_match.group(1), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def s_a(event): await universal_downloader(event, event.pattern_match.group(1), True, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def m_m(event):
    await event.edit("╔════════════════════╗\n      **🎬 مـركـز تـحـمـيـل كـومـن Pro**\n╚════════════════════╝\n\n**الـتـحـمـيـل (YT, Spotify, TikTok, FB):**\n• `.فيديو` + الرابط\n• `.صوت` + الرابط\n\n**الـبـحـث والـتـحـمـيـل:**\n• `.بحث_فيد` + الاسم\n• `.بحث_صوت` + الاسم")
