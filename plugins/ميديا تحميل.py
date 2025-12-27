import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events
from __main__ import client #

os.environ['SSL_CERT_FILE'] = certifi.where()

def get_pro_opts(is_audio=False, hook=None):
    return {
        'format': 'bestaudio/best' if is_audio else 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'user_agent': 'Mozilla/5.0',
    }

def progress_hook(d, event, loop, last_update_time):
    """شريط بسيط بدون تعقيد"""
    if d['status'] == 'downloading':
        current = time.time()
        if current - last_update_time[0] > 2:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            
            if total and total > 0:
                percent = (downloaded * 100) / total
                bar_length = 10
                filled = int(bar_length * percent // 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                speed = d.get('_speed_str', 'N/A')
                
                message = f"""
📥 **تحميل:** {bar} {percent:.1f}%
📊 **السرعة:** {speed}
                """
                
                loop.create_task(event.edit(message.strip()))
                last_update_time[0] = current

async def universal_downloader(event, url, is_audio=False, is_search=False):
    await event.edit("🔍 **جاري التحضير...**")
    
    if not url or len(url.strip()) == 0:
        await event.edit("❌ **الرجاء إدخال رابط أو كلمة للبحث**")
        return
    
    last_update_time = [time.time()]
    loop = asyncio.get_event_loop()
    
    try:
        def download():
            # تحديد الهدف (بحث أم رابط)
            if is_search or not url.startswith(('http://', 'https://')):
                target = f"ytsearch1:{url}"
            else:
                target = url
            
            hook = lambda d: progress_hook(d, event, loop, last_update_time)
            
            opts = get_pro_opts(is_audio, hook)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(target, download=True)
                
                # التعامل مع نتائج البحث
                if isinstance(info, dict) and 'entries' in info:
                    entries = [e for e in info['entries'] if e]
                    if entries:
                        info = entries[0]
                    else:
                        raise Exception("لم يتم العثور على نتائج")
                
                path = ydl.prepare_filename(info)
                
                # تحويل الصوت لـ mp3
                if is_audio and not path.endswith('.mp3'):
                    base_name = os.path.splitext(path)[0]
                    new_path = base_name + '.mp3'
                    if os.path.exists(path):
                        os.rename(path, new_path)
                    path = new_path
                
                return path, info

        file_path, info = await asyncio.to_thread(download)
        
        # الحصول على العنوان
        title = info.get('title', 'ملف')
        if len(title) > 50:
            title = title[:47] + "..."
        
        await event.edit("📤 **جاري الرفع...**")
        
        # إرسال الملف
        await client.send_file(
            event.chat_id,
            file_path,
            caption=f"✅ **{title}**\n💎 **S O U R C E  C O M M O N**",
            video=not is_audio,
            supports_streaming=True if not is_audio else False
        )
        
        await event.delete()
        
        # تنظيف الملف
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        error_msg = str(e)
        if "Unsupported URL" in error_msg:
            await event.edit("❌ **الرابط غير مدعوم**")
        elif "Video unavailable" in error_msg:
            await event.edit("❌ **الفيديو غير متاح**")
        else:
            await event.edit(f"❌ **خطأ:** `{error_msg[:80]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def video_cmd(event):
    url = event.pattern_match.group(1).strip()
    if url:
        await universal_downloader(event, url, False, False)
    else:
        await event.edit("❌ **الرجاء إدخال رابط**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def audio_cmd(event):
    url = event.pattern_match.group(1).strip()
    if url:
        await universal_downloader(event, url, True, False)
    else:
        await event.edit("❌ **الرجاء إدخال رابط**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def search_video_cmd(event):
    query = event.pattern_match.group(1).strip()
    if query:
        await universal_downloader(event, query, False, True)
    else:
        await event.edit("❌ **الرجاء إدخال كلمة للبحث**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def search_audio_cmd(event):
    query = event.pattern_match.group(1).strip()
    if query:
        await universal_downloader(event, query, True, True)
    else:
        await event.edit("❌ **الرجاء إدخال كلمة للبحث**")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def media_help(event):
    help_text = """
🎬 **أوامر التحميل:**

📹 **تحميل فيديو:**
`.فيديو` + الرابط

🎵 **تحميل صوت:**
`.صوت` + الرابط

🔍 **بحث وتحميل:**
`.بحث_فيد` + الكلمة
`.بحث_صوت` + الكلمة

✅ **يدعم:** YouTube، TikTok، Twitter، Instagram، وغيرها
    """
    await event.edit(help_text.strip())
