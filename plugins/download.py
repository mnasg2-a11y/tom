import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "📥 قـسـم الـتـحـمـيـل الـخـارق"
COMMANDS = (
    "• `.صوت` + الرابط : تـحـمـيـل مـلـف صـوتـي عـالـي الـجـودة\n"
    "• `.فيديو` + الرابط : تـحـمـيـل مـقـطـع فـيـديـو بـأعـلى دقـة\n"
    "• `.تحميل` + الرابط : الـتـحـمـيـل الـتـلـقـائـي (فـيـديـو/صـورة)"
)

# دالة إعدادات التحميل الاحترافية
def get_pro_opts(is_audio=True):
    return {
        "format": "bestaudio/best" if is_audio else "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }] if is_audio else [],
    }

# 1. أمر تحميل الصوت (MP3)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def pro_audio_down(event):
    url = event.pattern_match.group(1)
    if not url:
        return await event.edit("⚠️ **الـرجـاء وضـع رابـط الـمـقـطـع لـتـحـمـيـله كـصـوت.**")
    
    await event.edit("🎵 **جـارِ مـعـالـجـة الـرابـط واسـتـخـراج الـصـوت...**")
    
    try:
        # استخدام asyncio.to_thread لمنع تعليق السورس أثناء التحميل
        def download():
            with yt_dlp.YoutubeDL(get_pro_opts(True)) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3", info['title']

        file_path, title = await asyncio.to_thread(download)
        
        await event.edit(f"📤 **تـم الـتـحـضـيـر! جـارِ رفـع: {title}**")
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **تـم تـحـمـيـل الـصـوت بـنـجـاح**\n📌 `{title}`",
            reply_to=event.reply_to_msg_id
        )
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خـطأ فـي الـتـحـمـيـل:**\n`{str(e)[:150]}`")

# 2. أمر تحميل الفيديو (MP4)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def pro_video_down(event):
    url = event.pattern_match.group(1)
    if not url:
        return await event.edit("⚠️ **الـرجـاء وضـع رابـط الـفـيـديـو.**")
    
    await event.edit("🎬 **جـارِ تـحـمـيـل الـفـيـديـو بـأعـلى جـودة مـتـاحـة...**")
    
    try:
        def download():
            with yt_dlp.YoutubeDL(get_pro_opts(False)) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info), info['title']

        file_path, title = await asyncio.to_thread(download)
        
        await event.edit(f"📤 **جـارِ رفـع الـفـيـديـو: {title}**")
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **تـم تـحـمـيـل الـفـيـديـو بـنـجـاح**\n🎬 `{title}`",
            reply_to=event.reply_to_msg_id
        )
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **فـشـل الـتـحـمـيـل:**\n`{str(e)[:150]}`")

# 3. أمر التحميل الذكي (تلقائي)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحميل (.*)'))
async def smart_down(event):
    url = event.pattern_match.group(1)
    await event.edit("🚀 **جـارِ الـفـحـص والـتـحـمـيـل الـتـلـقـائـي...**")
    # يقوم بتحميل الفيديو كخيار افتراضي ذكي
    await pro_video_down(event)
