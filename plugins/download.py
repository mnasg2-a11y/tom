import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events, types
from __main__ import client #

os.environ['SSL_CERT_FILE'] = certifi.where()

def get_pro_opts(is_audio=False, hook=None):
    # **هنا التعديل المهم**: أجبر تحميل mp4 فقط
    if not is_audio:
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',  # هذا مهم
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
        }
    else:
        return {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
        }

def progress_bar(current, total):
    percentage = (current * 100) / total
    blocks = int(percentage / 10)
    bar = "█" * blocks + "░" * (10 - blocks)
    return f"[{bar}] {percentage:.1f}%"

def pro_hook(d, event, loop, last_upd):
    if d['status'] == 'downloading':
        curr = time.time()
        if curr - last_upd[0] > 2.5:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                bar = progress_bar(downloaded, total)
                speed = d.get('_speed_str', 'N/A')
                loop.create_task(event.edit(f"⏳ **جـاري التحميل...**\n\n{bar}\n🚀 **السرعة:** `{speed}`"))
                last_upd[0] = curr

async def universal_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("📡 **جاري فحص الرابط...**")
    last_upd = [time.time()]
    loop = asyncio.get_event_loop()
    
    if "spotify.com" in url:
        is_search = True
        await event.edit("🎧 **رابط Spotify.. جاري البحث...**")

    try:
        def start():
            target = f"ytsearch1:{url}" if is_search else url
            hook = lambda d: pro_hook(d, event, loop, last_upd)
            with yt_dlp.YoutubeDL(get_pro_opts(is_audio, hook)) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info: info = info['entries'][0]
                path = ydl.prepare_filename(info)
                # تأكد من أن الفيديو بصيغة mp4
                if not is_audio:
                    if not path.endswith('.mp4'):
                        new_path = path.rsplit(".", 1)[0] + ".mp4"
                        os.rename(path, new_path)
                        path = new_path
                return path, info

        file_path, info = await asyncio.to_thread(start)
        await event.edit("📤 **تم التحميل! جاري الرفع...**")
        
        if not is_audio:
            # **إرسال الفيديو مع وصف فيديو صريح**
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **{info.get('title', 'فيديو')[:50]}**",
                supports_streaming=True,
                attributes=[
                    types.DocumentAttributeVideo(
                        duration=info.get('duration', 0),
                        w=info.get('width', 1280),
                        h=info.get('height', 720),
                        supports_streaming=True
                    )
                ]
            )
        else:
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **{info.get('title', 'صوت')[:50]}**"
            )
        
        await event.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خطأ:**\n`{str(e)[:100]}`")

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
      🎬 **مركز تحميل كومن Pro**
╚════════════════════╝

**التحميل (YT, Spotify, TikTok, FB):**
• `.فيديو` + الرابط
• `.صوت` + الرابط

**البحث والتحميل:**
• `.بحث_فيد` + الاسم
• `.بحث_صوت` + الاسم""")
