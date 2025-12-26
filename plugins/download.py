import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "📥 مـحـرك الـتـحـمـيـل والـبـحـث الشامل"
COMMANDS = (
    "• `.بحث_فيد` + الاسم : بـحث عـن فـيـديـو وتـحـمـيـلـه فـوراً\n"
    "• `.بحث_صوت` + الاسم : بـحث عـن مـقـطـع وتـحـمـيـلـه MP3\n"
    "• `.تحميل_فيد` + الرابط : تـحـمـيـل فـيـديـو مـن أي مـنـصـة\n"
    "• `.تحميل_صوت` + الرابط : تـحـمـيـل صـوت MP3 مـن أي مـنـصـة"
)

# دالة إعدادات التحميل الاحترافية
def get_ytdl_settings(is_audio=False, is_search=False):
    query = "ytsearch1:" if is_search else ""
    opts = {
        "format": "bestaudio/best" if is_audio else "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "addmetadata": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    if is_audio:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    return opts

async def run_download(event, url, opts, title_prefix=""):
    try:
        def download_process():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'entries' in info: # في حالة البحث
                    info = info['entries'][0]
                filename = ydl.prepare_filename(info)
                if opts.get("postprocessors"):
                    filename = filename.rsplit(".", 1)[0] + ".mp3"
                return filename, info.get('title', 'Unknown')

        file_path, title = await asyncio.to_thread(download_process)
        
        await event.edit(f"📤 **جـارِ رفـع: {title}...**")
        await client.send_file(
            event.chat_id, 
            file_path, 
            caption=f"✅ **{title_prefix} بـنـجـاح**\n📌 `{title}`",
            reply_to=event.reply_to_msg_id
        )
        await event.delete()
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خـطأ:**\n`{str(e)[:100]}`")

# 1. بحث وتحميل فيديو
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def search_vid(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن فـيـديـو: `{query}`...**")
    await run_download(event, f"ytsearch1:{query}", get_ytdl_settings(False), "تـم تـحـمـيـل الـفـيـديـو")

# 2. بحث وتحميل صوت
@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def search_aud(event):
    query = event.pattern_match.group(1)
    await event.edit(f"🔍 **جـارِ الـبـحـث عـن صـوت: `{query}`...**")
    await run_download(event, f"ytsearch1:{query}", get_ytdl_settings(True), "تـم تـحـمـيـل الـصـوت")

# 3. تحميل فيديو برابط
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحميل_فيد (.*)'))
async def link_vid(event):
    url = event.pattern_match.group(1)
    await event.edit("🎬 **جـارِ تـحـمـيـل الـفـيـديـو مـن الـرابـط...**")
    await run_download(event, url, get_ytdl_settings(False), "تـم تـحـمـيـل الـفـيـديـو")

# 4. تحميل صوت برابط
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تحميل_صوت (.*)'))
async def link_aud(event):
    url = event.pattern_match.group(1)
    await event.edit("🎵 **جـارِ تـحـمـيـل الـصـوت مـن الـرابـط...**")
    await run_download(event, url, get_ytdl_settings(True), "تـم تـحـمـيـل الـصـوت")
