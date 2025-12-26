import os
import yt_dlp
import asyncio
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "📥 قـسـم الـتـحـمـيـل الـشـامـل"
COMMANDS = (
    "• `.صوتي` <رابط> : تـحـمـيل مـلـف صـوتـي مـن أي مـنـصـة\n"
    "• `.فيديو` <رابط> : تـحـمـيل مـقـطـع فـيـديـو مـن أي مـنـصـة\n"
    "• `.بحث_صوت` <عنوان> : الـبـحث والـتـحـمـيل بـالاسـم فـقـط"
)

# إعدادات yt-dlp الأساسية
def get_ytdl_opts(is_audio=True):
    opts = {
        "format": "bestaudio/best" if is_audio else "best",
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
    }
    if is_audio:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    return opts

# 1. أمر تحميل الصوت بالرابط
@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوتي (.*)'))
async def down_audio(event):
    url = event.pattern_match.group(1)
    if not url:
        return await event.edit("⚠️ **الـرجـاء وضـع رابـط الـمـقـطـع الصـوتـي.**")
    
    await event.edit("🎵 **جـارِ تـحـضـيـر مـلـف الـصـوت...**")
    
    try:
        with yt_dlp.YoutubeDL(get_ytdl_opts(True)) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).replace(".m4a", ".mp3").replace(".webm", ".mp3")
            
            await event.edit("📤 **جـارِ الـرفـع إلـى تـلـيـجـرام...**")
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **تـم تـحـمـيل الـصـوت:**\n📌 `{info['title']}`",
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ أثـنـاء الـتـحـمـيل:**\n`{str(e)[:100]}`")

# 2. أمر تحميل الفيديو بالرابط
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def down_video(event):
    url = event.pattern_match.group(1)
    if not url:
        return await event.edit("⚠️ **الـرجـاء وضـع رابـط الـفـيـديـو.**")
    
    await event.edit("🎬 **جـارِ تـحـمـيل الـفـيـديـو، انـتـظـر قـلـيـلاً...**")
    
    try:
        with yt_dlp.YoutubeDL(get_ytdl_opts(False)) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            await event.edit("📤 **جـارِ رفـع الـفـيـديـو الآن...**")
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **تـم تـحـمـيل الـفـيـديـو:**\n🎬 `{info['title']}`",
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **فـشـل الـتـحـمـيل:**\n`{str(e)[:100]}`")

# 3. أمر البحث والتحميل بالاسم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def search_audio(event):
    query = event.pattern_match.group(1)
    if not query:
        return await event.edit("⚠️ **اكـتـب عـنـوان الـمـقـطـع للـبـحـث عـنـه.**")
    
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن `{query}`...**")
    
    try:
        search_url = f"ytsearch1:{query}"
        with yt_dlp.YoutubeDL(get_ytdl_opts(True)) as ydl:
            info = ydl.extract_info(search_url, download=True)['entries'][0]
            file_path = ydl.prepare_filename(info).replace(".m4a", ".mp3").replace(".webm", ".mp3")
            
            await event.edit("📤 **جـارِ الـرفـع...**")
            await client.send_file(
                event.chat_id, 
                file_path, 
                caption=f"✅ **نـتـيـجـة الـبـحـث والـتـحـمـيل:**\n📌 `{info['title']}`",
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **لـم يـتـم الـعـثـور عـلى نـتـائـج:**\n`{str(e)[:100]}`")
