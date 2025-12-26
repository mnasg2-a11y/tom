import os
import asyncio
import yt_dlp
from telethon import events
from __main__ import client 

# بيانات القسم
SECTION_NAME = "📥 مـحـرك الـتـحـمـيـل الـعـالـمـي"
COMMANDS = (
    "• `.فيديو` + الرابط : تـحـمـيـل مـن تـيـك تـوك، يـوتـيـوب، انـسـتـا\n"
    "• `.صوت` + الرابط : تـحـمـيـل MP3 بـأعـلـى جـودة"
)

# إعدادات متطورة لتجنب الحظر (403 Forbidden)
def get_safe_opts(is_audio=False):
    opts = {
        'format': 'bestaudio/best' if is_audio else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'no_warnings': True,
        'quiet': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        # هذه الرؤوس توهم الموقع أنك متصفح حقيقي
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }
    if is_audio:
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    return opts

async def run_pro_download(event, url, is_audio=False):
    try:
        def proc():
            with yt_dlp.YoutubeDL(get_safe_opts(is_audio)) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if is_audio:
                    filename = filename.rsplit(".", 1)[0] + ".mp3"
                return filename, info.get('title', 'Video')

        file_path, title = await asyncio.to_thread(proc)
        
        if not os.path.exists(file_path):
            return await event.edit("❌ **فـشـل الـتـحـمـيـل: الـمـوقـع حـظر الاتـصـال حـالـياً.**")

        await event.edit(f"📤 **جـارِ الـرفـع: {title}...**")
        await client.send_file(event.chat_id, file_path, caption=f"✅ **تـم تـحـمـيـل الـطـلـب**\n📌 `{title}`")
        await event.delete()
        os.remove(file_path)
    except Exception as e:
        await event.edit(f"❌ **خـطأ فـي الـمـحـرك:**\n`{str(e)[:100]}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def down_v(event):
    url = event.pattern_match.group(1)
    await event.edit("🎬 **جـارِ الـتـحـمـيـل بـالـنـظـام الآمـن...**")
    await run_pro_download(event, url, False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def down_a(event):
    url = event.pattern_match.group(1)
    await event.edit("🎵 **جـارِ سـحـب الـصـوت بـالـنـظـام الآمـن...**")
    await run_pro_download(event, url, True)
