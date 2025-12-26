import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "📥 والـبـحـثـمـيـل الـتـحـمـيـل والـبـحـث الشامل"
COMMANDS = (
    "• `.بحث_فيد` + الاسم : بـحث عـن فـيـديـو وتـحـمـيـلـه فـوراً\n"
    "• `.بحث_صوت` + الاسم : بـحث عـن مـقـطـع وتـحـمـيـلـه MP3\n"
    "• `.فيديو` + الرابط : تـحـمـيـل فـيـديـو مـن أي مـنـصـة\n"
    "• `.صوت` + الرابط : تـحـمـيـل صـوت MP3 مـن أي مـنـصـة"
)

# دالة إعدادات التحميل الاحترافية لتجنب الحظر
def get_safe_settings(is_audio=False):
    opts = {
        "format": "bestaudio/best" if is_audio else "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "referer": "https://www.google.com/",
    }
    if is_audio:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    return opts

async def run_common_download(event, url, is_audio=False):
    try:
        def download_process():
            with yt_dlp.YoutubeDL(get_safe_settings(is_audio)) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info: # معالجة نتائج البحث
                    info = info['entries'][0]
                filename = ydl.prepare_filename(info)
                if is_audio:
                    filename = filename.rsplit(".", 1)[0] + ".mp3"
                return filename, info.get('title', 'Unknown')

        file_path, title = await asyncio.to_thread(download_process)
        
        if not os.path.exists(file_path):
             return await event.edit("❌ **فـشـل الـتـحـمـيـل: الـمـوقـع حـظر الاتـصـال حـالـياً.**")

        await event.edit(f"📤 **جـارِ رفـع: {title}...**")
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **تـم تـحـمـيـل الـطـلـب بـنـجـاح**\n📌 `{title}`",
            reply_to=event.reply_to_msg_id
        )
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **حـدث خـطأ فـي الـمـحـرك:**\n`{str(e)[:100]}`")

# 1. بحث وتحميل فيديو بالاسم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def search_vid_pro(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن فـيـديـو: `{query}`...**")
    await run_common_download(event, f"ytsearch1:{query}", False)

# 2. بحث وتحميل صوت بالاسم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def search_aud_pro(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن صـوت: `{query}`...**")
    await run_common_download(event, f"ytsearch1:{query}", True)

# 3. تحميل فيديو برابط مباشر (أي منصة)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def link_vid_pro(event):
    url = event.pattern_match.group(1)
    await event.edit("🎬 **جـارِ تـحـمـيـل الـفـيـديـو مـن الـرابـط بـالنظام الآمـن...**")
    await run_common_download(event, url, False)

# 4. تحميل صوت برابط مباشر (أي منصة)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def link_aud_pro(event):
    url = event.pattern_match.group(1)
    await event.edit("🎵 **جـارِ تـحـمـيـل الـصـوت مـن الـرابـط بـالنظام الآمـن...**")
    await run_common_download(event, url, True)
