import os
import asyncio
import yt_dlp
import time
from telethon import events
from __main__ import client 

# --- بيانات القسم ---
SECTION_NAME = "🚀 مـحـرك الـتـحـمـيـل الـعـالـمـي"
COMMANDS = "• `.ميديا` : لـوحـة الـتـحـمـيـل (YT, Spotify, TikTok, Music)"

# دالة لتنسيق شريط التحميل الحقيقي
def progress_bar(current, total):
    percentage = current * 100 / total
    finished_blocks = int(percentage / 10)
    unfinished_blocks = 10 - finished_blocks
    bar = "█" * finished_blocks + "░" * unfinished_blocks
    return f"[{bar}] {percentage:.1f}%"

# دالة معالجة التقدم (تحديث الرسالة بالتحميل الحقيقي)
def progress_hook(d, event, loop, last_update_time):
    if d['status'] == 'downloading':
        current_time = time.time()
        # تحديث الرسالة كل ثانيتين لتجنب حظر التليجرام (Flood Wait)
        if current_time - last_update_time[0] > 2:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                bar = progress_bar(downloaded, total)
                speed = d.get('_speed_str', '0KB/s')
                msg = f"⏳ **جـارِ الـتـحـمـيـل الـحـقـيـقـي...**\n\n{bar}\n🚀 **الـسـرعـة:** `{speed}`"
                loop.create_task(event.edit(msg))
                last_update_time[0] = current_time

# إعدادات التحميل الآمنة والشاملة (تجاوز 403 وحل مشكلة Spotify/YT Music)
def get_safe_opts(is_audio=False, hook=None):
    opts = {
        'format': 'bestaudio/best' if is_audio else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'progress_hooks': [hook] if hook else [],
    }
    if is_audio:
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    return opts

async def pro_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("🔍 **جـارِ فـحـص الـرابـط وتـجـاوز الـقـيـود...**")
    
    last_update = [time.time()]
    loop = asyncio.get_event_loop()
    
    # معالجة روابط سبوتيفاي (تحويلها لبحث في يوتيوب ميوزك تلقائياً)
    if "spotify.com" in url:
        is_search = True
        await event.edit("🎧 **رابط Spotify.. جـارِ جـلـب الـمـقـطع مـن YouTube Music...**")

    try:
        def run_ydl():
            target = f"ytsearch1:{url}" if is_search else url
            hook = lambda d: progress_hook(d, event, loop, last_update)
            with yt_dlp.YoutubeDL(get_safe_opts(is_audio, hook)) as ydl:
                info = ydl.extract_info(target, download=True)
                if 'entries' in info: info = info['entries'][0]
                path = ydl.prepare_filename(info)
                if is_audio: path = path.rsplit(".", 1)[0] + ".mp3"
                return path, info
        
        file_path, info = await asyncio.to_thread(run_ydl)
        
        await event.edit("📤 **تـم الـتـحـمـيـل! جـارِ الـرفع الـآن...**")
        
        caption = (
            f"✅ **تـم تـحـمـيـل الـطـلـب بـواسطـة Common**\n"
            f"───━━━━─ ● ─━━━━───\n"
            f"📌 **الـعـنـوان:** `{info.get('title')[:50]}`\n"
            f"🎬 **الـمـنـصـة:** {info.get('extractor_key', 'Direct Link')}\n"
            f"───━━━━─ ● ─━━━━───\n"
            f"💎 **S O U R C E  C O M M O N**"
        )
        
        await client.send_file(event.chat_id, file_path, caption=caption, reply_to=event.reply_to_msg_id)
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ فـي الـمـحـرك:**\n`{str(e)[:150]}`")

# --- الأوامر الموحدة ---
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def media_menu(event):
    await event.edit("╔════════════════════╗\n      **🎬 لـوحـة تـحـمـيـل كـومـن Pro**\n╚════════════════════╝\n\n**الـتـحـمـيـل مـن (YT, Spotify, TikTok, FB):**\n• `.فيديو` + الرابط\n• `.صوت` + الرابط\n\n**الـبـحـث والـتـحـمـيـل الـفـوري:**\n• `.بحث_فيد` + الاسم\n• `.بحث_صوت` + الاسم")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def d_v(event): await pro_downloader(event, event.pattern_match.group(1), False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def d_a(event): await pro_downloader(event, event.pattern_match.group(1), True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def s_v(event): await pro_downloader(event, event.pattern_match.group(1), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def s_a(event): await pro_downloader(event, event.pattern_match.group(1), True, True)
